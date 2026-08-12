"""
text_cleaner.py
===============
Làm sạch nhiễu trong văn bản pháp luật tiếng Việt đã được tải:

  1. Xóa số trang / header / footer (VD: "Trang 3/15", "15", "---Page 3---").
  2. Loại bỏ ký tự vô hình: zero-width space, BOM, soft-hyphen, form feed, ...
  3. Chuẩn hóa khoảng trắng CỪng dòng: tab → space, nhiều space → một space.
  4. Xử lý Dangling Clauses: dòng treo chỉ có "1." hoặc "a)" → merge
     với dòng text liền kề phía dưới.

⚠️  TUYỆT ĐỐI KHÔNG gộp dòng / thay \\n bằng space — ranh giới dòng
     là nền tảng để Regex của Module 2 hoạt động đúng.
"""

from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Ký tự vô hình / điều khiển cần xóa
# ---------------------------------------------------------------------------
_INVISIBLE_CHARS = re.compile(
    r"[\u200b\u200c\u200d\u200e\u200f"   # zero-width spaces
    r"\u00ad"                             # soft hyphen
    r"\ufeff"                             # BOM
    r"\x0c"                               # form feed (^L)
    r"\x0b"                               # vertical tab
    r"\x00-\x08\x0e-\x1f\x7f]"           # các ký tự điều khiển khác
)

# ---------------------------------------------------------------------------
# Pattern nhận diện số trang / header / footer
# ---------------------------------------------------------------------------
# "Trang 3/15" hoặc "trang 3/15"
_PAGE_MARKER_PATTERN = re.compile(
    r"^\s*[Tt]rang\s+\d+\s*/\s*\d+\s*$"
)
# "---Page 3---" hoặc "--- Page 3 ---"
_PAGE_DASH_PATTERN = re.compile(
    r"^\s*-{2,}\s*[Pp]age\s+\d+\s*-{2,}\s*$"
)
# Dòng chỉ chứa số thuần (số trang đứng riêng) — VD: "15"
# KHÔNG xóa nếu có dấu "." hoặc ")" vì đó là khoản/điểm
_BARE_NUMBER_PATTERN = re.compile(
    r"^\s*\d+\s*$"
)

# Chữ ký số / Metadata Header của Cổng thông tin điện tử / Công báo
_DIGITAL_SIGNATURE_PATTERN = re.compile(
    r"^\s*(Người ký:|Email:.*?Cơ quan:|CÔNG BÁO/Số).*$", 
    flags=re.IGNORECASE
)

# ---------------------------------------------------------------------------
# Pattern nhận diện "Dangling Clause" (dòng treo)
# Dòng chỉ chứa đúng một ký hiệu khoản/điểm, không có text theo sau.
# VD: "1." | "a)" | "12." | "đ)"
# ---------------------------------------------------------------------------
_DANGLING_CLAUSE = re.compile(
    r"^\s*(?:\d+\.|[a-zđA-ZĐ]\))\s*$"
)

# ---------------------------------------------------------------------------
# Khoảng trắng trong dòng (tab + nhiều space → 1 space)
# KHÔNG dùng re.MULTILINE vì chỉ xử lý từng dòng riêng lẻ
# ---------------------------------------------------------------------------
_MULTI_SPACE = re.compile(r"[ \t]+")


