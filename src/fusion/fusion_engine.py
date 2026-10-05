"""Module 8: merge Physical Graph and Canonical Semantic Graph."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from .conflict_resolver import ConflictResolver
from .edge_mapper import EdgeMapper
from .graph_contract import validate_graph_inputs
from .m7_adapter import M7GraphAdapter
from .merge_policy import MergePolicy
from .node_mapper import NodeMapper


class FusionEngine:
    def __init__(self, confidence_calibrator: Any | None = None) -> None:
        self.policy = MergePolicy()
        self.edge_mapper = EdgeMapper(calibrator=confidence_calibrator)
        self.conflict_resolver = ConflictResolver()

    @staticmethod
    def _load(path: str | Path) -> Dict[str, Any]:
        with Path(path).open(encoding="utf-8") as stream:
            data = json.load(stream)
        if not isinstance(data, dict):
            raise ValueError(f"Graph input must be an object: {path}")
        return data

    def fuse(
        self, physical_graph_path: str | Path, semantic_graph_path: str | Path,
        output_path: str | Path | None = None,
    ) -> Dict[str, Any]:
        physical = self._load(physical_graph_path)
        semantic = M7GraphAdapter.adapt(self._load(semantic_graph_path))
        physical_nodes, physical_edges, entities, relations = validate_graph_inputs(
            physical, semantic
        )

        mapper = NodeMapper(physical_nodes)
        nodes = [self.policy.physical_node(node) for node in physical_nodes]
        semantic_ids = {entity.get("canonical_id") for entity in entities}
        semantic_ids.discard(None)
        nodes.extend(
            self.policy.semantic_node(entity)
            for entity in entities if entity.get("canonical_id")
        )
        entities_by_id = {
            entity["canonical_id"]: entity
            for entity in entities if entity.get("canonical_id")
        }
        edges = [self.edge_mapper.physical(edge) for edge in physical_edges]
        semantic_edges = []
        rejected_relations = list(semantic.get("rejected_relations", []))
        mentions = set()
        resolved_reference_edges = set()
        reference_reports: list[Dict[str, Any]] = []
        denotes_edges = semantic.get("denotes_edges", [])
        for denotes_edge in denotes_edges:
            source_node_id = denotes_edge.get("properties", {}).get("source_node_id")
            if (
                not source_node_id
                or not mapper.exists(source_node_id)
                or denotes_edge.get("source") not in semantic_ids
                or denotes_edge.get("target") not in semantic_ids
            ):
                rejected_relations.append({
                    "relation_id": None,
                    "reason": "INVALID_DENOTES_EDGE",
                })
                continue
            edges.append(denotes_edge)
            key = (source_node_id, denotes_edge["source"])
            if key not in mentions:
                edges.append(self.edge_mapper.mentions(
                    source_node_id,
                    denotes_edge["source"],
                    denotes_edge.get("properties", {}).get("evidence", ""),
                ))
                mentions.add(key)
        for relation in relations:
            source_node_id = relation.get("source_node_id")
            if not source_node_id or not mapper.exists(source_node_id):
                rejected_relations.append({
                    "relation_id": relation.get("relation_id"),
                    "reason": "ORPHAN_SOURCE_NODE",
                })
                continue
            target_entity = entities_by_id.get(relation.get("target"), {})
            reference_text = str(target_entity.get("canonical_text", ""))
            is_reference = relation.get("relation_type") == "REFERENCE_TO"
            raw_reference_scope = relation.get("reference_scope")
            reference_scope = str(raw_reference_scope or "").strip().upper()
            reference_ids = []
            known_internal_scopes = {"SAME_ARTICLE", "SAME_DOCUMENT"}
            should_resolve = (
                not reference_scope
                or reference_scope in known_internal_scopes
            )
            if is_reference and should_resolve:
                reference_ids = mapper.resolve_reference_hint(
                    relation.get("target_hint"), source_node_id
                )
                if not reference_ids:
                    reference_ids = mapper.resolve_reference_text(
                        reference_text, source_node_id
                    )
            if is_reference and should_resolve and not reference_ids:
                if reference_scope not in {"EXTERNAL", "AMBIGUOUS"}:
                    reference_ids = mapper.resolve_anaphoric_reference(
                        reference_text, source_node_id
                    )
            if is_reference and reference_ids:
                resolution_status = "RESOLVED_IN_M4"
            elif is_reference and reference_scope == "EXTERNAL":
                resolution_status = "OUT_OF_SCOPE_PER_M7"
            elif is_reference and reference_scope == "AMBIGUOUS":
                resolution_status = "AMBIGUOUS_PER_M7"
            elif is_reference and reference_scope and not should_resolve:
                resolution_status = "NOT_ATTEMPTED_PER_M7_SCOPE"
            elif is_reference:
                resolution_status = "TARGET_NOT_FOUND_IN_M4"
            else:
                resolution_status = ""
            if is_reference:
                reference_reports.append({
                    "relation_id": relation.get("relation_id"),
                    "m7_scope": raw_reference_scope or None,
                    "resolution_status": resolution_status,
                    "target_hint": relation.get("target_hint"),
                    "resolved_physical_node_ids": reference_ids,
                })
            mapped = self.edge_mapper.semantic(
                relation, {"source_confidence": 1.0},
                None,
                reference_ids if relation.get("relation_type") == "REFERENCE_TO" else None,
            )
            if is_reference:
                mapped["properties"]["reference_resolution_status"] = resolution_status
            if mapped["source"] not in semantic_ids or mapped["target"] not in semantic_ids:
                rejected_relations.append({
                    "relation_id": relation.get("relation_id"),
                    "reason": "UNKNOWN_SEMANTIC_ENDPOINT",
                })
                continue
            semantic_edges.append(mapped)
            edges.append(mapped)
            if is_reference and reference_ids:
                for reference_id in reference_ids:
                    key = (str(relation["target"]), reference_id)
                    if key not in resolved_reference_edges:
                        edges.append(self.edge_mapper.resolves_to(
                            str(relation["target"]),
                            reference_id,
                            relation.get("relation_id"),
                        ))
                        resolved_reference_edges.add(key)
            for entity_id in (mapped["source"], mapped["target"]):
                key = (source_node_id, entity_id)
                if key not in mentions:
                    edges.append(self.edge_mapper.mentions(
                        source_node_id, entity_id, relation.get("evidence", "")
                    ))
                    mentions.add(key)

        conflicts = self.conflict_resolver.detect_deontic_conflicts(semantic_edges)
        conflicts.extend(self.conflict_resolver.validate_endpoints(
            edges, {node["id"] for node in nodes}
        ))
        result = {
            "metadata": {
                "schema_version": "fusion.v1",
                "confidence_mode": (
                    "calibrated" if self.edge_mapper.calibrator is not None
                    else "heuristic_uncalibrated"
                ),
                "physical_node_count": len(physical_nodes),
                "semantic_entity_count": len(entities),
                "total_node_count": len(nodes),
                "physical_edge_count": len(physical_edges),
                "semantic_edge_count": len(semantic_edges),
                "denotes_edge_count": sum(
                    edge["type"] == "DENOTES" for edge in edges
                ),
                "mentions_edge_count": sum(edge["type"] == "MENTIONS" for edge in edges),
                "conflict_count": len(conflicts),
            },
            "nodes": nodes, "edges": edges, "conflicts": conflicts,
            "fusion_report": {
                "rejected_relations": rejected_relations,
                "rejected_relation_count": len(rejected_relations),
                "reference_resolution": {
                    "total": len(reference_reports),
                    "scope_counts": {
                        scope: sum(
                            report.get("m7_scope") == scope
                            for report in reference_reports
                        )
                        for scope in sorted({
                            report["m7_scope"]
                            for report in reference_reports
                            if report.get("m7_scope")
                        })
                    },
                    "status_counts": {
                        status: sum(
                            report["resolution_status"] == status
                            for report in reference_reports
                        )
                        for status in sorted({
                            report["resolution_status"]
                            for report in reference_reports
                        })
                    },
                    "items": reference_reports,
                },
                "deontic_conflict_count": sum(
                    conflict.get("conflict_type") in {
                        "ALLOW_PROHIBIT",
                        "REQUIRE_PROHIBIT",
                        "ALLOW_REQUIRE_PROHIBIT",
                    }
                    for conflict in conflicts
                ),
                "reference_targets_not_found_in_m4_count": sum(
                    report["resolution_status"] == "TARGET_NOT_FOUND_IN_M4"
                    for report in reference_reports
                ),
            },
        }
        if output_path is not None:
            target = Path(output_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        return result