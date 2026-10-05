"""Batch ingestion of Unified Graph JSON into Neo4j."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .cypher_generator import CypherGenerator


class Neo4jIngestor:
    """Write UKG nodes and edges in bounded, idempotent transactions."""

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
    def _write_edges(tx: Any, rows: list[dict[str, str]]) -> None:
        result = tx.run(CypherGenerator.EDGE_BATCH, rows=rows)
        if hasattr(result, "consume"):
            result.consume()

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

    def ingest(self, graph: Mapping[str, Any], *, replace: bool = False) -> dict[str, int]:
        nodes, edges = CypherGenerator.validate_graph(graph)
        node_rows = [CypherGenerator.node_parameters(node) for node in nodes]
        edge_rows = [CypherGenerator.edge_parameters(edge) for edge in edges]

        self.initialize_schema()
        if replace:
            with self.driver.session(database=self.database) as session:
                session.execute_write(self._delete_graph)

        node_batches = self._write_batches(node_rows, self._write_nodes)
        edge_batches = self._write_batches(edge_rows, self._write_edges)
        return {
            "nodes": len(node_rows),
            "edges": len(edge_rows),
            "node_batches": node_batches,
            "edge_batches": edge_batches,
        }