class TextCleaner:
    """
    Làm sạch danh sách các dòng văn bản.

    Sử dụng:
        cleaner = TextCleaner()
        clean_lines = cleaner.clean(raw_lines)
    """

    def clean(self, lines: list[str]) -> list[str]:
        """
        Pipeline làm sạch chính.

        Args:
            lines: Danh sách dòng thô từ document_loader.

        Returns:
            Danh sách dòng đã làm sạch, thứ tự và ranh giới được bảo toàn.
        """
        # Bước 1: Làm sạch từng dòng riêng lẻ (KHÔNG join dòng)
        processed: list[str] = [self._clean_single_line(line) for line in lines]

        # Bước 2: Xử lý Dangling Clauses (cần nhìn sang dòng kế tiếp)
        processed = self._merge_dangling_clauses(processed)

        # Bước 3: Xóa số trang (dòng số trơn)
        processed = self._remove_page_numbers(processed)

        total_removed = len(lines) - len(processed)
        if total_removed > 0:
            logger.info("[TextCleaner] Đã xóa %d dòng nhiễu.", total_removed)

        return processed

    # ------------------------------------------------------------------
    # Làm sạch từng dòng — KHÔNG thay đổi ranh giới dòng
    # ------------------------------------------------------------------
    def _clean_single_line(self, line: str) -> str:
        """
        Làm sạch một dòng đơn lẻ:
          - Xóa ký tự vô hình / điều khiển
          - Chuẩn hóa khoảng trắng TRONG dòng (tab + multi-space → 1 space)
          - Strip đầu/cuối

        ⚠️ Không được thay \\n, không join dòng.
        """
        # Xóa ký tự vô hình
        line = _INVISIBLE_CHARS.sub("", line)

        # Tab và nhiều space liên tiếp → 1 space (chỉ trong dòng)
        line = _MULTI_SPACE.sub(" ", line)

        return line.strip()

    # ------------------------------------------------------------------
    # Xử lý Dangling Clauses
    # ------------------------------------------------------------------
    @staticmethod
    def _merge_dangling_clauses(lines: list[str]) -> list[str]:
        """
        Phát hiện "dòng treo" — dòng chỉ có ký hiệu khoản/điểm như "1." hoặc "a)"
        không có nội dung — rồi gộp với dòng text ngay phía dưới.

        Ví dụ:
            Input:  ["1.", "", "Được cấp Giấy chứng nhận..."]
            Output: ["1. Được cấp Giấy chứng nhận..."]

        Thuật toán: index-based loop để kiểm soát con trỏ chính xác,
        tránh nhập nhằng khi có dòng trống xen giữa.
        """
        result: list[str] = []
        skip: set[int] = set()  # Tập hợp index đã được merge (cần bỏ qua)

        i = 0
        while i < len(lines):
            if i in skip:
                i += 1
                continue

            line = lines[i]

            if _DANGLING_CLAUSE.match(line):
                # Tìm dòng text không rỗng tiếp theo (bỏ qua dòng trống ở giữa)
                found = _find_next_non_empty(lines, i + 1)
                if found is not None:
                    next_idx, next_line = found
                    # Gộp: "<nhãn> <nội dung>"
                    merged = f"{line.strip()} {next_line.strip()}"
                    result.append(merged)
                    logger.debug(
                        "[TextCleaner] Merge dangling clause tại dòng %d: '%s' + '%s'",
                        i, line.strip(), next_line[:40],
                    )
                    # Thêm các dòng trống xen giữa vào kết quả để giữ spacing
                    for gap_i in range(i + 1, next_idx):
                        result.append(lines[gap_i])
                    # Đánh dấu next_idx để bỏ qua (đã được merge)
                    skip.add(next_idx)
                else:
                    # Không tìm thấy dòng text tiếp → giữ nguyên dòng treo
                    result.append(line)
            else:
                result.append(line)

            i += 1

        return result

    # ------------------------------------------------------------------
    # Xóa số trang (dòng số trơn)
    # ------------------------------------------------------------------
    @staticmethod
    def _remove_page_numbers(lines: list[str]) -> list[str]:
        """
        Xóa các dòng được nhận diện là số trang và header:
          - "Trang 3/15" (có hoặc không có khoảng trắng)
          - "---Page 3---"
          - Dòng chỉ chứa số thuần (ví dụ: "15") — số trang đứng riêng lẻ
          - Header chữ ký số của Cổng thông tin điện tử / Công báo

        ⚠️ KHÔNG xóa dòng có dạng "1." hoặc "a)" — đây là khoản/điểm (đã
           được xử lý bởi _merge_dangling_clauses ở bước trước).
        """
        result: list[str] = []
        for line in lines:
            if (
                _PAGE_MARKER_PATTERN.match(line)
                or _PAGE_DASH_PATTERN.match(line)
                or _BARE_NUMBER_PATTERN.match(line)
                or _DIGITAL_SIGNATURE_PATTERN.match(line)
            ):
                logger.debug("[TextCleaner] Xóa dòng nhiễu: '%s'", line)
                continue
            result.append(line)
        return result


# ---------------------------------------------------------------------------
# Hàm trợ giúp nội bộ
# ---------------------------------------------------------------------------
def _find_next_non_empty(
    lines: list[str], start: int
) -> tuple[int, str] | None:
    """
    Tìm dòng không rỗng đầu tiên trong lines bắt đầu từ chỉ số start.

    Returns:
        Tuple (index, line) hoặc None nếu không tìm thấy.
    """
    for i in range(start, len(lines)):
        if lines[i].strip():
            return i, lines[i]
    return None
