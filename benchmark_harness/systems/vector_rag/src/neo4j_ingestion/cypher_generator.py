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
    
    INDEX_ONTOLOGY_CLASS = "CREATE INDEX idx_ontology_class IF NOT EXISTS FOR (n:UKG_NODE) ON (n.ontology_class)"
    INDEX_MODALITY = "CREATE INDEX idx_modality IF NOT EXISTS FOR (n:GLOBAL_NORM) ON (n.modality)"
    VECTOR_INDEX_NAME = "legal_node_vector_idx"

    @classmethod
    def vector_index_statement(cls, dimensions: int) -> str:
        if isinstance(dimensions, bool) or not isinstance(dimensions, int) or dimensions < 1:
            raise ValueError("Vector index dimensions must be a positive integer.")
        return (
            f"CREATE VECTOR INDEX {cls.VECTOR_INDEX_NAME} IF NOT EXISTS "
            "FOR (n:LegalNode) ON (n.embedding) "
            "OPTIONS {indexConfig: {"
            f"`vector.dimensions`: {dimensions}, "
            "`vector.similarity_function`: 'cosine'}}"
        )

    NODE_BATCH = """
        UNWIND $rows AS row
        MERGE (n:UKG_NODE {id: row.id})
        SET n += row.properties
    """
    
    CLEAR_NAMESPACE = "MATCH (n:UKG_NODE) DETACH DELETE n"

    @staticmethod
    def get_edge_batch_query(edge_type: str) -> str:
        return f"""
            UNWIND $rows AS row
            MATCH (s:UKG_NODE {{id: row.source}}), (t:UKG_NODE {{id: row.target}})
            MERGE (s)-[r:{edge_type} {{edge_key: row.properties.edge_key}}]->(t)
            SET r += row.properties
        """

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
    def node_parameters(node: Mapping[str, Any]) -> dict[str, Any]:
        labels = node.get("labels", [])
        properties = node.get("properties", {})
        search_text = " ".join(
            (
                node["id"],
                str(node.get("node_kind", "UNKNOWN")),
                " ".join(labels),
                json.dumps(properties, ensure_ascii=False, sort_keys=True),
            )
        )
        
        safe_properties = {}
        for k, v in properties.items():
            if isinstance(v, (dict, list)):
                if isinstance(v, list) and all(isinstance(i, (int, float, str, bool)) for i in v):
                    safe_properties[k] = v
                else:
                    safe_properties[k] = json.dumps(v, ensure_ascii=False)
            else:
                safe_properties[k] = v
                
        properties_json = json.dumps(properties, ensure_ascii=False, sort_keys=True)
        return {
            "id": node["id"],
            "properties_json": properties_json,
            "search_text": search_text,
            "properties": {
                "node_kind": str(node.get("node_kind", "UNKNOWN")),
                "search_text": search_text,
                **safe_properties,
            },
        }

    @classmethod
    def edge_parameters(cls, edge: Mapping[str, Any]) -> dict[str, Any]:
        edge_key = cls.edge_key(edge)
        properties = edge.get("properties", {})
        
        safe_properties = {}
        for k, v in properties.items():
            if isinstance(v, (dict, list)):
                if isinstance(v, list) and all(isinstance(i, (int, float, str, bool)) for i in v):
                    safe_properties[k] = v
                else:
                    safe_properties[k] = json.dumps(v, ensure_ascii=False)
            else:
                safe_properties[k] = v
                
        return {
            "source": edge["source"],
            "target": edge["target"],
            "source_id": edge["source"],
            "target_id": edge["target"],
            "edge_key": edge_key,
            "type": edge["type"],
            "properties": {
                "edge_key": edge_key,
                **safe_properties,
            },
        }