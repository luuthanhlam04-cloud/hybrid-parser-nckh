"""Incremental graph fusion support based on stable node and edge keys."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict


class DeltaEngine:
    @staticmethod
    def _edge_key(edge: Dict[str, Any]) -> tuple[str, str, str, str]:
        properties = edge.get("properties", {})
        discriminator = properties.get("relation_id")
        if discriminator is None:
            discriminator = properties.get("evidence", "")
        return (
            str(edge["source"]), str(edge["target"]), str(edge["type"]),
            f"{properties.get('source_node_id', '')}:{discriminator}",
        )

    def diff(self, previous: Dict[str, Any], current: Dict[str, Any]) -> Dict[str, Any]:
        old_nodes = {str(node["id"]): node for node in previous.get("nodes", [])}
        new_nodes = {str(node["id"]): node for node in current.get("nodes", [])}
        old_edges = {self._edge_key(edge): edge for edge in previous.get("edges", [])}
        new_edges = {self._edge_key(edge): edge for edge in current.get("edges", [])}
        updated_edges = [
            edge for key, edge in new_edges.items()
            if key in old_edges and edge != old_edges[key]
        ]
        return {
            "added_nodes": [node for key, node in new_nodes.items() if key not in old_nodes],
            "updated_nodes": [
                node for key, node in new_nodes.items()
                if key in old_nodes and node != old_nodes[key]
            ],
            "removed_nodes": [node for key, node in old_nodes.items() if key not in new_nodes],
            "added_edges": [edge for key, edge in new_edges.items() if key not in old_edges],
            "updated_edges": updated_edges,
            "removed_edges": [edge for key, edge in old_edges.items() if key not in new_edges],
        }


class Neo4jDeltaApplier:
    """Apply a graph delta in one Neo4j transaction using the official driver API."""

    def __init__(self, driver: Any, database: str | None = None) -> None:
        self.driver = driver
        self.database = database

    @staticmethod
    def _node_parameters(node: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": str(node["id"]),
            "node_kind": str(node.get("node_kind", "UNKNOWN")),
            "labels_json": json.dumps(node.get("labels", []), ensure_ascii=False),
            "properties_json": json.dumps(
                node.get("properties", {}), ensure_ascii=False, sort_keys=True
            ),
        }

    @classmethod
    def _edge_parameters(cls, edge: Dict[str, Any]) -> Dict[str, Any]:
        edge_key = hashlib.sha256(
            json.dumps(DeltaEngine._edge_key(edge), ensure_ascii=False).encode("utf-8")
        ).hexdigest()
        return {
            "edge_key": edge_key,
            "source": str(edge["source"]),
            "target": str(edge["target"]),
            "edge_type": str(edge["type"]),
            "properties_json": json.dumps(
                edge.get("properties", {}), ensure_ascii=False, sort_keys=True
            ),
            "provenance_json": json.dumps(edge.get("provenance", []), ensure_ascii=False),
        }

    @staticmethod
    def _write_transaction(tx: Any, delta: Dict[str, Any]) -> None:
        for edge in delta["removed_edges"] + delta["updated_edges"]:
            result = tx.run(
                "MATCH ()-[r:UKG_EDGE {edge_key: $edge_key}]-() DELETE r",
                edge_key=Neo4jDeltaApplier._edge_parameters(edge)["edge_key"],
            )
            if hasattr(result, "consume"):
                result.consume()
        for node in delta["removed_nodes"]:
            result = tx.run(
                "MATCH (n:UKG_NODE {id: $id}) DETACH DELETE n",
                id=str(node["id"]),
            )
            if hasattr(result, "consume"):
                result.consume()
        for node in delta["added_nodes"] + delta["updated_nodes"]:
            result = tx.run(
                """
                MERGE (n:UKG_NODE {id: $id})
                SET n.node_kind = $node_kind,
                    n.labels_json = $labels_json,
                    n.properties_json = $properties_json
                """,
                **Neo4jDeltaApplier._node_parameters(node),
            )
            if hasattr(result, "consume"):
                result.consume()
        for edge in delta["added_edges"] + delta["updated_edges"]:
            result = tx.run(
                """
                MATCH (source:UKG_NODE {id: $source})
                MATCH (target:UKG_NODE {id: $target})
                MERGE (source)-[r:UKG_EDGE {edge_key: $edge_key}]->(target)
                SET r.edge_type = $edge_type,
                    r.properties_json = $properties_json,
                    r.provenance_json = $provenance_json
                RETURN r.edge_key AS edge_key
                """,
                **Neo4jDeltaApplier._edge_parameters(edge),
            )
            if hasattr(result, "single") and result.single() is None:
                raise RuntimeError(
                    "Neo4j delta edge endpoints are missing: "
                    f"{edge['source']} -> {edge['target']}"
                )

    def initialize_schema(self) -> None:
        with self.driver.session(database=self.database) as session:
            result = session.run(
                """
                CREATE CONSTRAINT ukg_node_id IF NOT EXISTS
                FOR (n:UKG_NODE) REQUIRE n.id IS UNIQUE
                """
            )
            if hasattr(result, "consume"):
                result.consume()

    def apply(self, delta: Dict[str, Any]) -> None:
        required_keys = {
            "added_nodes", "updated_nodes", "removed_nodes",
            "added_edges", "updated_edges", "removed_edges",
        }
        missing = required_keys - delta.keys()
        if missing:
            raise ValueError(f"Delta is missing required keys: {sorted(missing)}")
        with self.driver.session(database=self.database) as session:
            session.execute_write(self._write_transaction, delta)
