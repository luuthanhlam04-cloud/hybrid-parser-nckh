# -*- coding: utf-8 -*-
"""
Unit Tests cho Module 4 — Physical Graph Builder.

Test coverage:
  - TestEdgeDataclass        : Edge.to_dict() format chính xác.
  - TestNodeTransformation   : node_to_graph_node() labels và properties đúng.
  - TestBelongToEdges        : Sinh cạnh BELONG_TO đúng chiều, implicit property.
  - TestNextPreviousEdges    : Sinh NEXT/PREVIOUS đúng — group (parent_id, type).
  - TestGraphExporter        : assemble() output đúng schema.
  - TestEndToEnd             : Build từ 5-node fixture — count edges chính xác.

Fixture 5 nodes:
  ROOT (CHAPTER, parent=None, start_idx=0)
    ├── SECTION-1 (parent=ROOT, type=SECTION, start_idx=1)
    │     ├── CLAUSE-1 (parent=SECTION-1, type=CLAUSE, start_idx=2)
    │     └── CLAUSE-2 (parent=SECTION-1, type=CLAUSE, start_idx=3)
    └── SECTION-2 (parent=ROOT, type=SECTION, start_idx=4)

Expected edges:
  BELONG_TO : 4 (mỗi non-root 1 edge lên cha)
  NEXT      : 2 (SECTION-1→SECTION-2, CLAUSE-1→CLAUSE-2)
  PREVIOUS  : 2 (SECTION-2→SECTION-1, CLAUSE-2→CLAUSE-1)
  Tổng     : 8
"""

from __future__ import annotations

import pytest
from typing import Any, Dict, List

from src.physical_graph.edge_generator import Edge, EdgeGenerator
from src.physical_graph.json_exporter import GraphExporter


# ============================================================
# HELPERS & FIXTURES
# ============================================================

def _make_node(
    node_id: str,
    node_type: str,
    parent_id: str | None = None,
    start_idx: int = 0,
    implicit_parent: bool = False,
    **extra,
) -> Dict[str, Any]:
    """Tạo raw node dict cho test (giả lập validated_nodes.json entry)."""
    return {
        "id": node_id,
        "type": node_type,
        "parent_id": parent_id,
        "start_idx": start_idx,
        "end_idx": start_idx + 1,
        "implicit_parent": implicit_parent,
        "depth": 0,
        "title": None,
        "text": "nội dung test",
        "children_count": 0,
        "position": 1,
        "number": "1",
        "marker": None,
        "law_prefix": "doc",
        "law_code": "TEST",
        "source_doc": "test.docx",
        "word_style": None,
        **extra,
    }


@pytest.fixture
def five_node_fixture() -> List[Dict[str, Any]]:
    """5-node fixture cho TestEndToEnd."""
    return [
        _make_node("root",      "CHAPTER", parent_id=None,    start_idx=0),
        _make_node("section-1", "SECTION", parent_id="root",  start_idx=1),
        _make_node("clause-1",  "CLAUSE",  parent_id="section-1", start_idx=2),
        _make_node("clause-2",  "CLAUSE",  parent_id="section-1", start_idx=3),
        _make_node("section-2", "SECTION", parent_id="root",  start_idx=4),
    ]


@pytest.fixture
def gen() -> EdgeGenerator:
    return EdgeGenerator()


@pytest.fixture
def exporter() -> GraphExporter:
    return GraphExporter()


# ============================================================
# TEST CLASS 1: Edge dataclass
# ============================================================

class TestEdgeDataclass:
    def test_to_dict_belong_to(self):
        edge = Edge(
            source="child",
            target="parent",
            type="BELONG_TO",
            properties={"implicit": False},
        )
        d = edge.to_dict()
        assert d["source"] == "child"
        assert d["target"] == "parent"
        assert d["type"] == "BELONG_TO"
        assert d["properties"] == {"implicit": False}

    def test_to_dict_next_empty_properties(self):
        edge = Edge(source="a", target="b", type="NEXT")
        d = edge.to_dict()
        assert d["properties"] == {}


# ============================================================
# TEST CLASS 2: Node transformation
# ============================================================

