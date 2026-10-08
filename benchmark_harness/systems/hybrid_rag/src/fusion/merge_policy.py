"""Policies used when combining physical and semantic graphs."""

from __future__ import annotations

from typing import Any, Dict


class MergePolicy:
    """Keep physical structure authoritative and semantic data additive."""

    physical_edge_types = frozenset({"BELONG_TO", "NEXT", "PREVIOUS"})

    def physical_node(self, node: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": node["id"],
            "node_kind": "PHYSICAL",
            "labels": list(node.get("labels", [])),
            "properties": dict(node.get("properties", {})),
            "provenance": ["M4"],
        }

    def semantic_node(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        node_id = entity["canonical_id"]
        ontology_class = entity.get("ontology_class", "UNKNOWN")
        fusion_kind = entity.get("fusion_kind", "CANONICAL_CONCEPT")
        label = {
            "LOCAL_MENTION": "SemanticMention",
            "REFERENCE": "LegalReference",
        }.get(fusion_kind, "SemanticEntity")
        return {
            "id": node_id,
            "node_kind": "SEMANTIC",
            "labels": [label, ontology_class],
            "properties": {
                key: value
                for key, value in entity.items()
                if key != "canonical_id"
            },
            "provenance": ["M7"],
        }