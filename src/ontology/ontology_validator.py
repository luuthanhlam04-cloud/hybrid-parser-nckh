import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

class OntologyValidator:
    """
    Áp dụng ma trận Domain-Range để kiểm duyệt (Validate) các quan hệ canonical.
    """
    def __init__(self, canonical_mapper):
        self.mapper = canonical_mapper
        self.notified_max_depth = False

    def validate_relation(self, canonical_rel: Dict[str, Any], canonical_entities: Dict[str, Dict[str, Any]]) -> Tuple[bool, str]:
        """
        Kiểm tra tính hợp lệ của relation dựa trên domain/range matrix.
        Trả về (True, "") nếu hợp lệ, (False, "Lý do") nếu REJECT.
        """
        rel_type = canonical_rel.get("relation_type")
        source_id = canonical_rel.get("source")
        target_id = canonical_rel.get("target")
        
        source_node = canonical_entities.get(source_id)
        target_node = canonical_entities.get(target_id)
        
        if not source_node or not target_node:
            return False, f"MISSING_ENTITY: source or target missing for {rel_type}"
            
        constraints = self.mapper.get_relation_constraints(rel_type)
        if not constraints:
            return False, f"UNKNOWN_M6_RELATION: {rel_type}"
            
        if "max_depth" in constraints and not self.notified_max_depth:
            logger.warning("MAX_DEPTH_CHECK_NOT_IMPLEMENTED")
            self.notified_max_depth = True
            
        source_class = source_node.get("ontology_class")
        target_class = target_node.get("ontology_class")
        
        if source_class not in constraints.get("domain", []):
            return False, f"DOMAIN_VIOLATION: Source class {source_class} not in {constraints.get('domain')} for {rel_type}"
            
        if target_class not in constraints.get("range", []):
            return False, f"RANGE_VIOLATION: Target class {target_class} not in {constraints.get('range')} for {rel_type}"
            
        if source_id == target_id and not constraints.get("self_loop", False):
            return False, f"SELF_LOOP: Self-loop not allowed for {rel_type}"
            
        return True, ""