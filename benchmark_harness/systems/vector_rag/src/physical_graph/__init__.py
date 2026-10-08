# -*- coding: utf-8 -*-
"""
src/physical_graph/__init__.py — Public API cho Module 4: Physical Graph Builder.

Import lazy để tránh circular import khi chạy module bằng python -m.
"""

from __future__ import annotations

__all__ = [
    "Edge",
    "EdgeGenerator",
    "GraphExporter",
    "PhysicalGraphBuilder",
]


def __getattr__(name: str):
    """Lazy import — chỉ import khi được dùng."""
    if name in ("Edge", "EdgeGenerator"):
        from src.physical_graph.edge_generator import Edge, EdgeGenerator  # noqa: F401
        g = {"Edge": Edge, "EdgeGenerator": EdgeGenerator}
        return g[name]
    if name == "GraphExporter":
        from src.physical_graph.json_exporter import GraphExporter  # noqa: F401
        return GraphExporter
    if name == "PhysicalGraphBuilder":
        from src.physical_graph.graph_builder import PhysicalGraphBuilder  # noqa: F401
        return PhysicalGraphBuilder
    raise AttributeError(f"module 'src.physical_graph' has no attribute {name!r}")
