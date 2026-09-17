import pytest
from src.preprocessing.formatter import Formatter, _RE_DIEM, _RE_KHOAN, _is_structural

class TestFormatter:
    def test_re_diem_vietnamese_characters(self):
        """Kiểm tra Regex có bắt được chính xác các chữ cái đánh Điểm trong tiếng Việt không."""
        # Danh sách các chữ cái thường gặp trong văn bản luật VN (bao gồm đ, k, e, g)
        valid_markers = ["a", "b", "c", "d", "đ", "e", "g", "h", "i", "k", "l", "m", "n", "o", "p", "q", "x", "y"]
        
        for marker in valid_markers:
            line = f"{marker}) Đây là nội dung điểm {marker}."
            assert _RE_DIEM.match(line) is not None, f"Lỗi: Không bắt được điểm {marker})"
            assert _is_structural(line) is True, f"Lỗi: Không nhận diện được cấu trúc điểm {marker})"

    def test_re_diem_with_indentation(self):
        """Kiểm tra khả năng bắt điểm khi có khoảng trắng thụt lề đầu dòng."""
        lines_with_spaces = [
            "   đ) Điểm đ bị thụt lề 3 spaces",
            "\tk) Điểm k bị thụt lề 1 tab",
            " o) Điểm o có 1 space"
        ]
        for line in lines_with_spaces:
            assert _RE_DIEM.match(line) is not None
            assert _is_structural(line) is True

    def test_formatter_clean_and_newline(self):
        """Kiểm tra Pipeline làm sạch và định dạng lại dòng trống của Formatter."""
        formatter = Formatter()
        raw_lines = [
            "Điều 26. Quyền chung",
            "  1. Được cấp Giấy chứng nhận.",
            "  đ) Nội dung của điểm đ bị dính liền.",
            "",
            "   ",
            "k) Nội dung của điểm k cách điểm đ nhiều dòng rỗng."
        ]
        
        formatted = formatter.format(raw_lines)
        
        expected = (
            "Điều 26. Quyền chung\n"
            "\n"
            "1. Được cấp Giấy chứng nhận.\n"
            "\n"
            "đ) Nội dung của điểm đ bị dính liền.\n"
            "\n"
            "k) Nội dung của điểm k cách điểm đ nhiều dòng rỗng.\n"
        )
        assert formatted == expected
