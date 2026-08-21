# -*- coding: utf-8 -*-
"""
txt_recovery.py — C2 Recovery: Experimental Detectors cho TXT path.

Mỗi detector là một Hypothesis Candidate, KHÔNG phải Rule cứng.
Output là list[ClauseCandidate] — danh sách "điểm bắt đầu khả năng là CLAUSE",
chưa có claim về boundary hay parent.

Evaluation (FP/FN) được thực hiện ở c2_ablation.py bằng cách so sánh
candidates với Reference Annotation theo boundary overlap, không phải node count.

Tinh thần: Mỗi hypothesis là một câu hỏi cần đo, không phải giải pháp đã biết đúng.

=== H1 — Clause-Start Inference ===
Giả thuyết: Paragraph đầu tiên trong mỗi ARTICLE (không phải header) có khả năng
là điểm bắt đầu của CLAUSE đầu tiên.
Giới hạn rõ ràng: Không biết boundary của CLAUSE đó (kết thúc ở đâu?).
                   Paragraph đó có thể là body text trực tiếp của ARTICLE.

=== H2 — All-Paragraph Heuristic ===
Giả thuyết: Mỗi paragraph riêng biệt trong một ARTICLE (không phải header,
không có text marker Point) là ứng cử viên một CLAUSE độc lập.
Nguy cơ FP cao: Paragraph continuation của một CLAUSE bị nhầm thành CLAUSE mới.

=== H3 — Point-Anchor Inference ===
Giả thuyết: Paragraph ngay trước một POINT marker được tìm thấy trong text
có thể là CLAUSE cha của POINT đó.
Giới hạn rõ ràng: Paragraph đó có thể là body của ARTICLE hoặc continuation.
                   Không phải mọi POINT đều có CLAUSE cha trong TXT.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import re


# ---------------------------------------------------------------------------
# ClauseCandidate — đề xuất từ một Hypothesis Detector
# Lưu ý: đây là "ứng cử viên điểm bắt đầu", chưa có claim về boundary.
# ---------------------------------------------------------------------------
@dataclass
class ClauseCandidate:
    """
    Một đề xuất ứng cử viên CLAUSE từ Hypothesis Detector.

    Fields:
      para_index:          Index của paragraph trong TxtLoader output.
      text:                Nội dung text của paragraph.
      parent_article_id:   ID của ARTICLE cha trong TXT Baseline nodes.
      hypothesis:          "H1" | "H2" | "H3"
      confidence:          0.0–1.0 — estimate rủi ro của detector (không phải P(đúng)).
      reason:              Giải thích tại sao đề xuất.

    KHÔNG có field boundary (start/end) vì detector chưa biết.
    Evaluation sẽ so sánh para_index với Reference Annotation bằng overlap.
    """
    para_index: int
    text: str
    parent_article_id: str
    hypothesis: str
    confidence: float
    reason: str


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------
_STRUCTURAL_HEADERS = [
    re.compile(r"^Ch[uư]ơng\s+", re.UNICODE),     # Chương
    re.compile(r"^M[uụ]c\s+", re.UNICODE),          # Mục
    re.compile(r"^(?:Đ|Ð)i[eề]u\s+", re.UNICODE),  # Điều
    re.compile(r"^[a-zđ]\)\s+", re.UNICODE),         # Point marker a), b)...
    re.compile(r"^\d+\.\s+", re.UNICODE),            # Numbered item 1., 2.
]

def _is_structural_header(text: str) -> bool:
    """True nếu text là tiêu đề cấu trúc — không phải CLAUSE candidate."""
    t = text.strip()
    return any(p.match(t) for p in _STRUCTURAL_HEADERS)


# ---------------------------------------------------------------------------
# H1Detector — Clause-Start Inference
# ---------------------------------------------------------------------------
class H1Detector:
    """
    H1: Paragraph ĐẦU TIÊN trong mỗi ARTICLE (không phải header cấu trúc)
    được đề xuất là điểm bắt đầu có thể của CLAUSE đầu tiên.

    Chỉ đề xuất 1 candidate/ARTICLE.
    Không có thông tin về boundary hay các Khoản tiếp theo.

    Nguy cơ FP đã biết:
      - ARTICLE có body text trực tiếp (không có Khoản con nào) sẽ bị nhầm.
      - Ví dụ: "Điều 47. Ủy ban nhân dân..." — đoạn đầu là body, không phải Khoản.
    """

    def detect(self, txt_nodes: list[dict], txt_paragraphs: list) -> list[ClauseCandidate]:
        candidates = []

        article_nodes = sorted(
            [n for n in txt_nodes if n.get("type") == "ARTICLE"],
            key=lambda n: n.get("start_idx", 0)
        )
        para_text_map: dict[int, str] = {p.index: p.text for p in txt_paragraphs}
        para_indices = sorted(para_text_map.keys())

        for art in article_nodes:
            art_start = art.get("start_idx", 0) + 1  # bỏ qua chính dòng Điều XX.
            art_end   = art.get("end_idx", art_start)
            art_id    = art.get("id", "unknown_article")

            # Tìm paragraph đầu tiên trong khoảng [art_start, art_end)
            for idx in para_indices:
                if idx < art_start:
                    continue
                if idx >= art_end:
                    break
                text = para_text_map.get(idx, "").strip()
                if not text or _is_structural_header(text):
                    continue  # bỏ qua dòng trống / header

                candidates.append(ClauseCandidate(
                    para_index=idx,
                    text=text,
                    parent_article_id=art_id,
                    hypothesis="H1",
                    confidence=0.65,
                    reason=(
                        f"Paragraph đầu tiên (idx={idx}) trong ARTICLE '{art_id}'. "
                        f"Là điểm bắt đầu tiềm năng của CLAUSE đầu tiên — chưa rõ boundary."
                    )
                ))
                break  # chỉ lấy paragraph ĐẦU TIÊN

        return candidates


# ---------------------------------------------------------------------------
# H2Detector — All-Paragraph Heuristic
# ---------------------------------------------------------------------------
class H2Detector:
    """
    H2: MỌI paragraph trong mỗi ARTICLE (không phải header, không có Point marker)
    đều là ứng cử viên CLAUSE độc lập.

    H2 giả định: mỗi paragraph riêng biệt = một Khoản.
    Đây là giả định mạnh và sai với paragraph continuation (tiếp nối ý của Khoản trước).

    Nguy cơ FP cao: Trong corpus hiện tại, nhiều CLAUSE trải qua nhiều paragraph.
    Evaluation sẽ cho thấy FP của H2 so với H1 như thế nào.
    """

    def detect(self, txt_nodes: list[dict], txt_paragraphs: list) -> list[ClauseCandidate]:
        candidates = []

        article_nodes = sorted(
            [n for n in txt_nodes if n.get("type") == "ARTICLE"],
            key=lambda n: n.get("start_idx", 0)
        )
        para_text_map: dict[int, str] = {p.index: p.text for p in txt_paragraphs}
        para_indices = sorted(para_text_map.keys())

        for art in article_nodes:
            art_id    = art.get("id", "unknown_article")
            art_start = art.get("start_idx", 0) + 1
            art_end   = art.get("end_idx", art_start)
            position  = 0

            for idx in para_indices:
                if idx < art_start:
                    continue
                if idx >= art_end:
                    break
                text = para_text_map.get(idx, "").strip()
                if not text or _is_structural_header(text):
                    continue

                position += 1
                # Confidence giảm dần theo position — paragraph đầu ít rủi ro hơn
                conf = max(0.30, 0.60 - (position - 1) * 0.05)
                candidates.append(ClauseCandidate(
                    para_index=idx,
                    text=text,
                    parent_article_id=art_id,
                    hypothesis="H2",
                    confidence=conf,
                    reason=(
                        f"Paragraph thứ {position} trong ARTICLE '{art_id}'. "
                        f"Đề xuất mỗi paragraph = một CLAUSE — nguy cơ FP cao với continuation."
                    )
                ))

        return candidates


# ---------------------------------------------------------------------------
# H3Detector — Point-Anchor Boundary Inference
# ---------------------------------------------------------------------------
class H3Detector:
    """
    H3: Nếu tìm thấy một POINT marker trong text (ví dụ: 'd) ...'),
    paragraph ngay trước nó (không rỗng, không phải header cấu trúc)
    được đề xuất là ứng cử viên CLAUSE cha.

    Đây là suy ngược từ tín hiệu POINT → infer CLAUSE boundary.
    Không phải: "paragraph trước = chắc chắn là CLAUSE".
    Mà là: "đây là nơi có thể bắt đầu CLAUSE nếu POINT này có CLAUSE cha".

    Nguy cơ đã biết:
      - Paragraph trước có thể là body trực tiếp của ARTICLE.
      - POINT có thể là orphan (không có CLAUSE cha trong TXT).
      - Chỉ hoạt động với 8 POINT còn nhận diện được trong TXT — coverage thấp.
    """

    _POINT_RE = re.compile(r"^[a-zđ]\)\s+", re.UNICODE)

    def detect(self, txt_nodes: list[dict], txt_paragraphs: list) -> list[ClauseCandidate]:
        candidates = []
        seen_indices: set[int] = set()  # Không đề xuất cùng một paragraph hai lần

        # Build: para_index → article_id (ARTICLE chứa para đó)
        article_nodes = sorted(
            [n for n in txt_nodes if n.get("type") == "ARTICLE"],
            key=lambda n: n.get("start_idx", 0)
        )

        def get_article_id(idx: int) -> Optional[str]:
            result = None
            for art in article_nodes:
                if art.get("start_idx", 0) <= idx < art.get("end_idx", idx + 1):
                    result = art.get("id")
                    break
            return result

        para_list = sorted(txt_paragraphs, key=lambda p: p.index)

        for i, para in enumerate(para_list):
            text = para.text.strip()
            if not text:
                continue

            # Paragraph này có phải là POINT marker không?
            if not self._POINT_RE.match(text):
                continue

            # Tìm paragraph không rỗng ngay trước
            prev_para = None
            for j in range(i - 1, -1, -1):
                if para_list[j].text.strip():
                    prev_para = para_list[j]
                    break

            if prev_para is None or prev_para.index in seen_indices:
                continue

            prev_text = prev_para.text.strip()
            # Bỏ qua nếu prev_para là header cấu trúc
            if _is_structural_header(prev_text):
                continue

            art_id = get_article_id(prev_para.index)
            if art_id is None:
                continue

            seen_indices.add(prev_para.index)
            candidates.append(ClauseCandidate(
                para_index=prev_para.index,
                text=prev_text,
                parent_article_id=art_id,
                hypothesis="H3",
                confidence=0.45,
                reason=(
                    f"Suy ngược từ POINT '{text[:25]}' (idx={para.index}). "
                    f"Paragraph liền trước (idx={prev_para.index}) là ứng cử viên CLAUSE cha — "
                    f"chưa xác định được boundary."
                )
            ))

        return candidates
