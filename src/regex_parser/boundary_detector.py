# -*- coding: utf-8 -*-
"""
boundary_detector.py — Module 2: Regex Parser
Xác định ranh giới (start / end) của từng Legal Node.

Đây là bài toán RIÊNG với nhận diện marker:
  - Regex Engine → tìm điểm BẮT ĐẦU của node
  - Boundary Detector → tìm điểm KẾT THÚC của node

Ví dụ thực tế [CORPUS: Ch3-LDD]:
  a) Cá nhân được nhận chuyển đổi...    ← bắt đầu
     ...tiếp tục sang dòng tiếp theo... ← vẫn thuộc Điểm a
     ...và dòng tiếp theo nữa...
  b) Tổ chức kinh tế...                 ← bắt đầu node mới → Điểm a kết thúc

Boundary = "node kết thúc khi gặp marker cùng cấp hoặc cấp cao hơn".
"""

from dataclasses import dataclass, field
from typing import Optional
from regex_engine import MatchResult, NodeType


# ---------------------------------------------------------------------------
# Boundary — ranh giới vật lý của một node trong danh sách input
# ---------------------------------------------------------------------------
@dataclass
class Boundary:
    match: MatchResult       # Match result tại điểm bắt đầu
    start_idx: int           # Index bắt đầu trong danh sách input (inclusive)
    end_idx: int             # Index kết thúc (exclusive) — chưa biết khi tạo
    content_lines: list[str] = field(default_factory=list)  # Các dòng thuộc node này

    @property
    def node_type(self) -> NodeType:
        return self.match.node_type

    @property
    def raw_text(self) -> str:
        return self.match.raw_text

    @property
    def full_content(self) -> str:
        """Toàn bộ nội dung của node (dòng đầu + content_lines)."""
        all_lines = [self.raw_text] + self.content_lines
        return "\n".join(line for line in all_lines if line.strip())

    @property
    def body_text(self) -> str:
        """
        Nội dung BODY — không bao gồm dòng header (marker + title).
        Dùng cho CLAUSE và POINT khi cần lấy nội dung thuần.
        """
        return "\n".join(line for line in self.content_lines if line.strip())


# ---------------------------------------------------------------------------
# BoundaryDetector
# ---------------------------------------------------------------------------
class BoundaryDetector:
    """
    Xác định ranh giới của các Legal Node từ danh sách MatchResult.

    Logic cốt lõi:
      - Node bắt đầu tại vị trí của MatchResult.
      - Node kết thúc khi:
        a) Gặp MatchResult tiếp theo có depth <= depth của node hiện tại
        b) Hết danh sách input

    Đây là thuật toán Stack-based:
      - Khi gặp marker mới → đóng node cũ (nếu depth >= depth mới) → mở node mới
      - Dòng không phải marker → append vào content của node đang mở

    [HYPOTHESIS]: Thuật toán này chưa được benchmark.
    Sẽ được so sánh với Phương án khác khi có failure cases.
    """

    def detect(
        self,
        input_units: list,  # list[str] hoặc list[dict] với key 'text'
        match_results: list[Optional[MatchResult]],
    ) -> list[Boundary]:
        """
        Phát hiện ranh giới từ danh sách match_results.

        Args:
            input_units: Danh sách dòng text hoặc paragraph dicts.
            match_results: Kết quả match tương ứng (cùng index).

        Returns:
            Danh sách Boundary đã xác định đầy đủ start_idx, end_idx, content_lines.
        """
        assert len(input_units) == len(match_results), (
            "input_units và match_results phải có cùng độ dài"
        )

        boundaries: list[Boundary] = []
        current_boundary: Optional[Boundary] = None

        def get_text(unit) -> str:
            if isinstance(unit, str):
                return unit
            if isinstance(unit, dict):
                return unit.get("text", "")
            return str(unit)

        for idx, (unit, match) in enumerate(zip(input_units, match_results)):
            text = get_text(unit)

            if match is not None:
                # Gặp marker mới → đóng boundary đang mở nếu cần
                if current_boundary is not None:
                    new_depth = match.node_type.depth
                    cur_depth = current_boundary.node_type.depth

                    if new_depth <= cur_depth:
                        # Node mới có cùng hoặc cao hơn cấp → đóng node hiện tại
                        current_boundary.end_idx = idx
                        boundaries.append(current_boundary)
                        current_boundary = None
                    else:
                        # Node mới là con của node hiện tại
                        # Đóng node hiện tại trước khi xử lý node con
                        current_boundary.end_idx = idx
                        boundaries.append(current_boundary)
                        current_boundary = None

                # Mở boundary mới
                current_boundary = Boundary(
                    match=match,
                    start_idx=idx,
                    end_idx=idx + 1,  # Sẽ được cập nhật sau
                )

            else:
                # Dòng không phải marker → nội dung của node đang mở
                if current_boundary is not None:
                    if text.strip():
                        current_boundary.content_lines.append(text)

        # Đóng boundary cuối cùng nếu còn
        if current_boundary is not None:
            current_boundary.end_idx = len(input_units)
            boundaries.append(current_boundary)

        return boundaries

    # -----------------------------------------------------------------------
    # Utility: lọc boundaries theo NodeType
    # -----------------------------------------------------------------------
    @staticmethod
    def filter_by_type(
        boundaries: list[Boundary],
        node_type: NodeType,
    ) -> list[Boundary]:
        return [b for b in boundaries if b.node_type == node_type]

    @staticmethod
    def get_boundaries_in_range(
        boundaries: list[Boundary],
        start: int,
        end: int,
    ) -> list[Boundary]:
        """Lấy tất cả boundaries nằm trong range [start, end)."""
        return [b for b in boundaries if start <= b.start_idx < end]
