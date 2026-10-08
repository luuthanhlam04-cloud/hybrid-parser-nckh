"""Deontic conflict detection and structured conflict reporting."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, Iterable, List


class ConflictResolver:
    def detect_deontic_conflicts(
        self, nodes: Iterable[Dict[str, Any]], semantic_edges: Iterable[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        # Map norm_id -> subjects, actions, conditions, exceptions
        norm_subjects: Dict[str, set[str]] = defaultdict(set)
        norm_actions: Dict[str, set[str]] = defaultdict(set)
        norm_conditions: Dict[str, set[str]] = defaultdict(set)
        norm_exceptions: Dict[str, set[str]] = defaultdict(set)
        
        edges = list(semantic_edges)
        for edge in edges:
            source = edge["source"]
            target = edge["target"]
            rel_type = edge["type"]
            if rel_type == "HAS_SUBJECT":
                norm_subjects[source].add(target)
            elif rel_type == "HAS_ACTION":
                norm_actions[source].add(target)
            elif rel_type == "HAS_CONDITION":
                norm_conditions[source].add(target)
            elif rel_type == "HAS_EXCEPTION":
                norm_exceptions[source].add(target)
                
        # Group GLOBAL_NORM nodes by (subject, action) pairs
        # pair -> modality -> list of norm_ids
        grouped: Dict[tuple[str, str], Dict[str, List[str]]] = defaultdict(
            lambda: defaultdict(list)
        )
        
        global_norms = [n for n in nodes if n.get("properties", {}).get("ontology_class") == "GLOBAL_NORM"]
        
        for norm in global_norms:
            norm_id = norm["id"]
            modality = norm.get("properties", {}).get("modality", "").upper()
            if not modality:
                continue
                
            for subj in norm_subjects[norm_id]:
                for act in norm_actions[norm_id]:
                    grouped[(subj, act)][modality].append(norm_id)
                    
        conflicts = []
        for (subj, act), modalities in grouped.items():
            positive_norms = modalities.get("ALLOW", []) + modalities.get("REQUIRE", [])
            prohibit_norms = modalities.get("PROHIBIT", [])
            
            if not positive_norms or not prohibit_norms:
                continue
                
            # If there's an exception, it might explain the conflict
            # Wait, in V3.0 the logic is: compare their HAS_CONDITION / HAS_EXCEPTION targets.
            explained = False
            for p_norm in positive_norms:
                p_conds = norm_conditions[p_norm]
                p_excs = norm_exceptions[p_norm]
                
                for pr_norm in prohibit_norms:
                    pr_conds = norm_conditions[pr_norm]
                    pr_excs = norm_exceptions[pr_norm]
                    
                    # If they have disjoint conditions, they might conflict
                    if p_conds and pr_conds and p_conds.isdisjoint(pr_conds):
                        incompatible_condition_pair = (p_conds, pr_conds)
                    else:
                        incompatible_condition_pair = None
                        
                    # If exceptions explain it
                    if p_excs or pr_excs:
                        explained = True
                        break
                        
                if explained:
                    break
                    
            if not explained:
                positive_names = sorted(
                    mod
                    for mod in ("ALLOW", "REQUIRE")
                    if modalities.get(mod)
                )
                conflict_type = (
                    "ALLOW_PROHIBIT"
                    if positive_names == ["ALLOW"]
                    else "REQUIRE_PROHIBIT"
                    if positive_names == ["REQUIRE"]
                    else "ALLOW_REQUIRE_PROHIBIT"
                )
                conflicting_nodes = positive_norms + prohibit_norms
                conflicts.append({
                    "flag": "POTENTIAL_LEGAL_CONFLICT",
                    "conflict_type": conflict_type,
                    "subject": subj, "action": act,
                    "global_norm_ids": conflicting_nodes,
                    "message": (
                        f"{' and '.join(positive_names)} conflict with PROHIBIT "
                        "for the same subject/action without a linked exception."
                    ),
                    "relation_types": positive_names + ["PROHIBIT"],
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