"""
Unit Tests cho Module 3 - Validation Engine.
Giả lập các node bị lỗi: Trùng ID, Orphan, BrokenParent, Cyclic,
Missing Khoản 2, Missing Điểm c, EmptyNode.
"""
import pytest
from src.validation.schema_validator import LegalNode
from src.validation.validator import ValidationEngine
from src.validation.integrity_checker import check_integrity
from src.validation.sequence_checker import check_sequences


def _make_node(
    node_id: str,
    node_type: str,
    text: str = "nội dung",
    parent_id: str = None,
    title: str = None,
    start: int = 0,
    end: int = 100,
) -> LegalNode:
    """Helper: tạo LegalNode nhanh cho test."""
    return LegalNode(
        id=node_id,
        type=node_type,
        depth=0,
        title=title,
        text=text,
        parent_id=parent_id,
        children_count=0,
        position=0,
        number=None,
        marker=None,
        law_prefix="test",
        law_code=None,
        source_doc="test.txt",
        word_style=None,
        start_idx=start,
        end_idx=end,
        implicit_parent=False,
    )


# ============================================================
# INTEGRITY TESTS
# ============================================================

class TestDuplicateNodeID:
    def test_duplicate_id_detected(self):
        nodes = [
            _make_node("article_1_p0", "ARTICLE", start=0, end=50),
            _make_node("article_1_p0", "ARTICLE", start=50, end=100),
        ]
        issues = check_integrity(nodes)
        dup_issues = [i for i in issues if i["issue_type"] == "DuplicateNodeID"]
        assert len(dup_issues) == 1
        assert dup_issues[0]["severity"] == "ERROR"
        assert dup_issues[0]["node_id"] == "article_1_p0"

    def test_no_duplicate_when_unique(self):
        nodes = [
            _make_node("article_1_p0", "ARTICLE", start=0, end=50),
            _make_node("article_2_p50", "ARTICLE", start=50, end=100),
        ]
        issues = check_integrity(nodes)
        dup_issues = [i for i in issues if i["issue_type"] == "DuplicateNodeID"]
        assert len(dup_issues) == 0


class TestOrphanNode:
    def test_orphan_point_detected(self):
        nodes = [
            _make_node("article_1_point_a_p0", "POINT", parent_id=None, start=0),
        ]
        issues = check_integrity(nodes)
        orphan_issues = [i for i in issues if i["issue_type"] == "OrphanNode"]
        assert len(orphan_issues) == 1
        assert orphan_issues[0]["severity"] == "ERROR"

    def test_chapter_root_is_not_orphan(self):
        """CHAPTER cho phép parent_id = None (top-level)."""
        nodes = [
            _make_node("chapter_I_p0", "CHAPTER", parent_id=None, start=0),
        ]
        issues = check_integrity(nodes)
        orphan_issues = [i for i in issues if i["issue_type"] == "OrphanNode"]
        assert len(orphan_issues) == 0

    def test_text_root_is_not_orphan(self):
        """TEXT cho phép parent_id = None (preamble text)."""
        nodes = [
            _make_node("orphan_text_p0", "TEXT", parent_id=None, start=0),
        ]
        issues = check_integrity(nodes)
        orphan_issues = [i for i in issues if i["issue_type"] == "OrphanNode"]
        assert len(orphan_issues) == 0


class TestBrokenParent:
    def test_broken_parent_detected(self):
        nodes = [
            _make_node("article_1_p0", "ARTICLE", parent_id=None, start=0),
            _make_node(
                "article_1_clause_1_p50", "CLAUSE",
                parent_id="non_existent_parent_p999", start=50,
            ),
        ]
        issues = check_integrity(nodes)
        broken = [i for i in issues if i["issue_type"] == "BrokenParent"]
        assert len(broken) == 1
        assert broken[0]["severity"] == "ERROR"
        assert "non_existent_parent_p999" in broken[0]["message"]


class TestCyclicDependency:
    def test_cycle_detected(self):
        """A -> B -> A => cycle."""
        nodes = [
            _make_node("node_a_p0", "ARTICLE", parent_id="node_b_p50", start=0),
            _make_node("node_b_p50", "CLAUSE", parent_id="node_a_p0", start=50),
        ]
        issues = check_integrity(nodes)
        cycle_issues = [i for i in issues if i["issue_type"] == "CyclicDependency"]
        assert len(cycle_issues) >= 1
        assert cycle_issues[0]["severity"] == "ERROR"


