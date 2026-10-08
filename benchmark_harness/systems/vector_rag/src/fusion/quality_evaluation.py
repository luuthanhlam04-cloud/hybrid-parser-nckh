"""Evaluation metrics for expert-labeled fusion outputs."""

from __future__ import annotations

import csv
import itertools
from pathlib import Path
from typing import Any


def evaluate_classification(rows: list[dict[str, str]]) -> dict[str, Any]:
    if not rows:
        raise ValueError("Quality evaluation requires manually labeled rows")
    rows = [
        {
            **row,
            "expected": row.get("expected", "").strip(),
            "predicted": row.get("predicted", "").strip(),
        }
        for row in rows
    ]
    required = {"expected", "predicted"}
    if not required.issubset(rows[0]):
        raise ValueError("Quality gold data requires expected and predicted columns")
    labels = {value for row in rows for value in (row["expected"], row["predicted"])}
    if any(not row["expected"] or not row["predicted"] for row in rows):
        raise ValueError("Expected and predicted labels must not be empty")
    counts = {
        "true_positive": 0,
        "false_positive": 0,
        "false_negative": 0,
        "true_negative": 0,
        "exact_match": 0,
    }
    for row in rows:
        expected = row["expected"].strip()
        predicted = row["predicted"].strip()
        counts["exact_match"] += expected == predicted
        if expected == "1" and predicted == "1":
            counts["true_positive"] += 1
        elif expected != "1" and predicted == "1":
            counts["false_positive"] += 1
        elif expected == "1" and predicted != "1":
            counts["false_negative"] += 1
        else:
            counts["true_negative"] += 1
    tp, fp, fn = (
        counts["true_positive"], counts["false_positive"], counts["false_negative"]
    )
    if not labels.issubset({"0", "1"}):
        return {
            "count": len(rows),
            "labels": sorted(labels),
            "exact_match_accuracy": counts["exact_match"] / len(rows),
            "mismatches": [
                {"expected": row["expected"], "predicted": row["predicted"]}
                for row in rows if row["expected"] != row["predicted"]
            ],
        }
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return {
        "count": len(rows),
        "labels": sorted(labels),
        "exact_match_accuracy": counts["exact_match"] / len(rows),
        "precision_positive": precision,
        "recall_positive": recall,
        "f1_positive": 2 * precision * recall / (precision + recall)
        if precision + recall else 0.0,
        "confusion": {
            key: counts[key]
            for key in (
                "true_positive", "false_positive",
                "false_negative", "true_negative",
            )
        },
    }


def evaluate_quality_csv(
    path: str | Path, task: str, split: str = "test"
) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        selected = [
            row for row in csv.DictReader(stream)
            if row.get("task", "").strip() == task
            and row.get("split", "").strip().casefold() == split.casefold()
        ]
    grouped: dict[str, list[dict[str, str]]] = {}
    for index, row in enumerate(selected):
        case_id = row.get("case_id", "").strip()
        if not case_id:
            raise ValueError(f"Gold row {index + 2} has no case_id")
        grouped.setdefault(case_id, []).append(row)
    rows = []
    annotations: dict[str, dict[str, str]] = {}
    for case_id, case_rows in grouped.items():
        expected_values = {row.get("expected", "").strip() for row in case_rows}
        predicted_values = {row.get("predicted", "").strip() for row in case_rows}
        if len(predicted_values) != 1:
            raise ValueError(
                f"Rows for case {case_id} must agree on predicted values"
            )
        adjudicated = {value for value in expected_values if value}
        if len(adjudicated) > 1:
            raise ValueError(f"Rows for case {case_id} disagree on expected value")
        case_annotations: dict[str, str] = {}
        for row in case_rows:
            reviewer = row.get("reviewer", "").strip()
            annotation = row.get("annotation", "").strip()
            if reviewer and annotation:
                case_annotations[reviewer] = annotation
        annotations[case_id] = case_annotations
        if adjudicated:
            expected = next(iter(adjudicated))
        elif case_annotations:
            if len(set(case_annotations.values())) != 1:
                raise ValueError(
                    f"Reviewers disagree on case {case_id}; adjudicate it in expected"
                )
            expected = next(iter(case_annotations.values()))
        else:
            raise ValueError(
                f"Case {case_id} has no expert label; fill annotation or expected"
            )
        rows.append({"expected": expected, "predicted": next(iter(predicted_values))})
    result = evaluate_classification(rows)
    result["annotator_agreement_kappa"] = _pairwise_cohens_kappa(annotations)
    result["task"] = task
    result["split"] = split
    return result


def _pairwise_cohens_kappa(
    annotations: dict[str, dict[str, str]]
) -> float | None:
    reviewer_names = sorted({
        reviewer
        for case_annotations in annotations.values()
        for reviewer in case_annotations
    })
    pair_scores = []
    for first, second in itertools.combinations(reviewer_names, 2):
        pairs = [
            (case_values[first], case_values[second])
            for case_values in annotations.values()
            if first in case_values and second in case_values
        ]
        if not pairs:
            continue
        observed = sum(left == right for left, right in pairs) / len(pairs)
        classes = {
            label for pair in pairs for label in pair
        }
        first_marginal = {
            label: sum(left == label for left, _ in pairs) / len(pairs)
            for label in classes
        }
        second_marginal = {
            label: sum(right == label for _, right in pairs) / len(pairs)
            for label in classes
        }
        expected = sum(
            first_marginal[label] * second_marginal[label] for label in classes
        )
        pair_scores.append(
            (observed - expected) / (1 - expected)
            if expected < 1 else (1.0 if observed == 1 else 0.0)
        )
    return sum(pair_scores) / len(pair_scores) if pair_scores else None
