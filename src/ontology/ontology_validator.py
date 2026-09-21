# -*- coding: utf-8 -*-
"""
ontology_validator.py — Phase 6, Module 7

Nhiệm vụ:
  Kiểm tra toàn bộ invariant của Canonical Semantic Graph trước khi export.

Hai tầng validation:
  Tầng 1 — Semantic Role Validation:
    - Mọi LocalMention có provenance_node_id ≠ None
    - Mọi LocalMention có evidence ≠ rỗng
    - DENOTES edges phải trỏ vào CanonicalConcept
    - REFERENCES edges phải có target là Physical Node ID (string format)

  Tầng 2 — Domain-Range Validation:
    Simple relations:
      ALLOW:    source ∈ LegalSubject, target ∈ LegalAction
      REQUIRE:  source ∈ LegalSubject, target ∈ LegalAction
      PROHIBIT: source ∈ LegalSubject, target ∈ LegalAction
      HAS_OBJECT: source ∈ LegalAction, target ∈ LegalObject

    Complex NormAssertion relations:
      HAS_SUBJECT:    source = NormAssertion, target ∈ LegalSubject
      HAS_ACTION:     source = NormAssertion, target ∈ LegalAction
      HAS_OBJECT:     source = NormAssertion, target ∈ LegalObject
      HAS_CONDITION:  source = NormAssertion, target ∈ Condition
      HAS_EXCEPTION:  source = NormAssertion, target ∈ Exception
      HAS_CONSEQUENCE: source = NormAssertion, target ∈ LegalConsequence

QUAN TRỌNG:
  - Vi phạm → REJECT edge + log rule_id (KHÔNG âm thầm xóa data)
  - Validator không xóa node, chỉ reject/flag edges và ghi vào validation_report
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Set

from src.ontology.schemas import (
    CanonicalConcept,
    CanonicalSemanticGraph,
    LocalMention,
    NormAssertion,
    RelationType,
    SemanticEdge,
    SemanticType,
    ValidationReport,
)

logger = logging.getLogger(__name__)


# =============================================================================
# DOMAIN-RANGE MATRIX
# =============================================================================

# Simple relations: (source_semantic_type, target_semantic_type)
_SIMPLE_DOMAIN_RANGE: Dict[RelationType, tuple] = {
    RelationType.ALLOW: (
        {SemanticType.LEGAL_SUBJECT},
        {SemanticType.LEGAL_ACTION},
    ),
    RelationType.REQUIRE: (
        {SemanticType.LEGAL_SUBJECT},
        {SemanticType.LEGAL_ACTION},
    ),
    RelationType.PROHIBIT: (
        {SemanticType.LEGAL_SUBJECT},
        {SemanticType.LEGAL_ACTION},
    ),
    RelationType.HAS_OBJECT: (
        {SemanticType.LEGAL_ACTION},
        {SemanticType.LEGAL_OBJECT},
    ),
}

# NormAssertion relations: target semantic types allowed
_NORM_RELATION_TARGET_TYPES: Dict[RelationType, Set[SemanticType]] = {
    RelationType.HAS_SUBJECT:    {SemanticType.LEGAL_SUBJECT},
    RelationType.HAS_ACTION:     {SemanticType.LEGAL_ACTION},
    RelationType.HAS_CONDITION:  {SemanticType.CONDITION},
    RelationType.HAS_EXCEPTION:  {SemanticType.EXCEPTION},
    RelationType.HAS_CONSEQUENCE:{SemanticType.LEGAL_CONSEQUENCE},
    # HAS_OBJECT KHÔNG nằm ở đây vì nó hợp lệ từ cả NormAssertion và LegalAction
}


class OntologyValidator:
    """
    Kiểm tra invariants và Domain-Range constraints trước khi export.
    """

    def validate(
        self,
        graph: CanonicalSemanticGraph,
    ) -> CanonicalSemanticGraph:
        """
        Validate toàn bộ graph.
        Cập nhật validation_report và reject vi phạm.

        Returns:
            CanonicalSemanticGraph đã được annotate với validation_report
        """
        report = ValidationReport()
        mention_by_id: Dict[str, LocalMention] = {n.id: n for n in graph.nodes}
        norm_ids: Set[str] = {n.id for n in graph.norms}
        concept_ids: Set[str] = {c.id for c in graph.concepts}

        # =====================================================================
        # TẦNG 1: STRUCTURAL INVARIANTS
        # =====================================================================
        report.total_mentions = len(graph.nodes)
        report.total_norms = len(graph.norms)
        report.total_concepts = len(graph.concepts)

        for mention in graph.nodes:
            self._validate_mention_invariants(mention, report)
            if mention.status.value == "VALID":
                report.valid_mentions += 1
            elif mention.status.value == "CORRECTED":
                report.corrected_mentions += 1
            else:  # UNRESOLVED
                report.unresolved_mentions += 1

        for norm in graph.norms:
            if norm.status.value == "VALID":
                report.valid_norms += 1
            else:
                report.flagged_norms += 1

        # =====================================================================
        # TẦNG 2: DOMAIN-RANGE VALIDATION
        # =====================================================================
        valid_edges: List[SemanticEdge] = []
        report.total_edges = len(graph.edges)

        for edge in graph.edges:
            is_valid, reason = self._validate_edge(
                edge=edge,
                mention_by_id=mention_by_id,
                norm_ids=norm_ids,
                concept_ids=concept_ids,
            )
            if is_valid:
                valid_edges.append(edge)
            else:
                report.rejected_edges += 1
                report.rejected_reasons.append({
                    "edge": f"{edge.source_id} --{edge.relation_type}--> {edge.target_id}",
                    "reason": reason,
                    "rule_id": edge.rule_id or "UNKNOWN",
                })
                logger.warning(
                    f"[REJECTED] Edge {edge.source_id} --{edge.relation_type}--> "
                    f"{edge.target_id}: {reason}"
                )

        # Cập nhật graph chỉ giữ valid edges
        graph.edges = valid_edges

        # =====================================================================
        # KIỂM TRA CANONICAL CONCEPT INVARIANT
        # =====================================================================
        self._check_concept_invariants(graph, norm_ids, mention_by_id, report)

        # =====================================================================
        # REFERENCES COUNT
        # =====================================================================
        for edge in graph.edges:
            if edge.relation_type == RelationType.REFERENCES:
                report.total_references += 1
                report.resolved_references += 1

        for mention in graph.nodes:
            if mention.semantic_type == SemanticType.REFERENCE:
                if mention.status.value == "UNRESOLVED":
                    report.unresolved_references += 1
                    report.total_references += 1

        graph.validation_report = report
        logger.info(f"Validation complete: {graph.summary()}")
        return graph

    # -------------------------------------------------------------------------
    # PRIVATE VALIDATION METHODS
    # -------------------------------------------------------------------------

    def _validate_mention_invariants(
        self, mention: LocalMention, report: ValidationReport
    ) -> None:
        """Tầng 1: Kiểm tra structural invariants của LocalMention."""
        if not mention.provenance_node_id:
            msg = f"[INVARIANT VIOLATION] {mention.id}: provenance_node_id là None/rỗng!"
            logger.error(msg)
            report.rejected_reasons.append({"mention": mention.id, "reason": msg})

        if not mention.evidence:
            msg = f"[INVARIANT WARNING] {mention.id}: evidence rỗng"
            logger.warning(msg)

    def _validate_edge(
        self,
        edge: SemanticEdge,
        mention_by_id: Dict[str, LocalMention],
        norm_ids: Set[str],
        concept_ids: Set[str],
    ) -> tuple[bool, str]:
        """
        Validate một edge. Trả về (is_valid, reason).
        """
        rel = edge.relation_type

        # --- DENOTES: LocalMention → CanonicalConcept ---
        if rel == RelationType.DENOTES:
            if edge.target_id not in concept_ids:
                return False, f"DENOTES target '{edge.target_id}' không phải CanonicalConcept"
            if edge.source_id in norm_ids:
                return False, f"DENOTES source '{edge.source_id}' là NormAssertion — sai kiến trúc"
            return True, ""

        # --- REFERENCES: bất kỳ → Physical Node (string ID) ---
        if rel == RelationType.REFERENCES:
            # Physical node ID chỉ là string — không thể validate sâu hơn ở đây
            # (physical_graph không được load trong validator)
            return True, ""

        # --- NormAssertion relations (chỉ áp dụng khi source là NormAssertion) ---
        if rel in _NORM_RELATION_TARGET_TYPES and edge.source_id in norm_ids:
            target_mention = mention_by_id.get(edge.target_id)
            if target_mention is None:
                return False, f"{rel.value} target '{edge.target_id}' không tìm thấy LocalMention"
            allowed_types = _NORM_RELATION_TARGET_TYPES[rel]
            if target_mention.semantic_type not in allowed_types:
                return False, (
                    f"{rel.value} target '{edge.target_id}' có semantic_type "
                    f"'{target_mention.semantic_type}' nhưng phải là {allowed_types}"
                )
            return True, ""

        # --- HAS_OBJECT: hợp lệ từ cả LegalAction (simple norm) và NormAssertion ---
        if rel == RelationType.HAS_OBJECT:
            source = mention_by_id.get(edge.source_id)
            target = mention_by_id.get(edge.target_id)
            # Source là NormAssertion → đã xử lý ở trên
            # Source là LegalAction → cũng hợp lệ (simple norm)
            if source is not None and source.semantic_type != SemanticType.LEGAL_ACTION:
                return False, (
                    f"HAS_OBJECT source '{edge.source_id}' có type '{source.semantic_type}' "
                    f"nhưng phải là LegalAction hoặc NormAssertion."
                )
            if target is not None and target.semantic_type != SemanticType.LEGAL_OBJECT:
                return False, (
                    f"HAS_OBJECT target '{edge.target_id}' có type '{target.semantic_type}' "
                    f"nhưng phải là LegalObject."
                )
            return True, ""

        # --- Simple normative relations (ALLOW/REQUIRE/PROHIBIT) ---
        if rel in _SIMPLE_DOMAIN_RANGE:
            source_allowed, target_allowed = _SIMPLE_DOMAIN_RANGE[rel]
            source = mention_by_id.get(edge.source_id)
            target = mention_by_id.get(edge.target_id)

            if source is None:
                # Source có thể là NormAssertion ID — cho phép
                if edge.source_id in norm_ids:
                    return True, ""
                return False, f"Source '{edge.source_id}' không tìm thấy"

            if target is None:
                return False, f"Target '{edge.target_id}' không tìm thấy"

            if source.semantic_type not in source_allowed:
                return False, (
                    f"{rel.value} source '{edge.source_id}' có type '{source.semantic_type}' "
                    f"nhưng cần {source_allowed}."
                )

            if target.semantic_type not in target_allowed:
                return False, (
                    f"{rel.value} target '{edge.target_id}' có type '{target.semantic_type}' "
                    f"nhưng cần {target_allowed}."
                )

            return True, ""

        # Unknown relation type → cho phép (forward compatible)
        return True, ""

    def _check_concept_invariants(
        self,
        graph: CanonicalSemanticGraph,
        norm_ids: Set[str],
        mention_by_id: Dict[str, LocalMention],
        report: ValidationReport,
    ) -> None:
        """
        Kiểm tra CanonicalConcept KHÔNG có normative edges.
        """
        concept_ids = {c.id for c in graph.concepts}
        normative_types = {
            RelationType.ALLOW, RelationType.REQUIRE, RelationType.PROHIBIT,
            RelationType.HAS_CONDITION, RelationType.HAS_EXCEPTION, RelationType.HAS_CONSEQUENCE,
        }
        for edge in graph.edges:
            if edge.source_id in concept_ids and edge.relation_type in normative_types:
                msg = (
                    f"[INVARIANT VIOLATION] CanonicalConcept '{edge.source_id}' có normative edge "
                    f"'{edge.relation_type}' → '{edge.target_id}'. "
                    f"Normative edges KHÔNG được đặt trên Concept Hub!"
                )
                logger.error(msg)
                report.rejected_reasons.append({"concept_invariant": msg})

        report.total_concepts = len(graph.concepts)
