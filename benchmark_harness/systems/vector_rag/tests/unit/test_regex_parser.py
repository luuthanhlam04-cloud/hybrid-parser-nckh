import pytest
import os
import sys
import tempfile

# Thêm src/regex_parser vào sys.path để fix lỗi import (vì code dùng import trực tiếp)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/regex_parser')))

from parser import LegalParser
from regex_engine import NodeType

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
        assert "dieu-27_diem-d" in nodes[1]["id"]
        assert "dieu-27_diem-d" in nodes[2]["id"]
        
        # The parent id of both points should be exactly the article's id
        assert nodes[1]["parent_id"] == nodes[0]["id"]
        assert nodes[2]["parent_id"] == nodes[0]["id"]
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
