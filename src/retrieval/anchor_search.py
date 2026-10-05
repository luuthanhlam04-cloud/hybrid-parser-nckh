"""Vector anchor lookup for M10 using the M5 precomputed node embeddings."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np


DEFAULT_EMBEDDING_DIR = Path("outputs/embeddings/luat_dat_dai_ch3")
VECTOR_INDEX_NAME = "legal_node_vector_idx"


def load_embedding_cache(
    embedding_dir: str | Path = DEFAULT_EMBEDDING_DIR,
) -> tuple[list[str], np.ndarray, dict[str, Any]]:
    """Load M5 vectors and validate their metadata and row mapping."""
    directory = Path(embedding_dir)
    embeddings_path = directory / "embeddings.npy"
    node_ids_path = directory / "node_ids.json"
    metadata_path = directory / "embeddings.meta.json"
    for path in (embeddings_path, node_ids_path, metadata_path):
        if not path.is_file():
            raise FileNotFoundError(f"Embedding cache file not found: {path}")

    vectors = np.load(embeddings_path, mmap_mode="r")
    node_ids = json.loads(node_ids_path.read_text(encoding="utf-8"))
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if vectors.ndim != 2 or len(node_ids) != vectors.shape[0]:
        raise ValueError("Embedding rows and node IDs do not align.")
    if len(set(node_ids)) != len(node_ids):
        raise ValueError("Embedding node IDs must be unique.")
    if metadata.get("dimension") != vectors.shape[1]:
        raise ValueError("Embedding metadata dimension does not match the vector file.")
    if metadata.get("node_count") != len(node_ids):
        raise ValueError("Embedding metadata node count does not match the ID file.")
    if not isinstance(metadata.get("model"), str) or not metadata["model"].strip():
        raise ValueError("Embedding metadata must name the encoder model.")
    return node_ids, vectors, metadata


def attach_embeddings_to_graph(
    graph: dict[str, Any],
    embedding_dir: str | Path = DEFAULT_EMBEDDING_DIR,
) -> int:
    """Attach cached vectors to physical UKG nodes in memory for Neo4j ingestion."""
    node_ids, vectors, _ = load_embedding_cache(embedding_dir)
    nodes_by_id = {
        node["id"]: node
        for node in graph.get("nodes", [])
        if "LegalNode" in node.get("labels", [])
    }
    if set(nodes_by_id) != set(node_ids):
        missing_vectors = sorted(set(nodes_by_id) - set(node_ids))
        missing_nodes = sorted(set(node_ids) - set(nodes_by_id))
        raise ValueError(
            "M5 embeddings do not match physical UKG nodes; "
            f"nodes_without_vectors={missing_vectors[:3]}, "
            f"vectors_without_nodes={missing_nodes[:3]}"
        )

    for index, node_id in enumerate(node_ids):
        properties = nodes_by_id[node_id].setdefault("properties", {})
        properties["embedding"] = np.asarray(vectors[index], dtype=np.float32).tolist()
    return int(vectors.shape[1])


class AnchorSearch:
    """Embed a question and retrieve its nearest physical UKG nodes."""

    QUERY = """
        CALL db.index.vector.queryNodes($index_name, $top_k, $embedding)
        YIELD node, score
        WHERE node:LegalNode
        RETURN node.id AS node_id,
               score,
               node.text AS text,
               node.number AS number,
               node.title AS title,
               node.law_code AS law_code,
               labels(node) AS labels
        ORDER BY score DESC
    """

    def __init__(
        self,
        driver: Any,
        database: str | None = None,
        embedding_dir: str | Path = DEFAULT_EMBEDDING_DIR,
        encoder: Any | None = None,
    ) -> None:
        _, vectors, metadata = load_embedding_cache(embedding_dir)
        self.dimension = int(vectors.shape[1])
        self.model_name = metadata["model"]
        self.driver = driver
        self.database = database
        self.embedding_dir = Path(embedding_dir)
        self.encoder = encoder

    def _get_encoder(self) -> Any:
        if self.encoder is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as exc:
                raise RuntimeError(
                    "Anchor search requires sentence-transformers."
                ) from exc
            self.encoder = SentenceTransformer(
                self.model_name,
                trust_remote_code=True,
            )
        return self.encoder

    def search(self, question: str, *, top_k: int = 5) -> list[dict[str, Any]]:
        if not isinstance(question, str) or not question.strip():
            raise ValueError("question must be a non-empty string.")
        if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 1:
            raise ValueError("top_k must be a positive integer.")

        vector = np.asarray(
            self._get_encoder().encode(
                [question.strip()],
                normalize_embeddings=False,
                convert_to_numpy=True,
                show_progress_bar=False,
            ),
            dtype=np.float32,
        )
        if vector.shape != (1, self.dimension):
            raise ValueError(
                f"Query embedding has shape {vector.shape}; expected (1, {self.dimension})."
            )
        embedding = vector[0].tolist()
        with self.driver.session(database=self.database) as session:
            result = session.run(
                self.QUERY,
                index_name=VECTOR_INDEX_NAME,
                top_k=top_k,
                embedding=embedding,
            )
            return [dict(record) for record in result]