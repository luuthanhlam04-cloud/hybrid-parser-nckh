"""Classify opposite legal modalities with scope and provenance."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, Iterable, List


class ConflictResolver:
    @staticmethod
    def _condition_text(nodes_by_id: Dict[str, Dict[str, Any]], ids: set[str]) -> list[str]:
        return sorted(
            str(nodes_by_id.get(cid, {}).get("properties", {}).get("canonical_text", "")).casefold().strip()
            for cid in ids
        )

    @staticmethod
    def _scope_status(allow_text: list[str], prohibit_text: list[str], has_exception: bool) -> tuple[str, str]:
        if has_exception:
            return "REVIEW_REQUIRED", "EXCEPTION_SCOPE_REQUIRES_REVIEW"
        prohib = " ".join(prohibit_text)
        allow = " ".join(allow_text)
        if "pháp luật không cho phép" in prohib:
            return "REVIEW_REQUIRED", "CONDITIONAL_PROHIBITION_REQUIRES_LEGAL_REVIEW"
        if "không thu tiền sử dụng đất" in prohib and (
            "có thu tiền sử dụng đất" in allow or "thu tiền thuê đất một lần" in allow
            or "thu tiền thuê đất hằng năm" in allow
        ):
            return "CONTEXTUAL_DIFFERENCE", "DISTINCT_LAND_PAYMENT_REGIMES"
        if allow_text and prohibit_text and set(allow_text) == set(prohibit_text):
            return "POTENTIAL_LEGAL_CONFLICT", "MATCHING_EXPLICIT_CONDITIONS"
        return "REVIEW_REQUIRED", "CONDITION_SCOPE_NOT_PROVEN_EQUAL"

    def detect_deontic_conflicts(
        self, nodes: Iterable[Dict[str, Any]], semantic_edges: Iterable[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        node_list = list(nodes)
        nodes_by_id = {node["id"]: node for node in node_list}
        links: Dict[str, Dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
        for edge in semantic_edges:
            if edge.get("type") in {"HAS_SUBJECT", "HAS_ACTION", "HAS_CONDITION", "HAS_EXCEPTION", "HAS_OBJECT"}:
                links[edge["source"]][edge["type"]].add(edge["target"])

        grouped: Dict[tuple[str, str], Dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
        for norm in node_list:
            if norm.get("properties", {}).get("ontology_class") != "GLOBAL_NORM":
                continue
            modality = str(norm.get("properties", {}).get("modality", "")).upper()
            for subject in links[norm["id"]]["HAS_SUBJECT"]:
                for action in links[norm["id"]]["HAS_ACTION"]:
                    grouped[(subject, action)][modality].add(norm["id"])

        findings: List[Dict[str, Any]] = []
        for (subject, action), modalities in sorted(grouped.items()):
            for modality in ("ALLOW", "REQUIRE"):
                for positive_id in sorted(modalities.get(modality, set())):
                    for prohibit_id in sorted(modalities.get("PROHIBIT", set())):
                        positive, negative = links[positive_id], links[prohibit_id]
                        p_conditions = self._condition_text(nodes_by_id, positive["HAS_CONDITION"])
                        n_conditions = self._condition_text(nodes_by_id, negative["HAS_CONDITION"])
                        flag, reason = self._scope_status(
                            p_conditions, n_conditions,
                            bool(positive["HAS_EXCEPTION"] or negative["HAS_EXCEPTION"]),
                        )
                        if flag == "POTENTIAL_LEGAL_CONFLICT" and positive["HAS_OBJECT"] != negative["HAS_OBJECT"]:
                            flag, reason = "REVIEW_REQUIRED", "OBJECT_SCOPE_NOT_PROVEN_EQUAL"
                        source_nodes = {
                            nid: sorted(nodes_by_id[nid].get("properties", {}).get("source_node_ids", []))
                            for nid in (positive_id, prohibit_id)
                        }
                        findings.append({
                            "flag": flag,
                            "conflict_type": f"{modality}_PROHIBIT",
                            "subject": subject,
                            "action": action,
                            "global_norm_ids": [positive_id, prohibit_id],
                            "relation_types": [modality, "PROHIBIT"],
                            "context_status": reason,
                            "positive_conditions": p_conditions,
                            "prohibit_conditions": n_conditions,
                            "positive_object_ids": sorted(positive["HAS_OBJECT"]),
                            "prohibit_object_ids": sorted(negative["HAS_OBJECT"]),
                            "source_node_ids": source_nodes,
                        })
        return findings

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
