# -*- coding: utf-8 -*-
"""
semantic_quality_gate.py — Gate 1, Phase 3.5, Module 7

Nhiệm vụ:
  Đứng trước NormBuilder, kiểm tra tính toàn vẹn của mentions và normalized_relations.
  Phân loại MentionStatus (VALID, CORRECTED, UNRESOLVED, QUARANTINED) dựa trên heuristic.
  - Ngăn chặn Semantic Amplification (tự chế node).
  - Loại bỏ / Flag các "zombie nodes" không có ý nghĩa pháp lý cụ thể nếu không hợp lệ.

CONTRACT: Xem docs/m7_m8_adapter_contract.md §3 về Source=None Policy.
  - ALLOW/REQUIRE/PROHIBIT: source=None được phép (Partial Norm, subject_status=UNRESOLVED)
  - Các relation cấu trúc (HAS_OBJECT, HAS_CONDITION...): source=None → Quarantine ngay tại Gate 1
"""

from __future__ import annotations

import logging
from typing import List, Set, Tuple

from src.ontology.schemas import LocalMention, MentionStatus, RelationType
from src.ontology.relation_normalizer import NormalizedRelation

logger = logging.getLogger(__name__)

# --- GATE 1 SOURCE POLICY (CONTRACT m7_m8_adapter_contract.md §3 — Tầng Gate 1) ---
# Gate 1 chạy TRƯỚC NormBuilder, tức là norm_id chưa tồn tại.
# Gate 1 chỉ kiểm tra: source_mention_id có tồn tại không (là LocalMention hợp lệ)?
# ALLOW/REQUIRE/PROHIBIT: được phép source=None → Partial Norm.
# Các relation cấu trúc dưới: source phải là một LocalMention (not None).
# Lưu ý: HAS_SUBJECT, HAS_ACTION, DENOTES được NormBuilder tạo nội bộ,
# KHÔNG xuất hiện trong output M6 → không cần kiểm tra ở Gate 1.
GATE1_MANDATORY_SOURCE: Set[RelationType] = {
    RelationType.HAS_OBJECT,
    RelationType.HAS_CONDITION,
    RelationType.HAS_EXCEPTION,
    RelationType.HAS_CONSEQUENCE,
}


class SemanticQualityGate:
    """
    Gate 1: Pre-build Validation.
    Kiểm tra tổng thể cấu trúc semantic trước khi đưa vào NormBuilder.
    """

    def __init__(self):
        pass

    def evaluate(
        self,
        mentions: List[LocalMention],
        normalized_relations: List[NormalizedRelation],
    ) -> Tuple[List[LocalMention], List[NormalizedRelation]]:
        """
        Đánh giá và cập nhật status cho mentions.
        Những mention bị QUARANTINED sẽ không được NormBuilder xử lý
        (tùy thuộc vào chính sách của pipeline, hiện tại giữ nguyên để Gate 2 filter,
         nhưng gán status rõ ràng).

        Args:
            mentions: Danh sách các LocalMention sau khi đi qua EntityNormalizer.
            normalized_relations: Các relations đã chuẩn hóa.

        Returns:
            Tuple (mentions, normalized_relations) đã được cập nhật status/audit_note.
        """
        for mention in mentions:
            if mention.status == MentionStatus.VALID:
                pass

            # Rule 1: No Semantic Amplification
            if not mention.evidence or mention.evidence.strip() == "":
                mention.status = MentionStatus.QUARANTINED
                mention.audit_note = "Gate 1 [R1]: Missing evidence (Semantic Amplification)"
                logger.warning(f"Gate 1 QUARANTINED: {mention.id} (Missing evidence)")

            # Rule 2: Zombie node detection
            if mention.raw_text.strip().lower() in ("ai", "người nào", "tất cả"):
                if mention.status != MentionStatus.QUARANTINED:
                    mention.status = MentionStatus.UNRESOLVED
                    mention.audit_note = "Gate 1: Vague subject text"
                    logger.info(f"Gate 1 UNRESOLVED: {mention.id} (Vague subject)")

        quarantined_ids = {m.id for m in mentions if m.status == MentionStatus.QUARANTINED}

        valid_relations = []
        for rel in normalized_relations:
            # Check 1 [Bug #1 Fix — v2, tách Gate 1 vs Gate 2]:
            # Gate 1 chỉ hỏi: "source_mention_id có phải LocalMention hợp lệ không?"
            # Gate 2 mới hỏi: "source có phải NormAssertion ID không?"
            # ALLOW/REQUIRE/PROHIBIT được phép source=None (Partial Norm).
            if rel.source_mention_id is None and rel.relation_type in GATE1_MANDATORY_SOURCE:
                logger.warning(
                    f"Gate 1 Drop Relation [{rel.relation_type}]: "
                    f"source=None vi phạm GATE1_MANDATORY_SOURCE policy. "
                    f"target={rel.target_mention_id}"
                )
                continue

            # Check 2: source hoặc target bị quarantine
            if (rel.source_mention_id and rel.source_mention_id in quarantined_ids) or rel.target_mention_id in quarantined_ids:
                logger.warning(
                    f"Gate 1 Drop Relation {rel.relation_type}: "
                    f"source {rel.source_mention_id} or target {rel.target_mention_id} is quarantined."
                )
            else:
                valid_relations.append(rel)

        return mentions, valid_relations
