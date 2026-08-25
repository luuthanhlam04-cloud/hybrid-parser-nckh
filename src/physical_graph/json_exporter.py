# -*- coding: utf-8 -*-
"""
json_exporter.py — Format Graph Schema và lưu file Physical Graph.

Chức năng:
  1. node_to_graph_node(): Chuyển raw node dict sang Graph Node format
     (labels = ["LegalNode", type], properties = tất cả fields trừ id/type/parent_id).
  2. edge_to_graph_edge(): Chuyển Edge dataclass sang dict.
  3. export(): Ghi file physical_graph.json với indent=2, ensure_ascii=False.

Output format:
  {
    "graph_metadata": {"total_nodes": N, "total_edges": M},
    "nodes": [...],
    "edges": [...]
  }

Dependencies: stdlib only (json, pathlib).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from src.physical_graph.edge_generator import Edge


# ============================================================
# EXCLUDED FIELDS (không đưa vào properties, đã được nâng lên top-level)
# ============================================================

_NODE_TOP_LEVEL_KEYS = frozenset({"id", "type", "parent_id"})


class GraphExporter:
    """
    Chuyển đổi và xuất Physical Graph sang JSON.

    Usage:
        exporter = GraphExporter()
        graph_dict = exporter.assemble(raw_nodes, all_edges)
        exporter.export(graph_dict, output_path="outputs/physical_graphs/physical_graph.json")
    """

    # ----------------------------------------------------------
    # Node transformation
    # ----------------------------------------------------------

    def node_to_graph_node(self, raw_node: Dict[str, Any]) -> Dict[str, Any]:
        """
        Chuyển raw node dict sang Graph Node format.

        Output:
            {
              "id": "...",
              "labels": ["LegalNode", "<TYPE>"],
              "properties": { <tất cả keys trừ id, type, parent_id> }
            }

        Args:
            raw_node: Một phần tử từ validated_nodes.json.

        Returns:
            Graph Node dict theo spec.
        """
        properties = {
            key: value
            for key, value in raw_node.items()
            if key not in _NODE_TOP_LEVEL_KEYS
        }
        return {
            "id": raw_node["id"],
            "labels": ["LegalNode", raw_node["type"]],
            "properties": properties,
        }

    # ----------------------------------------------------------
    # Edge transformation
    # ----------------------------------------------------------

    def edge_to_graph_edge(self, edge: Edge) -> Dict[str, Any]:
        """
        Chuyển Edge dataclass sang dict theo spec.

        Output:
            {
              "source": "...",
              "target": "...",
              "type": "BELONG_TO" | "NEXT" | "PREVIOUS",
              "properties": {...}
            }
        """
        return edge.to_dict()

    # ----------------------------------------------------------
    # Assemble & export
    # ----------------------------------------------------------

    def assemble(
        self,
        raw_nodes: List[Dict[str, Any]],
        all_edges: List[Edge],
    ) -> Dict[str, Any]:
        """
        Kết hợp nodes và edges thành cấu trúc graph hoàn chỉnh.

        Args:
            raw_nodes: Danh sách raw node dict từ validated_nodes.json.
            all_edges: Danh sách Edge (BELONG_TO + NEXT + PREVIOUS gộp lại).

        Returns:
            Dict theo Graph Serialization Format.
        """
        graph_nodes = [self.node_to_graph_node(n) for n in raw_nodes]
        graph_edges = [self.edge_to_graph_edge(e) for e in all_edges]

        return {
            "graph_metadata": {
                "total_nodes": len(graph_nodes),
                "total_edges": len(graph_edges),
            },
            "nodes": graph_nodes,
            "edges": graph_edges,
        }

    def export(
        self,
        graph: Dict[str, Any],
        output_path: str | Path,
    ) -> None:
        """
        Ghi Physical Graph ra file JSON.

        Args:
            graph:       Dict trả về bởi assemble().
            output_path: Đường dẫn đầu ra (sẽ tự tạo thư mục cha nếu chưa có).
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", encoding="utf-8") as f:
            json.dump(graph, f, ensure_ascii=False, indent=2)
