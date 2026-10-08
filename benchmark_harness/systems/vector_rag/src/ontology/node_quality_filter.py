# -*- coding: utf-8 -*-
"""
node_quality_filter.py — Module 7 (v1.2)

Lọc rác đầu vào từ M6 TRƯỚC khi vào normalize pipeline.
Học từ bản M7 của Dương (nguồn: duong-domain branch), điều chỉnh theo
triết lý của Lâm: không xóa dữ liệu, chỉ filter + đếm rejection.

Bắt:
  - invalid node structure (node_id thiếu, extraction không phải dict)
  - entity text rỗng hoặc placeholder (n/a, ..., null, ...)
  - entity_type không hợp lệ
  - evidence rỗng hoặc placeholder
  - relation có endpoint không thuộc entity đã pass

Không bắt:
  - Semantic conflict (đó là việc của SemanticQualityGate + OntologyValidator)
  - Role mismatch (đó là việc của EntityNormalizer)
"""

from __future__ import annotations

import logging
import re
import unicodedata
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------

# Entity types hợp lệ từ M6
_VALID_ENTITY_TYPES = {
    "SUBJECT", "ACTION", "OBJECT", "CONDITION",
    "EXCEPTION", "REFERENCE", "PENALTY",
    "PERMISSION", "OBLIGATION",   # xử lý ở relation_normalizer, nhưng không filter ở đây
}

# Placeholder texts — EXACT match sau normalize
_PLACEHOLDER_TEXTS = {
    "",
    "n/a", "na", "none", "null", "unknown",
    "test", "...", "không có", "khong co",
    "n.a", "không xác định", "ko co",
}


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _norm(text: Any) -> str:
    """Normalize text để so sánh placeholder."""
    if not isinstance(text, str):
        return ""
    normalized = re.sub(r"\s+", " ", text).strip().casefold()
    return unicodedata.normalize("NFC", normalized)


def _is_placeholder(text: Any) -> bool:
    """Exact match — không dùng substring để tránh false positive."""
    return _norm(text) in _PLACEHOLDER_TEXTS


def _has_alnum(text: Any) -> bool:
    """Evidence phải có ít nhất 1 ký tự chữ hoặc số."""
    return any(c.isalnum() for c in str(text)) if text else False


def _is_valid_evidence(text: Any) -> bool:
    return bool(text) and not _is_placeholder(text) and _has_alnum(text)


# ---------------------------------------------------------------------------
# MAIN CLASS
# ---------------------------------------------------------------------------

