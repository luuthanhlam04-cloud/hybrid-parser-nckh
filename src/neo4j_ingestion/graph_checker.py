"""Check that the graph stored in Neo4j matches its Unified Graph source (Audit only)."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

from .cypher_generator import CypherGenerator


class GraphChecker:
    """Compare stored counts and structural integrity with a UKG document (Non-blocking)."""

    NODE_COUNT = "MATCH (n:UKG_NODE) RETURN count(n) AS count"
    EDGE_COUNT = "MATCH ()-[r]->() RETURN count(r) AS count"
    ORPHAN_COUNT = """
        MATCH (n:UKG_NODE)
        WHERE NOT (n)--()
        RETURN count(n) AS count
    """
    # Cypher query to detect HAS_CONDITION and HAS_EXCEPTION semantic cycles
    SEMANTIC_CYCLES = """
        MATCH p=(n:UKG_NODE)-[r:HAS_CONDITION|HAS_EXCEPTION*]->(n)
        RETURN count(p) AS count
    """

    def __init__(self, driver: Any, database: str | None = None) -> None:
        self.driver = driver
        self.database = database
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    @staticmethod
    def _single_count(session: Any, query: str) -> int:
        result = session.run(query)
        record = result.single()
        if record is None:
            return 0
        return int(record["count"])

    def check(self, graph: Mapping[str, Any]) -> dict[str, Any]:
        nodes, edges = CypherGenerator.validate_graph(graph)
        expected_nodes = len(nodes)
        
        # Pillar 1 RAM Validation guarantees only valid edges are ingested
        valid_node_ids = {node.get("id") for node in nodes}
        valid_edges = [
            e for e in edges 
            if e.get("source") in valid_node_ids and e.get("target") in valid_node_ids
        ]
        expected_edges = len(valid_edges)

        with self.driver.session(database=self.database) as session:
            actual_nodes = self._single_count(session, self.NODE_COUNT)
            actual_edges = self._single_count(session, self.EDGE_COUNT)
            orphan_nodes = self._single_count(session, self.ORPHAN_COUNT)
            semantic_cycles = self._single_count(session, self.SEMANTIC_CYCLES)

        counts_match = (
            actual_nodes == expected_nodes and actual_edges == expected_edges
        )
        
        report = {
            "expected_nodes": expected_nodes,
            "actual_nodes": actual_nodes,
            "expected_edges": expected_edges,
            "actual_edges": actual_edges,
            "orphan_nodes": orphan_nodes,
            "semantic_cycles": semantic_cycles,
            "counts_match": counts_match,
            "is_valid": counts_match
        }

        # Pillar 5: Lightweight Audit Reporting (Non-blocking)
        if not counts_match:
            self.logger.warning(
                "Graph Audit Discrepancy: Nodes (Expected %d, Actual %d). Edges (Expected %d, Actual %d)",
                expected_nodes, actual_nodes, expected_edges, actual_edges
            )
        else:
            self.logger.info("Graph Audit Passed: Counts Match.")

        if orphan_nodes > 0:
            self.logger.warning("Graph Audit Detected %d orphan nodes.", orphan_nodes)
            
        if semantic_cycles > 0:
            self.logger.warning("Graph Audit Detected %d semantic cycles (HAS_CONDITION/HAS_EXCEPTION).", semantic_cycles)

        return report