# -*- coding: utf-8 -*-
"""
relation_normalizer.py — Phase 2, Module 7

Nhiệm vụ:
  1. Chuẩn hóa M6 relation_type sang M7 canonical relation (từ relation_rules.yaml)
  2. Xử lý PERMISSION/OBLIGATION entity → normative modality trong NormAssertion
  3. Xây dựng danh sách normalized relations giữa các LocalMention IDs
  4. Quyết định: simple norm (direct edge) hay complex norm (NormAssertion)?

Input:
  - m6_relations: list từ m6_output["extraction"]["relations"]
  - m6_entities:  list gốc từ M6 (để xử lý PERMISSION/OBLIGATION entity)
  - mention_map:  Dict[m6_local_id → LocalMention] từ entity_normalizer

Output:
  - List[NormalizedRelation]: các relation đã chuẩn hóa, kèm metadata
  - suggested_modality: ALLOW/REQUIRE/PROHIBIT suy ra từ context

PERMISSION/OBLIGATION handling:
  - Nếu M6 có entity OBLIGATION và relation Subject --REQUIRE--> OBLIGATION --ACTION--> X
  - M7 rút gọn thành: Subject --REQUIRE--> X (loại bỏ "zombie node" OBLIGATION)
  - Modality được gán vào NormAssertion.modality
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from src.ontology.schemas import (
    LocalMention,
    NormativeModality,
    RelationType,
)

logger = logging.getLogger(__name__)


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class NormalizedRelation:
    """
    Một relation đã chuẩn hóa giữa hai LocalMentions.
    Dùng bởi norm_builder để xây dựng NormAssertion hoặc simple edge.
    """
    source_mention_id: str       # LocalMention ID
    target_mention_id: str       # LocalMention ID
    relation_type: RelationType
    evidence: str
    rule_id: str = ""
    # Metadata cho Boolean logic
    logic_group: Optional[str] = None
    operator: Optional[str] = None


@dataclass
class ModalityContext:
    """
    Context về normative modality được phát hiện trong một extraction node.
    """
    suggested_modality: Optional[NormativeModality] = None
    # Local IDs từ M6 của PERMISSION/OBLIGATION entities (nếu có)
    permission_obligation_ids: List[str] = field(default_factory=list)


# =============================================================================
# RELATION NORMALIZER CLASS
# =============================================================================

class RelationNormalizer:
    """
    Chuẩn hóa M6 relations sang M7 canonical relations.
    """

    def __init__(self, config_dir: Optional[Path] = None):
        if config_dir is None:
            config_dir = Path(__file__).parent / "configs"
        self.config_dir = Path(config_dir)
        self._modality_map: Dict[str, str] = {}
        self._load_configs()

    def _load_configs(self) -> None:
        rules_path = self.config_dir / "relation_rules.yaml"
        if rules_path.exists():
            with open(rules_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            self._modality_map = data.get("modality_normalization", {})
            logger.info(f"Đã load relation rules từ {rules_path}")
        else:
            logger.warning(f"Không tìm thấy {rules_path}")

    # -------------------------------------------------------------------------
    # PUBLIC API
    # -------------------------------------------------------------------------

    def normalize_all(
        self,
        m6_relations: List[Dict[str, Any]],
        m6_entities_raw: List[Dict[str, Any]],
        mention_map: Dict[str, LocalMention],    # key = m6_local_id (e1, e2, ...)
    ) -> tuple[List[NormalizedRelation], ModalityContext]:
        """
        Chuẩn hóa toàn bộ mảng relations từ một M6 extraction node.

        Args:
            m6_relations:     list từ m6_output["extraction"]["relations"]
            m6_entities_raw:  list gốc từ M6 (để detect PERMISSION/OBLIGATION entities)
            mention_map:      Dict[m6_local_id → LocalMention] đã normalize

        Returns:
            (List[NormalizedRelation], ModalityContext)
        """
        # Phát hiện PERMISSION/OBLIGATION entities từ M6 raw
        perm_oblig_map = self._extract_perm_oblig_entities(m6_entities_raw)

        # Normalize từng relation
        normalized: List[NormalizedRelation] = []
        modality_ctx = ModalityContext()

        for raw_rel in m6_relations:
            result = self._normalize_one(
                raw_rel=raw_rel,
                mention_map=mention_map,
                perm_oblig_map=perm_oblig_map,
                modality_ctx=modality_ctx,
            )
            if result is not None:
                normalized.append(result)

        return normalized, modality_ctx

    # -------------------------------------------------------------------------
    # PRIVATE METHODS
    # -------------------------------------------------------------------------

    def _extract_perm_oblig_entities(
        self, m6_entities_raw: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """
        Lấy dict: m6_local_id → loại (PERMISSION/OBLIGATION)
        cho các entities M6 có type PERMISSION hoặc OBLIGATION.
        """
        result = {}
        for ent in m6_entities_raw:
            t = ent.get("entity_type", "").upper()
            if t in ("PERMISSION", "OBLIGATION"):
                result[ent.get("id", "")] = t
        return result

    def _normalize_one(
        self,
        raw_rel: Dict[str, Any],
        mention_map: Dict[str, LocalMention],
        perm_oblig_map: Dict[str, str],
        modality_ctx: ModalityContext,
    ) -> Optional[NormalizedRelation]:
        """
        Normalize một M6 relation.
        Trả về None nếu relation không thể map (source/target không tồn tại).
        """
        source_m6_id = raw_rel.get("source", "")
        target_m6_id = raw_rel.get("target", "")
        m6_relation   = raw_rel.get("relation_type", "").upper()
        evidence      = raw_rel.get("evidence", "")

        # Map relation type
        canonical_rel_str = self._modality_map.get(m6_relation, m6_relation)

        # REFERENCE_TO / REFERENCES: được xử lý riêng bởi reference_classifier.py
        # (dùng string match trực tiếp trên m6_relations_raw trước khi vào đây)
        # relation_normalizer KHÔNG cần xử lý — explicit skip để tránh ValueError noise.
        if canonical_rel_str in ("REFERENCES", "REFERENCE_TO"):
            logger.debug(f"Skip '{m6_relation}' — handled by reference_classifier.py")
            return None

        try:
            canonical_rel = RelationType(canonical_rel_str)
        except ValueError:
            logger.warning(f"Unknown relation type '{m6_relation}' → skip")
            return None

        # === Xử lý PERMISSION/OBLIGATION entity ===
        # Trường hợp: source = SUBJECT (có LocalMention) → REQUIRE → target = OBLIGATION entity
        # M6 có thể sinh: e1(SUBJECT) --REQUIRE--> e2(OBLIGATION)
        #                  e2(OBLIGATION) --ACTION--> e3(ACTION)
        # M7 rút gọn: bỏ e2, giữ nguyên e1 --REQUIRE--> e3
        # (Logic này được xử lý tại norm_builder khi gom NormAssertion)

        # Nếu target là PERMISSION/OBLIGATION entity → extract modality, skip edge
        if target_m6_id in perm_oblig_map:
            perm_oblig_type = perm_oblig_map[target_m6_id]
            if canonical_rel in (RelationType.ALLOW, RelationType.REQUIRE, RelationType.PROHIBIT):
                # Ghi nhận modality
                modality_ctx.suggested_modality = self._rel_to_modality(canonical_rel)
                modality_ctx.permission_obligation_ids.append(target_m6_id)
                logger.debug(
                    f"Detected modality {canonical_rel} via PERMISSION/OBLIGATION entity {target_m6_id}"
                )
            # Skip cạnh này — không tạo LocalMention cho PERMISSION/OBLIGATION
            return None

        # Nếu source là PERMISSION/OBLIGATION entity → cũng skip
        if source_m6_id in perm_oblig_map:
            modality_ctx.permission_obligation_ids.append(source_m6_id)
            return None

        # Map m6_local_id → LocalMention ID
        source_mention = mention_map.get(source_m6_id)
        target_mention = mention_map.get(target_m6_id)

        if source_mention is None:
            logger.debug(f"Source entity '{source_m6_id}' không có LocalMention (có thể đã skip) → skip relation")
            return None
        if target_mention is None:
            logger.debug(f"Target entity '{target_m6_id}' không có LocalMention → skip relation")
            return None

        # Phát hiện modality từ direct ALLOW/REQUIRE/PROHIBIT edges
        if canonical_rel in (RelationType.ALLOW, RelationType.REQUIRE, RelationType.PROHIBIT):
            modality = self._rel_to_modality(canonical_rel)
            if modality_ctx.suggested_modality is None:
                modality_ctx.suggested_modality = modality

        return NormalizedRelation(
            source_mention_id=source_mention.id,
            target_mention_id=target_mention.id,
            relation_type=canonical_rel,
            evidence=evidence,
            rule_id=f"REL_{m6_relation}",
        )

    def _rel_to_modality(self, rel: RelationType) -> Optional[NormativeModality]:
        _map = {
            RelationType.ALLOW:    NormativeModality.ALLOW,
            RelationType.REQUIRE:  NormativeModality.REQUIRE,
            RelationType.PROHIBIT: NormativeModality.PROHIBIT,
        }
        return _map.get(rel)
