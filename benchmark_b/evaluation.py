"""Deterministic, auditable first-pass Benchmark B measurements."""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


ARTICLE_CITATION = re.compile(r"(?:Điều|điều)\s+(\d+)")
INSUFFICIENT_MARKERS = ("không đủ", "ngoài phạm vi", "không có căn cứ", "không được cung cấp")


def article_recall_at_k(retrieved_article_ids: list[str] | None, gold_article_ids: list[str], k: int = 5) -> float | None:
    if retrieved_article_ids is None:
        return None
    if not gold_article_ids:
        return None
    selected = set(retrieved_article_ids[:k])
    return len(selected & set(gold_article_ids)) / len(set(gold_article_ids))


def reciprocal_rank(retrieved_article_ids: list[str] | None, gold_article_ids: list[str], k: int = 5) -> float | None:
    if retrieved_article_ids is None or not gold_article_ids:
        return None
    gold = set(gold_article_ids)
    for index, article_id in enumerate(retrieved_article_ids[:k], start=1):
        if article_id in gold:
            return 1 / index
    return 0.0


def citation_article_numbers(answer: str) -> list[str]:
    return sorted(set(ARTICLE_CITATION.findall(answer or "")), key=int)


def evaluate_record(question: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    answer = result.get("answer", "")
    retrieved = result.get("retrieved_article_ids")
    positive = question.get("answerability") == "ANSWERABLE_IN_CHAPTER_III"
    gold = question.get("relevant_articles", [])
    cited = citation_article_numbers(answer)
    expected_numbers = sorted({str(location["article"]) for location in question.get("gold_locations", []) if location.get("article")}, key=int)
    record = {
        "question_id": question["question_id"],
        "system": result["system"],
        "category": question.get("benchmark_b_category"),
        "answerability": question.get("answerability"),
        "retrieval_recall_at_5": article_recall_at_k(retrieved, gold),
        "retrieval_mrr_at_5": reciprocal_rank(retrieved, gold),
        "cited_articles": cited,
        "expected_articles": expected_numbers,
        "citation_article_overlap": len(set(cited) & set(expected_numbers)) / len(expected_numbers) if expected_numbers and positive else None,
        "abstention_keyword_present": any(marker in answer.lower() for marker in INSUFFICIENT_MARKERS) if not positive else None,
        "latency_ms": result.get("latency_ms"),
        "retrieval_measurement": "available" if retrieved is not None else "not_measured",
    }
    return record


def summarise(records: list[dict[str, Any]]) -> dict[str, Any]:
    def average(field: str) -> float | None:
        values = [row[field] for row in records if row.get(field) is not None]
        return sum(values) / len(values) if values else None

    categories: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        categories[str(record.get("category"))].append(record)
    return {
        "questions": len(records),
        "retrieval_recall_at_5": average("retrieval_recall_at_5"),
        "retrieval_mrr_at_5": average("retrieval_mrr_at_5"),
        "citation_article_overlap": average("citation_article_overlap"),
        "not_measured_retrieval": sum(record["retrieval_measurement"] == "not_measured" for record in records),
        "by_category": {
            category: {
                "questions": len(rows),
                "recall_at_5": average_from(rows, "retrieval_recall_at_5"),
                "mrr_at_5": average_from(rows, "retrieval_mrr_at_5"),
            }
            for category, rows in categories.items()
        },
        "legal_correctness": "human_review_required",
    }


def average_from(rows: list[dict[str, Any]], field: str) -> float | None:
    values = [row[field] for row in rows if row.get(field) is not None]
    return sum(values) / len(values) if values else None


def write_review_csv(questions: list[dict[str, Any]], results: list[dict[str, Any]], output_path: str | Path) -> None:
    """Make a human-review sheet; never infer legal correctness from keyword overlap."""
    by_id = {result["question_id"]: result for result in results}
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["question_id", "question", "system", "answer", "relevant_articles", "required_atomic_facts", "required_exceptions", "forbidden_claims", "reference_chain", "retrieved_article_ids", "review_legal_correctness", "review_notes"]
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for question in questions:
            result = by_id[question["question_id"]]
            writer.writerow({
                "question_id": question["question_id"],
                "question": question["question"],
                "system": result["system"],
                "answer": result.get("answer", ""),
                "relevant_articles": json.dumps(question.get("relevant_articles", []), ensure_ascii=False),
                "required_atomic_facts": json.dumps(question.get("required_atomic_facts", []), ensure_ascii=False),
                "required_exceptions": json.dumps(question.get("required_exceptions", []), ensure_ascii=False),
                "forbidden_claims": json.dumps(question.get("forbidden_claims", []), ensure_ascii=False),
                "reference_chain": json.dumps(question.get("reference_chain", []), ensure_ascii=False),
                "retrieved_article_ids": json.dumps(result.get("retrieved_article_ids"), ensure_ascii=False),
                "review_legal_correctness": "",
                "review_notes": "",
            })
