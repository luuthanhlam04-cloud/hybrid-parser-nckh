# -*- coding: utf-8 -*-
"""
node_generator.py — Module 2: Regex Parser
Sinh Legal Node JSON từ HierarchyNode.

Schema Legal Node v1.2 (draft — chưa chốt chính thức):
{
  "id":              string  — hierarchical ID với law prefix
  "type":            string  — CHAPTER | SECTION | ARTICLE | CLAUSE | POINT
  "depth":           int     — 0..4
  "title":           string? — tiêu đề nếu có (Điều 26. -> "Quyền chung...")
  "text":            string  — nội dung trực tiếp của node (KHÔNG bao gồm children)
  "parent_id":       string? — ID của node cha, null nếu là gốc
  "children_count":  int     — số lượng children trực tiếp
  "position":        int     — thứ tự trong cùng parent (1-indexed)
  "number":          int|str? — số thứ tự pháp lý của CHAPTER/SECTION/ARTICLE/CLAUSE.
                               int nếu decimal (Khoản 3 → 3), str nếu khác (Đượng III).
                               null nếu M1 không phục hồi được (TXT mode).
                               KHÔNG dùng cho POINT — xem field 'marker'.
  "marker":          str?    — ký tự nhận diện của POINT (a, b, c, đ, e...) hoặc null.
                               null với mọi node type khác POINT.
  "law_prefix":      string  — prefix văn bản
  "law_code":        string? — mã văn bản pháp luật
  "source_doc":      string  — tên file nguồn
  "word_style":      string? — Word Style DOCX nếu có (để debug / trace)
  "start_idx":       int     — vị trí bắt đầu trong input list (paragraph index)
  "end_idx":         int     — vị trí kết thúc trong input list (exclusive)
  "implicit_parent": bool    — True nếu POINT thiếu CLAUSE cha (orphan)
}

Những gì CHƯA CHỐT (xem research_notes.md):
  - text = direct content hay full content gồm children?
    → Hiện tại: text = body content của node (không gồm children).
  - char_start / char_end dựa trên raw text hay clean text?
    → Hiện tại: dùng start_idx / end_idx (paragraph index), không character offset.
"""

import json
import re
from typing import Optional
from hierarchy_builder import HierarchyNode
from regex_engine import NodeType


