"""Run Module 8 fusion on the current M4 and M7 outputs."""

import json
from pathlib import Path

from src.fusion import FusionEngine, ShaclValidator
from src.fusion.confidence_calibration import IsotonicConfidenceCalibrator


ROOT = Path(__file__).parent
PHYSICAL = ROOT / "outputs" / "physical_graphs" / "physical_graph.json"
SEMANTIC_CANDIDATES = (
    ROOT / "outputs" / "semantic_graphs" / "canonical_semantic_graph.json",
    ROOT / "outputs" / "canonical_graphs" / "canonical_semantic_graph.json",
)
OUTPUT = ROOT / "outputs" / "unified_graphs" / "unified_knowledge_graph.json"
CONFLICTS = ROOT / "outputs" / "unified_graphs" / "fusion_conflicts.json"
SHACL_REPORT = ROOT / "outputs" / "unified_graphs" / "fusion_shacl_report.json"
CALIBRATOR = ROOT / "outputs" / "evaluation" / "fusion_confidence_calibrator.json"


def main() -> None:
    available_semantic = [path for path in SEMANTIC_CANDIDATES if path.exists()]
    semantic = (
        max(available_semantic, key=lambda path: path.stat().st_mtime)
        if available_semantic else None
    )
    if not PHYSICAL.exists():
        raise FileNotFoundError(f"Physical graph not found: {PHYSICAL}")
    if semantic is None:
        raise FileNotFoundError("Canonical semantic graph not found")
    calibrator = (
        IsotonicConfidenceCalibrator.load(CALIBRATOR)
        if CALIBRATOR.exists() else None
    )
    result = FusionEngine(confidence_calibrator=calibrator).fuse(
        PHYSICAL, semantic
    )
    CONFLICTS.parent.mkdir(parents=True, exist_ok=True)
    CONFLICTS.write_text(
        json.dumps(result["conflicts"], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    conforms, report_text, report_turtle = ShaclValidator().validate(result)
    SHACL_REPORT.write_text(
        json.dumps(
            {
                "conforms": conforms,
                "report_text": report_text,
                "report_turtle": report_turtle,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    if not conforms:
        raise RuntimeError(
            f"Unified graph failed SHACL validation. See {SHACL_REPORT}"
        )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(result["metadata"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
