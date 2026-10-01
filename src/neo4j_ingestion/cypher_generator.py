"""Cypher statements and stable parameter mappings for Unified Graph ingestion."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from typing import Any


class CypherGenerator:
    """Generate parameterized Cypher for the UKG's generic node/edge schema."""

    NODE_CONSTRAINT = """
        CREATE CONSTRAINT ukg_node_id IF NOT EXISTS
        FOR (n:UKG_NODE) REQUIRE n.id IS UNIQUE
    """
    NODE_TEXT_INDEX = """
        CREATE FULLTEXT INDEX ukg_node_text IF NOT EXISTS
        FOR (n:UKG_NODE) ON EACH [n.search_text]
    """
    EDGE_KEY_INDEX = """
        CREATE INDEX ukg_edge_key IF NOT EXISTS
        FOR ()-[r:UKG_EDGE]-() ON (r.edge_key)
    """
    NODE_BATCH = """
        UNWIND $rows AS row
        MERGE (n:UKG_NODE {id: row.id})
        SET n.node_kind = row.node_kind,
            n.labels_json = row.labels_json,
            n.properties_json = row.properties_json,
            n.provenance_json = row.provenance_json,
            n.search_text = row.search_text
    """
    EDGE_BATCH = """
        UNWIND $rows AS row
        OPTIONAL MATCH (source:UKG_NODE {id: row.source_id})
        OPTIONAL MATCH (target:UKG_NODE {id: row.target_id})
        WITH row, source, target,
             (source IS NOT NULL) AS src_exists,
             (target IS NOT NULL) AS tgt_exists
        CALL {
            WITH row, source, target, src_exists, tgt_exists
            WITH * WHERE src_exists = false OR tgt_exists = false
            RETURN false AS already_exists, false AS is_created
            UNION
            WITH row, source, target, src_exists, tgt_exists
            WITH * WHERE src_exists = true AND tgt_exists = true
            OPTIONAL MATCH (source)-[r_old:UKG_EDGE {edge_key: row.edge_key}]->(target)
            WITH row, source, target, (r_old IS NOT NULL) AS already_exists
            MERGE (source)-[r:UKG_EDGE {edge_key: row.edge_key}]->(target)
            SET r.edge_type = row.edge_type,
                r.source_id = row.source_id,
                r.target_id = row.target_id,
                r.properties_json = row.properties_json,
                r.provenance_json = row.provenance_json
            RETURN already_exists, NOT already_exists AS is_created
        }
        RETURN row.edge_key AS edge_key,
               src_exists, tgt_exists,
               already_exists, is_created
    """
    DELETE_GRAPH = "MATCH (n:UKG_NODE) DETACH DELETE n"

    @classmethod
    def validate_graph(
        cls, graph: Mapping[str, Any]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        if not isinstance(graph, Mapping):
            raise ValueError("Unified Graph must be a JSON object.")
        nodes = graph.get("nodes")
        edges = graph.get("edges")
        if not isinstance(nodes, list) or not isinstance(edges, list):
            raise ValueError("Unified Graph must contain 'nodes' and 'edges' lists.")

        node_ids: set[str] = set()
        for index, node in enumerate(nodes):
            if not isinstance(node, dict):
                raise ValueError(f"nodes[{index}] must be an object.")
            node_id = node.get("id")
            if not isinstance(node_id, str) or not node_id.strip():
                raise ValueError(f"nodes[{index}].id must be a non-empty string.")
            if node_id in node_ids:
                raise ValueError(f"Duplicate node ID: {node_id}")
            node_ids.add(node_id)
            labels = node.get("labels", [])
            if not isinstance(labels, list) or any(
                not isinstance(label, str) or not label.strip() for label in labels
            ):
                raise ValueError(f"nodes[{index}].labels must be a list of strings.")
            if not isinstance(node.get("properties", {}), dict):
                raise ValueError(f"nodes[{index}].properties must be an object.")
            if not isinstance(node.get("provenance", []), list):
                raise ValueError(f"nodes[{index}].provenance must be a list.")

        edge_keys: set[str] = set()
        for index, edge in enumerate(edges):
            if not isinstance(edge, dict):
                raise ValueError(f"edges[{index}] must be an object.")
            for endpoint in ("source", "target"):
                value = edge.get(endpoint)
                if not isinstance(value, str) or value not in node_ids:
                    raise ValueError(
                        f"edges[{index}].{endpoint} references an unknown node: {value!r}"
                    )
            edge_type = edge.get("type")
            if not isinstance(edge_type, str) or not re.fullmatch(
                r"[A-Z][A-Z0-9_]*", edge_type
            ):
                raise ValueError(f"edges[{index}].type must be an uppercase identifier.")
            if not isinstance(edge.get("properties", {}), dict):
                raise ValueError(f"edges[{index}].properties must be an object.")
            if not isinstance(edge.get("provenance", []), list):
                raise ValueError(f"edges[{index}].provenance must be a list.")
            key = cls.edge_key(edge)
            if key in edge_keys:
                raise ValueError(f"Duplicate edge identity at edges[{index}].")
            edge_keys.add(key)

        return nodes, edges

    @staticmethod
    def edge_key(edge: Mapping[str, Any]) -> str:
        properties = edge.get("properties", {})
        discriminator = properties.get("relation_id")
        if discriminator is None:
            discriminator = properties.get("evidence", "")
        identity = (
            str(edge["source"]),
            str(edge["target"]),
            str(edge["type"]),
            f"{properties.get('source_node_id', '')}:{discriminator}",
        )
        encoded = json.dumps(identity, ensure_ascii=False).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    @staticmethod
    def node_parameters(node: Mapping[str, Any]) -> dict[str, str]:
        labels = node.get("labels", [])
        properties = node.get("properties", {})
        return {
            "id": node["id"],
            "node_kind": str(node.get("node_kind", "UNKNOWN")),
            "labels_json": json.dumps(labels, ensure_ascii=False),
            "properties_json": json.dumps(
                properties, ensure_ascii=False, sort_keys=True
            ),
            "provenance_json": json.dumps(
                node.get("provenance", []), ensure_ascii=False, sort_keys=True
            ),
            "search_text": " ".join(
                (
                    node["id"],
                    str(node.get("node_kind", "UNKNOWN")),
                    " ".join(labels),
                    json.dumps(properties, ensure_ascii=False, sort_keys=True),
                )
            ),
        }

    @classmethod
    def edge_parameters(cls, edge: Mapping[str, Any]) -> dict[str, str]:
        return {
            "edge_key": cls.edge_key(edge),
            "source_id": edge["source"],
            "target_id": edge["target"],
            "edge_type": edge["type"],
            "properties_json": json.dumps(
                edge.get("properties", {}), ensure_ascii=False, sort_keys=True
            ),
            "provenance_json": json.dumps(
                edge.get("provenance", []), ensure_ascii=False, sort_keys=True
            ),
        }