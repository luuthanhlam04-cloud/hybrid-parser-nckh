"""Build the BM25 index and run the legal retrieval benchmark."""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

if __package__:
    from .core.bm25_index import BM25Index
else:
    from core.bm25_index import BM25Index


HARNESS_DIR = Path(__file__).resolve().parent
DEFAULT_CORPUS = HARNESS_DIR / "data" / "corpus_final.json"
DEFAULT_BENCHMARK = HARNESS_DIR / "data" / "benchmark_rewritten.json"
DEFAULT_INDEX = HARNESS_DIR / ".cache" / "bm25" / "index.json"
DEFAULT_RESULTS = HARNESS_DIR / "results" / "bm25_results.csv"


def load_benchmark(path: str | Path) -> list[dict[str, Any]]:
    benchmark_path = Path(path)
    questions = json.loads(benchmark_path.read_text(encoding="utf-8"))
    if not isinstance(questions, list) or not questions:
        raise ValueError(f"Benchmark must be a non-empty JSON array: {benchmark_path}")

    seen_ids: set[str] = set()
    for position, question in enumerate(questions):
        if not isinstance(question, dict):
            raise ValueError(f"Benchmark item {position} must be a JSON object.")
        question_id = question.get("question_id")
        text = question.get("question")
        relevant_articles = question.get("relevant_articles")
        if not isinstance(question_id, str) or not question_id.strip():
            raise ValueError(f"Benchmark item {position} has no valid question_id.")
        if question_id in seen_ids:
            raise ValueError(f"Duplicate question_id in benchmark: {question_id}")
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"Benchmark question {question_id} has no question text.")
        if not isinstance(relevant_articles, list) or not all(
            isinstance(article_id, str) for article_id in relevant_articles
        ):
            raise ValueError(
                f"Benchmark question {question_id} has invalid relevant_articles."
            )
        seen_ids.add(question_id)
    return questions


def validate_ground_truth(
    questions: list[dict[str, Any]], corpus_ids: set[str]
) -> None:
    missing = sorted(
        {
            article_id
            for question in questions
            for article_id in question["relevant_articles"]
            if article_id not in corpus_ids
        }
    )
    if missing:
        preview = ", ".join(missing[:10])
        raise ValueError(
            f"{len(missing)} ground-truth article IDs are missing from the corpus: "
            f"{preview}"
        )


def calculate_recall_mrr(
    retrieved_ids: list[str], ground_truth: list[str]
) -> tuple[float, float]:
    unique_ground_truth = list(dict.fromkeys(ground_truth))
    if not unique_ground_truth:
        return 0.0, 0.0

    relevant = set(unique_ground_truth)
    recall = len(relevant.intersection(retrieved_ids)) / len(relevant)
    mrr = next(
        (1.0 / rank for rank, article_id in enumerate(retrieved_ids, start=1)
         if article_id in relevant),
        0.0,
    )
    return recall, mrr


