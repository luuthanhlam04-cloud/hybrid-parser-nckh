"""Check that the graph stored in Neo4j matches its Unified Graph source."""

from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Mapping
from typing import Any

from .cypher_generator import CypherGenerator


class GraphChecker:
    """Compare stored counts and structural integrity with a UKG document."""

    NODE_COUNT = "MATCH (n:UKG_NODE) RETURN count(n) AS count"
    EDGE_COUNT = "MATCH ()-[r:UKG_EDGE]->() RETURN count(r) AS count"
    ORPHAN_COUNT = """
        MATCH (n:UKG_NODE)
        WHERE NOT (n)--()
        RETURN count(n) AS count
    """
    DANGLING_COUNT = """
        MATCH ()-[r:UKG_EDGE]->()
        OPTIONAL MATCH (source:UKG_NODE {id: r.source_id})
        OPTIONAL MATCH (target:UKG_NODE {id: r.target_id})
        WITH r, source, target
        WHERE source IS NULL OR target IS NULL
        RETURN count(r) AS count
    """
    STRUCTURAL_EDGES = """
        MATCH (source:UKG_NODE)-[r:UKG_EDGE]->(target:UKG_NODE)
        WHERE r.edge_type IN $edge_types
        RETURN r.edge_type AS edge_type, source.id AS source, target.id AS target
    """

    def __init__(self, driver: Any, database: str | None = None) -> None:
        self.driver = driver
        self.database = database

    @staticmethod
    def _single_count(session: Any, query: str) -> int:
        result = session.run(query)
        record = result.single()
        if record is None:
            raise RuntimeError("Neo4j count query returned no record.")
        return int(record["count"])

    @staticmethod
    def _has_cycle(edges: list[tuple[str, str]]) -> bool:
        adjacency: dict[str, list[str]] = defaultdict(list)
        vertices: set[str] = set()
        for source, target in edges:
            adjacency[source].append(target)
            vertices.update((source, target))

        indegree = {vertex: 0 for vertex in vertices}
        for targets in adjacency.values():
            for target in targets:
                indegree[target] += 1
        queue = deque(vertex for vertex, degree in indegree.items() if degree == 0)
        visited = 0
        while queue:
            vertex = queue.popleft()
            visited += 1
            for target in adjacency.get(vertex, []):
                indegree[target] -= 1
                if indegree[target] == 0:
                    queue.append(target)
        return visited != len(vertices)

    def check(self, graph: Mapping[str, Any]) -> dict[str, Any]:
        nodes, edges = CypherGenerator.validate_graph(graph)
        expected_nodes = len(nodes)
        expected_edges = len(edges)

        with self.driver.session(database=self.database) as session:
            actual_nodes = self._single_count(session, self.NODE_COUNT)
            actual_edges = self._single_count(session, self.EDGE_COUNT)
            orphan_nodes = self._single_count(session, self.ORPHAN_COUNT)
            dangling_edges = self._single_count(session, self.DANGLING_COUNT)
            result = session.run(
                self.STRUCTURAL_EDGES,
                edge_types=["BELONG_TO", "NEXT", "PREVIOUS"],
            )
            structural_edges: dict[str, list[tuple[str, str]]] = defaultdict(list)
            for record in result:
                structural_edges[record["edge_type"]].append(
                    (record["source"], record["target"])
                )

        cyclic_types = sorted(
            edge_type
            for edge_type, type_edges in structural_edges.items()
            if self._has_cycle(type_edges)
        )
        counts_match = (
            actual_nodes == expected_nodes and actual_edges == expected_edges
        )
        is_valid = counts_match and dangling_edges == 0 and not cyclic_types
        return {
            "expected_nodes": expected_nodes,
            "actual_nodes": actual_nodes,
            "expected_edges": expected_edges,
            "actual_edges": actual_edges,
            "orphan_nodes": orphan_nodes,
            "dangling_edges": dangling_edges,
            "structural_cycle_types": cyclic_types,
            "counts_match": counts_match,
            "is_valid": is_valid,
        }