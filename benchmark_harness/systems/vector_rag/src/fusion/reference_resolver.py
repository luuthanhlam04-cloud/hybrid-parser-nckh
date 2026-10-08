"""Reference Resolution Logic for M8."""

from __future__ import annotations
from typing import Any, Dict, List, Tuple
from .node_mapper import NodeMapper

class ReferenceResolver:
    def __init__(self, mapper: NodeMapper) -> None:
        self.mapper = mapper

    def resolve(self, relation: Dict[str, Any], source_node_id: str, entities_by_id: Dict[str, Any]) -> Tuple[List[str], str]:
        """
        Resolves a REFERENCE_TO relation to physical node IDs.
        Returns:
            reference_ids: List of resolved physical node IDs.
            resolution_status: Status string of the resolution.
        """
        target_entity = entities_by_id.get(relation.get("target"), {})
        reference_text = str(target_entity.get("canonical_text", ""))
        raw_reference_scope = relation.get("reference_scope")
        reference_scope = str(raw_reference_scope or "").strip().upper()
        reference_ids = []
        
        known_internal_scopes = {"SAME_ARTICLE", "SAME_DOCUMENT"}
        should_resolve = (
            not reference_scope
            or reference_scope in known_internal_scopes
        )
        
        if should_resolve:
            reference_ids = self.mapper.resolve_reference_hint(
                relation.get("target_hint"), source_node_id
            )
            if not reference_ids:
                reference_ids = self.mapper.resolve_reference_text(
                    reference_text, source_node_id
                )
        
        if should_resolve and not reference_ids:
            if reference_scope not in {"EXTERNAL", "AMBIGUOUS"}:
                reference_ids = self.mapper.resolve_anaphoric_reference(
                    reference_text, source_node_id
                )
                
        if reference_ids:
            resolution_status = "RESOLVED_IN_M4"
        elif reference_scope == "EXTERNAL":
            resolution_status = "OUT_OF_SCOPE_PER_M7"
        elif reference_scope == "AMBIGUOUS":
            resolution_status = "AMBIGUOUS_PER_M7"
        elif reference_scope and not should_resolve:
            resolution_status = "NOT_ATTEMPTED_PER_M7_SCOPE"
        else:
            resolution_status = "TARGET_NOT_FOUND_IN_M4"
            
        return reference_ids, resolution_status