class NodeQualityFilter:
    """
    Lọc garbage đầu vào từ M6 trước khi vào entity normalize pipeline.

    Thiết kế:
      - Không nâng exception, không làm crash pipeline.
      - Reject = return (None, [], []) và tăng counter.
      - Mọi entity/relation bị filter đều được đếm theo rejection_reason.
      - Không ảnh hưởng đến semantic logic phía sau.
    """

    def __init__(self) -> None:
        self.node_rejection_breakdown: Counter[str] = Counter()
        self.entity_rejection_breakdown: Counter[str] = Counter()
        self.relation_rejection_breakdown: Counter[str] = Counter()
        self.filtered_nodes_count: int = 0
        self.filtered_entities_count: int = 0
        self.filtered_relations_count: int = 0

    def filter_node(
        self,
        node: Any,
    ) -> Tuple[Optional[str], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Lọc một extraction node.

        Returns:
            (node_id, valid_entities, valid_relations)
            Nếu node không hợp lệ → (None, [], [])
        """
        if not isinstance(node, dict):
            self._reject_node("invalid_node_type")
            return None, [], []

        node_id = node.get("node_id")
        if not node_id or not isinstance(node_id, str) or not node_id.strip():
            self._reject_node("missing_node_id")
            return None, [], []

        extraction = node.get("extraction")
        if not isinstance(extraction, dict):
            self._reject_node("invalid_extraction_type")
            return None, [], []

        raw_entities: List[Dict] = extraction.get("entities", []) or []
        raw_relations: List[Dict] = extraction.get("relations", []) or []

        # Filter entities
        valid_entities, entity_ids = self._filter_entities(raw_entities)

        # Filter relations (chỉ giữ nếu endpoint thuộc entity đã pass)
        valid_relations = self._filter_relations(raw_relations, entity_ids)

        # Node bị reject nếu sau khi filter không còn gì
        if not valid_entities and not valid_relations:
            self._reject_node("empty_after_filter")
            return None, [], []

        return node_id.strip(), valid_entities, valid_relations

    def summary(self) -> Dict[str, Any]:
        """Trả về rejection report để log vào pipeline metadata."""
        return {
            "filtered_nodes"    : self.filtered_nodes_count,
            "filtered_entities" : self.filtered_entities_count,
            "filtered_relations": self.filtered_relations_count,
            "node_rejection"    : dict(self.node_rejection_breakdown),
            "entity_rejection"  : dict(self.entity_rejection_breakdown),
            "relation_rejection": dict(self.relation_rejection_breakdown),
        }

    # -------------------------------------------------------------------------
    # PRIVATE
    # -------------------------------------------------------------------------

    def _filter_entities(
        self, raw_entities: Any
    ) -> Tuple[List[Dict[str, Any]], set[str]]:
        if not isinstance(raw_entities, list):
            return [], set()

        valid: List[Dict[str, Any]] = []
        seen_ids: set[str] = set()
        valid_ids: set[str] = set()

        for ent in raw_entities:
            if not isinstance(ent, dict):
                self._reject_entity("invalid_entity_type")
                continue

            eid   = ent.get("id", "")
            text  = ent.get("text", "")
            etype = str(ent.get("entity_type", "")).upper().strip()
            ev    = ent.get("evidence", "")

            # id phải là string không rỗng
            if not isinstance(eid, str) or not eid.strip():
                self._reject_entity("missing_entity_id")
                continue

            # Duplicate id trong cùng node
            if eid in seen_ids:
                self._reject_entity("duplicate_entity_id")
                continue

            # Text rỗng hoặc placeholder
            if _is_placeholder(text):
                self._reject_entity("placeholder_text")
                continue

            # entity_type phải hợp lệ
            if etype not in _VALID_ENTITY_TYPES:
                self._reject_entity("invalid_entity_type_value")
                continue

            # Evidence phải có nội dung thật
            if not _is_valid_evidence(ev):
                self._reject_entity("invalid_evidence")
                continue

            seen_ids.add(eid)
            valid_ids.add(eid)
            valid.append(ent)

        return valid, valid_ids

    def _filter_relations(
        self, raw_relations: Any, entity_ids: set[str]
    ) -> List[Dict[str, Any]]:
        if not isinstance(raw_relations, list):
            return []

        valid: List[Dict[str, Any]] = []
        seen: set[tuple] = set()

        for rel in raw_relations:
            if not isinstance(rel, dict):
                self._reject_relation("invalid_relation_type")
                continue

            src  = rel.get("source", "")
            tgt  = rel.get("target", "")
            rtype = str(rel.get("relation_type", "")).upper().strip()
            ev   = rel.get("evidence", "")

            # Source và target phải có trong entity đã pass
            if not src or src not in entity_ids:
                self._reject_relation("orphan_source")
                continue
            if not tgt or tgt not in entity_ids:
                self._reject_relation("orphan_target")
                continue

            # Relation type phải có
            if not rtype:
                self._reject_relation("missing_relation_type")
                continue

            # Evidence
            if not _is_valid_evidence(ev):
                self._reject_relation("invalid_evidence")
                continue

            # Duplicate trong cùng node (source, type, target, evidence)
            key = (src, rtype, tgt, _norm(ev))
            if key in seen:
                self._reject_relation("duplicate_relation")
                continue
            seen.add(key)

            valid.append(rel)

        return valid

    def _reject_node(self, reason: str) -> None:
        self.node_rejection_breakdown[reason] += 1
        self.filtered_nodes_count += 1

    def _reject_entity(self, reason: str) -> None:
        self.entity_rejection_breakdown[reason] += 1
        self.filtered_entities_count += 1

    def _reject_relation(self, reason: str) -> None:
        self.relation_rejection_breakdown[reason] += 1
        self.filtered_relations_count += 1
