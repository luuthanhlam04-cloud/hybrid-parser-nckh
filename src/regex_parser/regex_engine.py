# -*- coding: utf-8 -*-
"""
regex_engine.py — Module 2: Regex Parser
Pattern Registry với metadata: source_corpus, known_fp, scope, confidence.

Thiết kế theo Pattern Taxonomy v1 [CORPUS: Ch3-LDD].
Mỗi pattern gắn tag [CORPUS] / [HYPOTHESIS] / [GENERAL] tương ứng.
Regex KHÔNG tự giải quyết toàn bộ bài toán — chỉ là Lớp 2 (Text Signal).
Lớp 1 (Style Signal từ DOCX) và Lớp 3 (Context) được xử lý ở các module khác.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# NodeType Enum — 5 loại cấu trúc vật lý
# Đây là Structural Taxonomy, KHÔNG phải Legal Ontology.
# Legal Ontology (Actor, Condition, Exception...) thuộc Module 7.
# ---------------------------------------------------------------------------
class NodeType(str, Enum):
    CHAPTER = "CHAPTER"
    SECTION = "SECTION"
    ARTICLE = "ARTICLE"
    CLAUSE  = "CLAUSE"
    POINT   = "POINT"

    @property
    def depth(self) -> int:
        """Độ sâu phân cấp: CHAPTER=0, SECTION=1, ARTICLE=2, CLAUSE=3, POINT=4"""
        return {
            NodeType.CHAPTER: 0,
            NodeType.SECTION: 1,
            NodeType.ARTICLE: 2,
            NodeType.CLAUSE:  3,
            NodeType.POINT:   4,
        }[self]


# ---------------------------------------------------------------------------
# PatternEntry — một entry trong Pattern Registry
# ---------------------------------------------------------------------------
@dataclass
class PatternEntry:
    """Một pattern đơn lẻ trong registry, kèm metadata truy xuất nguồn."""
    pattern: str                         # Regex pattern string
    source_corpus: str                   # 'Ch3-LDD-2024' | 'UNKNOWN' | 'GENERAL'
    confidence: str                      # 'HIGH' | 'MEDIUM' | 'HYPOTHESIS' | 'CONFIRMED'
    example: str                         # Ví dụ thực tế từ corpus
    known_fp: Optional[str] = None       # False positive đã biết
    scope: Optional[str] = None          # 'inside_ARTICLE' | 'inside_CLAUSE' | None
    required_style: Optional[str] = None # Bắt buộc Word Style này (nếu có)
    anchor: str = "start_of_line"        # 'start_of_line' | 'anywhere'
    note: Optional[str] = None           # Ghi chú thêm

    def compile(self, flags: int = re.UNICODE) -> re.Pattern:
        return re.compile(self.pattern, flags)


# ---------------------------------------------------------------------------
# PATTERN REGISTRY — bộ từ điển pattern có metadata
# Mỗi NodeType có danh sách các PatternEntry, theo thứ tự ưu tiên.
# Pattern nào được kiểm chứng từ corpus thực sẽ đứng trước.
# ---------------------------------------------------------------------------
PATTERN_REGISTRY: dict[NodeType, list[PatternEntry]] = {

    # -----------------------------------------------------------------------
    # CHAPTER — Chương
    # [CORPUS: Ch3-LDD]: Chương III (La Mã)
    # [HYPOTHESIS]: Chương 3 (Ả Rập), CHƯƠNG III (viết hoa)
    # -----------------------------------------------------------------------
    NodeType.CHAPTER: [
        PatternEntry(
            pattern=r"^\s*Ch[uư]ơng\s+(?P<number>[IVXivxLCDMlcdm]+)\s*$",
            source_corpus="Ch3-LDD-2024",
            confidence="HIGH",
            example="Chương III",
            known_fp=None,
            note="La Mã [CORPUS: Ch3-LDD]"
        ),
        PatternEntry(
            pattern=r"^\s*Ch[uư]ơng\s+(?P<number>\d+)\s*$",
            source_corpus="UNKNOWN",
            confidence="HYPOTHESIS",
            example="Chương 3",
            known_fp=None,
            note="Ả Rập [HYPOTHESIS]"
        ),
        PatternEntry(
            pattern=r"^\s*CH[UƯ]ƠNG\s+(?P<number>[IVXivx\d]+)\s*$",
            source_corpus="UNKNOWN",
            confidence="HYPOTHESIS",
            example="CHƯƠNG III",
            known_fp=None,
            note="Viết hoa [HYPOTHESIS]"
        ),
    ],

    # -----------------------------------------------------------------------
    # SECTION — Mục
    # [CORPUS: Ch3-LDD]: Mục 1, Mục 2 (Ả Rập)
    # [HYPOTHESIS]: Mục I (La Mã)
    # -----------------------------------------------------------------------
    NodeType.SECTION: [
        PatternEntry(
            pattern=r"^\s*M[uụ]c\s+(?P<number>\d+)\s*$",
            source_corpus="Ch3-LDD-2024",
            confidence="HIGH",
            example="Mục 1",
            known_fp=None,
            note="Ả Rập [CORPUS: Ch3-LDD]"
        ),
        PatternEntry(
            pattern=r"^\s*M[uụ]c\s+(?P<number>[IVXivx]+)\s*$",
            source_corpus="UNKNOWN",
            confidence="HYPOTHESIS",
            example="Mục I",
            known_fp=None,
            note="La Mã [HYPOTHESIS]"
        ),
    ],

    # -----------------------------------------------------------------------
    # ARTICLE — Điều
    # [CORPUS: Ch3-LDD]: Điều 26. Quyền chung... (Heading 2 + text)
    # Anchor đầu dòng bắt buộc để phân biệt với cross-ref trong câu.
    # VD cross-ref: "theo quy định tại Điều 37 của Luật này" → KHÔNG phải boundary
    # -----------------------------------------------------------------------
    NodeType.ARTICLE: [
        PatternEntry(
            pattern=r"^\s*(?:Đ|Ð)i[eề]u\s+(?P<number>\d+)\.?\s*(?P<title>.*)$",
            source_corpus="Ch3-LDD-2024",
            confidence="HIGH",
            example="Điều 26. Quyền chung của người sử dụng đất",
            known_fp="'Điều X' trong cross-reference (không có dấu chấm + đứng đầu dòng)",
            anchor="start_of_line",
            note="Anchor đầu dòng là điều kiện cần. [CORPUS: Ch3-LDD]"
        ),
        PatternEntry(
            pattern=r"^\s*(?:Đ|Ð)I[EỀ]U\s+(?P<number>\d+)\.?\s*(?P<title>.*)$",
            source_corpus="UNKNOWN",
            confidence="HYPOTHESIS",
            example="ĐIỀU 26.",
            known_fp=None,
            note="Viết hoa [HYPOTHESIS]"
        ),
    ],

    # -----------------------------------------------------------------------
    # CLAUSE — Khoản
    # [CORPUS: Ch3-LDD]: 1. Người nhận... (List Paragraph style, bắt đầu bằng số)
    # KHÔNG có chữ "Khoản" đứng trước trong corpus này.
    # Scope: chỉ tìm bên trong ARTICLE container (Phương án B).
    # KHÔNG dùng chữ hoa làm heuristic.
    # -----------------------------------------------------------------------
    NodeType.CLAUSE: [
        PatternEntry(
            pattern=r"^\s*(?P<number>\d+)\.\s+(?P<text>.+)$",
            source_corpus="Ch3-LDD-2024",
            confidence="HIGH",
            example="1. Người nhận quyền sử dụng đất được quy định như sau:",
            known_fp="Số thứ tự trong danh sách nội dung thông thường",
            scope=None,
            note="Không có chữ 'Khoản'. Bỏ scope để bắt được sibling. [CORPUS: Ch3-LDD]"
        ),
        PatternEntry(
            pattern=r"^(?P<text>.+)$",
            source_corpus="Ch3-LDD-2024",
            confidence="HIGH",
            example="<text không có số do python-docx không lấy được list number>",
            required_style="List Paragraph",
            scope=None,
            note="Phục hồi Khoản từ List Paragraph khi text bị mất số thứ tự."
        ),
        PatternEntry(
            pattern=r"^\s*Kho[aả]n\s+(?P<number>\d+)\.?\s*(?P<text>.*)$",
            source_corpus="UNKNOWN",
            confidence="HYPOTHESIS",
            example="Khoản 1.",
            known_fp=None,
            note="Có chữ 'Khoản' [HYPOTHESIS]"
        ),
        PatternEntry(
            pattern=r"^\s*\((?P<number>\d+)\)\s+(?P<text>.*)$",
            source_corpus="UNKNOWN",
            confidence="HYPOTHESIS",
            example="(1) Người nhận...",
            known_fp="Số trong ngoặc có thể có nghĩa khác",
            note="Format ngoặc [HYPOTHESIS]"
        ),
    ],

    # -----------------------------------------------------------------------
    # POINT — Điểm
    # [CORPUS: Ch3-LDD]: a) b) c) d) đ) e)... (Body Text style)
    # ĐẶC BIỆT: đ) là ký tự Unicode ngoài ASCII — phải xử lý riêng.
    # Scope: chỉ tìm bên trong CLAUSE container.
    # Bộ ký tự đầy đủ chưa xác định — pattern hiện tại dùng [a-zđ] là estimate.
    # -----------------------------------------------------------------------
    NodeType.POINT: [
        PatternEntry(
            pattern=r"^\s*(?P<marker>[a-zđ])\)\s+(?P<text>.+)$",
            source_corpus="Ch3-LDD-2024",
            confidence="HIGH",
            example="đ) Thế chấp quyền sử dụng đất...",
            known_fp="'điểm a' trong cross-reference nội dung câu",
            scope=None,
            note="Bộ ký tự [a-zđ]. Bỏ scope để bắt được orphan POINT. [CORPUS: Ch3-LDD]"
        ),
        PatternEntry(
            pattern=r"^\s*(?P<marker>[a-zđ])\.\s+(?P<text>.+)$",
            source_corpus="UNKNOWN",
            confidence="HYPOTHESIS",
            example="a. Cá nhân được...",
            known_fp=None,
            note="Format dấu chấm thay vì ngoặc [HYPOTHESIS]"
        ),
    ],
}


# ---------------------------------------------------------------------------
# MatchResult — kết quả match của một pattern trên một dòng/paragraph
# ---------------------------------------------------------------------------
@dataclass
class MatchResult:
    node_type: NodeType
    pattern_entry: PatternEntry
    raw_text: str            # Toàn bộ text của dòng/paragraph
    number: Optional[str]   # Số thứ tự (26 cho Điều 26)
    marker: Optional[str]   # Ký tự điểm (a, b, đ...)
    title: Optional[str]    # Tiêu đề nếu có
    text: Optional[str]     # Nội dung sau marker
    line_idx: int = 0        # Vị trí trong danh sách input
    para_idx: int = 0        # Index của paragraph (nếu từ DOCX)
    word_style: Optional[str] = None  # Word style từ DOCX nếu có


def _extract_groups(m: re.Match) -> dict:
    """Trích xuất named groups, trả về None nếu không có."""
    try:
        groups = m.groupdict()
    except Exception:
        groups = {}
    return {k: (v.strip() if v else None) for k, v in groups.items()}


# ---------------------------------------------------------------------------
# RegexEngine — thực thi match
# ---------------------------------------------------------------------------
class RegexEngine:
    """
    Engine thực thi Pattern Registry trên một đơn vị văn bản.
    Hỗ trợ cả 2 mode:
      - plain_text mode: input là list[str] (từ PDF/TXT)
      - docx mode: input là list[dict] với 'text' và 'style' (từ DOCX paragraphs)
    """

    def __init__(self):
        # Compile toàn bộ pattern một lần khi khởi tạo
        self._compiled: dict[NodeType, list[tuple[re.Pattern, PatternEntry]]] = {
            nt: [(entry.compile(), entry) for entry in entries]
            for nt, entries in PATTERN_REGISTRY.items()
        }

        # Style → NodeType hint từ DOCX inspection [CORPUS: Ch3-LDD]
        # Đây là hint, không phải ground truth.
        self.STYLE_HINTS: dict[str, NodeType] = {
            "Heading 2":       NodeType.ARTICLE,
            "List Paragraph":  NodeType.CLAUSE,
            "Body Text":       NodeType.POINT,
            "Normal":          None,   # Có thể là CHAPTER hoặc SECTION
            "Heading 1":       NodeType.CHAPTER,
        }

    # -----------------------------------------------------------------------
    # Public: match một đơn vị text
    # -----------------------------------------------------------------------
    def match_text(
        self,
        text: str,
        line_idx: int = 0,
        word_style: Optional[str] = None,
        para_idx: int = 0,
        scope_node_type: Optional[NodeType] = None,
    ) -> Optional[MatchResult]:
        """
        Match text với Pattern Registry.

        Args:
            text: Nội dung cần match.
            line_idx: Vị trí dòng trong input.
            word_style: Word Style từ DOCX (Lớp 1 tín hiệu). None nếu không có.
            para_idx: Index paragraph DOCX.
            scope_node_type: NodeType của container hiện tại (dùng cho scoped patterns).
                             VD: ARTICLE → chỉ xét CLAUSE patterns có scope='inside_ARTICLE'.

        Returns:
            MatchResult nếu match thành công, None nếu không.
        """
        stripped = text.strip()
        if not stripped:
            return None

        # Lấy style hint (Lớp 1 tín hiệu) nếu có
        style_hint: Optional[NodeType] = None
        if word_style:
            style_hint = self.STYLE_HINTS.get(word_style)

        # Thứ tự ưu tiên node types để thử
        # Nếu có style_hint → thử node type đó trước
        ordered_types = self._get_ordered_types(style_hint, scope_node_type)

        for node_type in ordered_types:
            for compiled_pattern, entry in self._compiled[node_type]:
                # Kiểm tra scope
                if not self._check_scope(entry.scope, scope_node_type):
                    continue
                # Kiểm tra required_style
                if entry.required_style and entry.required_style != word_style:
                    continue

                m = compiled_pattern.match(stripped)
                if m:
                    groups = _extract_groups(m)
                    return MatchResult(
                        node_type=node_type,
                        pattern_entry=entry,
                        raw_text=text,
                        number=groups.get("number"),
                        marker=groups.get("marker"),
                        title=groups.get("title"),
                        text=groups.get("text"),
                        line_idx=line_idx,
                        para_idx=para_idx,
                        word_style=word_style,
                    )

        return None

    # -----------------------------------------------------------------------
    # Public: match toàn bộ danh sách text (plain text mode)
    # -----------------------------------------------------------------------
    def match_lines(self, lines: list[str]) -> list[Optional[MatchResult]]:
        """Match toàn bộ list dòng text. Trả về list kết quả, None cho dòng không match."""
        results = []
        current_scope = None
        for i, line in enumerate(lines):
            res = self.match_text(line, line_idx=i, scope_node_type=current_scope)
            results.append(res)
            if res:
                if res.node_type in (NodeType.ARTICLE, NodeType.CLAUSE):
                    current_scope = res.node_type
                elif res.node_type in (NodeType.CHAPTER, NodeType.SECTION):
                    current_scope = None
        return results

    # -----------------------------------------------------------------------
    # Public: match toàn bộ paragraphs từ DOCX (docx mode)
    # -----------------------------------------------------------------------
    def match_paragraphs(
        self,
        paragraphs: list[dict],
    ) -> list[Optional[MatchResult]]:
        """
        Match danh sách paragraphs từ DOCX.

        Args:
            paragraphs: List dict với keys: 'text' (str), 'style' (str), 'index' (int).
        """
        results = []
        current_scope = None
        for i, p in enumerate(paragraphs):
            res = self.match_text(
                text=p.get("text", ""),
                line_idx=p.get("index", i),
                word_style=p.get("style"),
                para_idx=i,
                scope_node_type=current_scope
            )
            results.append(res)
            if res:
                if res.node_type in (NodeType.ARTICLE, NodeType.CLAUSE):
                    current_scope = res.node_type
                elif res.node_type in (NodeType.CHAPTER, NodeType.SECTION):
                    current_scope = None
        return results

    # -----------------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------------
    def _get_ordered_types(
        self,
        style_hint: Optional[NodeType],
        scope: Optional[NodeType],
    ) -> list[NodeType]:
        """
        Xác định thứ tự NodeType cần thử.
        style_hint được thử trước để tận dụng Lớp 1 tín hiệu.
        scope giới hạn: nếu đang trong ARTICLE → ưu tiên CLAUSE, POINT.
        """
        all_types = list(NodeType)
        if style_hint:
            # Style hint lên đầu
            ordered = [style_hint] + [t for t in all_types if t != style_hint]
        elif scope == NodeType.ARTICLE:
            # Đang trong ARTICLE → CLAUSE, POINT trước
            ordered = [NodeType.CLAUSE, NodeType.POINT] + [
                t for t in all_types if t not in (NodeType.CLAUSE, NodeType.POINT)
            ]
        elif scope == NodeType.CLAUSE:
            ordered = [NodeType.POINT] + [t for t in all_types if t != NodeType.POINT]
        else:
            ordered = all_types
        return ordered

    @staticmethod
    def _check_scope(
        pattern_scope: Optional[str],
        current_scope: Optional[NodeType],
    ) -> bool:
        """
        Kiểm tra xem pattern có scope có được phép match trong context hiện tại không.
        Pattern không có scope → luôn được phép.
        Pattern có scope → chỉ match khi current_scope khớp.
        """
        if pattern_scope is None:
            return True
        scope_map = {
            "inside_ARTICLE": NodeType.ARTICLE,
            "inside_CLAUSE":  NodeType.CLAUSE,
        }
        required = scope_map.get(pattern_scope)
        return required == current_scope


# ---------------------------------------------------------------------------
# Utility: load paragraphs từ DOCX
# ---------------------------------------------------------------------------
def load_docx_paragraphs(filepath: str) -> list[dict]:
    """
    Load paragraphs từ file DOCX, trả về list dict với text, style, index.
    Chỉ trả về paragraphs có nội dung (bỏ qua dòng trống).
    """
    import docx
    doc = docx.Document(filepath)
    result = []
    for i, p in enumerate(doc.paragraphs):
        text = p.text.strip()
        if not text:
            continue
        result.append({
            "index": i,
            "text": text,
            "style": p.style.name if p.style else None,
            "indent": p.paragraph_format.left_indent,
        })
    return result


def load_text_lines(filepath: str) -> list[str]:
    """Load plain text file thành list dòng."""
    with open(filepath, encoding="utf-8") as f:
        return [line.rstrip("\n\r") for line in f.readlines()]