class TestNodeTransformation:
    def test_labels_always_two_elements(self, exporter):
        node = _make_node("n1", "ARTICLE")
        result = exporter.node_to_graph_node(node)
        assert result["labels"] == ["LegalNode", "ARTICLE"]

    def test_labels_correct_type_for_each_node_type(self, exporter):
        for node_type in ["CHAPTER", "SECTION", "ARTICLE", "CLAUSE", "POINT"]:
            node = _make_node("n", node_type)
            result = exporter.node_to_graph_node(node)
            assert result["labels"][0] == "LegalNode"
            assert result["labels"][1] == node_type

    def test_id_is_top_level(self, exporter):
        node = _make_node("my-id", "CLAUSE")
        result = exporter.node_to_graph_node(node)
        assert result["id"] == "my-id"

    def test_id_not_in_properties(self, exporter):
        node = _make_node("my-id", "CLAUSE")
        result = exporter.node_to_graph_node(node)
        assert "id" not in result["properties"]

    def test_type_not_in_properties(self, exporter):
        node = _make_node("n", "CLAUSE")
        result = exporter.node_to_graph_node(node)
        assert "type" not in result["properties"]

    def test_parent_id_not_in_properties(self, exporter):
        node = _make_node("n", "CLAUSE", parent_id="parent")
        result = exporter.node_to_graph_node(node)
        assert "parent_id" not in result["properties"]

    def test_all_other_fields_in_properties(self, exporter):
        node = _make_node("n", "CLAUSE", parent_id="p", start_idx=5)
        result = exporter.node_to_graph_node(node)
        props = result["properties"]
        # Fields này phải có trong properties
        for key in ["start_idx", "end_idx", "depth", "text", "title",
                    "children_count", "position", "number", "marker",
                    "law_prefix", "law_code", "source_doc", "word_style",
                    "implicit_parent"]:
            assert key in props, f"Field '{key}' phải có trong properties"

    def test_start_idx_value_preserved(self, exporter):
        node = _make_node("n", "CLAUSE", start_idx=42)
        result = exporter.node_to_graph_node(node)
        assert result["properties"]["start_idx"] == 42


# ============================================================
# TEST CLASS 3: BELONG_TO edges
# ============================================================

class TestBelongToEdges:
    def test_root_node_has_no_belong_to_edge(self, gen):
        nodes = [_make_node("root", "CHAPTER", parent_id=None)]
        edges = gen.generate_belong_to_edges(nodes)
        assert len(edges) == 0

    def test_child_node_generates_one_edge(self, gen):
        nodes = [
            _make_node("root", "CHAPTER", parent_id=None),
            _make_node("child", "SECTION", parent_id="root"),
        ]
        edges = gen.generate_belong_to_edges(nodes)
        assert len(edges) == 1

    def test_edge_direction_child_to_parent(self, gen):
        nodes = [_make_node("child", "SECTION", parent_id="root")]
        edges = gen.generate_belong_to_edges(nodes)
        assert edges[0].source == "child"
        assert edges[0].target == "root"

    def test_edge_type_is_belong_to(self, gen):
        nodes = [_make_node("child", "CLAUSE", parent_id="parent")]
        edges = gen.generate_belong_to_edges(nodes)
        assert edges[0].type == "BELONG_TO"

    def test_implicit_false_property(self, gen):
        nodes = [_make_node("child", "CLAUSE", parent_id="parent", implicit_parent=False)]
        edges = gen.generate_belong_to_edges(nodes)
        assert edges[0].properties == {"implicit": False}

    def test_implicit_true_property(self, gen):
        nodes = [_make_node("child", "CLAUSE", parent_id="parent", implicit_parent=True)]
        edges = gen.generate_belong_to_edges(nodes)
        assert edges[0].properties == {"implicit": True}

    def test_multiple_children_all_get_edges(self, gen):
        nodes = [
            _make_node("root",  "CHAPTER", parent_id=None),
            _make_node("child1", "CLAUSE", parent_id="root"),
            _make_node("child2", "CLAUSE", parent_id="root"),
            _make_node("child3", "CLAUSE", parent_id="root"),
        ]
        edges = gen.generate_belong_to_edges(nodes)
        assert len(edges) == 3


# ============================================================
# TEST CLASS 4: NEXT & PREVIOUS edges
# ============================================================

