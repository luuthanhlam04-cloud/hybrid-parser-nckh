"""Adapter around the existing M10 Hybrid Parser/UKG retrieval pipeline."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from .base import BenchmarkSystem


class HybridUKGSystem(BenchmarkSystem):
    name = "hybrid_ukg"

    def __init__(self, output_dir: str | Path, *, mode: str = "AUTO_FUSION") -> None:
        super().__init__(output_dir)
        self.mode = mode
        self._pipeline: Any | None = None
        self._driver: Any | None = None
        self._jev_events: Any | None = None

    def readiness(self) -> dict[str, Any]:
        required = [
            Path("outputs/unified_graphs/unified_knowledge_graph.json"),
            Path("outputs/embeddings/luat_dat_dai_ch3/embeddings.npy"),
            Path("outputs/embeddings/luat_dat_dai_ch3/node_ids.json"),
        ]
        return {"system": self.name, "ready": all(path.is_file() for path in required), "required_paths": {str(path): path.is_file() for path in required}, "mode": self.mode}

    def index(self, corpus: list[dict[str, Any]], *, fresh: bool = False) -> dict[str, Any]:
        """Record current UKG readiness; rebuilding M1--M9 is always explicit elsewhere."""
        if fresh:
            raise ValueError("Hybrid UKG is not silently rebuilt by Benchmark B. Run its M1--M9 pipeline explicitly, then use index without --fresh.")
        report = {**self.readiness(), "corpus_article_count": len(corpus), "indexing_mode": "reuse_existing_ukg", "cost_note": "M1--M9 build costs are not inferred by this runner."}
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "index_metadata.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if not report["ready"]:
            raise RuntimeError("Hybrid UKG is not ready; inspect required_paths in index_metadata.json.")
        return report

    def _get_pipeline(self) -> Any:
        if self._pipeline is not None:
            return self._pipeline
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("LLM_API_KEY")
        if not api_key:
            raise RuntimeError("Hybrid benchmark requires OPENROUTER_API_KEY or LLM_API_KEY in .env.")
        os.environ["OPENROUTER_API_KEY"] = api_key
        try:
            from neo4j import GraphDatabase
            from src.retrieval.anchor_search import AnchorSearch
            from src.retrieval.answer_generator import AnswerGenerator
            from src.retrieval.context_assembler import ContextAssembler
            from src.retrieval.graph_query import GraphQuery
            from src.retrieval.jev_client import JevClient
            from src.retrieval.m10_pipeline import M10Pipeline
        except ImportError as exc:
            raise RuntimeError("Hybrid benchmark dependencies are missing; install requirements.txt.") from exc
        self._driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI", "neo4j+s://59bbc655.databases.neo4j.io"),
            auth=(os.getenv("NEO4J_USERNAME", "neo4j"), os.getenv("NEO4J_PASSWORD", "")),
        )
        from benchmark_b.events import EventLog
        self._jev_events = EventLog(
            self.output_dir / "jev_api_events.jsonl",
            self.name,
            self.output_dir.name,
        )
        jev_client = JevClient.from_environment(event_log=self._jev_events)
        self._pipeline = M10Pipeline(
            anchor_search=AnchorSearch(driver=self._driver),
            graph_query=GraphQuery(driver=self._driver),
            answer_generator=AnswerGenerator.from_environment(),
            context_assembler=ContextAssembler(),
            log_path=None,
            jev_client=jev_client,
        )
        return self._pipeline

    @staticmethod
    def _articles_from_anchors(anchors: list[dict[str, Any]]) -> list[str]:
        articles: list[str] = []
        for anchor in anchors:
            node_id = str(anchor.get("node_id", ""))
            marker = "_dieu-"
            if marker not in node_id:
                continue
            suffix = node_id.split(marker, 1)[1]
            number = suffix.split("_", 1)[0]
            article_id = f"31/2024/qh15#{number}"
            if article_id not in articles:
                articles.append(article_id)
        return articles

    @staticmethod
    def _articles_from_evidence(evidence: list[dict[str, Any]]) -> list[str]:
        articles=[]
        for item in evidence:
            locator=str(item.get('canonical_locator') or '')
            if ':A' not in locator:
                continue
            number=locator.split(':A',1)[1].split(':',1)[0]
            article_id=f"31/2024/qh15#{number}"
            if article_id not in articles:
                articles.append(article_id)
        return articles

    def answer(self, question: dict[str, Any], *, top_k: int) -> dict[str, Any]:
        started = time.perf_counter()
        result = self._get_pipeline().answer(
            question["question"], mode=self.mode, top_k=top_k, question_id=question["question_id"]
        )
        from benchmark_b.prepare import MAP
        from benchmark_b.alignment import hybrid_evidence, hybrid_paths
        evidence, context_evidence = hybrid_evidence(result, json.loads(MAP.read_text(encoding='utf-8')))
        anchor_articles=self._articles_from_anchors(result["anchors"])
        expanded_articles=self._articles_from_evidence(result.get('expanded_evidence',[]))
        context_articles=self._articles_from_evidence(result.get('context_evidence',[]))
        return {
            "evidence": evidence,
            "context_evidence": context_evidence,
            "reference_paths": result.get('reference_paths') if result.get('reference_paths') is not None else hybrid_paths(result.get('retrieval_records',[]),json.loads(MAP.read_text(encoding='utf-8'))),
            "answer_paths": result.get("answer_paths"),
            "explicit_reference_edges": result.get("explicit_reference_edges"),
            "selected_hierarchy_steps": result.get("selected_hierarchy_steps"),
            "answer_path_trace": result.get("answer_path_trace"),
            "reference_path_status": "OBSERVED_EXPLICIT_TEXT_TYPED_PATHS" if result.get('reference_paths') is not None else "LEGACY_MODE",
            "context": result.get("context"),
            "retrieval_records": result.get("retrieval_records"),
            "question_id": question["question_id"],
            "system": self.name,
            "answer": result["answer"],
            "retrieved_article_ids": anchor_articles,
            "anchor_article_ids": anchor_articles,
            "expanded_article_ids": expanded_articles,
            "context_article_ids": context_articles,
            "retrieval_evidence": "anchor_article_projection",
            "latency_ms": round((time.perf_counter() - started) * 1000, 2),
            "model": result.get("model"),
            "usage": result.get("usage"),
            "mode": result.get("mode"),
            "retrieved_count": result.get("retrieved_count"),
            "routing_trace": result.get("routing_trace"),
            "answerability_trace": result.get("answerability_trace"),
            "expanded_evidence": result.get("expanded_evidence"),
            "context_budget": result.get("context_budget"),
            "retrieval_stage_counts": result.get("retrieval_stage_counts"),
        }

    def jev_cost_summary(self) -> dict[str, Any] | None:
        return self._jev_events.summary(phase='jev',scope='m10_jev_routing_and_gating') if self._jev_events else None

    def close(self) -> None:
        if self._pipeline is not None and hasattr(self._pipeline,'close'):
            self._pipeline.close()
        self._pipeline = None
        if self._driver is not None:
            self._driver.close()
            self._driver = None
