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
from .norm_fuser import NormFuser
from .reference_resolver import ReferenceResolver


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
        
        # 1. STRICT PRUNING OF M7 NODES
        norm_argument_ids: set[str] = set()
        for relation in relations:
            if not relation.get("norm_id"):
                continue
            for key in (
                "source", "target", "object_ids", "condition_ids",
                "exception_ids", "consequence_ids",
            ):
                value = relation.get(key)
                if isinstance(value, str) and value:
                    norm_argument_ids.add(value)
                elif isinstance(value, list):
                    norm_argument_ids.update(
                        item for item in value if isinstance(item, str) and item
                    )
            for group in relation.get("condition_groups", []):
                norm_argument_ids.update(
                    item
                    for item in group.get("condition_ids", [])
                    if isinstance(item, str) and item
                )

        kept_semantic_nodes = []
        for entity in entities:
            # We use merge policy to get the final node structure
            node = self.policy.semantic_node(entity)
            props = node.get("properties", {})
            fusion_kind = props.get("fusion_kind", "")
            
            # STRICT KILL RULE: Do not allow LOCAL_MENTION or REFERENCE nodes into the final graph
            if fusion_kind in ["LOCAL_MENTION", "REFERENCE"] and node["id"] not in norm_argument_ids:
                continue 
                
            # STRIP EVIDENCE RULE: Remove raw text from semantic layer
            if "evidence" in props:
                del props["evidence"]
                
            kept_semantic_nodes.append(node)

        semantic_ids = {node["id"] for node in kept_semantic_nodes}
        entities_by_id = {node["id"]: node for node in kept_semantic_nodes}
        
        # Norm Promotion using relationships from M7 Adapter
        norm_fuser = NormFuser()
        global_norms, global_edges, remaining_relations = norm_fuser.fuse(relations)
        
        # 2. Add GLOBAL_NORM nodes generated from your norm_fuser.py
        kept_semantic_nodes.extend(global_norms)
        
        for gnorm in global_norms:
            semantic_ids.add(gnorm["id"])
            entities_by_id[gnorm["id"]] = gnorm

        nodes.extend(kept_semantic_nodes)

        edges = [self.edge_mapper.physical(edge) for edge in physical_edges]
        semantic_edges = []
        rejected_relations = list(semantic.get("rejected_relations", []))
        mentions = set()
        resolved_reference_edges = set()
        reference_reports: list[Dict[str, Any]] = []
        
        # Process global edges
        for rel in global_edges:
            gnorm_id = rel["source"]
            gnorm = entities_by_id[gnorm_id]
            source_node_ids = set(gnorm.get("properties", {}).get("source_node_ids", []))
            if not source_node_ids:
                source_node_ids = {"UNKNOWN"}
            mapped = self.edge_mapper.global_semantic(rel, source_node_ids)
            if mapped["target"] not in semantic_ids:
                continue
            semantic_edges.append(mapped)
            edges.append(mapped)
            
            # MENTIONS edges from source_node_ids to GLOBAL_NORM and Concepts
            for sid in source_node_ids:
                key = (sid, gnorm_id)
                if key not in mentions and mapper.exists(sid):
                    edges.append(self.edge_mapper.mentions(sid, gnorm_id, ""))
                    mentions.add(key)
                # Also MENTION the target concepts
                target_id = mapped["target"]
                key_tgt = (sid, target_id)
                if key_tgt not in mentions and mapper.exists(sid):
                    edges.append(self.edge_mapper.mentions(sid, target_id, ""))
                    mentions.add(key_tgt)

        ref_resolver = ReferenceResolver(mapper)
        
        for relation in remaining_relations:
            source_node_id = relation.get("source_node_id")
            if not source_node_id or not mapper.exists(source_node_id):
                rejected_relations.append({
                    "relation_id": relation.get("relation_id"),
                    "reason": "ORPHAN_SOURCE_NODE",
                })
                continue
            
            is_reference = relation.get("relation_type") == "REFERENCE_TO"
            reference_ids = []
            resolution_status = ""
            
            if is_reference:
                # Use entities_by_id to find canonical_text
                # Wait, entities_by_id has nodes, so text is in properties
                ref_node = entities_by_id.get(relation.get("target"), {})
                reference_text = str(ref_node.get("properties", {}).get("canonical_text", ""))
                # Mocking entities_by_id dict format expected by ref_resolver
                mock_entities = {relation.get("target"): {"canonical_text": reference_text}}
                
                reference_ids, resolution_status = ref_resolver.resolve(relation, source_node_id, mock_entities)
                reference_reports.append({
                    "relation_id": relation.get("relation_id"),
                    "m7_scope": relation.get("reference_scope") or None,
                    "resolution_status": resolution_status,
                    "target_hint": relation.get("target_hint"),
                    "resolved_physical_node_ids": reference_ids,
                })
                
            mapped = self.edge_mapper.global_semantic(
                relation, {source_node_id}, None, reference_ids if is_reference else None
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
                        source_node_id, entity_id, ""
                    ))
                    mentions.add(key)

        conflicts = self.conflict_resolver.detect_deontic_conflicts(nodes, semantic_edges)
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
                "semantic_entity_count": len(kept_semantic_nodes),
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