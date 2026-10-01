"""Train/evaluate M8 confidence calibration using manually labeled CSV data."""

import argparse
import json
from pathlib import Path

from src.fusion.confidence_calibration import (
    evaluate_confidence,
    fit_from_csv,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("gold_csv", type=Path)
    parser.add_argument("--fit", action="store_true")
    parser.add_argument("--split", default="train")
    parser.add_argument(
        "--calibrator",
        type=Path,
        default=Path("outputs/evaluation/fusion_confidence_calibrator.json"),
    )
    args = parser.parse_args()
    if args.fit:
        fit_from_csv(args.gold_csv, args.calibrator, args.split)
        print(f"Saved calibrator: {args.calibrator}")
        return
    import csv

    with args.gold_csv.open(encoding="utf-8-sig", newline="") as stream:
        rows = [
            row for row in csv.DictReader(stream)
            if row.get("split", "test").strip().casefold() == args.split.casefold()
        ]
    if args.calibrator.exists():
        from src.fusion.confidence_calibration import IsotonicConfidenceCalibrator

        calibrator = IsotonicConfidenceCalibrator.load(args.calibrator)
        scores = [calibrator.predict(float(row["score"])) for row in rows]
    else:
        scores = [float(row["score"]) for row in rows]
    result = evaluate_confidence(
        [int(row["label"]) for row in rows],
        scores,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
