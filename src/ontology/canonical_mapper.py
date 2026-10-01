# -*- coding: utf-8 -*-
"""
canonical_mapper.py — Phase 3, Module 7

Nhiệm vụ:
  1. Với mỗi LocalMention đã có canonical_concept_id (từ entity_normalizer):
     → Tạo/lấy CanonicalConcept tương ứng
     → Sinh edge DENOTES: LocalMention ──DENOTES──> CanonicalConcept
  2. Load và quản lý Concept Hub (concept_registry.yaml)
  3. Cập nhật source_mention_count cho CanonicalConcept

KIẾN TRÚC BẤT BIẾN:
  - Normative edges (ALLOW/REQUIRE/...) KHÔNG BAO GIỜ đặt trên CanonicalConcept
  - CanonicalConcept được tạo bằng MERGE (chỉ tồn tại DUY NHẤT trong graph)
  - Relation: LocalMention ──DENOTES──> CanonicalConcept (không phải INSTANCE_OF)
  - source_mentions chỉ là aggregation counter, không merge normative context
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from src.ontology.schemas import (
    CanonicalConcept,
    LocalMention,
    RelationType,
    SemanticEdge,
    SemanticType,
)

logger = logging.getLogger(__name__)


class CanonicalMapper:
    """
    Quản lý Canonical Concept Hub và sinh DENOTES edges.
    """

    def __init__(self, config_dir: Optional[Path] = None):
        if config_dir is None:
            config_dir = Path(__file__).parent / "configs"
        self.config_dir = Path(config_dir)

        # Concept Hub: concept_id → CanonicalConcept
        self._concept_hub: Dict[str, CanonicalConcept] = {}
        self._load_concept_registry()

    # -------------------------------------------------------------------------
    # CONFIG LOADING
    # -------------------------------------------------------------------------

    def _load_concept_registry(self) -> None:
        """Load Canonical Concepts từ concept_registry.yaml."""
        registry_path = self.config_dir / "concept_registry.yaml"
        if not registry_path.exists():
            logger.warning(f"Không tìm thấy {registry_path} — Concept Hub rỗng")
            return

        with open(registry_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        for entry in data.get("concepts", []):
            concept_id = entry.get("id")
            if not concept_id:
                continue
            concept = CanonicalConcept(
                id=concept_id,
                concept_type=SemanticType(entry.get("semantic_type", "LegalSubject")),
                preferred_name=entry.get("preferred_name", ""),
                alt_labels=entry.get("alt_labels", []),
                taxonomy_path=entry.get("taxonomy_path"),
                source_mention_count=0,
            )
            self._concept_hub[concept_id] = concept

        logger.info(f"Đã load {len(self._concept_hub)} Canonical Concepts từ {registry_path}")

    # -------------------------------------------------------------------------
    # PUBLIC API
    # -------------------------------------------------------------------------

    def map_mentions(
        self, mentions: List[LocalMention]
    ) -> List[SemanticEdge]:
        """
        Với danh sách LocalMentions đã có canonical_concept_id:
        → Sinh DENOTES edges
        → Cập nhật source_mention_count

        Args:
            mentions: List[LocalMention] đã qua entity_normalizer

        Returns:
            List[SemanticEdge] — các cạnh DENOTES được sinh ra
        """
        edges: List[SemanticEdge] = []

        for mention in mentions:
            concept_id = mention.canonical_concept_id
            if not concept_id:
                continue

            # Tạo/lấy CanonicalConcept (MERGE semantics)
            concept = self._get_or_create_concept(concept_id, mention)
            if concept is None:
                logger.warning(
                    f"Không tìm thấy concept '{concept_id}' trong registry. "
                    f"Skip DENOTES edge cho mention {mention.id}"
                )
                continue

            # Cập nhật count
            concept.source_mention_count += 1

            # Sinh DENOTES edge
            edge = SemanticEdge(
                source_id=mention.id,
                target_id=concept.id,
                relation_type=RelationType.DENOTES,
                evidence=None,
                rule_id="RULE_MAP_DENOTES",
            )
            edges.append(edge)
            logger.debug(f"DENOTES: {mention.id} → {concept.id}")

        return edges

    def get_all_concepts(self) -> List[CanonicalConcept]:
        """Trả về tất cả CanonicalConcepts đã được load và sử dụng."""
        # Chỉ trả về concepts có ít nhất 1 mention
        return [c for c in self._concept_hub.values() if c.source_mention_count > 0]

    def get_concept_by_id(self, concept_id: str) -> Optional[CanonicalConcept]:
        return self._concept_hub.get(concept_id)

    # -------------------------------------------------------------------------
    # PRIVATE METHODS
    # -------------------------------------------------------------------------

    def _get_or_create_concept(
        self,
        concept_id: str,
        source_mention: LocalMention,
    ) -> Optional[CanonicalConcept]:
        """
        MERGE semantics: trả về existing concept hoặc tạo mới nếu không có trong registry.
        """
        if concept_id in self._concept_hub:
            return self._concept_hub[concept_id]

        # Concept không có trong registry → tạo on-the-fly với minimal info
        # (thường không xảy ra nếu concept_registry.yaml đầy đủ)
        logger.warning(
            f"Concept '{concept_id}' không có trong registry — tạo minimal concept"
        )
        concept = CanonicalConcept(
            id=concept_id,
            concept_type=source_mention.semantic_type,
            preferred_name=source_mention.raw_text,
            alt_labels=[],
            taxonomy_path=None,
            source_mention_count=0,
        )
        self._concept_hub[concept_id] = concept
        return concept
