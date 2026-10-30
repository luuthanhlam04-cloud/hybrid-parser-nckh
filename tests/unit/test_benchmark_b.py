from __future__ import annotations

import json
from pathlib import Path

import pytest

from benchmark_b.corpus import build_article_corpus, write_article_corpus
from benchmark_b.costs import CostLedger
from benchmark_b.dataset import validate_dataset
from benchmark_b.evaluation import article_recall_at_k, evaluate_record
from benchmark_b.systems.lightrag_adapter import LightRAGSystem


def test_benchmark_b_dataset_is_fixed_and_covered():
    report = validate_dataset()
    assert report["questions"] == 50
    assert report["answerability"] == {"ANSWERABLE_IN_CHAPTER_III": 47, "INSUFFICIENT_CORPUS": 3}
    assert report["covered_articles"] == 23


def test_common_corpus_has_all_articles_and_evidence_ids(tmp_path: Path):
    corpus = build_article_corpus()
    assert len(corpus) == 23
    assert corpus[0]["article_id"] == "31/2024/qh15#26"
    assert all(document["physical_evidence_node_ids"] for document in corpus)
    manifest = write_article_corpus(output_dir=tmp_path)
    assert manifest["article_count"] == 23
    assert (tmp_path / "chapter_iii_articles.json").is_file()


def test_cost_ledger_only_bills_observed_usage():
    ledger = CostLedger("openai/gpt-4o-mini")
    ledger.add_usage("index", {"prompt_tokens": 1_000_000, "completion_tokens": 1_000_000})
    ledger.add_usage("index", None)
    report = ledger.to_dict()
    assert report["phases"]["index"]["observed_cost_usd"] == pytest.approx(0.75)
    assert report["phases"]["index"]["missing_usage_calls"] == 1


def test_unavailable_retrieval_is_not_scored_as_zero():
    question = {"question_id": "B001", "answerability": "ANSWERABLE_IN_CHAPTER_III", "relevant_articles": ["31/2024/qh15#26"], "gold_locations": [{"article": "26"}], "benchmark_b_category": "DIRECT"}
    result = {"question_id": "B001", "system": "lightrag", "answer": "Không có Điều 26.", "retrieved_article_ids": None, "latency_ms": 1}
    score = evaluate_record(question, result)
    assert score["retrieval_recall_at_5"] is None
    assert score["retrieval_measurement"] == "not_measured"
    assert article_recall_at_k(["31/2024/qh15#26"], ["31/2024/qh15#26"]) == 1.0


def test_system_outputs_are_isolated(tmp_path: Path):
    system = LightRAGSystem(tmp_path / "lightrag")
    assert system.output_dir == tmp_path / "lightrag"
    assert system.workspace == tmp_path / "lightrag" / "workspace"
