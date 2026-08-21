
# -*- coding: utf-8 -*-
"""
parser.py — Module 2: Regex Parser
Orchestrator — chạy toàn bộ pipeline Module 2.

Pipeline:
  Input (DOCX / plain text)
       ↓
  [1] RegexEngine.match_*()        — Lớp 2 (Text) + Lớp 1 (Style nếu DOCX)
       ↓
  [2] BoundaryDetector.detect()    — Tìm start/end của từng node
       ↓
  [3] HierarchyBuilder.build()     — Xây Parent-Child tree
       ↓
  [4] NodeGenerator.generate()     — Sinh Legal Node JSON
       ↓
  Output: list[dict] Legal Nodes JSON

Usage:
  # DOCX mode (tận dụng Word Style)
  parser = LegalParser(law_prefix="ldd-2024", law_code="59/2024/QH15")
  nodes = parser.parse_docx("Luat_dat_dai_chuong_3.docx")
  parser.save_json(nodes, "legal_nodes_ch3.json")

  # Plain text mode (fallback)
  nodes = parser.parse_text("clean_text.txt")
"""

import json
import sys
import os
from pathlib import Path
from typing import Optional

# Add parent dir to path nếu cần
sys.path.insert(0, os.path.dirname(__file__))

from regex_engine import RegexEngine, load_docx_paragraphs, load_text_lines
from boundary_detector import BoundaryDetector
from hierarchy_builder import HierarchyBuilder
from node_generator import NodeGenerator


# ---------------------------------------------------------------------------
# ParseResult — kết quả của một lần parse
# ---------------------------------------------------------------------------
class ParseResult:
    def __init__(
        self,
        nodes: list[dict],
        orphans: list = None,
        gaps: list = None,
        stats: dict = None,
    ):
        self.nodes = nodes
        self.orphans = orphans or []
        self.gaps = gaps or []
        self.stats = stats or {}

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.nodes, ensure_ascii=False, indent=indent)

    def print_summary(self):
        print("=" * 60)
        print("MODULE 2 — PARSE RESULT SUMMARY")
        print("=" * 60)
        for k, v in self.stats.items():
            print(f"  {k:30s}: {v}")
        if self.orphans:
            print(f"\n  ⚠ Orphan nodes ({len(self.orphans)}):")
            for o in self.orphans[:5]:
                print(f"    - {o.temp_id()} (parent={o.parent_id})")
        if self.gaps:
            print(f"\n  ⚠ Sequence gaps ({len(self.gaps)}):")
            for g in self.gaps[:5]:
                print(f"    - {g}")
        print("=" * 60)


