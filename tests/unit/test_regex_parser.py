import pytest
from src.regex_parser import RegexParser, NodeType, LegalNode

def test_normal_hierarchy():
    text = "Điều 1. Phạm vi\n1. Quy định chung\na) Nội dung a\n"
    parser = RegexParser()
    nodes = parser.parse(text)
    
    assert len(nodes) == 3
    assert nodes[0].type == NodeType.ARTICLE
    assert nodes[0].id.startswith("article_1_p")
    assert nodes[1].type == NodeType.CLAUSE
    assert nodes[1].id.startswith("article_1_clause_1_p")
    assert nodes[1].parent_id == nodes[0].id
    assert nodes[2].type == NodeType.POINT
    assert nodes[2].id.startswith("article_1_clause_1_point_a_p")
    assert nodes[2].parent_id == nodes[1].id

def test_article_to_point_missing_clause():
    text = "Điều 2. Test\na) Điểm a\n"
    parser = RegexParser()
    nodes = parser.parse(text)
    
    assert len(nodes) == 2
    assert nodes[1].type == NodeType.POINT
    assert nodes[1].id.startswith("article_2_point_a_p")
    assert nodes[1].parent_id == nodes[0].id

def test_vietnamese_points():
    text = "Điều 3.\nđ) Điểm đ\nĐ) Điểm Đ\n"
    parser = RegexParser()
    nodes = parser.parse(text)
    
    assert len(nodes) == 3
    assert nodes[1].type == NodeType.POINT
    assert nodes[1].title == "đ)"
    assert nodes[2].type == NodeType.POINT
    assert nodes[2].title == "Đ)"

def test_multiple_points_on_same_line():
    text = "Điều 4.\na) Điểm a; b) Điểm b; đ) Điểm đ\n"
    parser = RegexParser()
    nodes = parser.parse(text)
    
    assert len(nodes) == 4
    assert nodes[1].type == NodeType.POINT
    assert nodes[1].title == "a)"
    assert nodes[2].type == NodeType.POINT
    assert nodes[2].title == "b)"
    assert nodes[3].type == NodeType.POINT
    assert nodes[3].title == "đ)"

def test_newline_preservation():
    text = "Điều 5. Test\nNội dung dòng 1\nNội dung dòng 2\n"
    parser = RegexParser()
    nodes = parser.parse(text)
    
    assert len(nodes) == 1
    assert nodes[0].type == NodeType.ARTICLE
    assert nodes[0].text == "Nội dung dòng 1\nNội dung dòng 2"
    assert nodes[0].id.startswith("article_5_p")

def test_orphan_node(caplog):
    text = "a) Điểm a mồ côi\n"
    parser = RegexParser()
    nodes = parser.parse(text)
    
    assert len(nodes) == 1
    assert nodes[0].type == NodeType.POINT
    assert nodes[0].parent_id is None
    assert "Orphan node detected" in caplog.text

def test_title_continuation():
    text = "Chương III\nQUYỀN VÀ NGHĨA VỤ\nĐiều 1.\n"
    parser = RegexParser()
    nodes = parser.parse(text)
    
    assert len(nodes) == 2
    assert nodes[0].type == NodeType.CHAPTER
    assert "QUYỀN VÀ NGHĨA VỤ" in nodes[0].title
    assert "Chương III" in nodes[0].title
    assert nodes[1].type == NodeType.ARTICLE

def test_floating_text():
    text = "Điều 1.\nText 1\n1.\nText 2\n"
    parser = RegexParser()
    nodes = parser.parse(text)
    
    assert len(nodes) == 2
    assert nodes[0].type == NodeType.ARTICLE
    assert nodes[0].text == "Text 1"
    assert nodes[1].type == NodeType.CLAUSE
    assert nodes[1].text == "Text 2"
    assert nodes[1].parent_id == nodes[0].id

def test_pydantic_validation():
    text = "Phần I\nĐiều 1.\n"
    parser = RegexParser()
    nodes = parser.parse(text)
    
    for node in nodes:
        LegalNode.model_validate(node.model_dump())

def test_hybrid_id_collision_prevention():
    text = "Điều 27. Test\nđ) Điểm đ thứ nhất\nđ) Điểm đ thứ hai\n"
    parser = RegexParser()
    nodes = parser.parse(text)
    
    assert len(nodes) == 3
    # Both points will be parsed as POINT nodes directly under ARTICLE
    assert nodes[1].type == NodeType.POINT
    assert nodes[1].title == "đ)"
    assert nodes[2].type == NodeType.POINT
    assert nodes[2].title == "đ)"
    
    # Check that they have the exact same prefix but different suffixes
    assert nodes[1].id != nodes[2].id
    assert nodes[1].id.startswith("article_27_point_đ_p")
    assert nodes[2].id.startswith("article_27_point_đ_p")

def test_hybrid_id_determinism():
    text = "Điều 27. Test\n1. Khoản 1\na) Điểm a\nText lơ lửng\n"
    parser1 = RegexParser()
    nodes1 = parser1.parse(text)
    
    parser2 = RegexParser()
    nodes2 = parser2.parse(text)
    
    # Extract just the IDs
    ids1 = [node.id for node in nodes1]
    ids2 = [node.id for node in nodes2]
    
    assert ids1 == ids2