class TestNextPreviousEdges:
    def test_single_node_group_no_sequential_edges(self, gen):
        nodes = [_make_node("only", "CLAUSE", parent_id="parent", start_idx=0)]
        next_edges, prev_edges = gen.generate_sequential_edges(nodes)
        assert len(next_edges) == 0
        assert len(prev_edges) == 0

    def test_two_siblings_generate_one_next_one_previous(self, gen):
        nodes = [
            _make_node("a", "CLAUSE", parent_id="p", start_idx=0),
            _make_node("b", "CLAUSE", parent_id="p", start_idx=1),
        ]
        next_edges, prev_edges = gen.generate_sequential_edges(nodes)
        assert len(next_edges) == 1
        assert len(prev_edges) == 1

    def test_next_edge_direction(self, gen):
        nodes = [
            _make_node("a", "CLAUSE", parent_id="p", start_idx=0),
            _make_node("b", "CLAUSE", parent_id="p", start_idx=1),
        ]
        next_edges, _ = gen.generate_sequential_edges(nodes)
        assert next_edges[0].source == "a"
        assert next_edges[0].target == "b"
        assert next_edges[0].type == "NEXT"

    def test_previous_edge_direction(self, gen):
        nodes = [
            _make_node("a", "CLAUSE", parent_id="p", start_idx=0),
            _make_node("b", "CLAUSE", parent_id="p", start_idx=1),
        ]
        _, prev_edges = gen.generate_sequential_edges(nodes)
        assert prev_edges[0].source == "b"
        assert prev_edges[0].target == "a"
        assert prev_edges[0].type == "PREVIOUS"

    def test_sort_by_start_idx_ascending(self, gen):
        """Dù thứ tự trong input ngược, NEXT phải theo start_idx tăng dần."""
        nodes = [
            _make_node("b", "CLAUSE", parent_id="p", start_idx=10),  # xuất hiện trước
            _make_node("a", "CLAUSE", parent_id="p", start_idx=5),   # nhưng start_idx nhỏ hơn
        ]
        next_edges, _ = gen.generate_sequential_edges(nodes)
        assert next_edges[0].source == "a"  # start_idx=5 đi trước
        assert next_edges[0].target == "b"  # start_idx=10 đi sau

    def test_different_types_in_same_parent_not_connected(self, gen):
        """CLAUSE và POINT cùng parent không được nối với nhau."""
        nodes = [
            _make_node("clause", "CLAUSE", parent_id="p", start_idx=0),
            _make_node("point",  "POINT",  parent_id="p", start_idx=1),
        ]
        next_edges, prev_edges = gen.generate_sequential_edges(nodes)
        assert len(next_edges) == 0
        assert len(prev_edges) == 0

    def test_different_parents_same_type_not_connected(self, gen):
        """Nodes cùng type nhưng khác parent không được nối với nhau."""
        nodes = [
            _make_node("a", "CLAUSE", parent_id="parent-1", start_idx=0),
            _make_node("b", "CLAUSE", parent_id="parent-2", start_idx=1),
        ]
        next_edges, prev_edges = gen.generate_sequential_edges(nodes)
        assert len(next_edges) == 0
        assert len(prev_edges) == 0

    def test_three_siblings_generate_two_next_two_previous(self, gen):
        nodes = [
            _make_node("a", "CLAUSE", parent_id="p", start_idx=0),
            _make_node("b", "CLAUSE", parent_id="p", start_idx=1),
            _make_node("c", "CLAUSE", parent_id="p", start_idx=2),
        ]
        next_edges, prev_edges = gen.generate_sequential_edges(nodes)
        assert len(next_edges) == 2
        assert len(prev_edges) == 2

    def test_root_node_excluded_from_sequential(self, gen):
        """Root node (parent_id=None) không tham gia tạo cạnh tuần tự."""
        nodes = [_make_node("root", "CHAPTER", parent_id=None, start_idx=0)]
        next_edges, prev_edges = gen.generate_sequential_edges(nodes)
        assert len(next_edges) == 0
        assert len(prev_edges) == 0

    def test_next_properties_are_empty_dict(self, gen):
        nodes = [
            _make_node("a", "CLAUSE", parent_id="p", start_idx=0),
            _make_node("b", "CLAUSE", parent_id="p", start_idx=1),
        ]
        next_edges, _ = gen.generate_sequential_edges(nodes)
        assert next_edges[0].properties == {}


# ============================================================
# TEST CLASS 5: GraphExporter.assemble()
# ============================================================

class TestGraphExporter:
    def test_assemble_has_required_top_level_keys(self, exporter):
        nodes = [_make_node("n1", "ARTICLE")]
        edges: List[Edge] = []
        result = exporter.assemble(nodes, edges)
        assert "graph_metadata" in result
        assert "nodes" in result
        assert "edges" in result

    def test_graph_metadata_total_nodes_count(self, exporter):
        nodes = [_make_node(f"n{i}", "CLAUSE") for i in range(5)]
        result = exporter.assemble(nodes, [])
        assert result["graph_metadata"]["total_nodes"] == 5

    def test_graph_metadata_total_edges_count(self, exporter):
        nodes = [_make_node("n", "CLAUSE")]
        edges = [
            Edge(source="a", target="b", type="BELONG_TO", properties={"implicit": False}),
            Edge(source="b", target="c", type="NEXT"),
        ]
        result = exporter.assemble(nodes, edges)
        assert result["graph_metadata"]["total_edges"] == 2

    def test_nodes_list_same_length_as_input(self, exporter):
        nodes = [_make_node(f"n{i}", "SECTION") for i in range(3)]
        result = exporter.assemble(nodes, [])
        assert len(result["nodes"]) == 3

    def test_edges_list_same_length_as_input(self, exporter):
        nodes = [_make_node("n", "CLAUSE")]
        edges = [Edge(source="a", target="b", type="NEXT")]
        result = exporter.assemble(nodes, edges)
        assert len(result["edges"]) == 1

    def test_edge_dict_format(self, exporter):
        nodes = [_make_node("n", "CLAUSE")]
        edges = [Edge(source="src", target="tgt", type="BELONG_TO", properties={"implicit": True})]
        result = exporter.assemble(nodes, edges)
        edge_dict = result["edges"][0]
        assert edge_dict["source"] == "src"
        assert edge_dict["target"] == "tgt"
        assert edge_dict["type"] == "BELONG_TO"
        assert edge_dict["properties"] == {"implicit": True}


