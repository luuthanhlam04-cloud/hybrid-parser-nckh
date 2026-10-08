"""
unicode_normalizer.py
=====================
Chuẩn hóa Unicode NFC cho văn bản pháp luật tiếng Việt.

Vấn đề cốt lõi:
  Tiếng Việt có thể được biểu diễn theo hai dạng Unicode:
    - NFC  (Precomposed): "Điều" = 4 code points  (ký tự ghép sẵn)
    - NFD  (Decomposed):  "Điều" = 6 code points  (ký tự + dấu tách biệt)

  Nếu văn bản trộn lẫn NFC và NFD, các regex anchor như `^Điều`, `^Chương`
  trong Module 2 sẽ KHÔNG khớp với phần NFD, gây mất cấu trúc hoàn toàn.

Giải pháp:
  Áp dụng `unicodedata.normalize('NFC', text)` cho mỗi dòng.
  Ghi log cảnh báo khi phát hiện đoạn văn có ký tự NFD bị trộn lẫn.
"""

from __future__ import annotations

import logging
import unicodedata

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Ngưỡng cảnh báo: tỷ lệ ký tự bị biến đổi trên tổng ký tự của dòng
# ---------------------------------------------------------------------------
_WARN_CHANGE_RATIO = 0.05  # Cảnh báo nếu > 5% ký tự bị thay đổi sau normalize


class UnicodeNormalizer:
    """
    Chuẩn hóa NFC toàn bộ danh sách dòng văn bản tiếng Việt.

    Sử dụng:
        normalizer = UnicodeNormalizer()
        normalized_lines = normalizer.normalize(lines)

    Thuộc tính sau khi chạy:
        stats (dict): Thống kê quá trình chuẩn hóa.
    """

    def __init__(self) -> None:
        self.stats: dict[str, int] = {
            "total_lines":    0,
            "lines_changed":  0,
            "chars_changed":  0,
        }

    def normalize(self, lines: list[str]) -> list[str]:
        """
        Áp dụng NFC normalization cho mỗi dòng.

        Args:
            lines: Danh sách dòng văn bản (đầu ra của TextCleaner).

        Returns:
            Danh sách dòng đã được chuẩn hóa NFC.
        """
        # Reset stats trước mỗi lần chạy
        self.stats = {"total_lines": 0, "lines_changed": 0, "chars_changed": 0}

        result: list[str] = []
        for idx, line in enumerate(lines):
            normalized, changed_chars = self._normalize_line(line)

            self.stats["total_lines"] += 1
            if normalized != line:
                self.stats["lines_changed"] += 1
                self.stats["chars_changed"] += changed_chars
                self._log_change(idx, line, changed_chars)

            result.append(normalized)

        self._log_summary()
        return result

    # ------------------------------------------------------------------
    # Chuẩn hóa một dòng
    # ------------------------------------------------------------------
    @staticmethod
    def _normalize_line(line: str) -> tuple[str, int]:
        """
        Chuẩn hóa NFC một dòng và đếm số ký tự bị thay đổi.

        Args:
            line: Dòng văn bản gốc.

        Returns:
            Tuple (dòng_đã_chuẩn_hóa, số_ký_tự_thay_đổi).
        """
        normalized = unicodedata.normalize("NFC", line)

        # Đếm ký tự bị thay đổi (so sánh code point)
        changed = sum(
            1 for a, b in zip(line, normalized) if a != b
        ) + abs(len(line) - len(normalized))

        return normalized, changed

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    def _log_change(self, line_idx: int, original: str, changed_chars: int) -> None:
        """Ghi log cảnh báo cho dòng bị biến đổi nhiều."""
        if not original:
            return

        ratio = changed_chars / max(len(original), 1)
        preview = original[:60].replace("\n", "\\n")

        if ratio >= _WARN_CHANGE_RATIO:
            logger.warning(
                "[UnicodeNormalizer] Dòng %d có %d ký tự NFD (%.1f%% tổng): '%s...'",
                line_idx, changed_chars, ratio * 100, preview,
            )
        else:
            logger.debug(
                "[UnicodeNormalizer] Dòng %d: chuẩn hóa %d ký tự.",
                line_idx, changed_chars,
            )

    def _log_summary(self) -> None:
        """Ghi log tổng kết sau khi hoàn tất."""
        s = self.stats
        if s["lines_changed"] == 0:
            logger.info(
                "[UnicodeNormalizer] Tất cả %d dòng đã là NFC — không cần thay đổi.",
                s["total_lines"],
            )
        else:
            logger.info(
                "[UnicodeNormalizer] Chuẩn hóa NFC: %d/%d dòng bị ảnh hưởng, "
                "%d ký tự được chuyển đổi.",
                s["lines_changed"], s["total_lines"], s["chars_changed"],
            )


# ---------------------------------------------------------------------------
# Hàm tiện ích độc lập (dùng nhanh mà không cần tạo instance)
# ---------------------------------------------------------------------------
def normalize_nfc(text: str) -> str:
    """
    Chuẩn hóa NFC một chuỗi văn bản đơn.

    Args:
        text: Chuỗi văn bản cần chuẩn hóa.

    Returns:
        Chuỗi đã chuẩn hóa NFC.
    """
    return unicodedata.normalize("NFC", text)


def is_nfc(text: str) -> bool:
    """
    Kiểm tra xem chuỗi đã là NFC chưa.

    Args:
        text: Chuỗi cần kiểm tra.

    Returns:
        True nếu chuỗi đã là NFC, False nếu có ký tự NFD/NFKD.
    """
    return unicodedata.is_normalized("NFC", text)
