"""Batch ingestion of Unified Graph JSON into Neo4j."""

from __future__ import annotations

import json
import os
from collections import defaultdict
from collections.abc import Mapping
from typing import Any

from .cypher_generator import CypherGenerator


class Neo4jIngestor:
    """Write UKG nodes and edges in bounded, idempotent transactions with DLQ and Pre-indexing."""

    LABEL_ALLOWLIST: set[str] = {
        "LegalNode",
        "CHAPTER", "SECTION", "ARTICLE", "CLAUSE", "POINT",
        "SemanticEntity",
        "GLOBAL_NORM",
        "LEGAL_SUBJECT", "LEGAL_ACTION", "LEGAL_OBJECT",
        "LEGAL_DOCUMENT_REF",
        "CONDITION", "EXCEPTION", "PENALTY", "CANONICAL_CONCEPT"
    }

    def __init__(
        self, driver: Any, database: str | None = None, batch_size: int = 1000
    ) -> None:
        if batch_size < 1:
            raise ValueError("batch_size must be a positive integer.")
        self.driver = driver
        self.database = database
        self.batch_size = batch_size

    def initialize_schema(self, vector_dimensions: int | None = None) -> None:
        """Pillar 3: Hybrid Search Pre-Indexing"""
        statements = [
            CypherGenerator.NODE_CONSTRAINT,
            CypherGenerator.NODE_TEXT_INDEX,
            CypherGenerator.INDEX_ONTOLOGY_CLASS,
            CypherGenerator.INDEX_MODALITY,
        ]
        if vector_dimensions is not None:
            statements.append(CypherGenerator.vector_index_statement(vector_dimensions))
        with self.driver.session(database=self.database) as session:
            for statement in statements:
                result = session.run(statement)
                if hasattr(result, "consume"):
                    result.consume()

    def clear_namespace(self, law_code: str) -> None:
        """Pillar 4: Namespace Clear for Idempotent Ingestion."""
        if not law_code or law_code == "UNKNOWN":
            print("WARNING: Cannot clear namespace dynamically because law_code is UNKNOWN.")
        
        if law_code and law_code != "UNKNOWN":
            print(f"Clearing namespace for law_code: {law_code}")
        with self.driver.session(database=self.database) as session:
            session.run(CypherGenerator.CLEAR_NAMESPACE)

    def ingest(self, graph: Mapping[str, Any], *, replace: bool = False, cli_law_code: str = None) -> dict[str, int]:
        nodes, edges = CypherGenerator.validate_graph(graph)
        valid_node_ids = {node["id"] for node in nodes}
        invalid_edges = [
            edge for edge in edges
            if edge.get("source") not in valid_node_ids or edge.get("target") not in valid_node_ids
        ]
        if invalid_edges:
            details = ", ".join(
                f"{edge.get('source')}->{edge.get('target')}" for edge in invalid_edges[:5]
            )
            raise ValueError(f"unknown node reference in edge(s): {details}")

        vector_dimensions = {
            len(node["properties"]["embedding"])
            for node in nodes
            if "embedding" in node.get("properties", {})
        }
        if len(vector_dimensions) > 1:
            raise ValueError("All node embeddings must have the same dimension.")
        if vector_dimensions:
            dimension = next(iter(vector_dimensions))
            missing_vectors = [
                node["id"] for node in nodes
                if "LegalNode" in node.get("labels", [])
                and len(node.get("properties", {}).get("embedding", [])) != dimension
            ]
            if missing_vectors:
                raise ValueError(
                    "Every LegalNode must have an embedding when vector indexing is enabled. "
                    f"Missing: {missing_vectors[:3]}"
                )
        
        # Determine law_code dynamically for namespace clearing
        law_code = "UNKNOWN"
        if nodes and "properties" in nodes[0] and "law_code" in nodes[0]["properties"]:
            law_code = nodes[0]["properties"]["law_code"]
        elif cli_law_code:
            law_code = cli_law_code

        # Initialize schema and pre-indexes
        self.initialize_schema(
            next(iter(vector_dimensions)) if vector_dimensions else None
        )

        if replace:
            self.clear_namespace(law_code)

        # Process Nodes - Guarantee law_code for Idempotency
        for node in nodes:
            if "properties" not in node:
                node["properties"] = {}
            if "law_code" not in node["properties"] and law_code != "UNKNOWN":
                node["properties"]["law_code"] = law_code
                
        node_rows = [CypherGenerator.node_parameters(node) for node in nodes]
        node_batches = 0
        with self.driver.session(database=self.database) as session:
            for start in range(0, len(node_rows), self.batch_size):
                batch = node_rows[start : start + self.batch_size]
                session.run(CypherGenerator.NODE_BATCH, rows=batch)
                node_batches += 1

        # Phase 5: Apply native Neo4j labels using Python-loop fallback (Neo4j 5.x safe)
        labels_applied = 0
        with self.driver.session(database=self.database) as session:
            for node in nodes:
                node_id = node.get("id")
                for label in node.get("labels", []):
                    if label in self.LABEL_ALLOWLIST:
                        cypher = f"MATCH (n:UKG_NODE {{id: $node_id}}) SET n:`{label}`"
                        session.run(cypher, node_id=node_id)
                        labels_applied += 1

        # Pillar 1: In-Memory Dead Letter Queue
        valid_node_ids = {node["id"] for node in nodes}
        valid_edges = []
        dead_letter_edges = []
        
        edge_accounting = {
            "attempted": len(edges),
            "created": 0,
            "already_exists": 0,
            "missing_source": 0,
            "missing_target": 0,
            "missing_both": 0,
            "execution_failed": 0,
            "edge_batches": 0,
        }

        for edge in edges:
            src = edge.get("source")
            tgt = edge.get("target")
            src_exists = src in valid_node_ids
            tgt_exists = tgt in valid_node_ids
            
            if not src_exists and not tgt_exists:
                edge_accounting["missing_both"] += 1
                dead_letter_edges.append(edge)
            elif not src_exists:
                edge_accounting["missing_source"] += 1
                dead_letter_edges.append(edge)
            elif not tgt_exists:
                edge_accounting["missing_target"] += 1
                dead_letter_edges.append(edge)
            else:
                valid_edges.append(edge)
                edge_accounting["created"] += 1

        # Dump DLQ if any
        if dead_letter_edges:
            os.makedirs("outputs", exist_ok=True)
            dlq_path = "outputs/dlq_edges.json"
            with open(dlq_path, "w", encoding="utf-8") as f:
                json.dump(dead_letter_edges, f, ensure_ascii=False, indent=2)
            print(f"Logged {len(dead_letter_edges)} invalid edges to DLQ ({dlq_path}).")

        # Pillar 2: Fast-Path Cypher Grouping by Type
        edges_by_type = defaultdict(list)
        for edge in valid_edges:
            edges_by_type[edge["type"]].append(CypherGenerator.edge_parameters(edge))

        with self.driver.session(database=self.database) as session:
            for edge_type, rows in edges_by_type.items():
                query = CypherGenerator.get_edge_batch_query(edge_type)
                for start in range(0, len(rows), self.batch_size):
                    batch = rows[start : start + self.batch_size]
                    try:
                        session.run(query, rows=batch)
                        edge_accounting["edge_batches"] += 1
                    except Exception as e:
                        print(f"Edge batch execution failed for type {edge_type}: {e}")
                        edge_accounting["execution_failed"] += len(batch)
                        edge_accounting["created"] -= len(batch)

        return {
            "nodes": len(node_rows),
            "edges": len(valid_edges),
            "node_batches": node_batches,
            "edge_batches": edge_accounting["edge_batches"],
        }