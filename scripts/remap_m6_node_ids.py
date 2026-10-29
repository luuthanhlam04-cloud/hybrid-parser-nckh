#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Remap node_id của output M6 cũ sang Physical Graph/M5 hiện tại.

Script không sửa file nguồn và không vá trực tiếp output M7. Sau khi remap M6,
hãy chạy lại M7 để toàn bộ provenance ID, mention ID, norm và edge được sinh lại.

Ví dụ:
    python scripts/remap_m6_node_ids.py \
      --input old_semantic_extraction.json \
      --supplement outputs/semantic_graphs/semantic_extraction_added_node.jsonl
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PHYSICAL = PROJECT_ROOT / "outputs/physical_graphs/physical_graph.json"
DEFAULT_ROUTING = PROJECT_ROOT / "outputs/candidate_nodes/routing_candidates.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "outputs/semantic_graphs/semantic_extraction_remapped.json"
DEFAULT_REPORT = PROJECT_ROOT / "outputs/semantic_graphs/semantic_extraction_remap_report.json"

POSITION_SUFFIX_RE = re.compile(r"_p\d+$")


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def normalize_text(value: Any) -> str:
    text = unicodedata.normalize("NFC", str(value or "")).casefold()
    return re.sub(r"\s+", " ", text).strip()


def structural_key(node_id: str) -> str:
    """Khóa ổn định, bỏ offset `_p...` và gom d/đ vào cùng bucket.

    Bản graph cũ từng sinh cả điểm d và đ thành `diem-d`. Gom hai marker
    vào cùng bucket cho phép ghép theo thứ tự và evidence mà không làm mất
    semantic ID `diem-dd` ở output mới.
    """
    key = POSITION_SUFFIX_RE.sub("", node_id)
    return key.replace("_diem-dd", "_diem-d")


def extraction_fragments(node: dict[str, Any]) -> list[str]:
    extraction = node.get("extraction") or {}
    fragments: list[str] = []
    for entity in extraction.get("entities") or []:
        fragments.extend([entity.get("text", ""), entity.get("evidence", "")])
    for relation in extraction.get("relations") or []:
        fragments.append(relation.get("evidence", ""))
    return [normalize_text(item) for item in fragments if normalize_text(item)]


def physical_context(
    node_id: str,
    physical_by_id: dict[str, dict[str, Any]],
) -> tuple[str, str]:
    node = physical_by_id[node_id]
    direct = ""
    context_parts: list[str] = []
    visited: set[str] = set()
    while node and node.get("id") not in visited:
        visited.add(node["id"])
        props = node.get("properties") or {}
        text = normalize_text(f"{props.get('title') or ''} {props.get('text') or ''}")
        if not direct:
            direct = text
        if text:
            context_parts.append(text)
        parent_id = props.get("parent_id")
        node = physical_by_id.get(parent_id) if parent_id else None
    return direct, " ".join(context_parts)


def content_score(
    source_node: dict[str, Any],
    target_id: str,
    physical_by_id: dict[str, dict[str, Any]],
) -> float:
    fragments = extraction_fragments(source_node)
    if not fragments:
        return 0.0
    direct, context = physical_context(target_id, physical_by_id)
    scores: list[float] = []
    for fragment in fragments:
        if fragment in direct:
            scores.append(1.0)
        elif fragment in context:
            scores.append(0.9)
        else:
            scores.append(SequenceMatcher(None, fragment, direct).ratio() * 0.8)
    return round(max(scores, default=0.0), 4)


def validate_extraction(node: dict[str, Any]) -> list[str]:
    """Kiểm tra tối thiểu schema và referential integrity, không gọi LLM."""
    errors: list[str] = []
    extraction = node.get("extraction")
    if not isinstance(extraction, dict):
        return ["extraction_not_object"]
    entities = extraction.get("entities")
    relations = extraction.get("relations")
    if not isinstance(entities, list):
        errors.append("entities_not_array")
        entities = []
    if not isinstance(relations, list):
        errors.append("relations_not_array")
        relations = []

    ids = [entity.get("id") for entity in entities if isinstance(entity, dict)]
    if any(not isinstance(entity_id, str) or not entity_id for entity_id in ids):
        errors.append("missing_entity_id")
    if len(ids) != len(set(ids)):
        errors.append("duplicate_entity_id")
    valid_ids = set(ids)
    for index, relation in enumerate(relations):
        if not isinstance(relation, dict):
            errors.append(f"relation_{index}_not_object")
            continue
        source = relation.get("source")
        target = relation.get("target")
        if source is not None and source not in valid_ids:
            errors.append(f"relation_{index}_unknown_source")
        if target not in valid_ids:
            errors.append(f"relation_{index}_unknown_target")
    return errors


