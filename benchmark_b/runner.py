"""CLI for independent, reproducible Benchmark B runs."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from .corpus import DEFAULT_CORPUS_DIR, write_article_corpus
from .costs import CostLedger
from .dataset import DEFAULT_DATASET, load_questions, validate_dataset
from .evaluation import evaluate_record, summarise, write_review_csv
from .systems import HybridUKGSystem, LightRAGSystem


OUTPUT_ROOT = Path("outputs/benchmark_b")


def get_system(name: str, *, mode: str = "AUTO") -> Any:
    if name == "hybrid":
        return HybridUKGSystem(OUTPUT_ROOT / "hybrid", mode=mode)
    if name == "lightrag":
        return LightRAGSystem(OUTPUT_ROOT / "lightrag")
    raise ValueError(f"Unknown system: {name}")


def load_or_prepare_corpus() -> list[dict[str, Any]]:
    corpus_path = DEFAULT_CORPUS_DIR / "chapter_iii_articles.json"
    if not corpus_path.is_file():
        write_article_corpus()
    return json.loads(corpus_path.read_text(encoding="utf-8"))


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def run_benchmark(system_name: str, *, limit: int | None, top_k: int, mode: str) -> dict[str, Any]:
    system = get_system(system_name, mode=mode)
    questions = load_questions()
    if limit is not None:
        questions = questions[:limit]
    results: list[dict[str, Any]] = []
    started = time.perf_counter()
    try:
        for question in questions:
            result = system.answer(question, top_k=top_k)
            results.append(result)
    finally:
        if hasattr(system, "close"):
            system.close()
    output_dir = system.output_dir
    write_jsonl(output_dir / "answers.jsonl", results)
    scores = [evaluate_record(question, result) for question, result in zip(questions, results, strict=True)]
    write_jsonl(output_dir / "per_question_metrics.jsonl", scores)
    report = {
        "system": system.name,
        "questions_run": len(results),
        "duration_ms": round((time.perf_counter() - started) * 1000, 2),
        "metrics": summarise(scores),
        "query_cost_ledger": system.ledger.to_dict() if isinstance(system, LightRAGSystem) else aggregate_hybrid_usage(results),
        "dataset": str(DEFAULT_DATASET),
    }
    (output_dir / "metrics.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_review_csv(questions, results, output_dir / "human_review.csv")
    return report


def aggregate_hybrid_usage(results: list[dict[str, Any]]) -> dict[str, Any]:
    ledger = CostLedger("openai/gpt-4o-mini")
    for result in results:
        ledger.add_usage("query", result.get("usage"))
    return ledger.to_dict()


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark B: independent Hybrid Parser/UKG and LightRAG experiments")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate", help="validate the fixed 50-question dataset")
    subparsers.add_parser("prepare-corpus", help="build the common corpus from physical_graph.json")
    index_parser = subparsers.add_parser("index", help="prepare an individual system index")
    index_parser.add_argument("--system", choices=["hybrid", "lightrag"], required=True)
    index_parser.add_argument("--fresh", action="store_true", help="only applies to LightRAG and deletes its isolated workspace")
    run_parser = subparsers.add_parser("run", help="answer and score questions using an already-indexed system")
    run_parser.add_argument("--system", choices=["hybrid", "lightrag"], required=True)
    run_parser.add_argument("--limit", type=int)
    run_parser.add_argument("--top-k", type=int, default=5)
    run_parser.add_argument("--mode", choices=["A", "B", "AUTO"], default="AUTO", help="Hybrid M10 retrieval mode")
    args = parser.parse_args()

    if args.command == "validate":
        print(json.dumps(validate_dataset(), ensure_ascii=False, indent=2))
        return
    if args.command == "prepare-corpus":
        print(json.dumps(write_article_corpus(), ensure_ascii=False, indent=2))
        return
    if args.command == "index":
        corpus = load_or_prepare_corpus()
        system = get_system(args.system)
        print(json.dumps(system.index(corpus, fresh=args.fresh), ensure_ascii=False, indent=2))
        return
    print(json.dumps(run_benchmark(args.system, limit=args.limit, top_k=args.top_k, mode=args.mode), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
