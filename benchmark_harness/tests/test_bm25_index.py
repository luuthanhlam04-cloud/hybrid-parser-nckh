import json

import pytest

from benchmark_harness.core.bm25_index import BM25Index
from benchmark_harness.core.bm25_index import IndexedDocument
from benchmark_harness.core.dense_index import DenseIndex, reciprocal_rank_fusion
from benchmark_harness.run_retrieval_benchmark import (
    calculate_recall_mrr,
    validate_ground_truth,
)


def write_corpus(path, rows):
    path.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")


def test_build_persist_and_load_index(tmp_path):
    corpus_path = tmp_path / "corpus.json"
    index_path = tmp_path / "index" / "bm25.json"
    write_corpus(
        corpus_path,
        [
            {"article_id": "law#1", "text": "Người sử dụng đất được cấp giấy chứng nhận."},
            {"article_id": "law#2", "text": "Tổ chức phải nộp thuế theo quy định."},
        ],
    )

    built_index, rebuilt = BM25Index.build_or_load(corpus_path, index_path)
    loaded_index, rebuilt_again = BM25Index.build_or_load(corpus_path, index_path)

    assert rebuilt is True
    assert rebuilt_again is False
    assert index_path.is_file()
    assert loaded_index.retrieve("cấp giấy chứng nhận", top_k=1) == (
        built_index.retrieve("cấp giấy chứng nhận", top_k=1)
    )
    assert (
        loaded_index.retrieve("cấp giấy chứng nhận", top_k=1)[0]["article_id"]
        == "law#1"
    )


def test_changed_corpus_rebuilds_index(tmp_path):
    corpus_path = tmp_path / "corpus.json"
    index_path = tmp_path / "index.json"
    write_corpus(corpus_path, [{"article_id": "law#1", "text": "Điều khoản một."}])
    BM25Index.build_or_load(corpus_path, index_path)

    write_corpus(corpus_path, [{"article_id": "law#2", "text": "Điều khoản hai."}])
    rebuilt_index, rebuilt = BM25Index.build_or_load(corpus_path, index_path)

    assert rebuilt is True
    assert [document.article_id for document in rebuilt_index.documents] == ["law#2"]


def test_rejects_duplicate_article_ids(tmp_path):
    corpus_path = tmp_path / "corpus.json"
    write_corpus(
        corpus_path,
        [
            {"article_id": "law#1", "text": "Điều khoản một."},
            {"article_id": "law#1", "text": "Điều khoản khác."},
        ],
    )

    with pytest.raises(ValueError, match="Duplicate article_id"):
        BM25Index.build_or_load(corpus_path, tmp_path / "index.json")


def test_recall_mrr_and_ground_truth_validation():
    recall, mrr = calculate_recall_mrr(
        ["law#2", "law#1", "law#3"],
        ["law#1", "law#1"],
    )

    assert recall == 1.0
    assert mrr == 0.5
    with pytest.raises(ValueError, match="missing from the corpus"):
        validate_ground_truth(
            [{"relevant_articles": ["law#404"]}],
            {"law#1"},
        )


class FakeDenseEncoder:
    def encode(self, texts, **kwargs):
        assert texts == ["query"]
        return [[1.0, 0.0]]


class FakeCacheEncoder:
    device = "cpu"

    def __init__(self):
        self.document_encode_calls = 0

    def encode(self, texts, **kwargs):
        if texts == ["query"]:
            return [[1.0, 0.0]]
        self.document_encode_calls += 1
        return [[1.0, 0.0], [0.0, 1.0]]


def test_dense_search_ranks_by_cosine_similarity():
    documents = [
        IndexedDocument("law#1", "matching text", ["matching", "text"]),
        IndexedDocument("law#2", "other text", ["other", "text"]),
    ]
    index = DenseIndex(
        documents,
        [[1.0, 0.0], [0.0, 1.0]],
        FakeDenseEncoder(),
    )

    results = index.retrieve("query", top_k=1)

    assert results[0]["article_id"] == "law#1"
    assert results[0]["score"] == 1.0


def test_dense_index_is_persisted_and_reused(tmp_path, monkeypatch):
    corpus_path = tmp_path / "corpus.json"
    index_path = tmp_path / "dense.npz"
    write_corpus(
        corpus_path,
        [
            {"article_id": "law#1", "text": "Matching legal text."},
            {"article_id": "law#2", "text": "Other legal text."},
        ],
    )
    encoder = FakeCacheEncoder()
    monkeypatch.setattr(
        DenseIndex,
        "_load_encoder",
        staticmethod(lambda model_name, device, local_files_only: encoder),
    )

    built_index, rebuilt = DenseIndex.build_or_load(
        corpus_path,
        index_path,
        model_name="test/model",
        device="cpu",
    )
    cached_index, rebuilt_again = DenseIndex.build_or_load(
        corpus_path,
        index_path,
        model_name="test/model",
        device="cpu",
    )

    assert rebuilt is True
    assert rebuilt_again is False
    assert encoder.document_encode_calls == 1
    assert cached_index.retrieve("query", top_k=1)[0]["article_id"] == "law#1"
    assert built_index.embeddings.shape == (2, 2)


def test_reciprocal_rank_fusion_combines_sparse_and_dense_ranks():
    sparse = [
        {"article_id": "law#1", "text": "one", "score": 3.0},
        {"article_id": "law#2", "text": "two", "score": 2.0},
    ]
    dense = [
        {"article_id": "law#2", "text": "two", "score": 0.9},
        {"article_id": "law#3", "text": "three", "score": 0.8},
    ]

    results = reciprocal_rank_fusion(sparse, dense, top_k=3, rrf_k=60)

    assert [result["article_id"] for result in results] == [
        "law#2",
        "law#1",
        "law#3",
    ]
