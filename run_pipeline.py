"""Run the configured legal-text processing stages from M1 through M8."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any, Callable

from src.fusion import FusionEngine, ShaclValidator
from src.fusion.confidence_calibration import IsotonicConfidenceCalibrator
from src.llm_extraction.structured_extractor import StructuredExtractor
from src.ontology.ontology_builder import OntologyBuilder
from src.physical_graph.graph_builder import PhysicalGraphBuilder
from src.preprocessing.clean_document import run_pipeline as preprocess_document
from src.preprocessing.document_loader import DocxLoader
from src.regex_parser.parser import LegalParser
from src.validation import ValidationEngine


ROOT = Path(__file__).resolve().parent
OUTPUTS = ROOT / "outputs"
STAGES = ("M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8")
RAW_NODES = OUTPUTS / "physical_graphs" / "raw_nodes_pipeline.json"
VALIDATED_NODES = OUTPUTS / "physical_graphs" / "validated_nodes.json"
VALIDATION_REPORT = OUTPUTS / "physical_graphs" / "validation_report.json"
PHYSICAL_GRAPH = OUTPUTS / "physical_graphs" / "physical_graph.json"
ROUTING_CANDIDATES = OUTPUTS / "candidate_nodes" / "routing_candidates.json"
M6_GRAPH = OUTPUTS / "semantic_graphs" / "semantic_extraction.json"
M7_GRAPH = OUTPUTS / "canonical_graphs" / "canonical_semantic_graph.json"
M7_GRAPH_CANDIDATES = (
    OUTPUTS / "semantic_graphs" / "canonical_semantic_graph.json",
    M7_GRAPH,
)
UKG = OUTPUTS / "unified_graphs" / "unified_knowledge_graph.json"


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(
            f"Stage input is missing: {path}. Run its prerequisite stage(s) first."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def _run_parse(input_path: Path, law_code: str | None) -> None:
    law_prefix = "".join(char.lower() if char.isalnum() else "_" for char in input_path.stem)
    parser = LegalParser(
        law_prefix=law_prefix.strip("_") or "doc",
        law_code=law_code,
        source_doc=input_path.name,
    )
    if input_path.suffix.casefold() == ".docx":
        paragraphs = DocxLoader().load_structured(input_path)
        parsed = parser.parse_structured(paragraphs, source_doc=input_path.name)
    elif input_path.suffix.casefold() == ".txt":
        cleaned = OUTPUTS / "clean_texts" / f"clean_{input_path.stem}.txt"
        preprocess_document(input_path, cleaned)
        parsed = parser.parse_text(cleaned)
    else:
        raise ValueError("Input must be a .docx or .txt legal document")
    for node in parsed.nodes:
        node.setdefault("properties", {})["source_doc"] = input_path.name
        if law_code:
            node["properties"]["law_code"] = law_code
    ids = [node["id"] for node in parsed.nodes]
    if len(ids) != len(set(ids)):
        raise ValueError("M2 generated duplicate node IDs; refusing to continue")
    _write_json(RAW_NODES, parsed.nodes)
    print(f"M1/M2: extracted {len(parsed.nodes)} physical nodes -> {RAW_NODES}")


def _run_validation() -> None:
    report = ValidationEngine(
        input_path=str(RAW_NODES),
        validated_output_path=str(VALIDATED_NODES),
        report_output_path=str(VALIDATION_REPORT),
    ).run()
    summary = report["summary"]
    print(
        f"M3: {summary['total_nodes_validated']}/"
        f"{summary['total_nodes_received']} nodes validated"
    )


def _run_physical_graph() -> None:
    graph = PhysicalGraphBuilder(
        input_path=VALIDATED_NODES,
        output_path=PHYSICAL_GRAPH,
    ).build()
    PHYSICAL_GRAPH.parent.mkdir(parents=True, exist_ok=True)
    _write_json(PHYSICAL_GRAPH, graph)
    print(f"M4: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges")


def _run_router(force: bool) -> None:
    from run_semantic_router import ensure_routing_candidates

    ensure_routing_candidates(
        input_file=str(PHYSICAL_GRAPH),
        output_file=str(ROUTING_CANDIDATES),
        force=force,
    )


def _run_extraction(limit: int, node_ids: list[str]) -> None:
    extractor = StructuredExtractor(
        str(ROUTING_CANDIDATES), str(PHYSICAL_GRAPH)
    )
    extracted = extractor.run_extraction(limit=limit, node_ids=node_ids or None)
    extractor.export(extracted, str(M6_GRAPH))
    print(
        f"M6: extracted {len(extracted.get('extracted_nodes', []))} nodes "
        f"-> {M6_GRAPH}"
    )


def _run_ontology() -> None:
    graph = OntologyBuilder().build(
        m6_path=M6_GRAPH,
        physical_graph_path=PHYSICAL_GRAPH,
        output_path=M7_GRAPH,
    )
    print(
        f"M7: {graph.validation_report.total_concepts} concepts, "
        f"{graph.validation_report.total_edges} semantic edges"
    )


def _run_fusion() -> None:
    calibrator_path = OUTPUTS / "evaluation" / "fusion_confidence_calibrator.json"
    calibrator = (
        IsotonicConfidenceCalibrator.load(calibrator_path)
        if calibrator_path.exists() else None
    )
    semantic_candidates = [path for path in M7_GRAPH_CANDIDATES if path.exists()]
    if not semantic_candidates:
        raise FileNotFoundError(
            "M7 graph missing; run M7 first. Searched: "
            + ", ".join(map(str, M7_GRAPH_CANDIDATES))
        )
    semantic_graph = max(semantic_candidates, key=lambda path: path.stat().st_mtime)
    result = FusionEngine(confidence_calibrator=calibrator).fuse(
        PHYSICAL_GRAPH, semantic_graph
    )
    conforms, report_text, report_turtle = ShaclValidator().validate(result)
    _write_json(
        OUTPUTS / "unified_graphs" / "fusion_conflicts.json",
        result["conflicts"],
    )
    _write_json(
        OUTPUTS / "unified_graphs" / "fusion_shacl_report.json",
        {
            "conforms": conforms,
            "report_text": report_text,
            "report_turtle": report_turtle,
        },
    )
    if not conforms:
        raise RuntimeError("M8 SHACL validation failed; see fusion_shacl_report.json")
    _write_json(UKG, result)
    print(
        f"M8: {result['metadata']['total_node_count']} nodes, "
        f"{len(result['edges'])} edges, "
        f"{result['metadata']['conflict_count']} conflicts; SHACL conforms"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="Input legal document (.docx or .txt)")
    parser.add_argument("--from-stage", choices=STAGES, default="M1")
    parser.add_argument("--to-stage", choices=STAGES, default="M8")
    parser.add_argument("--law-code", help="Optional law identifier, e.g. 59/2024/QH15")
    parser.add_argument("--force-m5", action="store_true", help="Ignore M5 routing cache")
    parser.add_argument(
        "--allow-llm", action="store_true",
        help="Explicitly allow M6 OpenRouter API calls that may incur costs",
    )
    parser.add_argument(
        "--m6-limit", type=int,
        help="Maximum number of M6 candidate nodes; required with --allow-llm",
    )
    parser.add_argument(
        "--node-id", action="append", default=[],
        help="M6 candidate node ID to include; may be repeated",
    )
    args = parser.parse_args()
    first, last = STAGES.index(args.from_stage), STAGES.index(args.to_stage)
    if first > last:
        parser.error("--from-stage must not come after --to-stage")
    stages = STAGES[first:last + 1]
    if any(stage in stages for stage in ("M1", "M2")) and args.input is None:
        parser.error("--input is required when running M1/M2")
    if "M6" in stages:
        if not args.allow_llm:
            parser.error("M6 calls the paid LLM API; pass --allow-llm to opt in")
        if args.m6_limit is None or args.m6_limit < 1:
            parser.error("M6 requires an explicit positive --m6-limit")

    actions: dict[str, Callable[[], None]] = {
        "M3": _run_validation,
        "M4": _run_physical_graph,
        "M5": lambda: _run_router(args.force_m5),
        "M6": lambda: _run_extraction(args.m6_limit, args.node_id),
        "M7": _run_ontology,
        "M8": _run_fusion,
    }
    logging.basicConfig(level=logging.INFO)
    parse_ran = False
    for stage in stages:
        if stage in {"M1", "M2"}:
            if not parse_ran:
                _run_parse(args.input.resolve(), args.law_code)
                parse_ran = True
            continue
        print(f"\n=== Running {stage} ===")
        actions[stage]()
    print("\nPipeline completed.")


if __name__ == "__main__":
    main()
