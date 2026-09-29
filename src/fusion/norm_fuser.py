"""Norm Promotion: Aggregating Local Norms into Global Norm Hubs."""

from __future__ import annotations
import hashlib
from typing import Any, Dict, List, Set, Tuple

class NormFuser:
    def __init__(self) -> None:
        pass

    def fuse(
        self,
        relations: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Groups M7 adapter relations into GLOBAL_NORM hubs.
        Returns:
            global_norms: List of new GLOBAL_NORM node dicts.
            global_edges: List of relation dicts originating from the GLOBAL_NORM hubs.
            remaining_relations: List of relations not part of any norm.
        """
        norm_relations: Dict[str, List[Dict[str, Any]]] = {}
        remaining_relations = []
        
        for rel in relations:
            norm_id = rel.get("norm_id")
            if norm_id:
                if norm_id not in norm_relations:
                    norm_relations[norm_id] = []
                norm_relations[norm_id].append(rel)
            else:
                remaining_relations.append(rel)

        grouped_norms: Dict[str, Dict[str, Any]] = {}

        for norm_id, rels in norm_relations.items():
            modality = "ALLOW"
            subject_ids = []
            action_ids = []
            condition_ids = []
            exception_ids = []
            consequence_ids = []
            source_node_id = None
            
            for r in rels:
                if not source_node_id:
                    source_node_id = r.get("source_node_id")
                rel_type = r.get("relation_type")
                if rel_type in {"ALLOW", "PROHIBIT", "REQUIRE"}:
                    modality = rel_type
                    subject_ids.append(r["source"])
                    action_ids.append(r["target"])
                elif rel_type == "HAS_CONDITION":
                    condition_ids.append(r["target"])
                elif rel_type == "HAS_EXCEPTION":
                    exception_ids.append(r["target"])
                elif rel_type == "HAS_CONSEQUENCE":
                    consequence_ids.append(r["target"])
                    
            subject_ids = sorted(list(set([str(s) for s in subject_ids])))
            action_ids = sorted(list(set([str(a) for a in action_ids])))
            condition_ids = sorted(list(set([str(c) for c in condition_ids])))
            exception_ids = sorted(list(set([str(e) for e in exception_ids])))
            consequence_ids = sorted(list(set([str(c) for c in consequence_ids])))
            
            hash_input = f"{modality}_{'_'.join(subject_ids)}_{'_'.join(action_ids)}_{'_'.join(condition_ids)}"
            hash_key = f"GNORM_{hashlib.md5(hash_input.encode('utf-8')).hexdigest()[:12]}"
            
            if hash_key not in grouped_norms:
                global_norm = {
                    "id": hash_key,
                    "node_kind": "SEMANTIC",
                    "labels": ["SemanticEntity", "GLOBAL_NORM"],
                    "properties": {
                        "ontology_class": "GLOBAL_NORM",
                        "modality": modality,
                        "fusion_kind": "GLOBAL_NORM",
                    },
                    "provenance": ["M8"]
                }
                
                hub_relations = []
                for s in subject_ids:
                    hub_relations.append({"source": hash_key, "target": s, "relation_type": "HAS_SUBJECT"})
                for a in action_ids:
                    hub_relations.append({"source": hash_key, "target": a, "relation_type": "HAS_ACTION"})
                for c in condition_ids:
                    hub_relations.append({"source": hash_key, "target": c, "relation_type": "HAS_CONDITION"})
                for e in exception_ids:
                    hub_relations.append({"source": hash_key, "target": e, "relation_type": "HAS_EXCEPTION"})
                for c in consequence_ids:
                    hub_relations.append({"source": hash_key, "target": c, "relation_type": "HAS_CONSEQUENCE"})
                    
                grouped_norms[hash_key] = {
                    "norm_node": global_norm,
                    "source_node_ids": set(),
                    "relations": hub_relations
                }
            
            if source_node_id:
                grouped_norms[hash_key]["source_node_ids"].add(source_node_id)

        global_norms = []
        global_edges = []
        
        for hash_key, data in grouped_norms.items():
            norm_node = data["norm_node"]
            norm_node["properties"]["source_node_ids"] = list(data["source_node_ids"])
            global_norms.append(norm_node)
            global_edges.extend(data["relations"])
            
        return global_norms, global_edges, remaining_relations
