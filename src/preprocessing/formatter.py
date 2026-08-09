"""
formatter.py
============
Định dạng lại văn bản pháp luật đã làm sạch để Module 2 (Regex Parser)
có thể nhận diện cấu trúc chính xác.

Các đảm bảo cốt lõi:
  1. Mỗi phần tử cấu trúc (Chương, Mục, Điều, Khoản, Điểm) bắt đầu trên
     dòng riêng — regex anchor `^` sẽ luôn khớp.
  2. Gọi `.strip()` trên mỗi dòng TRƯỚC khi nhận diện cấu trúc — xử lý
     khoảng trắng thụt lề do Pandoc sinh ra (Edge Case #1).
  3. Pattern nhận diện dùng `^\s*` (vẫn bắt được dù chưa strip) và
     `[a-zđ]` thay vì `[a-đ]` để bắt đầy đủ bảng chữ cái Việt (Edge Case #2).
  4. Gộp 3+ dòng trống liên tiếp xuống còn tối đa 1 dòng trống.
  5. Đầu ra kết thúc bằng đúng một ký tự `\\n`.
"""

from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Pattern nhận diện các phần tử cấu trúc pháp luật Việt Nam
#
# ⚠️  Quy tắc quan trọng:
#   - Dùng ^\s* thay vì ^ để bắt được dù Pandoc có thêm thụt lề hay không.
#   - Dùng [a-zđ] (bao gồm đ) thay vì [a-đ] để tránh lỗi bảng mã Unicode
#     và bắt được m, n, p, q... (các điểm cấp sâu trong văn bản thực tế).
# ---------------------------------------------------------------------------

# Cấp 1: Chương  — VD: "Chương III", "CHƯƠNG III"
_RE_CHUONG = re.compile(
    r"^\s*(?:Chương|CHƯƠNG)\s+\S+",
    re.UNICODE,
)

# Cấp 2: Mục  — VD: "Mục 1", "MỤC 1"
_RE_MUC = re.compile(
    r"^\s*(?:Mục|MỤC)\s+\S+",
    re.UNICODE,
)

# Cấp 3: Điều  — VD: "Điều 26.", "ĐIỀU 26."
_RE_DIEU = re.compile(
    r"^\s*(?:Điều|ĐIỀU)\s+\d+",
    re.UNICODE,
)

# Cấp 4: Khoản  — VD: "1.", "12."
# Chỉ nhận diện nếu có text sau dấu chấm (không phải dòng treo — đã xử lý ở TextCleaner)
_RE_KHOAN = re.compile(
    r"^\s*\d+\.\s+\S",
    re.UNICODE,
)

# Cấp 5: Điểm  — VD: "a)", "b)", "đ)", "m)", "n)"
# [a-zđ]: bắt toàn bộ chữ thường ASCII + ký tự đ của tiếng Việt
_RE_DIEM = re.compile(
    r"^\s*[a-zđ]\)\s+\S",
    re.UNICODE,
)

# Tổng hợp: danh sách các pattern phân tách dòng theo thứ tự ưu tiên
_STRUCTURAL_PATTERNS: list[re.Pattern] = [
    _RE_CHUONG,
    _RE_MUC,
    _RE_DIEU,
    _RE_KHOAN,
    _RE_DIEM,
]


def _is_structural(line: str) -> bool:
    """Kiểm tra xem dòng (sau khi strip) có phải phần tử cấu trúc không."""
    return any(pat.match(line) for pat in _STRUCTURAL_PATTERNS)


class Formatter:
    """
    Định dạng lại danh sách dòng văn bản thành chuỗi cuối cùng.

    Sử dụng:
        formatter = Formatter()
        clean_text = formatter.format(lines)
    """

    def format(self, lines: list[str]) -> str:
        """
        Định dạng danh sách dòng thành văn bản pháp luật sạch.

        Pipeline:
          1. Strip từng dòng (loại bỏ thụt lề Pandoc).
          2. Đảm bảo phần tử cấu trúc bắt đầu trên dòng riêng.
          3. Gộp nhiều dòng trống liên tiếp.
          4. Trim đầu/cuối toàn văn bản.
          5. Kết thúc bằng đúng một ký tự \\n.

        Args:
            lines: Danh sách dòng sau khi đã làm sạch và chuẩn hóa Unicode.

        Returns:
            Chuỗi văn bản thuần UTF-8 đã định dạng, kết thúc bằng \\n.
        """
        # Bước 1: Strip từng dòng — xử lý thụt lề do Pandoc sinh ra
        stripped = [line.strip() for line in lines]

        # Bước 2: Đảm bảo mỗi phần tử cấu trúc bắt đầu trên dòng riêng
        separated = self._ensure_structural_newlines(stripped)

        # Bước 3: Gộp nhiều dòng trống liên tiếp (≥ 2 dòng trống → 1 dòng trống)
        collapsed = self._collapse_blank_lines(separated)

        # Bước 4 & 5: Join, trim và đảm bảo kết thúc bằng đúng 1 ký tự \n
        text = "\n".join(collapsed)
        text = text.strip()
        text = text + "\n"

        logger.info(
            "[Formatter] Hoàn tất: %d dòng đầu vào → %d ký tự đầu ra.",
            len(lines), len(text),
        )
        return text

    # ------------------------------------------------------------------
    # Bước 2: Đảm bảo phần tử cấu trúc trên dòng riêng
    # ------------------------------------------------------------------
    @staticmethod
    def _ensure_structural_newlines(lines: list[str]) -> list[str]:
        """
        Duyệt từng dòng, nếu phát hiện phần tử cấu trúc bị dính liền với
        dòng trước (không có dòng trống ngăn cách), thêm dòng trống phân tách.

        Trường hợp này xảy ra khi Pandoc không xuống dòng trước Khoản/Điểm
        nhưng vẫn thụt lề bằng khoảng trắng (đã được strip ở bước trên).

        Ví dụ đầu vào:
            ["Điều 26. Quyền chung...", "1. Được cấp Giấy...", "2. Hưởng thành quả..."]

        Đầu ra (thêm dòng trống trước "1." và "2." nếu dòng trước không trống):
            ["Điều 26. Quyền chung...", "", "1. Được cấp Giấy...", "", "2. Hưởng thành quả..."]

        Lưu ý: Formatter không xóa hay merge dòng — chỉ THÊM dòng trống khi cần.
        """
        result: list[str] = []
        for i, line in enumerate(lines):
            if line and _is_structural(line):
                # Nếu dòng trước không trống và không phải dòng trống, thêm separator
                if result and result[-1] != "":
                    result.append("")
                    logger.debug(
                        "[Formatter] Thêm dòng trống trước phần tử cấu trúc: '%s'",
                        line[:50],
                    )
            result.append(line)
        return result

    # ------------------------------------------------------------------
    # Bước 3: Gộp dòng trống liên tiếp
    # ------------------------------------------------------------------
    @staticmethod
    def _collapse_blank_lines(lines: list[str]) -> list[str]:
        """
        Gộp 2+ dòng trống liên tiếp xuống còn đúng 1 dòng trống.

        Ví dụ:
            ["Điều 26.", "", "", "", "1. Được cấp..."]
            → ["Điều 26.", "", "1. Được cấp..."]
        """
        result: list[str] = []
        prev_blank = False

        for line in lines:
            is_blank = line.strip() == ""
            if is_blank:
                if not prev_blank:
                    result.append("")
                prev_blank = True
            else:
                result.append(line)
                prev_blank = False

        return result
