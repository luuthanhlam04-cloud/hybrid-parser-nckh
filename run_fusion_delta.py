"""Apply a previously generated UKG delta to Neo4j transactionally."""

import argparse
import json
import os
from pathlib import Path

from src.fusion.delta_engine import DeltaEngine, Neo4jDeltaApplier


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("previous_graph", type=Path)
    parser.add_argument("current_graph", type=Path)
    parser.add_argument("--database")
    args = parser.parse_args()
    uri = os.environ.get("NEO4J_URI")
    username = os.environ.get("NEO4J_USERNAME")
    password = os.environ.get("NEO4J_PASSWORD")
    if not uri or not username or not password:
        raise RuntimeError(
            "Set NEO4J_URI, NEO4J_USERNAME and NEO4J_PASSWORD before applying a delta."
        )
    try:
        from neo4j import GraphDatabase
    except ImportError as exc:
        raise RuntimeError("Neo4j delta apply requires the neo4j Python package.") from exc

    previous = json.loads(args.previous_graph.read_text(encoding="utf-8"))
    current = json.loads(args.current_graph.read_text(encoding="utf-8"))
    delta = DeltaEngine().diff(previous, current)
    driver = GraphDatabase.driver(uri, auth=(username, password))
    try:
        driver.verify_connectivity()
        applier = Neo4jDeltaApplier(driver, args.database)
        applier.initialize_schema()
        applier.apply(delta)
    finally:
        driver.close()
    print(json.dumps({key: len(value) for key, value in delta.items()}, indent=2))


if __name__ == "__main__":
    main()