# ---------------------------------------------------------------------------
# NodeGenerator
# ---------------------------------------------------------------------------
class NodeGenerator:
    """
    Sinh Legal Node JSON từ danh sách HierarchyNode.

    ID strategy (draft, chưa chốt):
      Format: {law_prefix}_{chuong-III}_{muc-1}_{dieu-26}_{khoan-1}_{diem-a}
      Khi CLAUSE không có số (List Paragraph fallback): dùng position làm số.
    """

    # Prefix viết tắt cho mỗi NodeType trong ID
    TYPE_SHORT = {
        NodeType.CHAPTER: "chuong",
        NodeType.SECTION: "muc",
        NodeType.ARTICLE: "dieu",
        NodeType.CLAUSE:  "khoan",
        NodeType.POINT:   "diem",
    }

    def __init__(self, law_prefix: str = "doc", law_code: Optional[str] = None, source_doc: str = ""):
        """
        Args:
            law_prefix: Prefix cho document (vd: 'ldd-2024', 'ldoanhnghiep-2020').
            law_code:   Mã văn bản pháp luật (vd: '59/2024/QH15').
            source_doc: Tên file nguồn.
        """
        self.law_prefix = law_prefix
        self.law_code = law_code
        self.source_doc = source_doc
        # Maps được build trong generate(), reset mỗi lần gọi
        self._obj_id_map: dict[int, str] = {}          # id(node) -> final_id
        self._obj_map: dict[int, HierarchyNode] = {}   # id(node) -> node object

    def generate(self, nodes: list[HierarchyNode]) -> list[dict]:
        """
        Sinh danh sách Legal Node JSON.

        Args:
            nodes: Danh sách HierarchyNode đã build hierarchy.

        Returns:
            List of dict — Legal Node JSON objects.
        """
        # Reset state mỗi lần generate
        self._obj_id_map = {}
        self._obj_map = {}

        # Build object registry: id(node) -> node object
        for node in nodes:
            self._obj_map[id(node)] = node

        # Pass 1: build ID cho tất cả node theo thứ tự xuất hiện (preorder)
        # Đảm bảo parent luôn được xử lý trước child.
        self._build_id_map(nodes)

        # Pass 2: sinh node JSON đầy đủ
        return [self._build_node(node) for node in nodes]

    def to_json(self, nodes: list[HierarchyNode], indent: int = 2) -> str:
        """Xuất danh sách Legal Node thành JSON string."""
        return json.dumps(self.generate(nodes), ensure_ascii=False, indent=indent)

    # -----------------------------------------------------------------------
    # Internal: build ID map
    # -----------------------------------------------------------------------
    def _build_id_map(self, nodes: list[HierarchyNode]) -> None:
        """
        Build mapping: id(node) → final hierarchical ID string.

        Sử dụng object identity (id(node)) và node.parent_node (object reference
        được gán bởi HierarchyBuilder) — tránh hoàn toàn string temp_id lookup.

        Tại sao không dùng temp_id string:
          - Nhiều CLAUSE khác nhau (thuộc nhiều Điều khác nhau) có cùng
            temp_id ví dụ "khoan_pos5" → collision → parent_id sai.
          - Giải pháp: HierarchyBuilder giờ lưu node.parent_node là object reference.
            NodeGenerator dùng id(node.parent_node) để tra cứu — unambiguous.

        Thuật toán:
          1. Nodes đã được sắp xếp theo preorder (parent xuất hiện trước child).
          2. Với mỗi node, tra _obj_id_map với id(node.parent_node).
             Parent đã có ID vì được xử lý trước.
          3. Sinh ID = parent_final_id + "_" + node_suffix.
        """
        for node in nodes:
            parent_node = node.parent_node
            if parent_node is not None:
                parent_final = self._obj_id_map.get(id(parent_node))
                if parent_final:
                    self._obj_id_map[id(node)] = f"{parent_final}_{self._node_suffix(node)}"
                else:
                    # Không nên xảy ra với preorder — log để debug
                    self._obj_id_map[id(node)] = f"{self.law_prefix}_{self._node_suffix(node)}"
            else:
                # Root node (không có parent)
                self._obj_id_map[id(node)] = f"{self.law_prefix}_{self._node_suffix(node)}"
    def _node_suffix(self, node: HierarchyNode) -> str:
        """Tạo phần suffix của ID cho node.

        Khi marker là None (CLAUSE từ List Paragraph fallback), dùng position
        để đảm bảo ID unique giữa các siblings.
        """
        type_short = self.TYPE_SHORT[node.node_type]
        raw = node.raw_marker
        if raw:
            marker = self._normalize_marker(raw, node.node_type)
        else:
            # Không có marker (VD: List Paragraph CLAUSE mất số tự động)
            # Dùng position để tạo ID unique: khoan-1, khoan-2, ...
            marker = str(node.position)
        return f"{type_short}-{marker}"

    @staticmethod
    def _normalize_marker(marker: Optional[str], node_type: NodeType) -> str:
        """Chuẩn hóa marker về lowercase không dấu cho ID."""
        if not marker:
            return "unknown"
        # La Mã → lowercase
        marker = marker.strip().lower()
        # Chuyển 'đ' thành 'd' cho an toàn URL/ID
        marker = marker.replace('đ', 'd')
        # Loại ký tự đặc biệt (chỉ giữ alphanum và gạch ngang)
        marker = re.sub(r"[^a-z0-9\-]", "", marker)
        return marker or "unknown"

    # -----------------------------------------------------------------------
    # Internal: build một Legal Node dict
    # -----------------------------------------------------------------------
    def _build_node(self, node: HierarchyNode) -> dict:
        # Dùng obj_id_map để lấy final ID chính xác cho node này
        final_id = self._obj_id_map.get(id(node), f"{self.law_prefix}_{node.temp_id()}")

        # Tìm parent final ID trực tiếp qua object reference (giải pháp cho bug collision)
        parent_final = None
        if node.parent_node is not None:
            parent_final = self._obj_id_map.get(id(node.parent_node))
        elif node.parent_id:
            # Fallback: nếu không có parent_node (ví dụ node được tạo từ path khác)
            # Log cảnh báo vì đây là trường hợp không mong muốn
            pass  # parent_final giữ None

        match = node.boundary.match
        b = node.boundary

        return {
            "id":              final_id,
            "type":            node.node_type.value,
            "depth":           node.depth,
            "title":           (match.title or "").strip() or None,
            "text":            self._extract_text(node),
            "parent_id":       parent_final,
            "children_count":  len(node.children_ids),
            "position":        node.position,
            "number":          match.number,         # Số pháp lý (CHAPTER/SECTION/ARTICLE/CLAUSE), int|str|None
            "marker":          match.marker,          # Ký tự nhận diện POINT (a/b/đ/e...), None cho node khác
            "law_prefix":      self.law_prefix,
            "law_code":        self.law_code,
            "source_doc":      self.source_doc,
            "word_style":      match.word_style,
            "start_idx":       b.start_idx,
            "end_idx":         b.end_idx,
            "implicit_parent": self._is_implicit_parent(node, parent_final),
        }

    @staticmethod
    def _is_implicit_parent(node: HierarchyNode, parent_final: Optional[str]) -> bool:
        """Kiểm tra EC-3: Orphan POINT (có parent trực tiếp là ARTICLE, không qua CLAUSE).

        Dùng final parent ID đã được resolve để kiểm tra — tránh lookup bằng string temp_id.
        """
        if node.node_type != NodeType.POINT:
            return False
        if not parent_final:
            return False
        # ARTICLE ID chứa '_dieu-' nhưng không chứa '_khoan-'
        return "_dieu-" in parent_final and "_khoan-" not in parent_final

    @staticmethod
    def _extract_text(node: HierarchyNode) -> str:
        """
        Lấy text của node.

        Chiến lược hiện tại (CHƯA CHỐT):
          - text = nội dung trực tiếp của node, không gồm children text
          - Dùng match.text (phần sau marker) + content_lines
        """
        parts = []

        # Phần text từ dòng header (phần sau marker/tiêu đề)
        inline_text = (node.boundary.match.text or "").strip()
        if inline_text:
            parts.append(inline_text)

        # Content lines (các dòng tiếp theo chưa phải marker mới)
        body = node.boundary.body_text.strip()
        if body:
            parts.append(body)

        return "\n".join(parts).strip()
