# -*- coding: utf-8 -*-
"""
run_ontology_builder.py — Script chạy thử M7

Chạy:
    python run_ontology_builder.py

Output:
    outputs/canonical_graphs/canonical_semantic_graph.json
"""

import json
import logging
import sys
from pathlib import Path

# Fix Unicode on Windows console
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Thêm project root vào PYTHONPATH
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.ontology.ontology_builder import OntologyBuilder

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("outputs/m7_run.log", encoding="utf-8", mode="w"),
    ],
)
logger = logging.getLogger(__name__)


def main():
    # Paths
    m6_path = PROJECT_ROOT / "outputs" / "semantic_graphs" / "semantic_extraction.json"
    output_path = PROJECT_ROOT / "outputs" / "canonical_graphs" / "canonical_semantic_graph.json"

    # Physical graph (M4) — nếu tồn tại
    physical_graph_candidates = [
        PROJECT_ROOT / "outputs" / "physical_graphs" / "physical_graph.json",
        PROJECT_ROOT / "outputs" / "graph" / "physical_graph.json",
        PROJECT_ROOT / "outputs" / "physical_graph.json",
    ]
    physical_graph_path = None
    for candidate in physical_graph_candidates:
        if candidate.exists():
            physical_graph_path = candidate
            logger.info(f"Found Physical Graph at: {candidate}")
            break

    if not m6_path.exists():
        logger.error(f"M6 file không tìm thấy: {m6_path}")
        sys.exit(1)

    # Chạy M7
    builder = OntologyBuilder()
    graph = builder.build(
        m6_path=m6_path,
        physical_graph_path=physical_graph_path,
        output_path=output_path,
    )

    # In summary report
    report = graph.validation_report
    print("\n" + "=" * 60)
    print("MODULE 7 — VALIDATION REPORT")
    print("=" * 60)
    print(f"  LocalMentions  : {report.total_mentions}")
    print(f"    VALID        : {report.valid_mentions}")
    print(f"    CORRECTED    : {report.corrected_mentions}")
    print(f"    UNRESOLVED   : {report.unresolved_mentions}")
    print(f"  NormAssertions : {report.total_norms}")
    print(f"    VALID        : {report.valid_norms}")
    print(f"    FLAGGED      : {report.flagged_norms}")
    print(f"  CanonicalConc. : {report.total_concepts}")
    print(f"  Edges          : {report.total_edges}")
    print(f"    REJECTED     : {report.rejected_edges}")
    print(f"  References     : {report.resolved_references}/{report.total_references} resolved")
    print(f"    UNRESOLVED   : {report.unresolved_references}")

    if report.rejected_reasons:
        print(f"\n  Rejected reasons ({len(report.rejected_reasons)}):")
        for i, r in enumerate(report.rejected_reasons[:10], 1):
            print(f"    [{i}] {r}")
        if len(report.rejected_reasons) > 10:
            print(f"    ... (và {len(report.rejected_reasons) - 10} lỗi khác)")

    print("=" * 60)
    print(f"\nOutput: {output_path}")


if __name__ == "__main__":
    main()
