# -*- coding: utf-8 -*-
"""
entity_normalizer.py — Phase 2, Module 7

Nhiệm vụ:
  1. Semantic Role Consistency Check: M6 SUBJECT có thực sự là LegalSubject?
  2. Canonical Semantic Typing: SUBJECT → LegalSubject, PENALTY → LegalConsequence, ...
  3. Taxonomy lookup: tra mapping_rules.yaml → gán subtype + canonical_concept_id

Input : M6 LegalEntity (id, text, entity_type, evidence) + physical_node_id
Output: LocalMention với semantic_type, subtype, status đã được xác định

Trạng thái sau audit:
  VALID      — role hợp lệ, xử lý bình thường
  CORRECTED  — pattern đủ chắc → sửa role tự động, log rule_id
  UNRESOLVED — uncertain → giữ nguyên, cắm cờ để review thủ công

QUAN TRỌNG:
  - PERMISSION và OBLIGATION không được tạo LocalMention thành entity class.
    Chúng được relation_normalizer.py xử lý thành normative modality.
  - entity_normalizer KHÔNG được xóa mention, chỉ flag status.
"""

from __future__ import annotations

import logging
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from src.ontology.schemas import (
    LocalMention,
    MentionStatus,
    MentionType,
    SemanticType,
)

logger = logging.getLogger(__name__)

# =============================================================================
# CONSTANTS
# =============================================================================

# Map M6 entity_type → M7 SemanticType (bước đầu tiên, trước audit)
_M6_TO_SEMANTIC_TYPE: Dict[str, SemanticType] = {
    "SUBJECT":    SemanticType.LEGAL_SUBJECT,
    "ACTION":     SemanticType.LEGAL_ACTION,
    "OBJECT":     SemanticType.LEGAL_OBJECT,
    "CONDITION":  SemanticType.CONDITION,
    "EXCEPTION":  SemanticType.EXCEPTION,
    "REFERENCE":  SemanticType.REFERENCE,
    "PENALTY":    SemanticType.LEGAL_CONSEQUENCE,
    # PERMISSION và OBLIGATION: không tạo entity class
    # → xử lý tại relation_normalizer
    "PERMISSION": None,
    "OBLIGATION": None,
}

# Neo4j Core label mapping
_SEMANTIC_TO_NEO4J: Dict[SemanticType, str] = {
    SemanticType.LEGAL_SUBJECT:     "LegalSubject",
    SemanticType.LEGAL_ACTION:      "LegalAction",
    SemanticType.LEGAL_OBJECT:      "LegalObject",
    SemanticType.LEGAL_CONSEQUENCE: "LegalConsequence",
    SemanticType.CONDITION:         "Condition",
    SemanticType.EXCEPTION:         "Exception",
    SemanticType.REFERENCE:         "Reference",
}