def load_supplements(paths: Iterable[Path]) -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []
    for path in paths:
        if path.suffix.lower() == ".jsonl":
            for line_number, line in enumerate(
                path.read_text(encoding="utf-8-sig").splitlines(), start=1
            ):
                if not line.strip():
                    continue
                item = json.loads(line)
                if not isinstance(item, dict):
                    raise ValueError(f"{path}:{line_number} không phải JSON object")
                nodes.append(item)
            continue

        data = load_json(path)
        if isinstance(data, dict) and isinstance(data.get("extracted_nodes"), list):
            nodes.extend(data["extracted_nodes"])
        elif isinstance(data, dict) and data.get("node_id"):
            nodes.append(data)
        elif isinstance(data, list):
            nodes.extend(data)
        else:
            raise ValueError(f"Không nhận diện được định dạng supplement: {path}")
    return nodes


def remap(
    source_data: dict[str, Any],
    physical_data: dict[str, Any],
    routing_data: dict[str, Any],
    supplements: list[dict[str, Any]],
    fill_empty_point_objects: bool = False,
) -> tuple[dict[str, Any], dict[str, Any]]:
    source_nodes = source_data.get("extracted_nodes")
    if not isinstance(source_nodes, list):
        raise ValueError("Input M6 phải có mảng extracted_nodes")

    physical_nodes = physical_data.get("nodes") or []
    physical_by_id = {node["id"]: node for node in physical_nodes}
    candidate_ids = [
        item["node_id"]
        for item in routing_data.get("candidates") or []
        if item.get("route") == "LLM_CANDIDATE"
    ]
    missing_physical = [node_id for node_id in candidate_ids if node_id not in physical_by_id]
    if missing_physical:
        raise ValueError(
            f"{len(missing_physical)} LLM_CANDIDATE không tồn tại trong physical graph"
        )

    source_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    target_groups: dict[str, list[str]] = defaultdict(list)
    for node in source_nodes:
        node_id = node.get("node_id")
        if not isinstance(node_id, str) or not node_id:
            raise ValueError("Có extraction node thiếu node_id")
        source_groups[structural_key(node_id)].append(node)
    for node_id in candidate_ids:
        target_groups[structural_key(node_id)].append(node_id)

    output_by_id: dict[str, dict[str, Any]] = {}
    mappings: list[dict[str, Any]] = []
    unmatched_source: list[str] = []

    for key, old_group in source_groups.items():
        available = list(target_groups.get(key, []))
        if not available:
            unmatched_source.extend(node["node_id"] for node in old_group)
            continue

        for source_node in old_group:
            if not available:
                unmatched_source.append(source_node["node_id"])
                continue
            scored = [
                (content_score(source_node, target_id, physical_by_id), index, target_id)
                for index, target_id in enumerate(available)
            ]
            # Score cao nhất; nếu hòa thì giữ thứ tự hiện hành để xử lý d/đ ổn định.
            score, _, target_id = max(scored, key=lambda item: (item[0], -item[1]))
            available.remove(target_id)

            remapped_node = dict(source_node)
            remapped_node.pop("extraction_provenance", None)
            remapped_node["node_id"] = target_id
            output_by_id[target_id] = remapped_node
            mappings.append(
                {
                    "old_node_id": source_node["node_id"],
                    "new_node_id": target_id,
                    "structural_key": key,
                    "content_score": score,
                    "content_status": (
                        "NO_EXTRACTION_CONTENT"
                        if not extraction_fragments(source_node)
                        else "VERIFIED"
                        if score >= 0.6
                        else "LOW_CONFIDENCE"
                    ),
                }
            )

    supplement_ids: list[str] = []
    for node in supplements:
        node_id = node.get("node_id")
        if node_id not in candidate_ids:
            raise ValueError(f"Supplement node không phải LLM_CANDIDATE hiện tại: {node_id}")
        if node_id in output_by_id:
            raise ValueError(f"Supplement trùng node đã remap: {node_id}")
        clean_node = dict(node)
        clean_node.pop("extraction_provenance", None)
        output_by_id[node_id] = clean_node
        supplement_ids.append(node_id)

    backfilled_ids: list[str] = []
    if fill_empty_point_objects:
        for node_id, node in output_by_id.items():
            extraction = node.get("extraction") or {}
            if extraction.get("entities") or extraction.get("relations"):
                continue
            physical_node = physical_by_id[node_id]
            if "POINT" not in (physical_node.get("labels") or []):
                continue
            evidence = str((physical_node.get("properties") or {}).get("text") or "").strip()
            if not evidence:
                continue
            entity_text = evidence.rstrip(";. ").strip()
            if not entity_text:
                continue
            node["extraction"] = {
                "entities": [
                    {
                        "id": "e1",
                        "text": entity_text,
                        "entity_type": "OBJECT",
                        "evidence": evidence,
                    }
                ],
                "relations": [],
            }
            backfilled_ids.append(node_id)

    schema_errors: list[dict[str, Any]] = []
    ordered_output: list[dict[str, Any]] = []
    for node_id in candidate_ids:
        node = output_by_id.get(node_id)
        if node is None:
            continue
        errors = validate_extraction(node)
        if errors:
            schema_errors.append({"node_id": node_id, "errors": errors})
        ordered_output.append(node)

    unmatched_current = [node_id for node_id in candidate_ids if node_id not in output_by_id]
    source_metadata = source_data.get("metadata") or {}
    source_model = source_metadata.get("model", "unknown")
    is_composite = bool(supplement_ids)

    output = {
        "metadata": {
            "model": "composite/remapped" if is_composite else source_model,
            "source_model": source_model,
            "total_candidates_processed": len(ordered_output),
            "current_llm_candidate_count": len(candidate_ids),
            "remapped_node_count": len(mappings),
            "supplemented_node_count": len(supplement_ids),
            "deterministic_backfill_count": len(backfilled_ids),
            "dataset_type": "composite_migration" if is_composite else "id_remap",
            "provenance_note": (
                "ID được remap sang Physical Graph hiện tại; supplement được giữ nguyên "
                "provenance. Không phải một lần chạy duy nhất của một model."
            ),
            "source_metadata": source_metadata,
        },
        "extracted_nodes": ordered_output,
    }
    report = {
        "summary": {
            "source_nodes": len(source_nodes),
            "current_llm_candidates": len(candidate_ids),
            "mapped_nodes": len(mappings),
            "supplemented_nodes": len(supplement_ids),
            "deterministic_backfilled_nodes": len(backfilled_ids),
            "output_nodes": len(ordered_output),
            "unmatched_source_nodes": len(unmatched_source),
            "unmatched_current_nodes": len(unmatched_current),
            "schema_error_nodes": len(schema_errors),
            "low_confidence_mappings": sum(
                item["content_status"] == "LOW_CONFIDENCE" for item in mappings
            ),
            "contentless_mappings": sum(
                item["content_status"] == "NO_EXTRACTION_CONTENT" for item in mappings
            ),
        },
        "mappings": mappings,
        "supplement_node_ids": supplement_ids,
        "deterministic_backfill_node_ids": backfilled_ids,
        "unmatched_source_node_ids": unmatched_source,
        "unmatched_current_node_ids": unmatched_current,
        "schema_errors": schema_errors,
    }
    return output, report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Remap node_id của output M6 cũ sang Physical Graph/M5 hiện tại."
    )
    parser.add_argument("--input", required=True, type=Path, help="Output M6 cũ (.json)")
    parser.add_argument("--physical", type=Path, default=DEFAULT_PHYSICAL)
    parser.add_argument("--routing", type=Path, default=DEFAULT_ROUTING)
    parser.add_argument(
        "--supplement",
        type=Path,
        action="append",
        default=[],
        help="JSON/JSONL chứa node mới; có thể truyền nhiều lần",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="Không ghi output nếu còn candidate hiện tại chưa có extraction",
    )
    parser.add_argument(
        "--fill-empty-point-objects",
        action="store_true",
        help=(
            "Backfill node POINT rỗng thành một OBJECT lấy nguyên văn từ physical graph; "
            "ghi provenance deterministic/human_review_required"
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = load_json(args.input.resolve())
    physical = load_json(args.physical.resolve())
    routing = load_json(args.routing.resolve())
    supplements = load_supplements(path.resolve() for path in args.supplement)
    output, report = remap(
        source,
        physical,
        routing,
        supplements,
        fill_empty_point_objects=args.fill_empty_point_objects,
    )

    summary = report["summary"]
    if args.require_complete and (
        summary["unmatched_source_nodes"]
        or summary["unmatched_current_nodes"]
        or summary["schema_error_nodes"]
    ):
        write_json(args.report.resolve(), report)
        print("Remap chưa hoàn chỉnh; chỉ ghi report, không ghi output.")
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 2

    write_json(args.output.resolve(), output)
    write_json(args.report.resolve(), report)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Output: {args.output.resolve()}")
    print(f"Report: {args.report.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