# ---------------------------------------------------------------------------
# LegalParser — Orchestrator
# ---------------------------------------------------------------------------
class LegalParser:
    """
    Orchestrator cho Module 2: Regex Parser.

    Hỗ trợ 2 mode:
      - DOCX mode: tận dụng Word Style (Lớp 1 tín hiệu)
      - Plain text mode: chỉ dùng Regex (Lớp 2 tín hiệu)

    [HYPOTHESIS] Chiến lược hiện tại: Phương án A (single-pass với scope hint).
    Chưa benchmark với Phương án B (strict 2-pass container).
    """

    def __init__(
        self,
        law_prefix: str = "doc",
        law_code: Optional[str] = None,
        source_doc: str = "",
    ):
        self.regex_engine = RegexEngine()
        self.boundary_detector = BoundaryDetector()
        self.hierarchy_builder = HierarchyBuilder()
        self.node_generator = NodeGenerator(
            law_prefix=law_prefix,
            law_code=law_code,
            source_doc=source_doc,
        )

    # -----------------------------------------------------------------------
    # Public: parse từ DOCX (Recommended — có Style signal)
    # -----------------------------------------------------------------------
    def parse_docx(self, filepath: str) -> ParseResult:
        """
        Parse từ file DOCX.
        Tận dụng Word Style (Lớp 1 tín hiệu) + Regex (Lớp 2).

        Args:
            filepath: Đường dẫn đến file .docx

        Returns:
            ParseResult với danh sách Legal Node JSON.
        """
        self.node_generator.source_doc = Path(filepath).name
        paragraphs = load_docx_paragraphs(filepath)

        # Lớp 2 + Lớp 1: match với style hint
        match_results = self.regex_engine.match_paragraphs(paragraphs)

        return self._run_pipeline(
            input_units=paragraphs,
            match_results=match_results,
            mode="docx",
        )

    # -----------------------------------------------------------------------
    # Public: parse từ plain text (fallback khi không có DOCX)
    # -----------------------------------------------------------------------
    def parse_text(self, filepath: str) -> ParseResult:
        """
        Parse từ plain text file.
        Chỉ dùng Regex (Lớp 2 tín hiệu). Không có Style signal.

        Args:
            filepath: Đường dẫn đến file .txt

        Returns:
            ParseResult với danh sách Legal Node JSON.
        """
        self.node_generator.source_doc = Path(filepath).name
        lines = load_text_lines(filepath)
        match_results = self.regex_engine.match_lines(lines)

        return self._run_pipeline(
            input_units=lines,
            match_results=match_results,
            mode="text",
        )

    # -----------------------------------------------------------------------
    # Public: parse từ StructuredParagraph (M1→M2 contract)
    # -----------------------------------------------------------------------
    def parse_structured(self, paragraphs: list, source_doc: str = "") -> ParseResult:
        """
        Parse từ danh sách StructuredParagraph — interface chính của M1→M2 contract.

        Thay thế parse_docx() + parse_text() khi M1 đã trích xuất metadata.
        M2 không tự đọc lại DOCX khi sử dụng method này.

        Args:
            paragraphs:  list[StructuredParagraph] từ DocxLoader.load_structured()
                         hoặc TxtLoader.load_structured().
            source_doc:  Tên file nguồn (để ghi vào Legal Node JSON).

        Returns:
            ParseResult với danh sách Legal Node JSON.

        Flow:
            StructuredParagraph
              → to_engine_dict()  (giữ ilvl, num_fmt, number, marker)
              → RegexEngine.match_paragraphs()  (dùng ilvl+num_fmt hints)
              → _merge_contract_metadata()  (ghi number/marker từ M1 vào MatchResult)
              → BoundaryDetector / HierarchyBuilder / NodeGenerator
        """
        import sys as _sys
        import os as _os
        _contracts_path = _os.path.join(_os.path.dirname(__file__), "..", "..")
        if _contracts_path not in _sys.path:
            _sys.path.insert(0, _contracts_path)

        if source_doc:
            self.node_generator.source_doc = source_doc

        # Phân biệt DOCX và TXT path dựa vào metadata availability
        has_metadata = any(getattr(p, "has_metadata", False) for p in paragraphs)
        mode = "structured_docx" if has_metadata else "structured_txt"

        # Chuyển StructuredParagraph → dict (RegexEngine nhận dict)
        para_dicts = [p.to_engine_dict() for p in paragraphs]

        # Lớp 1+2 matching — RegexEngine sẽ dùng ilvl+num_fmt từ dict
        match_results = self.regex_engine.match_paragraphs(para_dicts)

        # Ghi number/marker từ M1 contract vào MatchResult (nguồn chính xác hơn Regex)
        # M1 đã tính sẵn counter — không để Regex ghi đè
        match_results = self._merge_contract_metadata(match_results, paragraphs)

        return self._run_pipeline(
            input_units=para_dicts,
            match_results=match_results,
            mode=mode,
        )

    @staticmethod
    def _merge_contract_metadata(match_results: list, paragraphs: list) -> list:
        """
        Ghi number / marker từ StructuredParagraph vào MatchResult.

        Lý do: RegexEngine có thể không extract được number nếu text không có label.
        M1 đã tính sẵn từ numbering XML — đây là nguồn truth.

        Rule:
          - Nếu paragraph.number is not None → ghi vào match.number (override)
          - Nếu paragraph.marker is not None → ghi vào match.marker (override)
          - Nếu match is None → bỏ qua
        """
        for match, para in zip(match_results, paragraphs):
            if match is None:
                continue
            p_number = getattr(para, "number", None)
            p_marker = getattr(para, "marker", None)
            if p_number is not None:
                match.number = str(p_number)  # MatchResult.number là str
            if p_marker is not None:
                match.marker = p_marker
        return match_results


    # -----------------------------------------------------------------------
    # Public: save output
    # -----------------------------------------------------------------------
    def save_json(self, result: ParseResult, output_path: str, indent: int = 2):
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result.nodes, f, ensure_ascii=False, indent=indent)
        print(f"[Module 2] Saved {len(result.nodes)} nodes -> {output_path}")

    # -----------------------------------------------------------------------
    # Internal: pipeline chính
    # -----------------------------------------------------------------------
    def _run_pipeline(
        self,
        input_units: list,
        match_results: list,
        mode: str,
    ) -> ParseResult:
        """Chạy pipeline sau khi đã có match_results."""

        # Bước 2: Boundary Detection
        boundaries = self.boundary_detector.detect(input_units, match_results)

        # Bước 3: Hierarchy Building
        hierarchy_nodes = self.hierarchy_builder.build(boundaries)

        # Kiểm tra cơ bản (sẽ chuyển sang Module 3 để xử lý đầy đủ hơn)
        orphans = self.hierarchy_builder.check_orphans(hierarchy_nodes)
        gaps = self.hierarchy_builder.check_gaps(hierarchy_nodes)

        # Bước 4: Node Generation
        legal_nodes = self.node_generator.generate(hierarchy_nodes)

        # Thống kê
        from collections import Counter
        type_counts = Counter(n["type"] for n in legal_nodes)
        stats = {
            "mode":          mode,
            "total_nodes":   len(legal_nodes),
            "orphan_count":  len(orphans),
            "gap_count":     len(gaps),
            **{f"count_{k}": v for k, v in type_counts.items()},
        }

        return ParseResult(
            nodes=legal_nodes,
            orphans=orphans,
            gaps=gaps,
            stats=stats,
        )


