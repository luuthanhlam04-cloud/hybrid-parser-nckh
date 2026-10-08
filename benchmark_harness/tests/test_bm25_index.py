import json

import pytest

from benchmark_harness.core.bm25_index import BM25Index
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
