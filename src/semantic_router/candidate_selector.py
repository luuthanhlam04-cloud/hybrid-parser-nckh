# -*- coding: utf-8 -*-
"""
candidate_selector.py — Định dạng và xuất file JSON cho output của M5.
"""
import json
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

@dataclass
class RoutingResult:
    node_id: str
    route: str           # "REJECT", "RULE_ONLY", "LLM_CANDIDATE"
    routing_score: float
    reason: str

class CandidateSelector:
    def __init__(self):
        pass

    def export(
        self,
        results: List[RoutingResult],
        metadata: Dict[str, Any],
        output_path: str | Path
    ) -> None:
        """
        Xuất danh sách candidates ra file JSON.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Calculate totals
        total_evaluated = len(results)
        total_candidates = sum(1 for r in results if r.route == "LLM_CANDIDATE")
        
        # Merge calculated stats into metadata
        final_metadata = {
            **metadata,
            "total_evaluated": total_evaluated,
            "total_candidates": total_candidates,
        }

        output_data = {
            "router_metadata": final_metadata,
            "candidates": [asdict(r) for r in results]
        }

        with output_path.open("w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
