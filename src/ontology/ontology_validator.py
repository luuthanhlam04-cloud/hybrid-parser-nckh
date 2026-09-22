import logging
from collections import defaultdict
from typing import Any, Dict, Set, Tuple

logger = logging.getLogger(__name__)

class OntologyValidator:
    """
    Áp dụng ma trận Domain-Range để kiểm duyệt (Validate) các quan hệ canonical.
    """
    def __init__(self, canonical_mapper):
        self.mapper = canonical_mapper
        self._accepted_edges: Dict[str, Dict[str, Set[str]]] = defaultdict(
            lambda: defaultdict(set)
        )

    def register_accepted_relation(self, canonical_rel: Dict[str, Any]) -> None:
        """Record an accepted edge for subsequent max-depth checks."""
        relation_type = canonical_rel.get("relation_type")
        source = canonical_rel.get("source")
        target = canonical_rel.get("target")
        if relation_type and source and target:
            self._accepted_edges[relation_type][source].add(target)

    def _relation_chain_depth(
        self, relation_type: str, source_id: str, target_id: str
    ) -> int:
        """Return the longest acyclic same-type chain ending at target."""
        adjacency = self._accepted_edges[relation_type]
        memo: Dict[str, int] = {}

        def depth(node_id: str, visiting: Set[str]) -> int:
            if node_id in memo:
                return memo[node_id]
            if node_id in visiting:
                return 0
            visiting = visiting | {node_id}
            predecessors = [
                predecessor
                for predecessor, targets in adjacency.items()
                if node_id in targets
            ]
            if not predecessors:
                result = 0
            else:
                result = 1 + max(
                    (depth(predecessor, visiting) for predecessor in predecessors),
                    default=0,
                )
            memo[node_id] = result
            return result

        # The candidate edge contributes one level to the chain.
        return depth(source_id, set()) + 1 if target_id else 0

    def validate_relation(
        self,
        canonical_rel: Dict[str, Any],
        canonical_entities: Dict[str, Dict[str, Any]],
    ) -> Tuple[bool, str]:
        """
        Kiểm tra tính hợp lệ của relation dựa trên domain/range matrix.
        Trả về (True, "") nếu hợp lệ hoặc (False, lý do) nếu REJECT.
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

        source_class = source_node.get("ontology_class")
        target_class = target_node.get("ontology_class")
        
        if source_class not in constraints.get("domain", []):
            return False, (
                f"DOMAIN_VIOLATION: Source class {source_class} not in "
                f"{constraints.get('domain')} for {rel_type}"
            )
            
        if target_class not in constraints.get("range", []):
            return False, (
                f"RANGE_VIOLATION: Target class {target_class} not in "
                f"{constraints.get('range')} for {rel_type}"
            )
            
        if source_id == target_id and not constraints.get("self_loop", False):
            return False, f"SELF_LOOP: Self-loop not allowed for {rel_type}"

        max_depth = constraints.get("max_depth")
        if max_depth is not None:
            chain_depth = self._relation_chain_depth(
                rel_type, source_id, target_id
            )
            if chain_depth > max_depth:
                return False, (
                    f"MAX_DEPTH: {rel_type} chain depth {chain_depth} "
                    f"exceeds maximum {max_depth}"
                )

        return True, ""
