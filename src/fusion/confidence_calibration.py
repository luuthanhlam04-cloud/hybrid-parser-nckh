"""Isotonic calibration and evaluation metrics for labeled confidence data."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable


class IsotonicConfidenceCalibrator:
    """Small dependency-free isotonic regression using the PAV algorithm."""

    def __init__(self) -> None:
        self.thresholds: list[float] = []
        self.values: list[float] = []

    def fit(self, scores: Iterable[float], labels: Iterable[int]) -> "IsotonicConfidenceCalibrator":
        score_values, label_values = list(scores), list(labels)
        if len(score_values) != len(label_values):
            raise ValueError("Confidence scores and labels must have equal lengths")
        if any(int(label) not in (0, 1) for label in label_values):
            raise ValueError("Calibration labels must be binary 0 or 1")
        if any(not 0.0 <= float(score) <= 1.0 for score in score_values):
            raise ValueError("Calibration scores must be within [0, 1]")
        grouped_scores: dict[float, list[int]] = {}
        for score, label in zip(score_values, label_values):
            grouped_scores.setdefault(float(score), []).append(int(label))
        pairs = sorted(
            (score, sum(labels), len(labels))
            for score, labels in grouped_scores.items()
        )
        if len(pairs) < 2:
            raise ValueError("At least two labeled examples are required to fit calibration")
        blocks: list[list[float]] = []
        for score, positive_count, total_count in pairs:
            blocks.append([score, score, float(positive_count), float(total_count)])
            while len(blocks) > 1:
                previous, current = blocks[-2], blocks[-1]
                if previous[2] / previous[3] <= current[2] / current[3]:
                    break
                blocks[-2:] = [[
                    previous[0], current[1], previous[2] + current[2],
                    previous[3] + current[3],
                ]]
        self.thresholds = [block[1] for block in blocks]
        self.values = [block[2] / block[3] for block in blocks]
        return self

    def predict(self, score: float) -> float:
        if not self.thresholds:
            raise RuntimeError("Calibrator has not been fitted")
        for threshold, value in zip(self.thresholds, self.values):
            if score <= threshold:
                return value
        return self.values[-1]

    def save(self, path: str | Path) -> None:
        if not self.thresholds:
            raise RuntimeError("Cannot save an unfitted calibrator")
        Path(path).write_text(
            json.dumps(
                {"method": "isotonic_pav_v1", "thresholds": self.thresholds, "values": self.values},
                indent=2,
            ),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: str | Path) -> "IsotonicConfidenceCalibrator":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if data.get("method") != "isotonic_pav_v1":
            raise ValueError("Unsupported confidence calibrator format")
        calibrator = cls()
        calibrator.thresholds = [float(value) for value in data["thresholds"]]
        calibrator.values = [float(value) for value in data["values"]]
        if not calibrator.thresholds or len(calibrator.thresholds) != len(calibrator.values):
            raise ValueError("Invalid confidence calibrator artifact")
        return calibrator


def evaluate_confidence(
    labels: Iterable[int],
    scores: Iterable[float],
    bins: int = 10,
    threshold: float = 0.8,
) -> dict[str, Any]:
    label_values, score_values = list(labels), list(scores)
    if len(label_values) != len(score_values):
        raise ValueError("Confidence scores and labels must have equal lengths")
    pairs = [
        (int(label), max(0.0, min(1.0, float(score))))
        for label, score in zip(label_values, score_values)
    ]
    if not pairs:
        raise ValueError("Confidence evaluation requires at least one labeled example")
    if bins < 1 or any(label not in (0, 1) for label, _ in pairs):
        raise ValueError("bins must be positive and labels must be binary")
    count = len(pairs)
    brier = sum((score - label) ** 2 for label, score in pairs) / count
    true_positive = sum(label == 1 and score >= threshold for label, score in pairs)
    false_positive = sum(label == 0 and score >= threshold for label, score in pairs)
    false_negative = sum(label == 1 and score < threshold for label, score in pairs)
    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
    ece = 0.0
    bin_metrics = []
    for index in range(bins):
        low = index / bins
        high = (index + 1) / bins
        values = [
            (label, score) for label, score in pairs
            if low <= score < high or (index == bins - 1 and score == 1.0)
        ]
        if not values:
            continue
        accuracy = sum(label for label, _ in values) / len(values)
        confidence = sum(score for _, score in values) / len(values)
        ece += len(values) / count * abs(accuracy - confidence)
        bin_metrics.append({
            "lower_bound": low,
            "upper_bound": high,
            "count": len(values),
            "accuracy": round(accuracy, 8),
            "mean_confidence": round(confidence, 8),
        })
    return {
        "count": count,
        "brier_score": round(brier, 8),
        "expected_calibration_error": round(ece, 8),
        "decision_threshold": threshold,
        "precision_at_threshold": round(precision, 8),
        "recall_at_threshold": round(recall, 8),
        "bins": bin_metrics,
    }


def evaluate_csv(path: str | Path, bins: int = 10) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if not rows or not {"label", "score"}.issubset(rows[0]):
        raise ValueError("Gold CSV must contain non-empty label and score columns")
    return evaluate_confidence(
        [int(row["label"]) for row in rows],
        [float(row["score"]) for row in rows],
        bins,
    )


def fit_from_csv(
    path: str | Path,
    output_path: str | Path,
    split: str = "train",
) -> IsotonicConfidenceCalibrator:
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        rows = [
            row for row in csv.DictReader(stream)
            if row.get("split", "train").strip().casefold() == split.casefold()
        ]
    if not rows or not {"label", "score"}.issubset(rows[0]):
        raise ValueError(f"Calibration CSV needs labeled rows in split={split!r}")
    calibrator = IsotonicConfidenceCalibrator().fit(
        [float(row["score"]) for row in rows],
        [int(row["label"]) for row in rows],
    )
    calibrator.save(output_path)
    return calibrator
