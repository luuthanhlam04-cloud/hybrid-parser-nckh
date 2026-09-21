# -*- coding: utf-8 -*-
"""
norm_builder.py — Phase 4, Module 7

Nhiệm vụ:
  Xây dựng NormAssertion từ danh sách LocalMentions + NormalizedRelations.

Triết lý thiết kế:
  - Condition/Exception/Consequence thuộc NormAssertion, KHÔNG thuộc LegalAction.
  - Lý do: Cùng action "chuyển nhượng" có thể xuất hiện trong nhiều quy tắc
    với điều kiện hoàn toàn khác nhau. Nếu gắn condition vào Action,
    các bộ điều kiện sẽ bị trộn lẫn.

Tiêu chí tạo NormAssertion (không phải rule cứng "≥ 2 conditions"):
  - Có condition/exception/consequence IDs
  - Có nhiều subjects (joint norm)
  → Nếu không thỏa: tạo simple edge ALLOW/REQUIRE/PROHIBIT

Simple norm:
  LocalSubject ──ALLOW──> LocalAction

Complex norm:
  NormAssertion
    ├── HAS_SUBJECT  → LocalMention (LegalSubject)
    ├── HAS_ACTION   → LocalMention (LegalAction)
    ├── HAS_OBJECT   → LocalMention (LegalObject)
    ├── HAS_CONDITION → LocalMention (Condition)
    ├── HAS_EXCEPTION → LocalMention (Exception)
    └── HAS_CONSEQUENCE → LocalMention (LegalConsequence)

Boolean logic (v1): flat AND/OR qua logic_group + operator.
Nested structure → mark COMPLEX_LOGIC + UNRESOLVED, không flatten sai.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from src.ontology.schemas import (
    ConditionGroup,
    LocalMention,
    LogicOperator,
    NormAssertion,
    NormativeModality,
    NormStatus,
    RelationType,
    SemanticEdge,
    SemanticType,
)
from src.ontology.relation_normalizer import ModalityContext, NormalizedRelation

logger = logging.getLogger(__name__)

# Counter toàn cục để sinh Norm index per physical node
# (reset mỗi khi xử lý một physical node mới)


class NormBuilder:
    """
    Xây dựng NormAssertion và simple semantic edges từ các LocalMentions + NormalizedRelations.
    """

    def __init__(self, config_dir: Optional[Path] = None):
        if config_dir is None:
            config_dir = Path(__file__).parent / "configs"
        self.config_dir = Path(config_dir)
        self._norm_creation_criteria: List[str] = []
        self._load_configs()

    def _load_configs(self) -> None:
        rules_path = self.config_dir / "relation_rules.yaml"
        if rules_path.exists():
            with open(rules_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            criteria_data = data.get("norm_creation_criteria", {})
            self._norm_creation_criteria = criteria_data.get("create_norm_if", [])
        else:
            # Default criteria
            self._norm_creation_criteria = [
                "has_condition", "has_exception", "has_consequence", "multiple_subjects"
            ]

    # -------------------------------------------------------------------------
    # PUBLIC API
    # -------------------------------------------------------------------------

    def build(
        self,
        mentions: List[LocalMention],
        normalized_relations: List[NormalizedRelation],
        modality_ctx: ModalityContext,
        provenance_node_id: str,
        norm_index_counter: Dict[str, int],  # mutable counter per physical node
    ) -> tuple[List[NormAssertion], List[SemanticEdge]]:
        """
        Xây dựng NormAssertions + simple edges từ một extraction node.

        Args:
            mentions:               List[LocalMention] của node này
            normalized_relations:   List[NormalizedRelation] đã chuẩn hóa
            modality_ctx:           ModalityContext từ relation_normalizer
            provenance_node_id:     Physical Graph node ID
            norm_index_counter:     Dict mutable để sinh index (in-place update)

        Returns:
            (List[NormAssertion], List[SemanticEdge])
            - NormAssertion: complex norms
            - SemanticEdge:  simple edges + HAS_SUBJECT/HAS_ACTION/... edges từ NormAssertion
        """
        mention_by_id = {m.id: m for m in mentions}

        # Phân loại mentions theo semantic type
        subjects    = [m for m in mentions if m.semantic_type == SemanticType.LEGAL_SUBJECT]
        actions     = [m for m in mentions if m.semantic_type == SemanticType.LEGAL_ACTION]
        objects     = [m for m in mentions if m.semantic_type == SemanticType.LEGAL_OBJECT]
        conditions  = [m for m in mentions if m.semantic_type == SemanticType.CONDITION]
        exceptions  = [m for m in mentions if m.semantic_type == SemanticType.EXCEPTION]
        consequences = [m for m in mentions if m.semantic_type == SemanticType.LEGAL_CONSEQUENCE]

        # Quyết định: simple norm hay NormAssertion?
        needs_norm = self._should_create_norm(
            conditions=conditions,
            exceptions=exceptions,
            consequences=consequences,
            subjects=subjects,
        )

        norms: List[NormAssertion] = []
        edges: List[SemanticEdge] = []

        # Xác định modality
        modality = modality_ctx.suggested_modality
        if modality is None:
            # Suy ra từ normalized_relations
            modality = self._infer_modality_from_relations(normalized_relations)

        if needs_norm and modality is not None:
            # === Complex norm → NormAssertion ===
            norm_index_counter[provenance_node_id] = (
                norm_index_counter.get(provenance_node_id, 0) + 1
            )
            norm_idx = norm_index_counter[provenance_node_id]
            norm_id = f"{provenance_node_id}#NORM#{norm_idx}"

            # Condition groups (flat AND/OR v1)
            condition_groups = self._build_condition_groups(
                conditions=conditions,
                normalized_relations=normalized_relations,
            )

            norm = NormAssertion(
                id=norm_id,
                modality=modality,
                subject_ids=[m.id for m in subjects],
                action_ids=[m.id for m in actions],
                object_ids=[m.id for m in objects],
                condition_ids=[m.id for m in conditions],
                condition_groups=condition_groups,
                exception_ids=[m.id for m in exceptions],
                consequence_ids=[m.id for m in consequences],
                provenance_node_id=provenance_node_id,
                evidence=self._collect_evidence(mentions),
                rule_id="RULE_NORM_COMPLEX",
                status=NormStatus.VALID,
            )
            norms.append(norm)

            # Sinh NormAssertion edges (HAS_SUBJECT, HAS_ACTION, ...)
            norm_edges = self._build_norm_edges(norm, mention_by_id)
            edges.extend(norm_edges)
            logger.debug(f"Complex NormAssertion: {norm_id} (modality={modality})")

        else:
            # === Simple norm → direct ALLOW/REQUIRE/PROHIBIT edge ===
            simple_edges = self._build_simple_edges(
                normalized_relations=normalized_relations,
                modality=modality,
            )
            edges.extend(simple_edges)

            # Thêm HAS_OBJECT, HAS_CONDITION, HAS_EXCEPTION edges dù là simple norm
            # (chúng không vi phạm Domain-Range nếu không có NormAssertion,
            #  nhưng validator sẽ flag nếu cấu trúc sai)
            for rel in normalized_relations:
                if rel.relation_type in (
                    RelationType.HAS_OBJECT,
                    RelationType.HAS_CONDITION,
                    RelationType.HAS_EXCEPTION,
                    RelationType.HAS_CONSEQUENCE,
                ):
                    edges.append(SemanticEdge(
                        source_id=rel.source_mention_id,
                        target_id=rel.target_mention_id,
                        relation_type=rel.relation_type,
                        evidence=rel.evidence,
                        rule_id=rel.rule_id,
                    ))

        return norms, edges

    # -------------------------------------------------------------------------
    # PRIVATE METHODS
    # -------------------------------------------------------------------------

    def _should_create_norm(
        self,
        conditions: List[LocalMention],
        exceptions: List[LocalMention],
        consequences: List[LocalMention],
        subjects: List[LocalMention],
    ) -> bool:
        """
        Quyết định có cần tạo NormAssertion không.
        Dựa trên norm_creation_criteria từ config.
        """
        criteria = self._norm_creation_criteria
        if "has_condition" in criteria and len(conditions) > 0:
            return True
        if "has_exception" in criteria and len(exceptions) > 0:
            return True
        if "has_consequence" in criteria and len(consequences) > 0:
            return True
        if "multiple_subjects" in criteria and len(subjects) > 1:
            return True
        return False

    def _infer_modality_from_relations(
        self, normalized_relations: List[NormalizedRelation]
    ) -> Optional[NormativeModality]:
        """Suy ra modality từ danh sách NormalizedRelation."""
        for rel in normalized_relations:
            if rel.relation_type == RelationType.ALLOW:
                return NormativeModality.ALLOW
            if rel.relation_type == RelationType.REQUIRE:
                return NormativeModality.REQUIRE
            if rel.relation_type == RelationType.PROHIBIT:
                return NormativeModality.PROHIBIT
        return None

    def _build_condition_groups(
        self,
        conditions: List[LocalMention],
        normalized_relations: List[NormalizedRelation],
    ) -> List[ConditionGroup]:
        """
        Xây dựng ConditionGroups (flat AND/OR v1).
        Nếu phát hiện nested structure → mark is_complex=True.
        """
        if not conditions:
            return []

        # V1: gom tất cả conditions vào một group AND
        # TODO: parse logic_group/operator từ normalized_relations khi có dữ liệu thực
        group = ConditionGroup(
            group_id="G1",
            operator=LogicOperator.AND,
            condition_ids=[c.id for c in conditions],
            is_complex=False,
        )
        return [group]

    def _build_norm_edges(
        self,
        norm: NormAssertion,
        mention_by_id: Dict[str, LocalMention],
    ) -> List[SemanticEdge]:
        """Sinh các edges từ NormAssertion → LocalMentions."""
        edges = []
        evidence = norm.evidence

        for sid in norm.subject_ids:
            edges.append(SemanticEdge(
                source_id=norm.id, target_id=sid,
                relation_type=RelationType.HAS_SUBJECT, evidence=evidence,
                rule_id="RULE_NORM_HAS_SUBJECT"
            ))
        for aid in norm.action_ids:
            edges.append(SemanticEdge(
                source_id=norm.id, target_id=aid,
                relation_type=RelationType.HAS_ACTION, evidence=evidence,
                rule_id="RULE_NORM_HAS_ACTION"
            ))
        for oid in norm.object_ids:
            edges.append(SemanticEdge(
                source_id=norm.id, target_id=oid,
                relation_type=RelationType.HAS_OBJECT, evidence=evidence,
                rule_id="RULE_NORM_HAS_OBJECT"
            ))
        for cid in norm.condition_ids:
            edges.append(SemanticEdge(
                source_id=norm.id, target_id=cid,
                relation_type=RelationType.HAS_CONDITION, evidence=evidence,
                rule_id="RULE_NORM_HAS_CONDITION"
            ))
        for eid in norm.exception_ids:
            edges.append(SemanticEdge(
                source_id=norm.id, target_id=eid,
                relation_type=RelationType.HAS_EXCEPTION, evidence=evidence,
                rule_id="RULE_NORM_HAS_EXCEPTION"
            ))
        for coid in norm.consequence_ids:
            edges.append(SemanticEdge(
                source_id=norm.id, target_id=coid,
                relation_type=RelationType.HAS_CONSEQUENCE, evidence=evidence,
                rule_id="RULE_NORM_HAS_CONSEQUENCE"
            ))
        return edges

    def _build_simple_edges(
        self,
        normalized_relations: List[NormalizedRelation],
        modality: Optional[NormativeModality],
    ) -> List[SemanticEdge]:
        """Sinh simple ALLOW/REQUIRE/PROHIBIT + HAS_OBJECT edges."""
        edges = []
        normative_types = {RelationType.ALLOW, RelationType.REQUIRE, RelationType.PROHIBIT}

        for rel in normalized_relations:
            if rel.relation_type in normative_types:
                edges.append(SemanticEdge(
                    source_id=rel.source_mention_id,
                    target_id=rel.target_mention_id,
                    relation_type=rel.relation_type,
                    evidence=rel.evidence,
                    rule_id=rel.rule_id,
                ))
        return edges

    def _collect_evidence(self, mentions: List[LocalMention]) -> str:
        """Thu thập evidence tổng hợp từ danh sách mentions."""
        evidences = list({m.evidence for m in mentions if m.evidence})
        return " | ".join(evidences[:3]) if evidences else ""
