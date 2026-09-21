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
        current_provenance_node_id: str,
    ) -> Tuple[List[LocalMention], List[ReferenceMention]]:
        """
        Phân loại Reference mentions, tách chúng ra khỏi general LocalMentions.

        Returns:
            (List[LocalMention] kept, List[ReferenceMention] classified)
        """
        kept_mentions: List[LocalMention] = []
        reference_mentions: List[ReferenceMention] = []

        for mention in mentions:
            if mention.mention_type != MentionType.REFERENCE:
                kept_mentions.append(mention)
                continue

            scope, target_hint = self._classify_one(mention.raw_text)
            
            ref = ReferenceMention(
                id=f"{current_provenance_node_id}#REFERENCE#{len(reference_mentions)+1}",
                raw_text=mention.raw_text,
                scope=scope,
                target_hint=target_hint,
                provenance_node_id=mention.provenance_node_id,
                evidence=mention.evidence,
                resolution_status="PENDING_M8"
            )
            reference_mentions.append(ref)
            logger.debug(f"CLASSIFIED REF: {ref.raw_text} -> {scope} (hint: {target_hint})")

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