class TestEmptyNode:
    def test_empty_clause_detected(self):
        """CLAUSE rỗng text -> WARNING."""
        nodes = [
            _make_node(
                "article_1_clause_1_p0", "CLAUSE", text="",
                parent_id="article_1_p0", start=0,
            ),
        ]
        issues = check_integrity(nodes)
        empty = [i for i in issues if i["issue_type"] == "EmptyNode"]
        assert len(empty) == 1
        assert empty[0]["severity"] == "WARNING"

    def test_empty_chapter_not_flagged(self):
        """CHAPTER/SECTION/ARTICLE rỗng text -> KHÔNG bị cảnh báo."""
        nodes = [
            _make_node("chapter_I_p0", "CHAPTER", text="", parent_id=None, start=0),
            _make_node("section_1_p50", "SECTION", text="", parent_id="chapter_I_p0", start=50),
            _make_node("article_1_p100", "ARTICLE", text="", parent_id="section_1_p50", start=100),
        ]
        issues = check_integrity(nodes)
        empty = [i for i in issues if i["issue_type"] == "EmptyNode"]
        assert len(empty) == 0


# ============================================================
# SEQUENCE TESTS
# ============================================================

class TestGapIndexClause:
    def test_missing_clause_2(self):
        """Khoản 1, 3, 4 -> Missing Khoản 2."""
        nodes = [
            _make_node(
                "article_45_p0", "ARTICLE",
                parent_id=None, title="Điều 45.", start=0,
            ),
            _make_node(
                "article_45_clause_1_p10", "CLAUSE",
                parent_id="article_45_p0", title="1.", start=10,
            ),
            _make_node(
                "article_45_clause_3_p30", "CLAUSE",
                parent_id="article_45_p0", title="3.", start=30,
            ),
            _make_node(
                "article_45_clause_4_p40", "CLAUSE",
                parent_id="article_45_p0", title="4.", start=40,
            ),
        ]
        issues = check_sequences(nodes)
        gap_issues = [i for i in issues if i["issue_type"] == "GapIndex"]
        assert len(gap_issues) == 1
        assert "clause_2" in gap_issues[0]["message"]
        assert gap_issues[0]["severity"] == "WARNING"


class TestGapIndexPoint:
    def test_missing_point_c(self):
        """Điểm a, b, d, đ -> Missing Điểm c."""
        parent = "article_45_clause_1_p10"
        nodes = [
            _make_node(
                "article_45_clause_1_point_a_p20", "POINT",
                parent_id=parent, title="a)", start=20,
            ),
            _make_node(
                "article_45_clause_1_point_b_p30", "POINT",
                parent_id=parent, title="b)", start=30,
            ),
            _make_node(
                "article_45_clause_1_point_d_p40", "POINT",
                parent_id=parent, title="d)", start=40,
            ),
            _make_node(
                "article_45_clause_1_point_đ_p50", "POINT",
                parent_id=parent, title="đ)", start=50,
            ),
        ]
        issues = check_sequences(nodes)
        gap_issues = [i for i in issues if i["issue_type"] == "GapIndex"]
        assert len(gap_issues) == 1
        assert "point_c" in gap_issues[0]["message"]

    def test_vn_alphabet_d_đ_no_gap(self):
        """a, b, c, d, đ liên tiếp -> KHÔNG có gap."""
        parent = "article_1_clause_1_p10"
        nodes = [
            _make_node("p_a", "POINT", parent_id=parent, title="a)", start=20),
            _make_node("p_b", "POINT", parent_id=parent, title="b)", start=30),
            _make_node("p_c", "POINT", parent_id=parent, title="c)", start=40),
            _make_node("p_d", "POINT", parent_id=parent, title="d)", start=50),
            _make_node("p_đ", "POINT", parent_id=parent, title="đ)", start=60),
        ]
        issues = check_sequences(nodes)
        gap_issues = [i for i in issues if i["issue_type"] == "GapIndex"]
        assert len(gap_issues) == 0


# ============================================================
# ORCHESTRATOR / FILTERING TESTS
# ============================================================

