# -*- coding: utf-8 -*-
"""
hierarchy_builder.py — Module 2: Regex Parser
Xây dựng quan hệ Parent-Child từ danh sách Boundary.

Nguyên tắc: Linear text → Tree structure.
Sử dụng Stack để track parent node hiện tại theo depth.

Stack logic:
  - Khi gặp node có depth d:
    → Pop stack cho đến khi top có depth < d
    → Top của stack = parent node
    → Push node hiện tại vào stack
"""

from dataclasses import dataclass, field
from typing import Optional
from boundary_detector import Boundary
from regex_engine import NodeType


# ---------------------------------------------------------------------------
# HierarchyNode — node có đầy đủ thông tin phân cấp
# ---------------------------------------------------------------------------
@dataclass
class HierarchyNode:
    boundary: Boundary
    parent_id: Optional[str] = None
    # Object reference đến parent node — dùng trong NodeGenerator để tránh
    # collision khi tra cứu parent bằng temp_id string (bug đã xác nhận).
    # Không serialize — chỉ dùng nội bộ trong quá trình build.
    parent_node: Optional['HierarchyNode'] = field(default=None, repr=False)
    children_ids: list[str] = field(default_factory=list)
    position: int = 1   # Thứ tự trong cùng parent (bắt đầu từ 1)

    @property
    def node_type(self) -> NodeType:
        return self.boundary.node_type

    @property
    def depth(self) -> int:
        return self.node_type.depth

    @property
    def raw_marker(self) -> Optional[str]:
        """Số thứ tự hoặc ký tự marker (26, 1, a, đ...)"""
        m = self.boundary.match
        return m.number or m.marker

    def temp_id(self, position_override: int = 0) -> str:
        """ID tạm thời dùng trong quá trình build, trước khi có law_prefix.
        
        Khi raw_marker là None (CLAUSE từ fallback List Paragraph pattern),
        dùng position_override để tạo ID duy nhất.
        """
        type_short = {
            NodeType.CHAPTER: "ch",
            NodeType.SECTION: "sec",
            NodeType.ARTICLE: "dieu",
            NodeType.CLAUSE:  "khoan",
            NodeType.POINT:   "diem",
        }[self.node_type]
        marker = self.raw_marker
        if marker:
            return f"{type_short}_{marker}"
        else:
            # Không có marker (VD: CLAUSE từ List Paragraph mất số)
            # Dùng position để đảm bảo unique temp_id
            pos = position_override or self.position
            return f"{type_short}_pos{pos}"


# ---------------------------------------------------------------------------
# HierarchyBuilder
# ---------------------------------------------------------------------------
class HierarchyBuilder:
    """
    Xây dựng cây phân cấp từ danh sách Boundary đã sắp xếp theo thứ tự xuất hiện.

    Thuật toán Stack-based:
      parent_stack = []
      Với mỗi boundary:
        Pop stack cho đến khi top.depth < current.depth
        parent = top của stack (nếu có)
        Assign parent_id
        Push current vào stack
    """

    def build(self, boundaries: list[Boundary]) -> list[HierarchyNode]:
        """
        Args:
            boundaries: Danh sách Boundary theo thứ tự xuất hiện trong văn bản.

        Returns:
            Danh sách HierarchyNode với parent_id, children_ids, position đã được gán.
        """
        nodes: list[HierarchyNode] = []
        stack: list[HierarchyNode] = []   # Stack of HierarchyNode
        position_counter: dict[Optional[str], int] = {}  # parent_id → count

        for boundary in boundaries:
            node = HierarchyNode(boundary=boundary)
            current_depth = node.depth

            # Pop stack cho đến khi tìm được parent có depth < current_depth
            while stack and stack[-1].depth >= current_depth:
                stack.pop()

            # Gán parent: lưu CẢ object reference VÀ temp_id string
            # - parent_node: object reference — dùng bởi NodeGenerator (unambiguous)
            # - parent_id: temp_id string — giữ backward compat, dùng trong check_orphans
            if stack:
                p = stack[-1]
                node.parent_node = p                          # Object reference (fix bug)
                node.parent_id = self._get_node_id(p)        # Temp_id string (compat)
            else:
                node.parent_node = None
                node.parent_id = None

            # Gán position TRƯỚC khi gọi temp_id (temp_id dùng position khi marker=None)
            parent_key = (node.parent_id, node.node_type)
            position_counter[parent_key] = position_counter.get(parent_key, 0) + 1
            node.position = position_counter[parent_key]

            # Sau khi có position, mới append vào children_ids của parent
            if stack:
                stack[-1].children_ids.append(self._get_node_id(node))

            stack.append(node)
            nodes.append(node)

        return nodes

    @staticmethod
    def _get_node_id(node: HierarchyNode) -> str:
        """ID tạm thời của node — sẽ được thay thế bởi NodeGenerator."""
        return node.temp_id(position_override=node.position)

    # -----------------------------------------------------------------------
    # Utility: kiểm tra tính hợp lệ cơ bản
    # -----------------------------------------------------------------------
    @staticmethod
    def check_orphans(nodes: list[HierarchyNode]) -> list[HierarchyNode]:
        """
        Trả về danh sách node mồ côi (có parent_id nhưng parent không tồn tại).
        Đây là input cho Module 3 (Validation Engine).
        """
        existing_ids = set()
        for node in nodes:
            existing_ids.add(node.temp_id())

        orphans = []
        for node in nodes:
            if node.parent_id and node.parent_id not in existing_ids:
                orphans.append(node)
        return orphans

    @staticmethod
    def check_gaps(nodes: list[HierarchyNode]) -> list[dict]:
        """
        Kiểm tra đứt gãy sequence trong cùng parent (1, 3 nhưng thiếu 2).
        Trả về danh sách gap reports.
        """
        from collections import defaultdict
        parent_children: dict[Optional[str], list[HierarchyNode]] = defaultdict(list)
        for node in nodes:
            parent_children[node.parent_id].append(node)

        gaps = []
        for parent_id, children in parent_children.items():
            positions = sorted(c.position for c in children)
            for i in range(len(positions) - 1):
                if positions[i + 1] - positions[i] > 1:
                    gaps.append({
                        "parent_id": parent_id,
                        "gap_after_position": positions[i],
                        "missing_to": positions[i + 1],
                    })
        return gaps
