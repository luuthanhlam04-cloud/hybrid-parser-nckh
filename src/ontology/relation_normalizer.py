from typing import Dict, Any, List

class RelationNormalizer:
    """
    Thực thi việc tiêm ngữ cảnh vào cạnh (Edge-Level Provenance).
    """
    def __init__(self):
        self.rule_counter = 1

    def normalize(self, raw_relation: Dict[str, Any], local_to_canonical: Dict[str, str], source_node_id: str) -> Dict[str, Any]:
        """
        Chuyển đổi relation thô thành canonical relation.
        - Thay thế source/target ID.
        - Tiêm ngữ cảnh (source_node_id, evidence).
        - Gán rule_id và assertion_status.
        """
        source_local = raw_relation.get("source")
        target_local = raw_relation.get("target")
        
        source_canonical = local_to_canonical.get(source_local)
        target_canonical = local_to_canonical.get(target_local)
        
        if not source_canonical or not target_canonical:
            # Bỏ qua nếu ánh xạ ID thất bại (mặc dù hiếm khi xảy ra nếu quarantine hoạt động)
            return None
            
        rule_id = f"RULE_M7_REL_{self.rule_counter:04d}"
        self.rule_counter += 1
        
        canonical_rel = {
            "relation_id": rule_id.replace("RULE_M7", "REL"),
            "relation_type": raw_relation.get("relation_type"),
            "source_node_id": source_node_id,
            "source": source_canonical,
            "target": target_canonical,
            "evidence": raw_relation.get("evidence", ""),
            "rule_id": rule_id,
            "assertion_status": "ASSERTED"
        }
        
        # Preserve logic fields if they exist
        if "logic_group" in raw_relation:
            canonical_rel["logic_group"] = raw_relation["logic_group"]
        if "operator" in raw_relation:
            canonical_rel["operator"] = raw_relation["operator"]
            
        return canonical_rel
