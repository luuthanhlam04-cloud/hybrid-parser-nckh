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
            object_ids = []
            condition_ids = []
            exception_ids = []
            consequence_ids = []
            condition_groups = []
            source_node_id = None
            
            for r in rels:
                if not source_node_id:
                    source_node_id = r.get("source_node_id")
                rel_type = r.get("relation_type")
                if rel_type in {"ALLOW", "PROHIBIT", "REQUIRE"}:
                    modality = rel_type
                    # I5 Fix: Subject-Only PARTIAL norm has target=None (no action)
                    if r.get("source") is not None:
                        subject_ids.append(r["source"])
                    if r.get("target") is not None:
                        action_ids.append(r["target"])
                    object_ids.extend(r.get("object_ids", []))
                    condition_ids.extend(r.get("condition_ids", []))
                    exception_ids.extend(r.get("exception_ids", []))
                    consequence_ids.extend(r.get("consequence_ids", []))
                    condition_groups.extend(r.get("condition_groups", []))
                elif rel_type == "HAS_OBJECT":
                    object_ids.append(r["target"])
                elif rel_type == "HAS_CONDITION":
                    condition_ids.append(r["target"])
                elif rel_type == "HAS_EXCEPTION":
                    exception_ids.append(r["target"])
                elif rel_type == "HAS_CONSEQUENCE":
                    consequence_ids.append(r["target"])
                    
            subject_ids = sorted(list(set([str(s) for s in subject_ids])))
            action_ids = sorted(list(set([str(a) for a in action_ids])))
            object_ids = sorted(list(set(str(item) for item in object_ids if item is not None)))
            condition_ids = sorted(list(set(str(item) for item in condition_ids if item is not None)))
            exception_ids = sorted(list(set(str(item) for item in exception_ids if item is not None)))
            consequence_ids = sorted(list(set(str(item) for item in consequence_ids if item is not None)))
            normalized_groups = []
            for group in condition_groups:
                normalized_groups.append({
                    **group,
                    "condition_ids": sorted(set(
                        str(item) for item in group.get("condition_ids", [])
                    )),
                })
            normalized_groups.sort(key=lambda group: (
                str(group.get("group_id", "")),
                str(group.get("operator", "")),
                tuple(group.get("condition_ids", [])),
                bool(group.get("is_complex", False)),
            ))
            
            # Hash key chuẩn — dạng tuple thay vì string join để tránh hash collision.
            # CONTRACT (m7_m8_adapter_contract.md §4):
            # PARTIAL+PARTIAL chỉ merge khi TẤT CẢ context tương thích:
            # modality, actions, conditions, exceptions, consequences phải giống nhau.
            # subject=[] ở cả hai → hash key giống nhau → merge đúng.
            # Nếu exception khác nhau → hash key khác → KHÔNG merge (đã fix Bug #2).
            hash_key_tuple = (
                modality,
                tuple(subject_ids),
                tuple(action_ids),
                tuple(object_ids),
                tuple(condition_ids),
                tuple(exception_ids),
                tuple(consequence_ids),
                tuple(
                    (
                        str(group.get("group_id", "")),
                        str(group.get("operator", "")),
                        tuple(group.get("condition_ids", [])),
                        bool(group.get("is_complex", False)),
                    )
                    for group in normalized_groups
                ),
            )
            hash_key = f"GNORM_{hashlib.md5(str(hash_key_tuple).encode('utf-8')).hexdigest()[:12]}"
            
            if hash_key not in grouped_norms:
                global_norm = {
                    "id": hash_key,
                    "node_kind": "SEMANTIC",
                    "labels": ["SemanticEntity", "GLOBAL_NORM"],
                    "properties": {
                        "ontology_class": "GLOBAL_NORM",
                        "modality": modality,
                        "fusion_kind": "GLOBAL_NORM",
                        "object_ids": object_ids,
                        "condition_ids": condition_ids,
                        "exception_ids": exception_ids,
                        "consequence_ids": consequence_ids,
                        "condition_groups": normalized_groups,
                    },
                    "provenance": ["M8"]
                }
                
                hub_relations = []
                for s in subject_ids:
                    hub_relations.append({"source": hash_key, "target": s, "relation_type": "HAS_SUBJECT"})
                for a in action_ids:
                    hub_relations.append({"source": hash_key, "target": a, "relation_type": "HAS_ACTION"})
                for o in object_ids:
                    hub_relations.append({"source": hash_key, "target": o, "relation_type": "HAS_OBJECT"})
                for c in condition_ids:
                    hub_relations.append({"source": hash_key, "target": c, "relation_type": "HAS_CONDITION"})
                for e in exception_ids:
                    hub_relations.append({"source": hash_key, "target": e, "relation_type": "HAS_EXCEPTION"})
                for c in consequence_ids:
                    hub_relations.append({"source": hash_key, "target": c, "relation_type": "HAS_CONSEQUENCE"})
                    
                grouped_norms[hash_key] = {
                    "norm_node": global_norm,
                    "source_node_ids": set(),
                    "source_norm_ids": set(),
                    "relations": hub_relations
                }
            
            if source_node_id:
                grouped_norms[hash_key]["source_node_ids"].add(source_node_id)
            grouped_norms[hash_key]["source_norm_ids"].add(norm_id)

        global_norms = []
        global_edges = []
        
        for hash_key, data in grouped_norms.items():
            norm_node = data["norm_node"]
            norm_node["properties"]["source_node_ids"] = list(data["source_node_ids"])
            norm_node["properties"]["source_norm_ids"] = sorted(data["source_norm_ids"])
            global_norms.append(norm_node)
            global_edges.extend(data["relations"])
            
        return global_norms, global_edges, remaining_relations
