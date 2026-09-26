# -*- coding: utf-8 -*-
"""
semantic_quality_gate.py — Gate 1, Phase 3.5, Module 7

Nhiệm vụ:
  Đứng trước NormBuilder, kiểm tra tính toàn vẹn của mentions và normalized_relations.
  Phân loại MentionStatus (VALID, CORRECTED, UNRESOLVED, QUARANTINED) dựa trên heuristic.
  - Ngăn chặn Semantic Amplification (tự chế node).
  - Loại bỏ / Flag các "zombie nodes" không có ý nghĩa pháp lý cụ thể nếu không hợp lệ.
"""

from __future__ import annotations

import logging
from typing import List, Tuple

from src.ontology.schemas import LocalMention, MentionStatus
from src.ontology.relation_normalizer import NormalizedRelation

logger = logging.getLogger(__name__)


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
        # Set default status if not set
        for mention in mentions:
            if mention.status == MentionStatus.VALID:
                # Nếu chưa có audit_note, set mặc định (có thể là VALID từ đầu)
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
                    
        # Lọc các relation không hợp lệ (source/target bị QUARANTINED)
        quarantined_ids = {m.id for m in mentions if m.status == MentionStatus.QUARANTINED}
        
        valid_relations = []
        for rel in normalized_relations:
            if rel.source_mention_id in quarantined_ids or rel.target_mention_id in quarantined_ids:
                logger.warning(
                    f"Gate 1 Drop Relation {rel.relation_type}: "
                    f"source {rel.source_mention_id} or target {rel.target_mention_id} is quarantined."
                )
            else:
                valid_relations.append(rel)

        return mentions, valid_relations