# ============================================================
# TEST CLASS 6: End-to-End (5-node fixture)
# ============================================================

class TestEndToEnd:
    """
    Kiểm tra toàn bộ pipeline với 5-node fixture.

    Fixture:
      ROOT (CHAPTER, parent=None, start_idx=0)
        ├── SECTION-1 (parent=ROOT, type=SECTION, start_idx=1)
        │     ├── CLAUSE-1 (parent=SECTION-1, type=CLAUSE, start_idx=2)
        │     └── CLAUSE-2 (parent=SECTION-1, type=CLAUSE, start_idx=3)
        └── SECTION-2 (parent=ROOT, type=SECTION, start_idx=4)

    Expected:
      BELONG_TO : 4  (ROOT bỏ qua, 4 non-root nodes mỗi node 1 edge)
      NEXT      : 2  (SECTION-1→SECTION-2, CLAUSE-1→CLAUSE-2)
      PREVIOUS  : 2  (SECTION-2→SECTION-1, CLAUSE-2→CLAUSE-1)
      Tổng     : 8
    """

    def test_total_belong_to_edges(self, gen, five_node_fixture):
        edges = gen.generate_belong_to_edges(five_node_fixture)
        assert len(edges) == 4, f"Expected 4 BELONG_TO edges, got {len(edges)}"

    def test_total_next_edges(self, gen, five_node_fixture):
        next_edges, _ = gen.generate_sequential_edges(five_node_fixture)
        assert len(next_edges) == 2, f"Expected 2 NEXT edges, got {len(next_edges)}"

    def test_total_previous_edges(self, gen, five_node_fixture):
        _, prev_edges = gen.generate_sequential_edges(five_node_fixture)
        assert len(prev_edges) == 2, f"Expected 2 PREVIOUS edges, got {len(prev_edges)}"

    def test_section_siblings_are_connected_via_next(self, gen, five_node_fixture):
        """SECTION-1 và SECTION-2 cùng (parent=ROOT, type=SECTION) ⇒ phải có cạnh NEXT."""
        next_edges, _ = gen.generate_sequential_edges(five_node_fixture)
        section_next = [
            e for e in next_edges
            if e.source == "section-1" and e.target == "section-2"
        ]
        assert len(section_next) == 1, "Phải có đúng 1 cạnh NEXT từ section-1 → section-2"

    def test_clause_siblings_are_connected_via_next(self, gen, five_node_fixture):
        next_edges, _ = gen.generate_sequential_edges(five_node_fixture)
        clause_next = [
            e for e in next_edges
            if e.source == "clause-1" and e.target == "clause-2"
        ]
        assert len(clause_next) == 1, "Phải có đúng 1 cạnh NEXT từ clause-1 → clause-2"

    def test_section_siblings_are_connected_via_previous(self, gen, five_node_fixture):
        _, prev_edges = gen.generate_sequential_edges(five_node_fixture)
        section_prev = [
            e for e in prev_edges
            if e.source == "section-2" and e.target == "section-1"
        ]
        assert len(section_prev) == 1, "Phải có đúng 1 cạnh PREVIOUS từ section-2 → section-1"

    def test_full_graph_total_edges(self, gen, exporter, five_node_fixture):
        belong_to, next_edges, prev_edges = gen.generate_all(five_node_fixture)
        all_edges = belong_to + next_edges + prev_edges
        graph = exporter.assemble(five_node_fixture, all_edges)
        assert graph["graph_metadata"]["total_nodes"] == 5
        assert graph["graph_metadata"]["total_edges"] == 8

    def test_no_self_loop_edges(self, gen, five_node_fixture):
        belong_to, next_edges, prev_edges = gen.generate_all(five_node_fixture)
        for edge in belong_to + next_edges + prev_edges:
            assert edge.source != edge.target, (
                f"Self-loop phát hiện: {edge.source} → {edge.target} ({edge.type})"
            )