# ---------------------------------------------------------------------------
# CLI — chạy trực tiếp để test
# ---------------------------------------------------------------------------
def process_single_file(parser: LegalParser, input_path: Path, output_path: Path):
    if input_path.suffix.lower() == ".docx":
        result = parser.parse_docx(str(input_path))
    else:
        result = parser.parse_text(str(input_path))

    result.print_summary()
    
    # Fail-Fast: duplicate ID check
    seen_ids = set()
    for node in result.nodes:
        if node["id"] in seen_ids:
            import logging
            duplicate_id = node["id"]
            logging.error("CRITICAL: ID Collision detected: %s", duplicate_id)
            raise ValueError(f"ID Collision detected: {duplicate_id}")
        seen_ids.add(node["id"])
        
    parser.save_json(result, str(output_path))
    
    print("\n[Sample output - first 3 nodes]:")
    for node in result.nodes[:3]:
        print(json.dumps(node, ensure_ascii=False, indent=2))
        
def main():
    import argparse

    ap = argparse.ArgumentParser(description="Module 2 — Legal Regex Parser")
    ap.add_argument("input", nargs="?", default="outputs/clean_texts",
                    help="Đường dẫn file input (.docx hoặc .txt) HOẶC thư mục (mặc định: outputs/clean_texts)")
    ap.add_argument("--output", "-o", default="outputs/physical_graphs",
                    help="Thư mục output (mặc định: outputs/physical_graphs) hoặc file output JSON cụ thể")
    ap.add_argument("--law-prefix", default="doc",
                    help="Prefix cho document ID (vd: ldd-2024)")
    ap.add_argument("--law-code", default=None,
                    help="Mã văn bản pháp luật (vd: 59/2024/QH15)")
    args = ap.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    
    # Tạo thư mục output nếu chưa có
    if not output_path.exists() and output_path.suffix == "":
        output_path.mkdir(parents=True, exist_ok=True)

    if input_path.is_file():
        parser = LegalParser(
            law_prefix=args.law_prefix,
            law_code=args.law_code,
            source_doc=input_path.name,
        )
        if output_path.is_dir() or output_path.suffix == "":
            final_out = output_path / f"raw_nodes_{input_path.stem}.json"
        else:
            final_out = output_path
            final_out.parent.mkdir(parents=True, exist_ok=True)
            
        process_single_file(parser, input_path, final_out)
        
    elif input_path.is_dir():
        if output_path.suffix != "":
            print("Lỗi: Khi input là thư mục, output cũng phải là một thư mục.")
            return
            
        valid_files = [f for f in input_path.iterdir() if f.is_file() and f.suffix.lower() in [".txt", ".docx"]]
        print(f"Tìm thấy {len(valid_files)} file hợp lệ trong thư mục {input_path}")
        
        for file in valid_files:
            print(f"\n--- Đang xử lý: {file.name} ---")
            parser = LegalParser(
                law_prefix=args.law_prefix,
                law_code=args.law_code,
                source_doc=file.name,
            )
            final_out = output_path / f"raw_nodes_{file.stem}.json"
            process_single_file(parser, file, final_out)
    else:
        print(f"Không tìm thấy file hoặc thư mục: {args.input}")

if __name__ == "__main__":
    main()

