# -*- coding: utf-8 -*-
"""
reference_resolver.py — Phase 5, Module 7

Nhiệm vụ:
  Resolve "Reference" LocalMentions sang Physical Graph node IDs.

Hai loại reference:
  1. Relative: "khoản này", "điểm b khoản này", "điều này"
     → Duyệt ngược cây Physical Graph từ current_node lên theo parent_id
  2. Absolute: "Điều 27", "khoản 2 Điều 48", "điểm b khoản 3 Điều 27"
     → Tìm theo index (article_number, clause_number, marker) trong Physical Graph

Physical Graph node structure (từ M4 output):
  node = {
    "id": "doc_chuong-iii_dieu-27_khoan-3_p180",
    "labels": ["Node", "CLAUSE"],        # labels[1] = node type
    "properties": {
        "number": "3",                   # số khoản
        "marker": "b",                   # ký tự điểm (nếu là POINT)
        "parent_id": "...",              # ID của node cha
        "text": "...",
    }
  }

Output:
  - Thành công: sinh SemanticEdge REFERENCES từ LocalMention → Physical Node ID
  - Thất bại: set mention.status = UNRESOLVED + log warning
              KHÔNG được âm thầm xóa reference
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
    RelationType,
    SemanticEdge,
    SemanticType,
)

logger = logging.getLogger(__name__)

# Physical node type constants (labels[1] trong Physical Graph)
NODE_TYPE_ARTICLE  = "ARTICLE"
NODE_TYPE_CLAUSE   = "CLAUSE"
NODE_TYPE_POINT    = "POINT"
NODE_TYPE_SECTION  = "SECTION"
NODE_TYPE_PARAGRAPH = "PARAGRAPH"


class ReferenceResolver:
    """
    Resolve Reference LocalMentions về Physical Graph node IDs.
    """

    def __init__(self, config_dir: Optional[Path] = None):
        if config_dir is None:
            config_dir = Path(__file__).parent / "configs"
        self.config_dir = Path(config_dir)
        self._patterns: List[Dict[str, Any]] = []
        self._load_configs()

    # -------------------------------------------------------------------------
    # CONFIG LOADING
    # -------------------------------------------------------------------------

    def _load_configs(self) -> None:
        rules_path = self.config_dir / "reference_rules.yaml"
        if not rules_path.exists():
            logger.warning(f"Không tìm thấy {rules_path} — Reference Resolver không có patterns")
            return

        with open(rules_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        self._patterns = data.get("patterns", [])
        logger.info(f"Đã load {len(self._patterns)} reference patterns")

    # -------------------------------------------------------------------------
    # PUBLIC API
    # -------------------------------------------------------------------------

    def resolve_all(
        self,
        mentions: List[LocalMention],
        physical_graph: Dict[str, Any],
        current_provenance_node_id: str,
    ) -> Tuple[List[SemanticEdge], List[LocalMention]]:
        """
        Resolve tất cả Reference mentions trong danh sách.

        Args:
            mentions:                   List[LocalMention] của node này
            physical_graph:             Dict chứa toàn bộ Physical Graph
                                        {"nodes": [...], "edges": [...]}
            current_provenance_node_id: Physical node ID hiện tại (để resolve relative refs)

        Returns:
            (List[SemanticEdge] REFERENCES, List[LocalMention] đã update status)
        """
        # Build lookup structures từ Physical Graph
        node_by_id = self._build_node_by_id(physical_graph)
        nodes_by_type_number = self._build_nodes_by_type_number(physical_graph)

        edges: List[SemanticEdge] = []

        for mention in mentions:
            if mention.semantic_type != SemanticType.REFERENCE:
                continue

            target_node_id = self._resolve_one(
                mention=mention,
                raw_text=mention.raw_text,
                current_node_id=current_provenance_node_id,
                node_by_id=node_by_id,
                nodes_by_type_number=nodes_by_type_number,
            )

            if target_node_id:
                edges.append(SemanticEdge(
                    source_id=mention.id,
                    target_id=target_node_id,
                    relation_type=RelationType.REFERENCES,
                    evidence=mention.raw_text,
                    rule_id="RULE_REF_RESOLVED",
                ))
                logger.debug(f"REFERENCES: {mention.id} → {target_node_id}")
            else:
                # Không resolve được → FLAG, không xóa
                mention.status = MentionStatus.UNRESOLVED
                mention.audit_note = (
                    f"[UNRESOLVED_REF] Không thể resolve reference: '{mention.raw_text}' "
                    f"từ node {current_provenance_node_id}"
                )
                logger.warning(mention.audit_note)

        return edges, mentions

    # -------------------------------------------------------------------------
    # RESOLVE LOGIC
    # -------------------------------------------------------------------------

    def _resolve_one(
        self,
        mention: LocalMention,
        raw_text: str,
        current_node_id: str,
        node_by_id: Dict[str, Dict],
        nodes_by_type_number: Dict[str, List[Dict]],
    ) -> Optional[str]:
        """
        Thử tất cả patterns theo thứ tự (specificity: từ cụ thể → tổng quát).
        """
        normalized_text = self._normalize(raw_text)

        for pattern_def in self._patterns:
            regex = pattern_def.get("regex", "")
            resolve_strategy = pattern_def.get("resolve_strategy", "")
            groups_def = pattern_def.get("capture_groups", {})

            match = re.search(regex, normalized_text, re.IGNORECASE)
            if not match:
                continue

            # Extract capture groups
            captures: Dict[str, str] = {}
            for name, group_index in groups_def.items():
                try:
                    captures[name] = match.group(group_index).strip()
                except (IndexError, AttributeError):
                    pass

            # Resolve theo strategy
            result = self._apply_strategy(
                strategy=resolve_strategy,
                captures=captures,
                current_node_id=current_node_id,
                node_by_id=node_by_id,
                nodes_by_type_number=nodes_by_type_number,
            )

            if result:
                return result

        return None

    def _apply_strategy(
        self,
        strategy: str,
        captures: Dict[str, str],
        current_node_id: str,
        node_by_id: Dict[str, Dict],
        nodes_by_type_number: Dict[str, List[Dict]],
    ) -> Optional[str]:
        """Áp dụng resolve strategy cụ thể."""
        current_node = node_by_id.get(current_node_id)
        if current_node is None and "RELATIVE" in strategy:
            logger.warning(f"Current node '{current_node_id}' không tìm thấy trong Physical Graph")
            return None

        if strategy == "RELATIVE_PARENT":
            return self._get_parent_id(current_node, node_by_id)

        elif strategy == "RELATIVE_SIBLING":
            marker = captures.get("marker")
            number = captures.get("number")
            # Lên cấp cha
            parent_id = self._get_parent_id(current_node, node_by_id)
            if not parent_id:
                return None
            parent_node = node_by_id.get(parent_id)
            if not parent_node:
                return None
            # Tìm child với marker hoặc number
            return self._find_child(parent_node, node_by_id, marker=marker, number=number)

        elif strategy == "RELATIVE_TRAVERSE":
            # Lên article level, rồi xuống clause → point
            article_id = self._get_ancestor_of_type(
                current_node, NODE_TYPE_ARTICLE, node_by_id
            )
            if not article_id:
                return None
            article_node = node_by_id.get(article_id)
            if not article_node:
                return None
            clause_num = captures.get("clause_number")
            marker = captures.get("marker")
            clause_id = self._find_child(article_node, node_by_id, number=clause_num)
            if not clause_id:
                return None
            clause_node = node_by_id.get(clause_id)
            if not clause_node:
                return None
            return self._find_child(clause_node, node_by_id, marker=marker)

        elif strategy == "ABSOLUTE_ARTICLE":
            article_number = captures.get("article_number")
            return self._find_absolute(
                nodes_by_type_number, NODE_TYPE_ARTICLE, number=article_number
            )

        elif strategy == "ABSOLUTE_CLAUSE":
            article_number = captures.get("article_number")
            clause_number  = captures.get("clause_number")
            article_id = self._find_absolute(
                nodes_by_type_number, NODE_TYPE_ARTICLE, number=article_number
            )
            if not article_id:
                return None
            article_node = node_by_id.get(article_id)
            if not article_node:
                return None
            return self._find_child(article_node, node_by_id, number=clause_number)

        elif strategy == "ABSOLUTE_POINT":
            article_number = captures.get("article_number")
            clause_number  = captures.get("clause_number")
            marker         = captures.get("marker")
            article_id = self._find_absolute(
                nodes_by_type_number, NODE_TYPE_ARTICLE, number=article_number
            )
            if not article_id:
                return None
            article_node = node_by_id.get(article_id)
            clause_id = self._find_child(article_node, node_by_id, number=clause_number)
            if not clause_id:
                return None
            clause_node = node_by_id.get(clause_id)
            return self._find_child(clause_node, node_by_id, marker=marker)

        return None

    # -------------------------------------------------------------------------
    # PHYSICAL GRAPH TRAVERSAL HELPERS
    # -------------------------------------------------------------------------

    def _build_node_by_id(self, physical_graph: Dict[str, Any]) -> Dict[str, Dict]:
        """Build lookup dict: node_id → node."""
        result = {}
        for node in physical_graph.get("nodes", []):
            nid = node.get("id") or node.get("properties", {}).get("id")
            if nid:
                result[nid] = node
        return result

    def _build_nodes_by_type_number(
        self, physical_graph: Dict[str, Any]
    ) -> Dict[str, List[Dict]]:
        """Build lookup: "ARTICLE_27" → [node1, node2, ...]."""
        result: Dict[str, List[Dict]] = {}
        for node in physical_graph.get("nodes", []):
            labels = node.get("labels", [])
            node_type = labels[1] if len(labels) > 1 else ""
            props = node.get("properties", {})
            number = str(props.get("number", ""))
            if node_type and number:
                key = f"{node_type}_{number}"
                result.setdefault(key, []).append(node)
        return result

    def _get_node_type(self, node: Dict) -> str:
        labels = node.get("labels", [])
        return labels[1] if len(labels) > 1 else ""

    def _get_parent_id(
        self, node: Optional[Dict], node_by_id: Dict[str, Dict]
    ) -> Optional[str]:
        if node is None:
            return None
        props = node.get("properties", {})
        return props.get("parent_id")

    def _get_ancestor_of_type(
        self,
        node: Optional[Dict],
        target_type: str,
        node_by_id: Dict[str, Dict],
        max_depth: int = 5,
    ) -> Optional[str]:
        """Traverse lên cây Physical Graph tìm ancestor có type = target_type."""
        current = node
        for _ in range(max_depth):
            if current is None:
                break
            if self._get_node_type(current) == target_type:
                props = current.get("properties", {})
                return current.get("id") or props.get("id")
            parent_id = self._get_parent_id(current, node_by_id)
            if not parent_id:
                break
            current = node_by_id.get(parent_id)
        return None

    def _find_child(
        self,
        parent_node: Optional[Dict],
        node_by_id: Dict[str, Dict],
        marker: Optional[str] = None,
        number: Optional[str] = None,
    ) -> Optional[str]:
        """Tìm child node của parent với marker hoặc number cụ thể."""
        if parent_node is None:
            return None

        parent_id = (
            parent_node.get("id")
            or parent_node.get("properties", {}).get("id")
        )

        for node in node_by_id.values():
            props = node.get("properties", {})
            node_parent_id = props.get("parent_id")
            if node_parent_id != parent_id:
                continue

            if marker and str(props.get("marker", "")).lower() == marker.lower():
                return node.get("id") or props.get("id")
            if number and str(props.get("number", "")) == str(number):
                return node.get("id") or props.get("id")

        return None

    def _find_absolute(
        self,
        nodes_by_type_number: Dict[str, List[Dict]],
        node_type: str,
        number: Optional[str],
    ) -> Optional[str]:
        """Tìm node theo type + number tuyệt đối."""
        if not number:
            return None
        key = f"{node_type}_{number}"
        candidates = nodes_by_type_number.get(key, [])
        if not candidates:
            return None
        # Nếu có nhiều candidates (nhiều chương có cùng số điều) → lấy đầu tiên
        node = candidates[0]
        props = node.get("properties", {})
        return node.get("id") or props.get("id")

    def _normalize(self, text: str) -> str:
        text = unicodedata.normalize("NFC", text).lower().strip()
        text = re.sub(r"\s+", " ", text)
        return text
