# -*- coding: utf-8 -*-
"""
edge_generator.py — Thuật toán sinh cạnh (Edge Generation) cho Physical Graph.

Sinh 3 loại cạnh có hướng:
  - BELONG_TO : Con → Cha (phân cấp)
  - NEXT      : Node hiện tại → Node kế tiếp (tuần tự)
  - PREVIOUS  : Node hiện tại → Node liền trước (tuần tự)

Quy tắc nhóm Sibling (NEXT/PREVIOUS):
  - Chỉ nối giữa các node CÙNG (parent_id, type).
  - Sort theo start_idx ASC (tọa độ vật lý tuyệt đối trên tài liệu gốc).

Dependencies: stdlib only (dataclasses, collections).
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple


# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class Edge:
    """Biểu diễn một cạnh có hướng trong Physical Graph."""
    source: str
    target: str
    type: str        # "BELONG_TO" | "NEXT" | "PREVIOUS"
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "type": self.type,
            "properties": self.properties,
        }


# ============================================================
# EDGE GENERATOR
# ============================================================

class EdgeGenerator:
    """
    Sinh toàn bộ các cạnh (edges) cho Physical Graph từ danh sách raw nodes.

    Usage:
        gen = EdgeGenerator()
        belong_to, next_edges, previous_edges = gen.generate_all(raw_nodes)
    """

    # ----------------------------------------------------------
    # Public API
    # ----------------------------------------------------------

    def generate_all(
        self,
        nodes: List[Dict[str, Any]],
    ) -> Tuple[List[Edge], List[Edge], List[Edge]]:
        """
        Entry point chính. Sinh toàn bộ 3 loại cạnh.

        Args:
            nodes: Danh sách raw node dict từ validated_nodes.json.

        Returns:
            Tuple (belong_to_edges, next_edges, previous_edges).
        """
        belong_to = self.generate_belong_to_edges(nodes)
        next_edges, previous_edges = self.generate_sequential_edges(nodes)
        return belong_to, next_edges, previous_edges

    # ----------------------------------------------------------
    # A. BELONG_TO edges  (Con → Cha)
    # ----------------------------------------------------------

    def generate_belong_to_edges(
        self,
        nodes: List[Dict[str, Any]],
    ) -> List[Edge]:
        """
        Sinh cạnh BELONG_TO từ node con lên node cha.

        Rule:
          - source = node["id"]
          - target = node["parent_id"]
          - Chỉ tạo khi parent_id không phải None/null.
          - properties = {"implicit": node["implicit_parent"]}
        """
        edges: List[Edge] = []
        for node in nodes:
            parent_id = node.get("parent_id")
            if parent_id is None:
                continue  # Root node — bỏ qua

            edges.append(Edge(
                source=node["id"],
                target=parent_id,
                type="BELONG_TO",
                properties={"implicit": bool(node.get("implicit_parent", False))},
            ))
        return edges

    # ----------------------------------------------------------
    # B. NEXT + PREVIOUS edges  (Sibling tuần tự)
    # ----------------------------------------------------------

    def generate_sequential_edges(
        self,
        nodes: List[Dict[str, Any]],
    ) -> Tuple[List[Edge], List[Edge]]:
        """
        Sinh cạnh NEXT và PREVIOUS giữa các sibling nodes.

        Grouping rule:
          - Nhóm theo (parent_id, type).
          - Bỏ qua root nodes (parent_id is None).

        Sort rule:
          - Sắp xếp trong mỗi nhóm theo start_idx ASC.
          - start_idx là tọa độ vật lý tuyệt đối đảm bảo đúng reading flow.

        Edge rule:
          - NEXT     : curr → next  (source=curr.id, target=next.id)
          - PREVIOUS : next → curr  (source=next.id, target=curr.id)
        """
        # Bước 1: Nhóm nodes theo (parent_id, type)
        groups: Dict[Tuple[str, str], List[Dict[str, Any]]] = defaultdict(list)
        for node in nodes:
            parent_id = node.get("parent_id")
            if parent_id is None:
                continue  # Root không tham gia sequential edges
            key = (parent_id, node["type"])
            groups[key].append(node)

        next_edges: List[Edge] = []
        previous_edges: List[Edge] = []

        # Bước 2: Trong mỗi nhóm, sort theo start_idx rồi sinh cạnh
        for (_parent_id, _node_type), siblings in groups.items():
            # Sort theo start_idx ASC (tọa độ vật lý)
            sorted_siblings = sorted(siblings, key=lambda n: n.get("start_idx", 0))

            # Bước 3: Sinh cạnh cho mỗi cặp liền kề
            for i in range(len(sorted_siblings) - 1):
                curr = sorted_siblings[i]
                nxt  = sorted_siblings[i + 1]

                # NEXT: node hiện tại → node kế tiếp
                next_edges.append(Edge(
                    source=curr["id"],
                    target=nxt["id"],
                    type="NEXT",
                    properties={},
                ))

                # PREVIOUS: node kế tiếp → node hiện tại
                previous_edges.append(Edge(
                    source=nxt["id"],
                    target=curr["id"],
                    type="PREVIOUS",
                    properties={},
                ))

        return next_edges, previous_edges
