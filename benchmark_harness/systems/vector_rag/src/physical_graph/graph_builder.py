# -*- coding: utf-8 -*-
"""
graph_builder.py — Main Orchestrator: Đọc JSON, điều phối build Physical Graph.

Luồng dữ liệu:
  validated_nodes.json  →  PhysicalGraphBuilder  →  physical_graph.json

Chức năng:
  1. load()  — Đọc và validate validated_nodes.json.
  2. build() — Gọi EdgeGenerator và GraphExporter để tạo graph dict.
  3. run()   — Orchestrate toàn bộ pipeline và log kết quả.

CLI entry point:
  python -m src.physical_graph.graph_builder

Dependencies: stdlib only (json, pathlib, logging).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from src.physical_graph.edge_generator import Edge, EdgeGenerator
from src.physical_graph.json_exporter import GraphExporter

# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("physical_graph.builder")


# ============================================================
# DEFAULT PATHS
# ============================================================

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_DEFAULT_INPUT  = _PROJECT_ROOT / "outputs" / "physical_graphs" / "validated_nodes.json"
_DEFAULT_OUTPUT = _PROJECT_ROOT / "outputs" / "physical_graphs" / "physical_graph.json"


# ============================================================
# PHYSICAL GRAPH BUILDER
# ============================================================

class PhysicalGraphBuilder:
    """
    Main Orchestrator của Module 4.

    Nhận validated_nodes.json → sinh edges → xuất physical_graph.json.

    Usage:
        builder = PhysicalGraphBuilder()
        builder.run()

        # Hoặc tuỳ chỉnh đường dẫn:
        builder = PhysicalGraphBuilder(
            input_path="path/to/validated_nodes.json",
            output_path="path/to/physical_graph.json",
        )
        builder.run()
    """

    def __init__(
        self,
        input_path: str | Path = _DEFAULT_INPUT,
        output_path: str | Path = _DEFAULT_OUTPUT,
    ) -> None:
        self.input_path  = Path(input_path)
        self.output_path = Path(output_path)
        self._edge_gen   = EdgeGenerator()
        self._exporter   = GraphExporter()

    # ----------------------------------------------------------
    # Step 1: Load
    # ----------------------------------------------------------

    def load(self) -> List[Dict[str, Any]]:
        """
        Đọc validated_nodes.json và trả về danh sách raw node dict.

        Raises:
            FileNotFoundError: Nếu file đầu vào không tồn tại.
            ValueError:        Nếu JSON không phải array hoặc rỗng.
        """
        if not self.input_path.exists():
            raise FileNotFoundError(
                f"Input file không tồn tại: {self.input_path}\n"
                f"Hãy chạy Module 3 (Validation) trước để sinh file này."
            )

        logger.info("Loading input: %s", self.input_path)
        with self.input_path.open(encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError(
                f"validated_nodes.json phải là JSON array. Đọc được: {type(data).__name__}."
            )
        if len(data) == 0:
            raise ValueError("validated_nodes.json rỗng — không có node nào để xử lý.")

        logger.info("Loaded %d nodes thành công.", len(data))
        return data

    # ----------------------------------------------------------
    # Step 2: Build
    # ----------------------------------------------------------

    def build(self) -> Dict[str, Any]:
        """
        Xây dựng toàn bộ Physical Graph dict từ file đầu vào.

        Returns:
            Dict theo Graph Serialization Format (có graph_metadata, nodes, edges).
        """
        raw_nodes = self.load()

        # Sinh tất cả cạnh
        logger.info("Generating edges...")
        belong_to_edges, next_edges, previous_edges = self._edge_gen.generate_all(raw_nodes)

        # Log breakdown
        logger.info(
            "Edges generated — BELONG_TO: %d | NEXT: %d | PREVIOUS: %d | Tổng: %d",
            len(belong_to_edges),
            len(next_edges),
            len(previous_edges),
            len(belong_to_edges) + len(next_edges) + len(previous_edges),
        )

        # Gộp tất cả cạnh theo thứ tự: BELONG_TO → NEXT → PREVIOUS
        all_edges: List[Edge] = belong_to_edges + next_edges + previous_edges

        # Assemble graph
        graph = self._exporter.assemble(raw_nodes, all_edges)

        logger.info(
            "Graph assembled — Nodes: %d | Edges: %d",
            graph["graph_metadata"]["total_nodes"],
            graph["graph_metadata"]["total_edges"],
        )
        return graph

    # ----------------------------------------------------------
    # Step 3: Run (full pipeline)
    # ----------------------------------------------------------

    def run(self) -> None:
        """
        Chạy toàn bộ pipeline: load → build → export.

        Output file được ghi ra self.output_path.
        """
        logger.info("=" * 60)
        logger.info("Module 4 — Physical Graph Builder");
        logger.info("Input : %s", self.input_path)
        logger.info("Output: %s", self.output_path)
        logger.info("=" * 60)

        graph = self.build()

        logger.info("Exporting to %s ...", self.output_path)
        self._exporter.export(graph, self.output_path)

        logger.info("✅ Hoàn thành! physical_graph.json đã được lưu tại: %s", self.output_path)


# ============================================================
# CLI ENTRY POINT
# ============================================================

if __name__ == "__main__":
    builder = PhysicalGraphBuilder()
    builder.run()
