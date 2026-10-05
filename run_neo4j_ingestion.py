"""Load and verify the current Unified Graph in Neo4j."""

from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from src.neo4j_ingestion import GraphChecker, Neo4jIngestor
from src.retrieval.anchor_search import DEFAULT_EMBEDDING_DIR, attach_embeddings_to_graph


DEFAULT_GRAPH = Path("outputs/unified_graphs/unified_knowledge_graph.json")
DEFAULT_CANONICAL = Path("outputs/canonical_graphs/canonical_semantic_graph.json")


def _run_completeness_gate(canonical_path: Path, ukg_graph: dict) -> None:
    """Phase 3: Block ingestion if M7->M8 norm coverage is not 100% (1:N cardinality check)."""
    if not canonical_path.is_file():
        print(f"[GATE] WARNING: canonical graph not found. Skipping completeness gate.")
        return
    canonical = json.loads(canonical_path.read_text(encoding="utf-8"))
    valid_norms = [n for n in canonical.get("norms", []) if n.get("status") == "VALID"]
    valid_norm_ids = set(n["id"] for n in valid_norms)
    prov_to_norms: dict = defaultdict(list)
    for n in valid_norms:
        prov = n.get("provenance_node_id")
        if prov:
            prov_to_norms[prov].append(n["id"])
    global_norms = [nd for nd in ukg_graph.get("nodes", []) if "GLOBAL_NORM" in nd.get("labels", [])]
    ukg_prov_ids: set = set()
    for gn in global_norms:
        for sid in gn["properties"].get("source_node_ids", []):
            ukg_prov_ids.add(sid)
    covered_norm_ids: set = set()
    for prov in ukg_prov_ids:
        for nid in prov_to_norms.get(prov, []):
            covered_norm_ids.add(nid)
    missing = valid_norm_ids - covered_norm_ids
    unexpected = ukg_prov_ids - set(prov_to_norms.keys())
    print(f"[GATE] M7 VALID norms={len(valid_norm_ids)}, UKG GLOBAL_NORM={len(global_norms)}, covered={len(covered_norm_ids)}, missing={len(missing)}")
    if missing:
        raise RuntimeError(
            f"[GATE BLOCKED] {len(missing)} M7 VALID norms are missing from UKG. "
            "Fix M8 fusion first. Sample missing: " + ", ".join(sorted(missing)[:3])
        )
    print("[GATE] Completeness gate PASSED.")


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
        "--embedding-dir",
        type=Path,
        default=DEFAULT_EMBEDDING_DIR,
        help="M5 embedding cache used to create the Neo4j vector index.",
    )
    parser.add_argument(
        "--skip-vector-embeddings",
        action="store_true",
        help="Ingest without attaching M5 vectors or creating a vector index.",
    )
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
    if not args.skip_vector_embeddings:
        dimensions = attach_embeddings_to_graph(graph, args.embedding_dir)
        print(f"[VECTOR] Attached M5 embeddings ({dimensions} dimensions).")

    # Phase 3: Completeness Gate
    _run_completeness_gate(DEFAULT_CANONICAL, graph)

    try:
        from neo4j import GraphDatabase
    except ImportError as exc:
        raise RuntimeError(
            "Neo4j ingestion requires the neo4j Python package."
        ) from exc

    # For AuraDB (neo4j+s:// scheme), TLS is handled by the URI scheme itself.
    # Driver 6.x does not accept ssl_context with +s:// schemes.
    # If cert verification fails due to system trust store, convert to +ssc:// (skips cert verify).
    effective_uri = uri.replace("neo4j+s://", "neo4j+ssc://").replace("bolt+s://", "bolt+ssc://")
    driver = GraphDatabase.driver(effective_uri, auth=(username, password))
    try:
        driver.verify_connectivity()
        ingestor = Neo4jIngestor(driver, database, args.batch_size)
        write_report = ingestor.ingest(graph, replace=args.replace)
        check_report = GraphChecker(driver, database).check(graph)

        # Phase 2: Edge accounting summary
        acct_keys = ("attempted","created","already_exists","missing_source","missing_target","missing_both","execution_failed")
        edge_acct = {k: write_report.get(k, 0) for k in acct_keys if k in write_report}
        if edge_acct:
            total_missing = edge_acct.get("missing_source",0) + edge_acct.get("missing_target",0) + edge_acct.get("missing_both",0)
            print(f"[ACCOUNTING] {edge_acct}")
            if total_missing > 0:
                print(f"[ACCOUNTING] WARNING: {total_missing} edges had missing endpoints.")

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
