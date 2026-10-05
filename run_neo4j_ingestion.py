"""Load and verify the current Unified Graph in Neo4j."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from src.neo4j_ingestion import GraphChecker, Neo4jIngestor


DEFAULT_GRAPH = Path("outputs/unified_graphs/unified_knowledge_graph.json")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Batch-ingest and verify a Unified Graph in Neo4j."
    )
    parser.add_argument(
        "graph", nargs="?", type=Path, default=DEFAULT_GRAPH,
        help=f"Unified Graph JSON (default: {DEFAULT_GRAPH})",
    )
    parser.add_argument(
        "--database",
        default=None,
        help="Database name (defaults to NEO4J_DATABASE or the server's home database).",
    )
    parser.add_argument("--batch-size", type=int, default=1000)
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Delete existing UKG_NODE data before loading (does not touch other labels).",
    )
    args = parser.parse_args()

    load_dotenv()
    uri = os.environ.get("NEO4J_URI")
    username = os.environ.get("NEO4J_USERNAME")
    password = os.environ.get("NEO4J_PASSWORD")
    database = args.database or os.environ.get("NEO4J_DATABASE")
    if not uri or not username or not password:
        raise RuntimeError(
            "Set NEO4J_URI, NEO4J_USERNAME, and NEO4J_PASSWORD in the ignored .env file."
        )
    if not args.graph.is_file():
        raise FileNotFoundError(f"Unified Graph JSON not found: {args.graph}")

    graph: dict[str, Any] = json.loads(args.graph.read_text(encoding="utf-8"))
    try:
        from neo4j import GraphDatabase
    except ImportError as exc:
        raise RuntimeError(
            "Neo4j ingestion requires the neo4j Python package."
        ) from exc

    driver = GraphDatabase.driver(uri, auth=(username, password))
    try:
        driver.verify_connectivity()
        ingestor = Neo4jIngestor(driver, database, args.batch_size)
        write_report = ingestor.ingest(graph, replace=args.replace)
        check_report = GraphChecker(driver, database).check(graph)
        print(
            json.dumps(
                {"ingestion": write_report, "integrity": check_report},
                ensure_ascii=False,
                indent=2,
            )
        )
        if not check_report["is_valid"]:
            raise RuntimeError("Neo4j integrity check failed; inspect the report above.")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
