"""
document_loader.py
==================
Tải văn bản từ file .docx và phục hồi đánh số tự động (Auto-numbering)
của MS Word (Khoản: 1, 2, 3 và Điểm: a, b, c).

Chiến lược hai tầng:
  - Tầng 1 (Chính):   pypandoc → Pandoc tự hiểu w:numPr và tái tạo nhãn số.
  - Tầng 2 (Dự phòng): Phân tích XML thủ công bằng lxml + zipfile khi Pandoc
                        chưa được cài đặt trên hệ thống.

Giao diện mở rộng:
  BaseLoader (ABC) → DocxLoader, TxtLoader (tương lai), PdfLoader (tương lai)
"""

from __future__ import annotations

import logging
import re
import zipfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
from xml.etree import ElementTree as ET

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Namespace XML của OOXML (dùng cho fallback parser)
# ---------------------------------------------------------------------------
NS = {
    "w":  "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r":  "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


# ---------------------------------------------------------------------------
# Abstract Base Loader
# ---------------------------------------------------------------------------
class BaseLoader(ABC):
    """Giao diện cơ sở cho tất cả các loader văn bản."""

    @abstractmethod
    def load(self, path: str | Path) -> list[str]:
        """
        Tải văn bản từ file và trả về danh sách các dòng (có đánh số đã phục hồi).

        Args:
            path: Đường dẫn tới file cần tải.

        Returns:
            Danh sách các dòng văn bản (chưa join, mỗi phần tử là một dòng).
        """


# ---------------------------------------------------------------------------
# Fallback: XML Parser (khi Pandoc không khả dụng)
# ---------------------------------------------------------------------------
class _NumXmlParser:
    """
    Phân tích word/numbering.xml để dựng bảng tra cứu:
        numId → { ilvl → (numFmt, lvlText, start) }

    Sau đó theo dõi bộ đếm theo từng (numId, ilvl) để tái tạo nhãn số/chữ
    cho từng đoạn văn có thuộc tính w:numPr.
    """

    # Định dạng số được hỗ trợ
    _ALPHA_LOWER = "abcdefghijklmnopqrstuvwxyz"

    def __init__(self, docx_path: str | Path) -> None:
        self._docx_path = Path(docx_path)
        # numId → { ilvl(int) → dict(numFmt, lvlText, start) }
        self._num_map: dict[int, dict[int, dict]] = {}
        # Bộ đếm hiện tại: (numId, ilvl) → count
        self._counters: dict[tuple[int, int], int] = {}
        self._load_numbering()

    # ------------------------------------------------------------------
    # Nội bộ: xây dựng bảng tra cứu từ numbering.xml
    # ------------------------------------------------------------------
    def _load_numbering(self) -> None:
        """Đọc word/numbering.xml từ trong archive ZIP của DOCX."""
        try:
            with zipfile.ZipFile(self._docx_path, "r") as zf:
                if "word/numbering.xml" not in zf.namelist():
                    logger.warning("Không tìm thấy word/numbering.xml — file không dùng danh sách tự động.")
                    return
                numbering_xml = zf.read("word/numbering.xml")
        except (zipfile.BadZipFile, KeyError) as exc:
            logger.error("Không thể đọc numbering.xml: %s", exc)
            return

        root = ET.fromstring(numbering_xml)

        # Bước 1: Đọc abstractNum → { ilvl → (numFmt, lvlText, start) }
        abstract_nums: dict[int, dict[int, dict]] = {}
        for abs_num in root.findall("w:abstractNum", NS):
            abs_id_attr = abs_num.get(f"{{{NS['w']}}}abstractNumId")
            if abs_id_attr is None:
                continue
            abs_id = int(abs_id_attr)
            levels: dict[int, dict] = {}
            for lvl in abs_num.findall("w:lvl", NS):
                ilvl_attr = lvl.get(f"{{{NS['w']}}}ilvl")
                if ilvl_attr is None:
                    continue
                ilvl = int(ilvl_attr)
                fmt_el = lvl.find("w:numFmt", NS)
                txt_el = lvl.find("w:lvlText", NS)
                start_el = lvl.find("w:start", NS)
                levels[ilvl] = {
                    "numFmt":  fmt_el.get(f"{{{NS['w']}}}val", "decimal") if fmt_el is not None else "decimal",
                    "lvlText": txt_el.get(f"{{{NS['w']}}}val", "%1.") if txt_el is not None else "%1.",
                    "start":   int(start_el.get(f"{{{NS['w']}}}val", "1")) if start_el is not None else 1,
                }
            abstract_nums[abs_id] = levels

        # Bước 2: Ánh xạ numId → abstractNumId
        for num_el in root.findall("w:num", NS):
            num_id_attr = num_el.get(f"{{{NS['w']}}}numId")
            if num_id_attr is None:
                continue
            num_id = int(num_id_attr)
            abs_ref = num_el.find("w:abstractNumId", NS)
            if abs_ref is None:
                continue
            abs_id = int(abs_ref.get(f"{{{NS['w']}}}val", "0"))
            self._num_map[num_id] = abstract_nums.get(abs_id, {})

    # ------------------------------------------------------------------
    # Công khai: lấy nhãn cho một đoạn văn có numPr
    # ------------------------------------------------------------------
    def get_label(self, num_id: int, ilvl: int) -> str:
        """
        Trả về nhãn tái tạo (VD: '1.', 'a)', '2.') cho đoạn văn.
        Tự động tăng bộ đếm.

        Args:
            num_id: Giá trị w:numId của đoạn văn.
            ilvl:   Giá trị w:ilvl (cấp thụt lề).

        Returns:
            Chuỗi nhãn, ví dụ '1.' hoặc 'a)'.
        """
        levels = self._num_map.get(num_id, {})
        if ilvl not in levels:
            return ""

        lvl_info = levels[ilvl]
        key = (num_id, ilvl)

        # Khởi tạo bộ đếm nếu chưa có, bắt đầu từ giá trị start-1 để sau increment = start
        if key not in self._counters:
            self._counters[key] = lvl_info["start"] - 1

        # Reset bộ đếm của cấp con khi cấp cha tăng
        self._reset_child_counters(num_id, ilvl)

        self._counters[key] += 1
        count = self._counters[key]

        return self._format_label(lvl_info["numFmt"], lvl_info["lvlText"], count)

    def _reset_child_counters(self, num_id: int, parent_ilvl: int) -> None:
        """Reset bộ đếm của tất cả cấp con (ilvl > parent_ilvl)."""
        levels = self._num_map.get(num_id, {})
        for child_ilvl in levels:
            if child_ilvl > parent_ilvl:
                child_key = (num_id, child_ilvl)
                if child_key in self._counters:
                    del self._counters[child_key]

    @staticmethod
    def _format_label(num_fmt: str, lvl_text: str, count: int) -> str:
        """
        Tái tạo nhãn từ numFmt, lvlText template và bộ đếm hiện tại.

        Ví dụ: numFmt='lowerLetter', lvlText='%1)', count=1 → 'a)'
        """
        if num_fmt == "lowerLetter":
            idx = (count - 1) % 26
            value = _NumXmlParser._ALPHA_LOWER[idx]
        elif num_fmt == "decimal":
            value = str(count)
        elif num_fmt == "upperLetter":
            idx = (count - 1) % 26
            value = _NumXmlParser._ALPHA_LOWER[idx].upper()
        elif num_fmt == "lowerRoman":
            value = _to_roman(count).lower()
        elif num_fmt == "upperRoman":
            value = _to_roman(count).upper()
        else:
            value = str(count)

        # Thay thế placeholder %1, %2, ... trong lvlText
        label = re.sub(r"%(\d+)", lambda m: value, lvl_text)
        return label.strip()


def _to_roman(num: int) -> str:
    """Chuyển số nguyên sang số La Mã (tối đa 3999)."""
    val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    syms = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
    result = ""
    for i, v in enumerate(val):
        while num >= v:
            result += syms[i]
            num -= v
    return result


# ---------------------------------------------------------------------------
# Loader chính: DocxLoader
# ---------------------------------------------------------------------------
class DocxLoader(BaseLoader):
    """
    Loader cho file .docx — ưu tiên dùng pypandoc, tự động fallback sang
    XML parser nếu Pandoc chưa được cài đặt.
    """

    def load(self, path: str | Path) -> list[str]:
        """
        Tải văn bản từ file DOCX, phục hồi đánh số tự động.

        Args:
            path: Đường dẫn tới file .docx.

        Returns:
            Danh sách các dòng văn bản (mỗi dòng là một str, chưa join).

        Raises:
            FileNotFoundError: Nếu file không tồn tại.
            ValueError:        Nếu file không phải .docx.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Không tìm thấy file: {path}")
        if path.suffix.lower() != ".docx":
            raise ValueError(f"DocxLoader chỉ hỗ trợ .docx, nhận được: {path.suffix}")

        # BỎ HOÀN TOÀN pypandoc.
        # Ép dùng bộ phân tích XML tùy chỉnh để giữ được chữ "đ)" của tiếng Việt
        logger.info("[DocxLoader] Đọc file và phục hồi Auto-numbering: %s", path.name)
        return self._load_via_xml(path)

    # ------------------------------------------------------------------
    # Tầng 1: pypandoc
    # ------------------------------------------------------------------
    @staticmethod
    def _try_pypandoc(path: Path) -> Optional[list[str]]:
        """
        Chuyển đổi DOCX sang plain text qua Pandoc.
        Trả về None nếu pypandoc / Pandoc chưa được cài đặt.
        """
        try:
            import pypandoc  # type: ignore
        except ImportError:
            logger.debug("pypandoc chưa được cài. Bỏ qua tầng 1.")
            return None

        try:
            # extra_args đảm bảo Pandoc giữ nguyên danh sách dạng số/chữ
            raw: str = pypandoc.convert_file(
                str(path),
                to="plain",
                format="docx",
                extra_args=["--wrap=none"],
            )
            # Tách theo dòng, giữ nguyên cấu trúc — KHÔNG join
            lines = raw.splitlines()
            return lines
        except Exception as exc:
            logger.warning("[pypandoc] Lỗi khi chuyển đổi '%s': %s", path.name, exc)
            return None

    # ------------------------------------------------------------------
    # Tầng 2: XML fallback
    # ------------------------------------------------------------------
    @staticmethod
    def _load_via_xml(path: Path) -> list[str]:
        """
        Phân tích trực tiếp word/document.xml và word/numbering.xml bằng
        ElementTree + zipfile để phục hồi đánh số tự động.
        """
        try:
            with zipfile.ZipFile(path, "r") as zf:
                doc_xml = zf.read("word/document.xml")
        except (zipfile.BadZipFile, KeyError) as exc:
            logger.error("[XML Fallback] Không thể đọc document.xml: %s", exc)
            return []

        num_parser = _NumXmlParser(path)
        root = ET.fromstring(doc_xml)
        body = root.find(".//w:body", NS)
        if body is None:
            logger.error("[XML Fallback] Không tìm thấy w:body trong document.xml.")
            return []

        lines: list[str] = []
        for para in body.findall("w:p", NS):
            # --- Lấy thuộc tính đánh số ---
            num_id, ilvl = _get_num_props(para)

            # --- Lấy toàn bộ text thuần của đoạn ---
            text_parts: list[str] = []
            for run in para.findall(".//w:r", NS):
                for t_el in run.findall("w:t", NS):
                    text_parts.append(t_el.text or "")
            para_text = "".join(text_parts).strip()

            # --- Gắn nhãn đánh số nếu có ---
            if num_id > 0 and para_text:
                label = num_parser.get_label(num_id, ilvl)
                if label:
                    para_text = f"{label} {para_text}"

            lines.append(para_text)

        return lines


    def load_structured(self, path: str | Path) -> list:
        """
        Tải văn bản từ DOCX và trả về list[StructuredParagraph] — M1→M2 contract.

        Khác với load() (trả về list[str] với label đã render),
        load_structured() GIỮ metadata dưới dạng structured fields:
          - text: nội dung text thuần, KHÔNG có label đứng trước
          - word_style: Word Style name
          - num_id, ilvl, num_fmt: numbering metadata
          - number: giá trị counter đã tính (int hoặc str), None nếu không có
          - marker: ký tự POINT (a, b, đ...), None nếu không phải POINT
          - is_empty: True nếu text trống

        Thiết kế theo RQ6: bảo toàn thông tin cấu trúc xuyên suốt preprocessing.
        Khi nào mà M2 cần recover hierarchy, nó dùng metadata này thay vì
        phải suy diễn lại từ text đã bị render.

        Args:
            path: Đường dẫn tới file .docx.

        Returns:
            list[StructuredParagraph] — sẵn sàng truyền vào LegalParser.parse_structured().
        """
        # Import ở đây để tránh circular dependency nếu contracts.py nằm cùng package
        import sys as _sys
        _contracts_path = str(Path(__file__).resolve().parents[1])
        if _contracts_path not in _sys.path:
            _sys.path.insert(0, _contracts_path)
        from contracts import StructuredParagraph

        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Không tìm thấy file: {path}")
        if path.suffix.lower() != ".docx":
            raise ValueError(f"load_structured chỉ hỗ trợ .docx, nhận được: {path.suffix}")

        logger.info("[DocxLoader] load_structured: %s", path.name)

        try:
            with zipfile.ZipFile(path, "r") as zf:
                doc_xml = zf.read("word/document.xml")
        except (zipfile.BadZipFile, KeyError) as exc:
            logger.error("[load_structured] Không thể đọc document.xml: %s", exc)
            return []

        num_parser = _NumXmlParser(path)
        root = ET.fromstring(doc_xml)
        body = root.find(".//w:body", NS)
        if body is None:
            return []

        paragraphs: list[StructuredParagraph] = []
        for idx, para in enumerate(body.findall("w:p", NS)):
            # Numbering metadata
            num_id, ilvl = _get_num_props(para)

            # Word Style name
            word_style = _get_word_style(para)

            # Text thuần — KHÔNG gắn label
            text_parts: list[str] = []
            for run in para.findall(".//w:r", NS):
                for t_el in run.findall("w:t", NS):
                    text_parts.append(t_el.text or "")
            para_text = "".join(text_parts).strip()

            # Numbering metadata đầy đủ (chỉ khi có num_id > 0)
            p_num_id:  int | None = None
            p_ilvl:    int | None = None
            p_num_fmt: str | None = None
            p_number:  object | None = None
            p_marker:  str | None = None

            if num_id > 0 and para_text:
                levels = num_parser._num_map.get(num_id, {})
                lvl_info = levels.get(ilvl)
                if lvl_info:
                    p_num_id  = num_id
                    p_ilvl    = ilvl
                    p_num_fmt = lvl_info["numFmt"]

                    # Tính counter (tăng bộ đếm nội bộ)
                    counter_key = (num_id, ilvl)
                    if counter_key not in num_parser._counters:
                        num_parser._counters[counter_key] = lvl_info["start"] - 1
                    num_parser._reset_child_counters(num_id, ilvl)
                    num_parser._counters[counter_key] += 1
                    count = num_parser._counters[counter_key]

                    # Tách number (ordinal) và marker (letter) theo num_fmt
                    fmt = lvl_info["numFmt"]
                    if fmt == "decimal":
                        p_number = count        # int: 1, 2, 3...
                    elif fmt == "lowerLetter":
                        alpha = "abcdefghijklmnopqrstuvwxyz"
                        idx_letter = (count - 1) % 26
                        p_marker = alpha[idx_letter]   # str: "a", "b", "k", "o"...
                    elif fmt in ("lowerRoman", "upperRoman"):
                        p_number = _to_roman(count).upper() if fmt == "upperRoman" else _to_roman(count).lower()
                    elif fmt in ("upperLetter",):
                        p_number = chr(ord('A') + (count - 1) % 26)
                    else:
                        p_number = count  # fallback

            paragraphs.append(StructuredParagraph(
                index=idx,
                text=para_text,
                word_style=word_style,
                num_id=p_num_id,
                ilvl=p_ilvl,
                num_fmt=p_num_fmt,
                number=p_number,
                marker=p_marker,
                is_empty=(para_text.strip() == ""),
            ))

        logger.info("[load_structured] Đã trích xuất %d paragraphs.", len(paragraphs))
        return paragraphs




def _get_num_props(para: ET.Element) -> tuple[int, int]:
    """
    Trích xuất (numId, ilvl) từ thuộc tính w:numPr của đoạn văn.
    Trả về (0, 0) nếu đoạn không có đánh số tự động.
    """
    ppr = para.find("w:pPr", NS)
    if ppr is None:
        return 0, 0
    num_pr = ppr.find("w:numPr", NS)
    if num_pr is None:
        return 0, 0

    ilvl_el = num_pr.find("w:ilvl", NS)
    num_id_el = num_pr.find("w:numId", NS)

    ilvl = int(ilvl_el.get(f"{{{NS['w']}}}val", "0")) if ilvl_el is not None else 0
    num_id = int(num_id_el.get(f"{{{NS['w']}}}val", "0")) if num_id_el is not None else 0
    return num_id, ilvl



def _get_word_style(para: ET.Element) -> str | None:
    """
    Trích xuất Word Style name từ w:pStyle của đoạn văn.
    Trả về None nếu không có style.

    Ví dụ: "List Paragraph", "Heading 2", "Body Text", "Normal".
    """
    ppr = para.find("w:pPr", NS)
    if ppr is None:
        return None
    pstyle = ppr.find("w:pStyle", NS)
    if pstyle is None:
        return None
    return pstyle.get(f"{{{NS['w']}}}val")




# ---------------------------------------------------------------------------
# Loader đơn giản cho .txt (mở rộng tương lai)
# ---------------------------------------------------------------------------
class TxtLoader(BaseLoader):
    """Loader đơn giản cho file .txt thuần túy."""

    def load(self, path: str | Path) -> list[str]:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Không tìm thấy file: {path}")
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read().splitlines()


    def load_structured(self, path: str | Path) -> list:
        """
        Trả về list[StructuredParagraph] từ file .txt.

        TXT path — information loss đã xảy ra:
          - word_style = None (không có Word Style)
          - num_id = None (không có numbering metadata)
          - ilvl = None
          - num_fmt = None
          - number = None (không biết số thứ tự pháp lý)
          - marker = None (không biết ký tự điểm)

        Đây là honest representation của information loss.
        Module 2 sẽ phải dùng Regex + Context (Lớp 2+3) để xử lý.
        So sánh với DOCX path (4 tín hiệu) giúp đo information loss — RQ6.

        PDF: KHÔNG hỗ trợ. Xem limitation notes.
        """
        import sys as _sys
        _contracts_path = str(Path(__file__).resolve().parents[1])
        if _contracts_path not in _sys.path:
            _sys.path.insert(0, _contracts_path)
        from contracts import txt_paragraph

        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Không tìm thấy file: {path}")

        lines = self.load(path)
        return [txt_paragraph(index=i, text=line) for i, line in enumerate(lines)]





# ---------------------------------------------------------------------------
# Factory tiện ích
# ---------------------------------------------------------------------------
def get_loader(path: str | Path) -> BaseLoader:
    """
    Trả về loader phù hợp dựa vào phần mở rộng của file.

    Args:
        path: Đường dẫn tới file đầu vào.

    Returns:
        Instance của loader tương ứng.

    Raises:
        ValueError: Nếu không có loader nào hỗ trợ định dạng file.
    """
    suffix = Path(path).suffix.lower()
    loaders: dict[str, BaseLoader] = {
        ".docx": DocxLoader(),
        ".txt":  TxtLoader(),
    }
    if suffix not in loaders:
        raise ValueError(
            f"Không hỗ trợ định dạng '{suffix}'. "
            f"Các định dạng được hỗ trợ: {list(loaders.keys())}"
        )
    return loaders[suffix]
