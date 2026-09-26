"""Create expert-review CSV samples from a unified fusion graph."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any


RELATION_TYPES = ("ALLOW", "REQUIRE", "PROHIBIT", "RESOLVES_TO", "HAS_EXCEPTION")
CONFIDENCE_FIELDS = (
    "relation_id", "relation_type", "source", "target", "evidence", "score",
    "label", "split",
)
QUALITY_FIELDS = (
    "task", "case_id", "expected", "predicted", "split", "reviewer",
    "annotation", "notes",
)


def _split_for_group(group: str, seed: int, test_ratio: float) -> str:
    digest = hashlib.sha256(f"{seed}:{group}".encode("utf-8")).digest()
    value = int.from_bytes(digest[:8], "big") / (2**64)
    return "test" if value < test_ratio else "train"


def _edge_id(edge: dict[str, Any], index: int) -> str:
    properties = edge.get("properties", {})
    return str(
        properties.get("relation_id")
        or edge.get("id")
        or f"edge-{index:06d}"
    )


def _sample_edges(
    edges: list[dict[str, Any]], size: int, seed: int
) -> list[tuple[int, dict[str, Any]]]:
    rng = random.Random(seed)
    buckets: dict[str, list[tuple[int, dict[str, Any]]]] = defaultdict(list)
    for index, edge in enumerate(edges):
        if edge.get("type") in RELATION_TYPES:
            buckets[str(edge["type"])].append((index, edge))
    available = sum(len(bucket) for bucket in buckets.values())
    if not available:
        raise ValueError("The unified graph contains no supported relation types")

    target = min(size, available)
    active = [kind for kind in RELATION_TYPES if buckets[kind]]
    quota = {kind: target // len(active) for kind in active}
    for kind in active[: target % len(active)]:
        quota[kind] += 1

    selected: list[tuple[int, dict[str, Any]]] = []
    leftovers: list[tuple[int, dict[str, Any]]] = []
    for kind in active:
        bucket = buckets[kind]
        rng.shuffle(bucket)
        selected.extend(bucket[: min(quota[kind], len(bucket))])
        leftovers.extend(bucket[min(quota[kind], len(bucket)):])
    if len(selected) < target:
        rng.shuffle(leftovers)
        selected.extend(leftovers[: target - len(selected)])
    rng.shuffle(selected)
    return selected


def sample_fusion_eval(
    graph_path: Path,
    confidence_path: Path,
    quality_path: Path,
    size: int = 80,
    seed: int = 42,
    test_ratio: float = 0.2,
) -> tuple[int, int]:
    if size < 1:
        raise ValueError("Sample size must be positive")
    if not 0.0 < test_ratio < 1.0:
        raise ValueError("test_ratio must be between 0 and 1")
    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    edges = graph.get("edges", [])
    sampled = _sample_edges(edges, size, seed)
    node_map = {
        str(node.get("id")): node
        for node in graph.get("nodes", [])
        if node.get("node_kind") in {"PHYSICAL", "DOCUMENT"}
    }
    confidence_rows = []
    quality_rows = []
    relation_groups = {
        _edge_id(edge, index): str(
            edge.get("properties", {}).get("source_node_id")
            or edge.get("source", "")
        )
        for index, edge in enumerate(edges)
    }

    for index, edge in sampled:
        properties = edge.get("properties", {})
        relation_id = _edge_id(edge, index)
        source = str(edge.get("source", ""))
        split = _split_for_group(
            str(properties.get("source_node_id") or source), seed, test_ratio
        )
        evidence = properties.get("evidence", "")
        confidence_rows.append({
            "relation_id": relation_id,
            "relation_type": str(edge.get("type", "")),
            "source": source,
            "target": str(edge.get("target", "")),
            "evidence": str(evidence),
            "score": str(properties.get("confidence", "")),
            "label": "",
            "split": split,
        })
        quality_rows.append({
            "task": "relation_support",
            "case_id": relation_id,
            "expected": "",
            "predicted": "1",
            "split": split,
            "reviewer": "",
            "annotation": "",
            "notes": f"{edge.get('type', '')}: {evidence}",
        })

        if edge.get("type") == "RESOLVES_TO":
            quality_rows.append({
                "task": "reference_resolution",
                "case_id": relation_id,
                "expected": "",
                "predicted": str(edge.get("target", "UNRESOLVED")),
                "split": split,
                "reviewer": "",
                "annotation": "",
                "notes": f"Resolved to {edge.get('target', '')}",
            })

    reference_edges = [
        (index, edge) for index, edge in enumerate(edges)
        if edge.get("type") == "REFERENCE_TO"
    ]
    rng = random.Random(seed + 1)
    rng.shuffle(reference_edges)
    for index, edge in reference_edges[:size]:
        properties = edge.get("properties", {})
        relation_id = _edge_id(edge, index)
        source_node_id = str(properties.get("source_node_id") or "")
        resolved_ids = properties.get("resolved_reference_node_ids") or []
        if not resolved_ids and edge.get("target") in node_map:
            resolved_ids = [str(edge["target"])]
        predicted_target = (
            "|".join(sorted(str(value) for value in resolved_ids))
            if resolved_ids else str(
                properties.get("reference_resolution_status", "UNRESOLVED")
            )
        )
        quality_rows.append({
            "task": "reference_resolution",
            "case_id": relation_id,
            "expected": "",
            "predicted": predicted_target,
            "split": _split_for_group(
                source_node_id or str(edge.get("source", "")), seed, test_ratio
            ),
            "reviewer": "",
            "annotation": "",
            "notes": str(properties.get("evidence", "")),
        })

    known_conflicts = {
        tuple(sorted(str(value) for value in conflict.get("relation_ids", [])))
        for conflict in graph.get("conflicts", [])
    }
    conflict_cases = []
    for conflict in graph.get("conflicts", []):
        relation_ids = sorted(str(value) for value in conflict.get("relation_ids", []))
        if len(relation_ids) < 2:
            continue
        group = next(
            (relation_groups[relation_id] for relation_id in relation_ids
             if relation_id in relation_groups),
            "",
        )
        conflict_cases.append({
            "task": "deontic_conflict",
            "case_id": "conflict:" + ":".join(relation_ids),
            "expected": "",
            "predicted": "1",
            "split": _split_for_group(group, seed, test_ratio),
            "reviewer": "",
            "annotation": "",
            "notes": str(conflict.get("message", conflict.get("conflict_type", ""))),
        })
    grouped_modalities: dict[tuple[str, str], dict[str, list[tuple[str, str]]]] = {}
    for index, edge in enumerate(edges):
        modality = edge.get("type")
        if modality not in {"ALLOW", "REQUIRE", "PROHIBIT"}:
            continue
        relation_id = _edge_id(edge, index)
        properties = edge.get("properties", {})
        source_group = str(properties.get("source_node_id") or edge.get("source", ""))
        key = (str(edge.get("source", "")), str(edge.get("target", "")))
        grouped_modalities.setdefault(key, {}).setdefault(modality, []).append(
            (relation_id, source_group)
        )
    negative_cases = []
    negative_case_ids: set[str] = set()
    for modalities in grouped_modalities.values():
        positive_modalities = modalities.get("ALLOW", []) + modalities.get("REQUIRE", [])
        prohibitions = modalities.get("PROHIBIT", [])
        for positive in positive_modalities:
            for prohibition in prohibitions:
                pair = tuple(sorted((positive[0], prohibition[0])))
                if pair in known_conflicts:
                    continue
                case_id = "pair:" + ":".join(pair)
                negative_cases.append({
                    "task": "deontic_conflict",
                    "case_id": case_id,
                    "expected": "",
                    "predicted": "0",
                    "split": _split_for_group(
                        positive[1] or prohibition[1], seed, test_ratio
                    ),
                    "reviewer": "",
                    "annotation": "",
                    "notes": "Review whether differing context/conditions explain this pair.",
                })
                negative_case_ids.add(case_id)
    prohibitions = [
        (index, edge) for index, edge in enumerate(edges)
        if edge.get("type") == "PROHIBIT"
    ]
    positive_norms = [
        (index, edge) for index, edge in enumerate(edges)
        if edge.get("type") in {"ALLOW", "REQUIRE"}
    ]
    unrelated_pairs = []
    for prohibit_index, prohibition in prohibitions:
        for positive_index, positive in positive_norms:
            if (
                prohibition.get("source"), prohibition.get("target")
            ) == (
                positive.get("source"), positive.get("target")
            ):
                continue
            relation_pair = tuple(sorted((
                _edge_id(prohibition, prohibit_index),
                _edge_id(positive, positive_index),
            )))
            case_id = "pair:" + ":".join(relation_pair)
            if case_id in negative_case_ids:
                continue
            negative_case_ids.add(case_id)
            source_group = relation_groups.get(
                relation_pair[0], relation_groups.get(relation_pair[1], "")
            )
            unrelated_pairs.append({
                "task": "deontic_conflict",
                "case_id": case_id,
                "expected": "",
                "predicted": "0",
                "split": _split_for_group(source_group, seed, test_ratio),
                "reviewer": "",
                "annotation": "",
                "notes": "Review if these distinct subject/action pairs can conflict.",
            })
    rng.shuffle(unrelated_pairs)
    negative_cases.extend(unrelated_pairs[:20])
    rng.shuffle(negative_cases)
    quality_rows.extend(conflict_cases)
    quality_rows.extend(negative_cases[: max(20, len(conflict_cases))])

    for path, fields, rows in (
        (confidence_path, CONFIDENCE_FIELDS, confidence_rows),
        (quality_path, QUALITY_FIELDS, quality_rows),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
    return len(confidence_rows), len(quality_rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--graph",
        type=Path,
        default=Path("outputs/unified_graphs/unified_knowledge_graph.json"),
    )
    parser.add_argument(
        "--confidence-output",
        type=Path,
        default=Path("outputs/evaluation/fusion_confidence_gold_template.csv"),
    )
    parser.add_argument(
        "--quality-output",
        type=Path,
        default=Path("outputs/evaluation/fusion_quality_gold_template.csv"),
    )
    parser.add_argument("--size", type=int, default=80)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--test-ratio", type=float, default=0.2)
    args = parser.parse_args()
    confidence_count, quality_count = sample_fusion_eval(
        args.graph, args.confidence_output, args.quality_output,
        args.size, args.seed, args.test_ratio,
    )
    print(f"Wrote {confidence_count} confidence rows to {args.confidence_output}")
    print(f"Wrote {quality_count} quality rows to {args.quality_output}")


if __name__ == "__main__":
    main()