class TestValidationEngine:
    def test_error_nodes_filtered_out(self):
        """Node bị ERROR phải bị loại khỏi validated_nodes."""
        engine = ValidationEngine()
        nodes = [
            _make_node("chapter_I_p0", "CHAPTER", parent_id=None, start=0),
            _make_node("article_1_p50", "ARTICLE", parent_id="chapter_I_p0", start=50),
            # Orphan POINT -> sẽ bị lọc
            _make_node("point_orphan_p100", "POINT", parent_id=None, start=100),
            # BrokenParent -> sẽ bị lọc
            _make_node(
                "clause_broken_p150", "CLAUSE",
                parent_id="non_existent_p999", start=150,
            ),
        ]
        validated, report = engine.validate_nodes(nodes)

        # 2 node ERROR bị loại
        assert len(validated) == 2
        validated_ids = {n.id for n in validated}
        assert "point_orphan_p100" not in validated_ids
        assert "clause_broken_p150" not in validated_ids

        # Report phản ánh đúng
        assert report["summary"]["fatal_errors_count"] == 2
        assert report["summary"]["total_nodes_validated"] == 2

    def test_warning_nodes_kept(self):
        """Node dính WARNING (EmptyNode) vẫn phải ở trong validated_nodes."""
        engine = ValidationEngine()
        nodes = [
            _make_node("chapter_I_p0", "CHAPTER", parent_id=None, start=0),
            _make_node(
                "article_1_p50", "ARTICLE",
                parent_id="chapter_I_p0", start=50,
            ),
            _make_node(
                "article_1_clause_1_p100", "CLAUSE", text="",
                parent_id="article_1_p50", title="1.", start=100,
            ),
        ]
        validated, report = engine.validate_nodes(nodes)

        assert len(validated) == 3
        assert report["summary"]["warnings_count"] >= 1
        assert report["summary"]["fatal_errors_count"] == 0

    def test_integrity_score_calculation(self):
        """Kiểm tra công thức score = (1 - errors/total) * 100."""
        engine = ValidationEngine()
        nodes = [
            _make_node("chapter_I_p0", "CHAPTER", parent_id=None, start=0),
            _make_node("article_1_p50", "ARTICLE", parent_id="chapter_I_p0", start=50),
            _make_node("article_2_p100", "ARTICLE", parent_id="chapter_I_p0", start=100),
            # 1 orphan ERROR
            _make_node("orphan_clause_p200", "CLAUSE", parent_id=None, start=200),
        ]
        _, report = engine.validate_nodes(nodes)

        # 1 error / 4 total => (1 - 0.25) * 100 = 75.0
        assert report["summary"]["structural_integrity_score"] == 75.0

    def test_deterministic_output(self):
        """Chạy 2 lần với cùng input -> kết quả giống hệt nhau."""
        engine = ValidationEngine()
        nodes = [
            _make_node("chapter_I_p0", "CHAPTER", parent_id=None, start=0),
            _make_node("article_1_p50", "ARTICLE", parent_id="chapter_I_p0", start=50),
            _make_node(
                "article_1_clause_1_p100", "CLAUSE",
                parent_id="article_1_p50", title="1.", start=100,
            ),
        ]
        validated1, report1 = engine.validate_nodes(nodes)
        validated2, report2 = engine.validate_nodes(nodes)

        assert [n.id for n in validated1] == [n.id for n in validated2]
        assert report1["summary"] == report2["summary"]

    def test_cascading_quarantine(self):
        """Khi Khoản 1 bị orphan ERROR -> Điểm a, Điểm b con cũng bị cascade xóa."""
        engine = ValidationEngine()
        nodes = [
            _make_node("chapter_I_p0", "CHAPTER", parent_id=None, start=0),
            _make_node("article_1_p50", "ARTICLE", parent_id="chapter_I_p0", start=50),
            # Khoản 1 là Orphan (CLAUSE with parent_id=None) -> ERROR
            _make_node(
                "article_1_clause_1_p100", "CLAUSE",
                parent_id=None, title="1.", start=100,
            ),
            # Điểm a, Điểm b là con của Khoản 1 -> sẽ bị cascade xóa
            _make_node(
                "article_1_clause_1_point_a_p150", "POINT",
                parent_id="article_1_clause_1_p100", title="a)", start=150,
            ),
            _make_node(
                "article_1_clause_1_point_b_p200", "POINT",
                parent_id="article_1_clause_1_p100", title="b)", start=200,
            ),
        ]
        validated, report = engine.validate_nodes(nodes)

        validated_ids = {n.id for n in validated}
        # Khoản 1 bị loại vì OrphanNode
        assert "article_1_clause_1_p100" not in validated_ids
        # Điểm a, b cũng bị cascade loại
        assert "article_1_clause_1_point_a_p150" not in validated_ids
        assert "article_1_clause_1_point_b_p200" not in validated_ids
        # Chỉ còn Chapter + Article
        assert len(validated) == 2
        # 3 errors total: 1 orphan + 2 cascading BrokenParent
        assert report["summary"]["fatal_errors_count"] == 3

    def test_sequence_checker_ignores_text_nodes(self):
        """TEXT nodes lơ lửng giữa các CLAUSE không gây nhầm lẫn sequence check."""
        engine = ValidationEngine()
        nodes = [
            _make_node("chapter_I_p0", "CHAPTER", parent_id=None, start=0),
            _make_node(
                "article_1_p50", "ARTICLE",
                parent_id="chapter_I_p0", title="Điều 1.", start=50,
            ),
            _make_node(
                "article_1_clause_1_p100", "CLAUSE",
                parent_id="article_1_p50", title="1.", start=100,
            ),
            # TEXT lơ lửng giữa Khoản 1 và Khoản 2
            _make_node(
                "article_1_text_p150", "TEXT",
                parent_id="article_1_p50", start=150,
            ),
            _make_node(
                "article_1_clause_2_p200", "CLAUSE",
                parent_id="article_1_p50", title="2.", start=200,
            ),
        ]
        validated, report = engine.validate_nodes(nodes)

        # Không có GapIndex vì 1 -> 2 là liên tiếp (TEXT bị bỏ qua)
        gap_issues = [i for i in report["issues"] if i["issue_type"] == "GapIndex"]
        assert len(gap_issues) == 0
