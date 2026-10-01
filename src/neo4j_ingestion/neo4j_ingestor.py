"""Batch ingestion of Unified Graph JSON into Neo4j."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .cypher_generator import CypherGenerator


class Neo4jIngestor:
    """Write UKG nodes and edges in bounded, idempotent transactions."""

    # Phase 5: Ontology-defined label allowlist.
    # Only these labels may be applied as native Neo4j labels.
    # Source: UKG label distribution + ontology schema.
    LABEL_ALLOWLIST: set[str] = {
        "LegalNode",
        "CHAPTER", "SECTION", "ARTICLE", "CLAUSE", "POINT",
        "SemanticEntity",
        "GLOBAL_NORM",
        "LEGAL_SUBJECT", "LEGAL_ACTION", "LEGAL_OBJECT",
        "LEGAL_DOCUMENT_REF",
    }

    # Cypher template for Python-loop label assignment (Neo4j 5.x compatible)
    # Safe: label names come from LABEL_ALLOWLIST (not user input / LLM output)
    APPLY_LABEL_TEMPLATE = """
        MATCH (n:UKG_NODE {{id: $node_id}})
        SET n:{label}
    """

    def __init__(
        self, driver: Any, database: str | None = None, batch_size: int = 1000
    ) -> None:
        if batch_size < 1:
            raise ValueError("batch_size must be a positive integer.")
        self.driver = driver
        self.database = database
        self.batch_size = batch_size

    def initialize_schema(self) -> None:
        with self.driver.session(database=self.database) as session:
            for statement in (
                CypherGenerator.NODE_CONSTRAINT,
                CypherGenerator.NODE_TEXT_INDEX,
                CypherGenerator.EDGE_KEY_INDEX,
            ):
                result = session.run(statement)
                if hasattr(result, "consume"):
                    result.consume()

    @staticmethod
    def _delete_graph(tx: Any) -> None:
        result = tx.run(CypherGenerator.DELETE_GRAPH)
        if hasattr(result, "consume"):
            result.consume()

    @staticmethod
    def _write_nodes(tx: Any, rows: list[dict[str, str]]) -> None:
        result = tx.run(CypherGenerator.NODE_BATCH, rows=rows)
        if hasattr(result, "consume"):
            result.consume()

    @staticmethod
    def _write_edges_with_accounting(
        tx: Any, rows: list[dict[str, str]]
    ) -> list[dict]:
        """Per-row accounting: look before MERGE, return status per edge."""
        result = tx.run(CypherGenerator.EDGE_BATCH, rows=rows)
        records = list(result)
        summary = result.consume()
        return records, summary

    def _write_batches(
        self, rows: list[dict[str, str]], writer: Any
    ) -> int:
        batches = 0
        with self.driver.session(database=self.database) as session:
            for start in range(0, len(rows), self.batch_size):
                session.execute_write(
                    writer, rows[start : start + self.batch_size]
                )
                batches += 1
        return batches

    def _write_edges_batched(self) -> dict[str, int]:
        """Write edges with full per-row accounting pipeline."""
        raise NotImplementedError  # implemented inline in ingest()

    def ingest(self, graph: Mapping[str, Any], *, replace: bool = False) -> dict[str, int]:
        nodes, edges = CypherGenerator.validate_graph(graph)
        node_rows = [CypherGenerator.node_parameters(node) for node in nodes]
        edge_rows = [CypherGenerator.edge_parameters(edge) for edge in edges]

        self.initialize_schema()
        if replace:
            with self.driver.session(database=self.database) as session:
                session.execute_write(self._delete_graph)

        node_batches = self._write_batches(node_rows, self._write_nodes)

        # Phase 2: Edge accounting pipeline (per-row Data Status)
        edge_accounting = {
            "attempted": len(edge_rows),
            "created": 0,
            "already_exists": 0,
            "missing_source": 0,
            "missing_target": 0,
            "missing_both": 0,
            "execution_failed": 0,
            "edge_batches": 0,
        }
        with self.driver.session(database=self.database) as session:
            for start in range(0, len(edge_rows), self.batch_size):
                batch = edge_rows[start : start + self.batch_size]
                try:
                    records, _summary = session.execute_write(
                        self._write_edges_with_accounting, batch
                    )
                    for rec in records:
                        src_exists = rec.get("src_exists", False)
                        tgt_exists = rec.get("tgt_exists", False)
                        is_created = rec.get("is_created", False)
                        already_exists = rec.get("already_exists", False)
                        if not src_exists and not tgt_exists:
                            edge_accounting["missing_both"] += 1
                        elif not src_exists:
                            edge_accounting["missing_source"] += 1
                        elif not tgt_exists:
                            edge_accounting["missing_target"] += 1
                        elif is_created:
                            edge_accounting["created"] += 1
                        elif already_exists:
                            edge_accounting["already_exists"] += 1
                except Exception as e:
                    print(f"Edge batch execution failed: {e}")
                    edge_accounting["execution_failed"] += len(batch)
                edge_accounting["edge_batches"] += 1

        # Phase 2 Invariant: Ensure accounting states are mutually exclusive and total up to attempted.
        total_accounted = (
            edge_accounting["created"] +
            edge_accounting["already_exists"] +
            edge_accounting["missing_source"] +
            edge_accounting["missing_target"] +
            edge_accounting["missing_both"] +
            edge_accounting["execution_failed"]
        )
        if edge_accounting["attempted"] != total_accounted:
            raise RuntimeError(f"Edge accounting invariant failed! Attempted {edge_accounting['attempted']} != Total Accounted {total_accounted}")

        # Phase 5: Apply native Neo4j labels using Python-loop fallback (Neo4j 5.x safe)
        # Labels come from Allowlist ONLY - never raw LLM output or labels_json directly.
        labels_applied = 0
        with self.driver.session(database=self.database) as session:
            for node in nodes:
                node_id = node.get("id")
                for label in node.get("labels", []):
                    if label in self.LABEL_ALLOWLIST:
                        cypher = f"MATCH (n:UKG_NODE {{id: $node_id}}) SET n:`{label}`"
                        result = session.run(cypher, node_id=node_id)
                        result.consume()
                        labels_applied += 1

        return {
            "nodes": len(node_rows),
            "edges": len(edge_rows),
            "node_batches": node_batches,
            "labels_applied": labels_applied,
            **edge_accounting,
        }