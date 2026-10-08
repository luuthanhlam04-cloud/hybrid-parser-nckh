# -*- coding: utf-8 -*-
"""
contracts.py — Data Contract giữa Module 1 (Document Preprocessing) và Module 2 (Regex Parser).

Research context (RQ6 — Information Preservation):
  Khi tài liệu được chuyển qua các bước tiền xử lý, những tín hiệu cấu trúc nào
  cần được giữ lại để Module 2 khôi phục hierarchy mà không phải suy diễn lại thông tin đã mất?

Contract này là câu trả lời kỹ thuật cho câu hỏi đó:
  - DOCX path:      Truyền đủ 7 fields → M2 có 4 nhóm tín hiệu.
  - TXT path:       Chỉ có text + is_empty → M2 fallback về Regex+Context.
  - Sự khác biệt này là dữ liệu đo lường của bài toán information loss.

Schema quyết định quan trọng:
  - number:  Thứ tự pháp lý nguyên bản của CHAPTER, SECTION, ARTICLE, CLAUSE (int hoặc str La Mã).
             None nếu M1 không khôi phục được.
  - marker:  Ký tự nhận diện của POINT (a, b, c, đ, e...).
             None nếu không phải POINT hoặc M1 không biết.
  → number và marker được giữ riêng để tránh lẫn semantics.
  → M2 giữ nguyên cả hai vào Legal Node. Không được tự tính từ position.

Dependency:
  - Module 1 (Producer):  DocxLoader.load_structured(), TxtLoader.load_structured()
  - Module 2 (Consumer):  LegalParser.parse_structured()
  - Không phụ thuộc vào thư viện bên ngoài (chỉ dùng stdlib dataclasses).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class StructuredParagraph:
    """
    Đơn vị dữ liệu truyền từ Module 1 sang Module 2.

    === DOCX path — M1 điền đầy đủ ===
      Module 2 có 4 nhóm tín hiệu:
        Lớp 1 (Style):   word_style
        Lớp 1 (Number):  num_id, ilvl, num_fmt, number, marker
        Lớp 2 (Regex):   text
        Lớp 3 (Context): thứ tự, depth từ ilvl

    === TXT path — chỉ có text ===
      Module 2 fallback về Lớp 2+3.
      Các field metadata = None.
      Module 2 phải handle gracefully khi metadata = None.

    === Semantics của các fields ===

    index: int
        Thứ tự paragraph trong tài liệu gốc (0-indexed).
        Bất biến trong toàn pipeline. M2 dùng làm start_idx / end_idx.
        [Luôn có, cả DOCX và TXT]

    text: str
        Nội dung text thuần đã làm sạch và chuẩn hóa NFC.
        KHÔNG chứa label số đã render (không có "1. ", "a) " đứng trước).
        [Luôn có, cả DOCX và TXT]

    word_style: Optional[str]
        Word Style name từ DOCX (e.g. "List Paragraph", "Heading 2", "Body Text", "Normal").
        Tín hiệu Lớp 1 — M2 dùng STYLE_HINTS để map sang NodeType.
        None nếu không có (TXT path).
        [DOCX: có; TXT: None]

    num_id: Optional[int]
        w:numId từ DOCX numbering XML.
        Định danh numbering list instance — dùng để trace provenance, KHÔNG phải classifier chính.
        M2 không dùng num_id để quyết định loại node một mình.
        None nếu paragraph không thuộc numbering list hoặc TXT.
        [DOCX List Paragraph: có; khác: None]

    ilvl: Optional[int]
        w:ilvl (indent level) từ DOCX numbering XML.
        Tín hiệu cấu trúc — kết hợp với num_fmt để nhận diện node type.
        Evidence từ Ch3-LDD-2024: ilvl=0 + decimal → CLAUSE, ilvl=1 + lowerLetter → POINT.
        CẢNH BÁO: mapping này là [CORPUS: Ch3-LDD] — không hard-code cross-corpus.
        None nếu không có (TXT path hoặc paragraph không phải List Paragraph).
        [DOCX List Paragraph: có; khác: None]

    num_fmt: Optional[str]
        Định dạng đánh số từ DOCX numbering XML ("decimal", "lowerLetter", "lowerRoman"...).
        Kết hợp với ilvl để xác định loại node. Xem note về ilvl.
        None nếu không có.
        [DOCX List Paragraph: có; khác: None]

    number: Optional[object]
        Thứ tự pháp lý nguyên bản của node — CHỈ cho CHAPTER, SECTION, ARTICLE, CLAUSE.
        Được M1 tính sẵn từ w:numId/w:ilvl counters.
        Ví dụ: Khoản 3 → number=3 (int). Chương III → number="III" (str).
        KHÔNG dùng cho POINT — dùng field marker riêng.
        None nếu M1 không khôi phục được (e.g. TXT path, hoặc paragraph rỗng).
        M2 KHÔNG được tự tính number = position.
        [DOCX List Paragraph decimal: int; DOCX Roman: str; TXT: None]

    marker: Optional[str]
        Ký tự nhận diện của POINT — a, b, c, đ, e, g...
        Được M1 tính sẵn từ w:ilvl lowerLetter counter.
        KHÔNG dùng cho các node type khác — chỉ POINT.
        None nếu không phải POINT hoặc M1 không biết.
        [DOCX List Paragraph lowerLetter: str; khác: None]

    is_empty: bool
        True nếu text.strip() == "".
        M2 skip paragraph này trong quá trình parsing.
        Được tính sẵn bởi M1 để tránh M2 phải tự detect.
        [Luôn có]

    === Invariants (bất biến) ===
      1. number và marker không được cùng có giá trị. Một trong hai là None.
      2. Nếu num_id is None → ilvl, num_fmt, number, marker đều là None.
      3. is_empty = (text.strip() == "").
      4. index là duy nhất trong một batch từ cùng một tài liệu.
      5. M2 KHÔNG được ghi đè number hoặc marker.
    """

    # Bắt buộc — luôn có
    index: int
    text: str

    # Optional — có ở DOCX, None ở TXT
    word_style: Optional[str]   = None
    num_id:     Optional[int]   = None
    ilvl:       Optional[int]   = None
    num_fmt:    Optional[str]   = None

    # Số pháp lý: tách riêng CLAUSE/ARTICLE/... (number) và POINT (marker)
    number:     Optional[object] = None   # int hoặc str, không phải vị trí
    marker:     Optional[str]   = None   # ký tự điểm: "a", "b", "đ"...

    # Tiện ích
    is_empty:   bool            = False

    def __post_init__(self):
        """Validate invariant cơ bản."""
        # Invariant 1: number và marker không đồng thời có giá trị
        if self.number is not None and self.marker is not None:
            raise ValueError(
                f"StructuredParagraph invariant violated at index={self.index}: "
                f"number ({self.number!r}) và marker ({self.marker!r}) không thể cùng khác None. "
                f"Một trong hai phải là None."
            )

    @property
    def has_metadata(self) -> bool:
        """True nếu có ít nhất word_style (DOCX path)."""
        return self.word_style is not None

    @property
    def has_numbering(self) -> bool:
        """True nếu có đầy đủ numbering metadata (num_id + ilvl + num_fmt)."""
        return self.num_id is not None and self.ilvl is not None and self.num_fmt is not None

    def to_engine_dict(self) -> dict:
        """
        Chuyển StructuredParagraph sang dict format mà RegexEngine hiện đang nhận.
        Giúp tích hợp contract với RegexEngine mà không cần rewrite ngay.

        Dict format:
          {"index": int, "text": str, "style": str|None, "ilvl": int|None, "num_fmt": str|None,
           "num_id": int|None, "number": int|str|None, "marker": str|None}
        """
        return {
            "index":    self.index,
            "text":     self.text,
            "style":    self.word_style,     # Mapping sang key mà RegexEngine dùng
            "ilvl":     self.ilvl,
            "num_fmt":  self.num_fmt,
            "num_id":   self.num_id,
            "number":   self.number,
            "marker":   self.marker,
        }


def txt_paragraph(index: int, text: str) -> StructuredParagraph:
    """
    Factory để tạo StructuredParagraph từ một dòng TXT.
    Tất cả metadata fields = None. is_empty tự tính.
    """
    return StructuredParagraph(
        index=index,
        text=text,
        word_style=None,
        num_id=None,
        ilvl=None,
        num_fmt=None,
        number=None,
        marker=None,
        is_empty=(text.strip() == ""),
    )
