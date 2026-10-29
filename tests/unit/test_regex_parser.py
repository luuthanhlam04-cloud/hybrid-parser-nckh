import pytest
import os
import sys
import tempfile

# Thêm src/regex_parser vào sys.path để fix lỗi import (vì code dùng import trực tiếp)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/regex_parser')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from parser import LegalParser
from regex_engine import NodeType
from src.preprocessing.document_loader import split_inline_point_markers

def create_temp_file(content: str) -> str:
    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
        f.write(content)
        return f.name

def test_hybrid_id_collision_prevention():
    text = "Điều 27. Test\nđ) Điểm đ thứ nhất\nđ) Điểm đ thứ hai\n"
    temp_path = create_temp_file(text)
        
    try:
        parser = LegalParser(law_prefix="doc", source_doc="test.txt")
        result = parser.parse_text(temp_path)
        nodes = result.nodes
        
        # Should have 3 nodes: ARTICLE, POINT, POINT
        assert len(nodes) == 3
        assert nodes[1]["type"] == NodeType.POINT.value
        assert nodes[1]["marker"] == "đ"
        assert nodes[2]["type"] == NodeType.POINT.value
        assert nodes[2]["marker"] == "đ"
        
        # Check that they have different suffixes (different char_start offsets)
        assert nodes[1]["id"] != nodes[2]["id"]
        assert "dieu-27_diem-dd" in nodes[1]["id"]
        assert "dieu-27_diem-dd" in nodes[2]["id"]
        
        # The parent id of both points should be exactly the article's id
        assert nodes[1]["parent_id"] == nodes[0]["id"]
        assert nodes[2]["parent_id"] == nodes[0]["id"]
    finally:
        os.remove(temp_path)


def test_inline_point_marker_is_split_without_losing_d_point():
    parts = split_inline_point_markers(
        "Thời hạn sử dụng đất; đ) Tiến độ sử dụng đất."
    )
    assert parts == [
        (None, "Thời hạn sử dụng đất;"),
        ("đ", "Tiến độ sử dụng đất."),
    ]


def test_point_position_resets_for_each_real_parent():
    text = (
        "Điều 1. Điều thứ nhất\n"
        "1. Khoản một\n"
        "a) Điểm a\n"
        "b) Điểm b\n"
        "Điều 2. Điều thứ hai\n"
        "1. Khoản một\n"
        "a) Điểm a\n"
        "b) Điểm b\n"
    )
    temp_path = create_temp_file(text)
    try:
        result = LegalParser(law_prefix="doc").parse_text(temp_path)
        positions = [
            node["position"] for node in result.nodes if node["type"] == "POINT"
        ]
        assert positions == [1, 2, 1, 2]
    finally:
        os.remove(temp_path)


def test_d_and_d_stroke_have_distinct_semantic_id_prefixes():
    text = "Điều 1. Test\n1. Khoản một\nd) Điểm d\nđ) Điểm đ\n"
    temp_path = create_temp_file(text)
    try:
        result = LegalParser(law_prefix="doc").parse_text(temp_path)
        points = [node for node in result.nodes if node["type"] == "POINT"]
        assert "diem-d_" in points[0]["id"]
        assert "diem-dd_" in points[1]["id"]
        assert points[0]["id"] != points[1]["id"]
    finally:
        os.remove(temp_path)

def test_hybrid_id_determinism():
    text = "Điều 27. Test\n1. Khoản 1\na) Điểm a\nText lơ lửng\n"
    temp_path = create_temp_file(text)
        
    try:
        parser1 = LegalParser(law_prefix="doc", source_doc="test.txt")
        result1 = parser1.parse_text(temp_path)
        
        parser2 = LegalParser(law_prefix="doc", source_doc="test.txt")
        result2 = parser2.parse_text(temp_path)
        
        # Extract just the IDs
        ids1 = [node["id"] for node in result1.nodes]
        ids2 = [node["id"] for node in result2.nodes]
        
        assert ids1 == ids2
    finally:
        os.remove(temp_path)