def run_benchmark(
    index: BM25Index,
    questions: list[dict[str, Any]],
    *,
    top_k: int,
    limit: int | None,
    output_path: str | Path,
) -> dict[str, Any]:
    selected_questions = questions if limit is None else questions[:limit]
    if not selected_questions:
        raise ValueError("No benchmark questions selected.")

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    category_metrics: dict[str, dict[str, float]] = defaultdict(
        lambda: {"recall": 0.0, "mrr": 0.0, "count": 0}
    )
    total_recall = 0.0
    total_mrr = 0.0
    started_at = time.perf_counter()

    for position, question in enumerate(selected_questions, start=1):
        query_started_at = time.perf_counter()
        retrieved = index.retrieve(question["question"], top_k=top_k)
        latency_ms = (time.perf_counter() - query_started_at) * 1000
        retrieved_ids = [document["article_id"] for document in retrieved]
        ground_truth = question["relevant_articles"]
        recall, mrr = calculate_recall_mrr(retrieved_ids, ground_truth)
        category = question.get("category") or "unknown"

        rows.append(
            {
                "question_id": question["question_id"],
                "question": question["question"],
                "category": category,
                "retrieved_articles": "|".join(retrieved_ids),
                "ground_truth": "|".join(ground_truth),
                f"recall@{top_k}": recall,
                f"mrr@{top_k}": mrr,
                "latency_ms": round(latency_ms, 3),
            }
        )
        total_recall += recall
        total_mrr += mrr
        category_metrics[category]["recall"] += recall
        category_metrics[category]["mrr"] += mrr
        category_metrics[category]["count"] += 1

        if position % 50 == 0 or position == len(selected_questions):
            print(f"Benchmarked {position}/{len(selected_questions)} questions.")

    fieldnames = [
        "question_id",
        "question",
        "category",
        "retrieved_articles",
        "ground_truth",
        f"recall@{top_k}",
        f"mrr@{top_k}",
        "latency_ms",
    ]
    with output_file.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    elapsed_seconds = time.perf_counter() - started_at
    question_count = len(rows)
    summary = {
        "question_count": question_count,
        "top_k": top_k,
        f"mean_recall_at_{top_k}": total_recall / question_count,
        f"mean_mrr_at_{top_k}": total_mrr / question_count,
        "mean_latency_ms": sum(row["latency_ms"] for row in rows) / question_count,
        "elapsed_seconds": elapsed_seconds,
        "category_metrics": {
            category: {
                "question_count": int(metrics["count"]),
                f"mean_recall_at_{top_k}": metrics["recall"] / metrics["count"],
                f"mean_mrr_at_{top_k}": metrics["mrr"] / metrics["count"],
            }
            for category, metrics in sorted(category_metrics.items())
        },
        "results_csv": str(output_file.resolve()),
    }

    print("\nRetrieval benchmark summary")
    print(f"Questions: {question_count}")
    print(f"Recall@{top_k}: {summary[f'mean_recall_at_{top_k}']:.4f}")
    print(f"MRR@{top_k}: {summary[f'mean_mrr_at_{top_k}']:.4f}")
    print(f"Mean query latency: {summary['mean_latency_ms']:.2f} ms")
    print(f"Elapsed: {elapsed_seconds:.2f} s")
    print(f"Results: {output_file}")
    print("\nBy category:")
    for category, metrics in summary["category_metrics"].items():
        print(
            f"  {category}: n={metrics['question_count']}, "
            f"Recall@{top_k}={metrics[f'mean_recall_at_{top_k}']:.4f}, "
            f"MRR@{top_k}={metrics[f'mean_mrr_at_{top_k}']:.4f}"
        )
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Index the legal corpus and benchmark BM25 retrieval."
    )
    commands = parser.add_subparsers(dest="command", required=True)

    index_parser = commands.add_parser("index", help="Build or refresh the BM25 index.")
    benchmark_parser = commands.add_parser(
        "benchmark", help="Run Recall/MRR retrieval evaluation."
    )
    for command_parser in (index_parser, benchmark_parser):
        command_parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
        command_parser.add_argument("--index", type=Path, default=DEFAULT_INDEX)
        command_parser.add_argument(
            "--rebuild-index",
            action="store_true",
            help="Rebuild the index even if a matching cache exists.",
        )
    index_parser.set_defaults(limit=None)
    benchmark_parser.add_argument("--benchmark", type=Path, default=DEFAULT_BENCHMARK)
    benchmark_parser.add_argument("--output", type=Path, default=DEFAULT_RESULTS)
    benchmark_parser.add_argument("--top-k", type=int, default=5)
    benchmark_parser.add_argument(
        "--limit",
        type=int,
        help="Run only the first N questions (defaults to all questions).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "benchmark":
        if args.top_k < 1:
            raise ValueError("--top-k must be a positive integer.")
        if args.limit is not None and args.limit < 1:
            raise ValueError("--limit must be a positive integer.")

    index, rebuilt = BM25Index.build_or_load(
        args.corpus,
        args.index,
        force_rebuild=args.rebuild_index,
    )
    print(
        f"BM25 index {'built' if rebuilt else 'loaded'}: "
        f"{len(index.documents)} documents ({args.index})"
    )
    if args.command == "index":
        return 0

    questions = load_benchmark(args.benchmark)
    validate_ground_truth(
        questions,
        {document.article_id for document in index.documents},
    )
    run_benchmark(
        index,
        questions,
        top_k=args.top_k,
        limit=args.limit,
        output_path=args.output,
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
