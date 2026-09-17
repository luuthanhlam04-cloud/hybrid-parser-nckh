import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class OntologyValidator:
    """
    Áp dụng ma trận Domain-Range để kiểm duyệt (Validate) các quan hệ canonical.
    """
    def __init__(self, canonical_mapper):
        self.mapper = canonical_mapper

    def validate_relation(self, canonical_rel: Dict[str, Any], canonical_entities: Dict[str, Dict[str, Any]]) -> bool:
        """
        Kiểm tra tính hợp lệ của relation dựa trên domain/range matrix.
        Trả về True nếu hợp lệ, False nếu REJECT.
        """
        rel_type = canonical_rel.get("relation_type")
        source_id = canonical_rel.get("source")
        target_id = canonical_rel.get("target")
        
        source_node = canonical_entities.get(source_id)
        target_node = canonical_entities.get(target_id)
        
        if not source_node or not target_node:
            logger.warning(f"REJECT: Missing source or target entity for relation {rel_type} ({source_id} -> {target_id})")
            return False
            
        constraints = self.mapper.get_relation_constraints(rel_type)
        if not constraints:
            logger.warning(f"REJECT: Unknown relation_type {rel_type}")
            return False
            
        source_class = source_node.get("ontology_class")
        target_class = target_node.get("ontology_class")
        
        if source_class not in constraints.get("domain", []):
            logger.warning(f"REJECT: Domain violation for {rel_type}. Source class {source_class} not in {constraints.get('domain')}")
            return False
            
        if target_class not in constraints.get("range", []):
            logger.warning(f"REJECT: Range violation for {rel_type}. Target class {target_class} not in {constraints.get('range')}")
            return False
            
        if source_id == target_id and not constraints.get("self_loop", False):
            logger.warning(f"REJECT: Self-loop not allowed for {rel_type}")
            return False
            
        return True
