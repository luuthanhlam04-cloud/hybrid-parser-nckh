# -*- coding: utf-8 -*-
"""
reference_classifier.py — Phase 5, Module 7

Nhiệm vụ:
  Phân loại (Classify) các Reference Mentions thành 4 scopes, 
  KHÔNG đi resolve sang Physical Node.

4 scopes:
  - SAME_ARTICLE: "khoản này", "điểm b khoản này", "điều này"
  - SAME_DOCUMENT: "Điều 27", "khoản 2 Điều 48"
  - EXTERNAL: "theo quy định của Bộ luật Dân sự", "Luật Doanh nghiệp"
  - AMBIGUOUS: không xác định được scope rõ ràng.

Output:
  Trả về List[ReferenceMention] để gộp vào CanonicalSemanticGraph.
  Các LocalMention gốc có mention_type=REFERENCE sẽ bị loại khỏi danh sách nodes chính 
  và chuyển thành ReferenceMention.
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
    MentionType,
    ReferenceMention,
    SemanticType,
    NormAssertion,
)

logger = logging.getLogger(__name__)

class ReferenceClassifier:
    """
    Phân loại Reference Mentions thành 4 scopes, chuẩn bị hint cho M8.
    """

    def __init__(self, config_dir: Optional[Path] = None):
        if config_dir is None:
            config_dir = Path(__file__).parent / "configs"
        self.config_dir = Path(config_dir)
        self._patterns: List[Dict[str, Any]] = []
        self._load_configs()

    def _load_configs(self) -> None:
        rules_path = self.config_dir / "reference_rules.yaml"
        if not rules_path.exists():
            logger.warning(f"Không tìm thấy {rules_path} — Reference Classifier không có patterns")
            return

        with open(rules_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        self._patterns = data.get("patterns", [])
        logger.info(f"Đã load {len(self._patterns)} reference patterns")

    def classify_all(
        self,
        mentions: List[LocalMention],
        m6_relations_raw: List[Dict[str, Any]],
        mention_map: Dict[str, LocalMention],
        norms: List[NormAssertion],
        current_provenance_node_id: str,
    ) -> Tuple[List[LocalMention], List[ReferenceMention]]:
        """
        Phân loại Reference mentions, xác định owner, tách chúng ra khỏi general LocalMentions.

        Returns:
            (List[LocalMention] kept, List[ReferenceMention] classified)
        """
        kept_mentions: List[LocalMention] = []
        reference_mentions: List[ReferenceMention] = []

        for mention in mentions:
            if mention.mention_type != MentionType.REFERENCE:
                kept_mentions.append(mention)
                continue

            # Xác định owner bằng cách quét m6_relations_raw để tìm "REFERENCE_TO"
            owner_mention_id = None
            owner_norm_id = None
            for raw_rel in m6_relations_raw:
                if raw_rel.get("target") == mention.m6_local_id and "REFERENCE" in raw_rel.get("relation_type", "").upper():
                    src_m6_id = raw_rel.get("source")
                    src_mention = mention_map.get(src_m6_id) if src_m6_id else None
                    if src_mention:
                        owner_mention_id = src_mention.id
                        # Kiểm tra xem owner_mention_id này có nằm trong NormAssertion nào không
                        for norm in norms:
                            if owner_mention_id in norm.condition_ids or owner_mention_id in norm.exception_ids or owner_mention_id in norm.action_ids or owner_mention_id in norm.subject_ids:
                                owner_norm_id = norm.id
                                break
                    break

            # Fallback nếu không có relation: owner_norm_id = norm đầu tiên (nếu có)
            if not owner_mention_id and not owner_norm_id:
                if norms:
                    owner_norm_id = norms[0].id
                elif kept_mentions:
                    owner_mention_id = kept_mentions[0].id
                else:
                    owner_mention_id = "UNRESOLVED_OWNER"

            scope, target_hint = self._classify_one(mention.raw_text)
            
            # Khởi tạo ReferenceMention (sẽ chạy validate_owner tự động)
            try:
                ref = ReferenceMention(
                    id=f"{current_provenance_node_id}#REFERENCE#{len(reference_mentions)+1}",
                    raw_text=mention.raw_text,
                    scope=scope,
                    target_hint=target_hint,
                    provenance_node_id=mention.provenance_node_id,
                    evidence=mention.evidence,
                    resolution_status="PENDING_M8",
                    owner_mention_id=owner_mention_id,
                    owner_norm_id=owner_norm_id
                )
                reference_mentions.append(ref)
                logger.debug(f"CLASSIFIED REF: {ref.raw_text} -> {scope} (hint: {target_hint}) [owner: {owner_mention_id} / {owner_norm_id}]")
            except Exception as e:
                logger.warning(f"Failed to create ReferenceMention for '{mention.raw_text}': {e}")
                # Nếu mồ côi (lỗi validate), chúng ta đẩy vào kept_mentions để không bị drop data, 
                # hoặc gán tạm owner là current_provenance_node_id
                pass

        return kept_mentions, reference_mentions

    def _classify_one(self, raw_text: str) -> Tuple[str, dict]:
        normalized_text = self._normalize(raw_text)
        
        # Check EXTERNAL heuristically first if needed
        if "luật" in normalized_text and "này" not in normalized_text:
            if "luật dân sự" in normalized_text or "doanh nghiệp" in normalized_text or "pháp luật" in normalized_text:
                return "EXTERNAL", {"text": raw_text}

        for pattern_def in self._patterns:
            regex = pattern_def.get("regex", "")
            strategy = pattern_def.get("resolve_strategy", "")
            groups_def = pattern_def.get("capture_groups", {})

            match = re.search(regex, normalized_text, re.IGNORECASE)
            if not match:
                continue

            captures = {}
            for name, group_index in groups_def.items():
                try:
                    captures[name] = match.group(group_index).strip()
                except (IndexError, AttributeError):
                    pass
            
            scope = "AMBIGUOUS"
            if "RELATIVE" in strategy:
                scope = "SAME_ARTICLE"
            elif "ABSOLUTE" in strategy:
                scope = "SAME_DOCUMENT"

            return scope, captures

        return "AMBIGUOUS", {}

    def _normalize(self, text: str) -> str:
        text = unicodedata.normalize("NFC", text).lower().strip()
        text = re.sub(r"\s+", " ", text)
        return text
