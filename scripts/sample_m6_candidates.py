"""Select complex M5 candidates for a bounded, manually approved M6 run."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ANAPHORA = re.compile(r"\b(?:điều|khoản|mục|chương) này\b", re.IGNORECASE)
REFERENCES = re.compile(
    r"\b(?:khoản|điều|điểm|mục|chương)\s+(?:\d+|[ivxlcdm]+)\b",
    re.IGNORECASE,
)
MODALITIES = re.compile(
    r"\b(?:được|phải|có quyền|có nghĩa vụ|không được|nghiêm cấm|bị cấm)\b",
    re.IGNORECASE,
)
CONDITIONS = re.compile(
    r"\b(?:trừ trường hợp|trong trường hợp|nếu|khi|với điều kiện)\b",
    re.IGNORECASE,
)


def _complexity(text: str) -> tuple[float, list[str]]:
    signals: list[str] = []
    score = 0.0
    if len(text) >= 500:
        score += 1.0
        signals.append("long_provision")
    if len(re.findall(r"(?:^|\n)\s*(?:[-•]|\d+[.)]|[a-zđ][.)])", text, re.I)) >= 2:
        score += 2.0
        signals.append("enumeration")
    if ANAPHORA.search(text):
        score += 2.0
        signals.append("anaphoric_reference")
    reference_count = len(REFERENCES.findall(text))
    if reference_count:
        score += min(2.0, 0.5 * reference_count)
        signals.append("explicit_citation")
    if CONDITIONS.search(text):
        score += 2.0
        signals.append("condition_or_exception")
    modality_count = len(MODALITIES.findall(text))
    if modality_count >= 2:
        score += 1.0
        signals.append("multiple_normative_markers")
    return score, signals


def sample_m6_candidates(
    candidates_path: Path,
    physical_graph_path: Path,
    output_path: Path,
    limit: int = 10,
) -> list[dict[str, Any]]:
    if limit < 1:
        raise ValueError("Candidate sample size must be positive")
    candidates = json.loads(candidates_path.read_text(encoding="utf-8"))
    physical_graph = json.loads(physical_graph_path.read_text(encoding="utf-8"))
    node_text = {
        str(node.get("id")): str(node.get("properties", {}).get("text", ""))
        for node in physical_graph.get("nodes", [])
    }
    ranked = []
    for candidate in candidates.get("candidates", []):
        if candidate.get("route") != "LLM_CANDIDATE":
            continue
        node_id = str(candidate.get("node_id", ""))
        text = node_text.get(node_id, "")
        if not node_id or not text:
            continue
        score, signals = _complexity(text)
        ranked.append({
            "node_id": node_id,
            "complexity_score": score,
            "signals": signals,
            "text_length": len(text),
        })
    ranked.sort(
        key=lambda item: (-item["complexity_score"], -item["text_length"], item["node_id"])
    )
    selected = ranked[:limit]
    if not selected:
        raise ValueError("No text-backed LLM_CANDIDATE nodes were available")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(
            {
                "selection_method": "rule-based complexity ranking",
                "limit": limit,
                "selected_candidates": selected,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return selected


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--candidates",
        type=Path,
        default=Path("outputs/candidate_nodes/routing_candidates.json"),
    )
    parser.add_argument(
        "--physical-graph",
        type=Path,
        default=Path("outputs/physical_graphs/physical_graph.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/evaluation/m6_complex_candidate_sample.json"),
    )
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()
    selected = sample_m6_candidates(
        args.candidates, args.physical_graph, args.output, args.limit
    )
    print(f"Selected {len(selected)} candidates -> {args.output}")
    for item in selected:
        print(
            f"{item['node_id']}: score={item['complexity_score']}, "
            f"signals={','.join(item['signals']) or 'baseline'}"
        )
    ids = " ".join(f"--node-id {item['node_id']}" for item in selected)
    print(
        "M6 is not run by this sampler. After reviewing the sample, run:\n"
        f"python run_llm_extraction.py --limit {len(selected)} {ids}"
    )


if __name__ == "__main__":
    main()
