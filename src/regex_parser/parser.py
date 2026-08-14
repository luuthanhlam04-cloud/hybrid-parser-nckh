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
def main():
    import argparse

    ap = argparse.ArgumentParser(description="Module 2 — Legal Regex Parser")
    ap.add_argument("input", help="Đường dẫn file input (.docx hoặc .txt)")
    ap.add_argument("--output", "-o", default="legal_nodes.json",
                    help="File output JSON (default: legal_nodes.json)")
    ap.add_argument("--law-prefix", default="doc",
                    help="Prefix cho document ID (vd: ldd-2024)")
    ap.add_argument("--law-code", default=None,
                    help="Mã văn bản pháp luật (vd: 59/2024/QH15)")
    args = ap.parse_args()

    parser = LegalParser(
        law_prefix=args.law_prefix,
        law_code=args.law_code,
        source_doc=Path(args.input).name,
    )

    if args.input.lower().endswith(".docx"):
        result = parser.parse_docx(args.input)
    else:
        result = parser.parse_text(args.input)

    result.print_summary()
    parser.save_json(result, args.output)

    # In 3 node đầu để kiểm tra nhanh
    print("\n[Sample output - first 3 nodes]:")
    for node in result.nodes[:3]:
        print(json.dumps(node, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