# Taxonomy path → Neo4j labels (từ taxonomy_registry)
_TAXONOMY_TO_NEO4J_LABELS: Dict[str, List[str]] = {
    "LegalSubject.DomesticEntity.Individual": ["LegalSubject", "DomesticEntity", "Individual"],
    "LegalSubject.DomesticEntity.EthnicMinorityIndividual": ["LegalSubject", "DomesticEntity", "EthnicMinority"],
    "LegalSubject.DomesticEntity.Organization": ["LegalSubject", "DomesticEntity", "Organization"],
    "LegalSubject.Authority.ProvincialAuthority": ["LegalSubject", "Authority", "ProvincialAuthority"],
    "LegalSubject.Authority.DistrictAuthority": ["LegalSubject", "Authority", "DistrictAuthority"],
    "LegalSubject.Authority.CentralAuthority": ["LegalSubject", "Authority", "CentralAuthority"],
    "LegalSubject.ForeignRelatedEntity.OverseasVietnamese": ["LegalSubject", "ForeignRelatedEntity", "OverseasVietnamese"],
    "LegalSubject.ForeignRelatedEntity.FDIEnterprise": ["LegalSubject", "ForeignRelatedEntity", "FDIEnterprise"],
    "LegalAction.RealEstateTransaction.TransferAction": ["LegalAction", "Transaction", "TransferAction"],
    "LegalAction.RealEstateTransaction.MortgageAction": ["LegalAction", "Transaction", "MortgageAction"],
    "LegalAction.AdministrativeProcedure.CertificationAction": ["LegalAction", "AdminProcedure", "CertificationAction"],
    "LegalAction.AdministrativeProcedure.CertIssuanceAction": ["LegalAction", "AdminProcedure", "CertIssuanceAction"],
    "LegalAction.AdministrativeProcedure.LandRegistrationAction": ["LegalAction", "AdminProcedure", "LandRegistration"],
    "LegalObject.LandRight.LandUseRight": ["LegalObject", "LandRight", "LandUseRight"],
    "LegalObject.LandDocument.LandCertificate": ["LegalObject", "LandDocument", "LandCertificate"],
    "LegalObject.PhysicalLand.AgriculturalLand": ["LegalObject", "PhysicalLand", "AgriculturalLand"],
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _normalize_text(text: str) -> str:
    """
    Chuẩn hóa text để matching:
    - NFC unicode normalization
    - lowercase
    - loại bỏ dấu chấm, phẩy thừa
    - nhiều space → một space
    """
    text = unicodedata.normalize("NFC", text)
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


# =============================================================================
# ENTITY NORMALIZER CLASS
# =============================================================================

class EntityNormalizer:
    """
    Chuẩn hóa M6 entities thành LocalMention với semantic type và audit status.
    """

    def __init__(self, config_dir: Optional[Path] = None):
        if config_dir is None:
            config_dir = Path(__file__).parent / "configs"
        self.config_dir = Path(config_dir)
        self._mapping_rules: List[Dict[str, Any]] = []
        self._load_configs()

    def _load_configs(self) -> None:
        rules_path = self.config_dir / "mapping_rules.yaml"
        if rules_path.exists():
            with open(rules_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            self._mapping_rules = data.get("mapping_rules", [])
            logger.info(f"Đã load {len(self._mapping_rules)} mapping rules từ {rules_path}")
        else:
            logger.warning(f"Không tìm thấy {rules_path} — chạy với 0 mapping rules")

    # -------------------------------------------------------------------------
    # PUBLIC API
    # -------------------------------------------------------------------------

    def normalize_all(
        self,
        m6_entities: List[Dict[str, Any]],
        provenance_node_id: str,
    ) -> List[LocalMention]:
        """
        Chuẩn hóa toàn bộ mảng entities từ một M6 extraction node.

        Args:
            m6_entities: list từ m6_output["extraction"]["entities"]
            provenance_node_id: Physical Graph node ID (VD: doc_chuong-iii_dieu-27_khoan-3_p180)

        Returns:
            List[LocalMention] — có thể ít hơn m6_entities nếu filter PERMISSION/OBLIGATION
        """
        results: List[LocalMention] = []
        # Track counter per mention_type để sinh index
        type_counter: Dict[str, int] = {}

        for raw in m6_entities:
            mention = self._normalize_one(raw, provenance_node_id, type_counter)
            if mention is not None:
                results.append(mention)

        return results

    # -------------------------------------------------------------------------
    # PRIVATE METHODS
    # -------------------------------------------------------------------------

    def _normalize_one(
        self,
        raw: Dict[str, Any],
        provenance_node_id: str,
        type_counter: Dict[str, int],
    ) -> Optional[LocalMention]:
        """
        Normalize một M6 entity.
        Trả về None nếu entity type là PERMISSION/OBLIGATION (xử lý ở relation_normalizer).
        """
        m6_type = raw.get("entity_type", "").upper()
        raw_text = raw.get("text", "").strip()
        evidence = raw.get("evidence", "").strip()
        m6_local_id = raw.get("id", "")

        # PERMISSION/OBLIGATION → không tạo entity, chuyển sang relation_normalizer
        if m6_type in ("PERMISSION", "OBLIGATION"):
            logger.debug(
                f"Skip {m6_type} entity '{raw_text}' — "
                "sẽ xử lý như normative modality tại relation_normalizer"
            )
            return None

        # Map M6 type → SemanticType
        semantic_type = _M6_TO_SEMANTIC_TYPE.get(m6_type)
        if semantic_type is None:
            logger.warning(f"Unknown M6 entity_type '{m6_type}' — skip")
            return None

        # Sinh MentionType enum
        try:
            mention_type = MentionType(m6_type)
        except ValueError:
            mention_type = MentionType.SUBJECT  # fallback

        # Sinh local index
        type_counter[m6_type] = type_counter.get(m6_type, 0) + 1
        local_index = type_counter[m6_type]

        # Sinh LocalMention ID
        mention_id = f"{provenance_node_id}#{m6_type}#{local_index}"

        # Semantic Role Audit
        audited_type, status, audit_note, subtype, concept_id = self._audit_and_map(
            m6_type=m6_type,
            semantic_type=semantic_type,
            raw_text=raw_text,
        )

        # Neo4j labels
        neo4j_labels = self._build_neo4j_labels(audited_type, subtype)

        return LocalMention(
            id=mention_id,
            mention_type=mention_type,
            raw_text=raw_text,
            m6_local_id=m6_local_id,
            semantic_type=audited_type,
            subtype=subtype,
            canonical_concept_id=concept_id,
            provenance_node_id=provenance_node_id,
            evidence=evidence if evidence else raw_text,  # fallback evidence = raw_text
            status=status,
            audit_note=audit_note,
            neo4j_labels=neo4j_labels,
        )

    def _audit_and_map(
        self,
        m6_type: str,
        semantic_type: SemanticType,
        raw_text: str,
    ) -> Tuple[SemanticType, MentionStatus, Optional[str], Optional[str], Optional[str]]:
        """
        Thực hiện Semantic Role Audit + taxonomy mapping.

        Returns:
            (audited_semantic_type, status, audit_note, subtype, canonical_concept_id)
        """
        normalized = _normalize_text(raw_text)

        # Tìm matching rule
        for rule in self._mapping_rules:
            rule_m6_type = rule.get("m6_type", "").upper()
            if rule_m6_type != m6_type:
                continue

            triggers = [_normalize_text(t) for t in rule.get("triggers", [])]
            neg_triggers = [_normalize_text(t) for t in rule.get("negative_triggers", [])]

            # Check negative triggers trước
            if any(neg in normalized for neg in neg_triggers):
                continue

            # Check triggers
            if any(trigger in normalized for trigger in triggers):
                action = rule.get("action", "CORRECT")
                confidence = rule.get("confidence", "HIGH")
                rule_id = rule.get("id", "UNKNOWN_RULE")
                target_subtype = rule.get("target_subtype")
                target_concept_id = rule.get("target_concept_id")

                if action == "FLAG" or confidence == "LOW":
                    # Semantic role conflict
                    if m6_type == "SUBJECT" and target_subtype and "Object" in target_subtype:
                        note = (
                            f"[{rule_id}] Anti-auto-cast (QUARANTINED): '{raw_text}' "
                            f"được gán {m6_type} nhưng match pattern '{triggers[0]}'. "
                            f"Thực thể mang bản chất {target_subtype} (Object)."
                        )
                        logger.warning(note)
                        return semantic_type, MentionStatus.QUARANTINED, note, target_subtype, target_concept_id
                    
                    note = (
                        f"[{rule_id}] Potential role conflict (UNRESOLVED): '{raw_text}' "
                        f"được gán {m6_type} nhưng match pattern '{triggers[0]}'."
                    )
                    logger.warning(note)
                    return semantic_type, MentionStatus.UNRESOLVED, note, None, None

                else:
                    # CORRECT — sửa tự động
                    if target_subtype:
                        note = (
                            f"[{rule_id}] Auto-corrected: '{raw_text}' → "
                            f"subtype={target_subtype}, concept={target_concept_id}"
                        )
                        logger.debug(note)
                        return (
                            semantic_type,
                            MentionStatus.CORRECTED if target_subtype else MentionStatus.VALID,
                            note,
                            target_subtype,
                            target_concept_id,
                        )
                    else:
                        return semantic_type, MentionStatus.VALID, None, None, None

        # Không match rule nào → VALID với subtype=None
        return semantic_type, MentionStatus.VALID, None, None, None

    def _build_neo4j_labels(
        self,
        semantic_type: SemanticType,
        subtype: Optional[str],
    ) -> List[str]:
        """
        Xây dựng Neo4j labels cho Layer 6 projection.
        Chỉ gán labels có giá trị truy vấn thực tế.
        """
        if subtype:
            # Tìm taxonomy path từ subtype
            for path, labels in _TAXONOMY_TO_NEO4J_LABELS.items():
                if path.endswith(subtype):
                    return labels

        # Fallback: chỉ core label
        core_label = _SEMANTIC_TO_NEO4J.get(semantic_type, str(semantic_type.value))
        return [core_label]
