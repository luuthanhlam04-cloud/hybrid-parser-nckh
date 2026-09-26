"""Evaluate manually reviewed Module 8 conflict/reference/relation cases."""

import argparse
import json
from pathlib import Path

from src.fusion.quality_evaluation import evaluate_quality_csv


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("gold_csv", type=Path)
    parser.add_argument(
        "--task",
        choices=("relation_support", "deontic_conflict", "reference_resolution"),
        required=True,
    )
    parser.add_argument("--split", default="test")
    args = parser.parse_args()
    report = evaluate_quality_csv(args.gold_csv, args.task, args.split)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
