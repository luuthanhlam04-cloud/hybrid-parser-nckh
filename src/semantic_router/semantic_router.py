# -*- coding: utf-8 -*-
"""
semantic_router.py — Orchestrator cho Module 5 (Semantic Router).
"""

import logging
from pathlib import Path
from typing import Dict, Any, List

from src.semantic_router.routing_engine import RoutingEngine
from src.semantic_router.threshold_controller import ThresholdController
from src.semantic_router.candidate_selector import CandidateSelector, RoutingResult
from src.semantic_router.embedding_engine import EmbeddingEngine

logger = logging.getLogger("semantic_router")

class SemanticRouter:
    def __init__(self, graph: Dict[str, Any], config: Dict[str, Any]):
        self.graph = graph
        self.config = config
        
        self.routing_engine = RoutingEngine()
        self.threshold_controller = ThresholdController(
            mode=config.get("threshold_mode", "fixed"),
            threshold=config.get("threshold", 0.75)
        )
        self.candidate_selector = CandidateSelector()
        
        # Load embedding engine if we need it (EXP-B or EXP-C)
        self.embedding_engine = None
        if self.config.get("ablation_mode") in ["EXP-B", "EXP-C"]:
            self.embedding_engine = EmbeddingEngine(
                embeddings_path="outputs/embeddings/embeddings.npy",
                node_ids_path="outputs/embeddings/node_ids.json",
                anchors_path="outputs/embeddings/anchors.npy"
            )

    def _pre_filter_rule_only(self, node: Dict[str, Any]) -> bool:
        """
        Type-based pre-filter: CHAPTER, SECTION -> RULE_ONLY
        (Vì chỉ là tiêu đề, không chứa semantic quan trọng để query)
        """
        labels = node.get("labels", [])
        if "CHAPTER" in labels or "SECTION" in labels:
            return True
        return False

    def run(self) -> List[RoutingResult]:
        """
        Chạy routing trên toàn bộ node trong graph.
        """
        results = []
        nodes = self.graph.get("nodes", [])
        threshold = self.threshold_controller.get_threshold()

        for node in nodes:
            node_id = node.get("id")
            
            # 1. Pre-filter (Type-based)
            if self._pre_filter_rule_only(node):
                results.append(RoutingResult(
                    node_id=node_id,
                    route="RULE_ONLY",
                    routing_score=0.0,
                    reason="TYPE_FILTER"
                ))
                continue

            # 2. Lấy nội dung text
            props = node.get("properties", {})
            text = props.get("text", "")

            # 3. Tính điểm Regex (Tín hiệu A)
            regex_score, category = self.routing_engine.evaluate_regex(text)

            # 4. Tính điểm Embedding (Tín hiệu B)
            embed_score = 0.0
            if self.embedding_engine is not None and self.embedding_engine.anchors is not None:
                text_vec = self.embedding_engine.get_embedding(node_id)
                if text_vec is not None:
                    embed_score = self.routing_engine.embed_score(
                        text_vec=text_vec,
                        anchor_vecs=self.embedding_engine.anchors,
                        engine=self.embedding_engine
                    )

            # 5. Fusion
            final_score = self.routing_engine.fuse(
                regex_s=regex_score,
                embed_s=embed_score,
                ablation_mode=self.config.get("ablation_mode", "EXP-A")
            )

            # 6. Ra quyết định (Decision)
            route = "REJECT"
            reason = "NO_TRIGGER"
            
            if final_score >= threshold:
                route = "LLM_CANDIDATE"
                reason = category if category != "NONE" else "EMBEDDING_MATCH"
            elif final_score > 0: # Dưới threshold nhưng có tín hiệu
                reason = f"LOW_CONFIDENCE"
                if category != "NONE":
                    reason += f"_{category}"

            results.append(RoutingResult(
                node_id=node_id,
                route=route,
                routing_score=final_score,
                reason=reason
            ))

        return results

    def export(self, results: List[RoutingResult], output_path: str | Path):
        """
        Xuất kết quả ra JSON.
        """
        metadata = {
            "document_id": self.graph.get("graph_metadata", {}).get("document_id", "doc"),
            "schema_version": "1.0",
            "routing_model": "regex_only" if self.config.get("ablation_mode") == "EXP-A" else "qwen3",
            "threshold": self.threshold_controller.get_threshold()
        }
        self.candidate_selector.export(results, metadata, output_path)

