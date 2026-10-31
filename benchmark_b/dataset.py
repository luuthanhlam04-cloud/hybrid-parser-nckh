"""Loading and structural validation for the fixed Benchmark B question set."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_DATASET = Path("datasets/benchmarks/benchmark_B_50_chuong_III.json")
EXPECTED_ARTICLES = {str(number) for number in range(26, 49)}


def load_dataset(path: str | Path = DEFAULT_DATASET) -> dict[str, Any]:
    """Load the source dataset without mutating its legal annotations."""
    dataset_path = Path(path)
    with dataset_path.open(encoding="utf-8") as stream:
        payload = json.load(stream)
    if not isinstance(payload, dict):
        raise ValueError("Benchmark dataset must be a JSON object.")
    return payload


def load_questions(path: str | Path = DEFAULT_DATASET) -> list[dict[str, Any]]:
    payload = load_dataset(path)
    questions = payload.get("questions")
    if not isinstance(questions, list):
        raise ValueError("Benchmark dataset must contain a questions array.")
    return questions


def validate_dataset(path: str | Path = DEFAULT_DATASET) -> dict[str, Any]:
    """Validate research invariants, returning a small report suitable for logs."""
    payload = load_dataset(path)
    questions = load_questions(path)
    ids = [question.get("question_id") for question in questions]
    if len(questions) != 50:
        raise ValueError(f"Benchmark B must contain exactly 50 questions, found {len(questions)}.")
    if any(not isinstance(question_id, str) or not question_id.strip() for question_id in ids):
        raise ValueError("Every question must have a non-empty question_id.")
    if len(set(ids)) != len(ids):
        raise ValueError("Benchmark B question_id values must be unique.")

    answerability = Counter(question.get("answerability") for question in questions)
    if answerability["ANSWERABLE_IN_CHAPTER_III"] != 47:
        raise ValueError("Benchmark B must contain 47 answerable Chapter III questions.")
    if answerability["INSUFFICIENT_CORPUS"] != 3:
        raise ValueError("Benchmark B must contain 3 insufficient-corpus questions.")

    articles: set[str] = set()
    for question in questions:
        relevant = question.get("relevant_articles")
        if not isinstance(relevant, list):
            raise ValueError(f"{question['question_id']} has invalid relevant_articles.")
        for locator in relevant:
            if not isinstance(locator, str) or "#" not in locator:
                raise ValueError(f"{question['question_id']} has invalid article locator: {locator!r}")
            articles.add(locator.rsplit("#", 1)[1])
        if question.get("answerability") == "INSUFFICIENT_CORPUS" and relevant:
            raise ValueError(f"{question['question_id']} is out of corpus but has positive retrieval gold.")

    missing_articles = sorted(EXPECTED_ARTICLES - articles, key=int)
    if missing_articles:
        raise ValueError(f"Benchmark B does not cover all Chapter III articles: {missing_articles}")
    return {
        "dataset": str(path),
        "version": payload.get("metadata", {}).get("version"),
        "questions": len(questions),
        "answerability": dict(answerability),
        "covered_articles": len(articles),
        "status": payload.get("metadata", {}).get("status"),
    }
