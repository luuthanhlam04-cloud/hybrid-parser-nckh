"""Deontic conflict detection and structured conflict reporting."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, Iterable, List


class ConflictResolver:
    def detect_deontic_conflicts(
        self, semantic_edges: Iterable[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        grouped: Dict[tuple[str, str], Dict[str, List[Dict[str, Any]]]] = defaultdict(
            lambda: defaultdict(list)
        )
        exception_sources = set()
        conditions_by_scope: Dict[tuple[str, str], set[str]] = defaultdict(set)
        edges = list(semantic_edges)
        for edge in edges:
            source_node_id = edge["properties"].get("source_node_id")
            if edge["type"] == "HAS_EXCEPTION":
                exception_sources.add(
                    (edge["source"], source_node_id)
                )
            elif edge["type"] == "HAS_CONDITION":
                conditions_by_scope[(edge["source"], source_node_id)].add(edge["target"])
            if edge["type"] in {"ALLOW", "PROHIBIT", "REQUIRE"}:
                grouped[(edge["source"], edge["target"])][edge["type"]].append(edge)

        conflicts = []
        for (source, target), modalities in grouped.items():
            positive = modalities.get("ALLOW", []) + modalities.get("REQUIRE", [])
            if not positive or not modalities.get("PROHIBIT"):
                continue
            explained = any(
                (subject, edge["properties"].get("source_node_id")) in exception_sources
                for subject in (source, target)
                for edge in positive + modalities["PROHIBIT"]
            )
            if not explained:
                conflicting_edges = positive + modalities["PROHIBIT"]
                positive_names = sorted(
                    relation_type
                    for relation_type in ("ALLOW", "REQUIRE")
                    if modalities.get(relation_type)
                )
                conflict_type = (
                    "ALLOW_PROHIBIT"
                    if positive_names == ["ALLOW"]
                    else "REQUIRE_PROHIBIT"
                    if positive_names == ["REQUIRE"]
                    else "ALLOW_REQUIRE_PROHIBIT"
                )
                incompatible_condition_pair = None
                for positive_edge in positive:
                    positive_scope = positive_edge["properties"].get("source_node_id")
                    positive_conditions = set().union(
                        *(
                            conditions_by_scope.get((endpoint, positive_scope), set())
                            for endpoint in (source, target)
                        )
                    )
                    if not positive_conditions:
                        continue
                    for prohibited_edge in modalities["PROHIBIT"]:
                        prohibited_scope = prohibited_edge["properties"].get("source_node_id")
                        prohibited_conditions = set().union(
                            *(
                                conditions_by_scope.get((endpoint, prohibited_scope), set())
                                for endpoint in (source, target)
                            )
                        )
                        if prohibited_conditions and positive_conditions.isdisjoint(
                            prohibited_conditions
                        ):
                            incompatible_condition_pair = (
                                positive_conditions, prohibited_conditions
                            )
                            break
                    if incompatible_condition_pair:
                        break
                conflicts.append({
                    "flag": "POTENTIAL_LEGAL_CONFLICT",
                    "conflict_type": conflict_type,
                    "source": source, "target": target,
                    "relation_ids": [
                        edge["properties"].get("relation_id")
                        for edge in conflicting_edges
                        if edge["properties"].get("relation_id")
                    ],
                    "message": (
                        f"{' and '.join(positive_names)} conflict with PROHIBIT "
                        "for the same subject/action without a linked exception."
                    ),
                    "relation_types": positive_names + ["PROHIBIT"],
                    "conditions": (
                        {
                            "positive": sorted(incompatible_condition_pair[0]),
                            "prohibited": sorted(incompatible_condition_pair[1]),
                        }
                        if incompatible_condition_pair
                        else None
                    ),
                    "context_status": (
                        "DISTINCT_EXPLICIT_CONDITIONS_REQUIRES_REVIEW"
                        if incompatible_condition_pair
                        else "SAME_OR_UNSPECIFIED_CONDITIONS"
                    ),
                })
        return conflicts

    def validate_endpoints(
        self, edges: Iterable[Dict[str, Any]], node_ids: set[str]
    ) -> List[Dict[str, Any]]:
        conflicts = []
        for edge in edges:
            missing = [endpoint for endpoint in (edge["source"], edge["target"])
                       if endpoint not in node_ids]
            if missing:
                conflicts.append({
                    "flag": "ORPHAN_EDGE", "source": edge["source"],
                    "target": edge["target"], "missing_nodes": missing,
                })
        return conflicts