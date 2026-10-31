"""Vector anchor lookup for M10 using the M5 precomputed node embeddings."""

from __future__ import annotations

import json
import math
import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np


DEFAULT_EMBEDDING_DIR = Path("outputs/embeddings/luat_dat_dai_ch3")
DEFAULT_PHYSICAL_GRAPH = Path("outputs/physical_graphs/physical_graph.json")
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
        physical_graph_path: str | Path = DEFAULT_PHYSICAL_GRAPH,
        lexical_slots: int = 4,
    ) -> None:
        _, vectors, metadata = load_embedding_cache(embedding_dir)
        self.dimension = int(vectors.shape[1])
        self.model_name = metadata["model"]
        self.driver = driver
        self.database = database
        self.embedding_dir = Path(embedding_dir)
        self.encoder = encoder
        self.physical_graph_path = Path(physical_graph_path)
        self.lexical_slots = lexical_slots
        self._lexical_documents: list[dict[str, Any]] | None = None

    @staticmethod
    def _lexical_tokens(text: str) -> list[str]:
        normalized = unicodedata.normalize("NFD", text.casefold())
        normalized = "".join(char for char in normalized if unicodedata.category(char) != "Mn")
        stop = {
            "va", "la", "cua", "co", "duoc", "thi", "theo", "nay", "do", "mot",
            "nhung", "cac", "cho", "tai", "trong", "khi", "ve", "voi", "phai",
        }
        return [token for token in re.findall(r"[a-z0-9]+", normalized) if len(token) > 1 and token not in stop]

    def _load_lexical_documents(self) -> list[dict[str, Any]]:
        if self._lexical_documents is not None:
            return self._lexical_documents
        if not self.physical_graph_path.is_file():
            self._lexical_documents = []
            return self._lexical_documents
        graph = json.loads(self.physical_graph_path.read_text(encoding="utf-8"))
        documents=[]
        for node in graph.get("nodes",[]):
            properties=node.get("properties",{})
            text=" ".join(str(value) for value in (properties.get("title"),properties.get("text")) if value).strip()
            if not text:
                continue
            documents.append({
                "node_id":node["id"], "text":properties.get("text") or "", "title":properties.get("title"),
                "number":properties.get("number"), "law_code":properties.get("law_code"), "labels":node.get("labels",[]),
                "tokens":self._lexical_tokens(text), "raw":text.casefold(),
            })
        self._lexical_documents=documents
        return documents

    def _lexical_search(self, question: str, *, top_k: int) -> list[dict[str, Any]]:
        documents=self._load_lexical_documents()
        query_tokens=self._lexical_tokens(question)
        if not documents or not query_tokens:
            return []
        document_frequency=Counter()
        for document in documents:
            document_frequency.update(set(document["tokens"]))
        average_length=sum(len(document["tokens"]) for document in documents)/len(documents)
        explicit_articles=set(re.findall(r"(?:điều|dieu)\s+(\d+)", unicodedata.normalize("NFC",question).casefold()))
        scored=[]
        for document in documents:
            frequencies=Counter(document["tokens"])
            length=max(1,len(document["tokens"]))
            score=0.0
            for token in set(query_tokens):
                tf=frequencies[token]
                if not tf:
                    continue
                idf=math.log(1+(len(documents)-document_frequency[token]+.5)/(document_frequency[token]+.5))
                score+=idf*(tf*2.2)/(tf+1.2*(.25+.75*length/max(1,average_length)))
            # Explicit legal locators are deterministic query facts, not gold annotations.
            if explicit_articles and any(f"_dieu-{article}" in document["node_id"] for article in explicit_articles):
                score+=8.0
            if score>0:
                scored.append((score,document))
        scored.sort(key=lambda item:(-item[0],item[1]["node_id"]))
        maximum=scored[0][0] if scored else 1.0
        return [{
            **{key:value for key,value in document.items() if key not in {"tokens","raw"}},
            "score":score/maximum,
            "lexical_score":score,
            "retrieval_source":"LEXICAL_PHYSICAL_GRAPH",
        } for score,document in scored[:top_k]]

    def search_lexical_auxiliary(self, question: str, *, top_k: int = 10) -> list[dict[str, Any]]:
        """Extra local-only anchors for reference expansion; not part of anchor@5."""
        if not isinstance(question, str) or not question.strip():
            raise ValueError("question must be a non-empty string.")
        return self._lexical_search(question.strip(), top_k=top_k)

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
            vector_rows = [dict(record) for record in result]
        for row in vector_rows:
            row["vector_score"] = row.get("score")
            row["retrieval_source"] = "NEO4J_VECTOR"
        # Custom embedding caches used by unit tests remain vector-only. Production
        # Chapter III retrieval fuses deterministic lexical anchors with the local vector index.
        if self.embedding_dir.resolve() != DEFAULT_EMBEDDING_DIR.resolve() or self.lexical_slots <= 0:
            return vector_rows
        lexical=self._lexical_search(question.strip(),top_k=max(top_k,self.lexical_slots))
        merged=[]
        for row in lexical[:min(top_k,self.lexical_slots)]+vector_rows:
            if row.get("node_id") not in {item.get("node_id") for item in merged}:
                merged.append(row)
            if len(merged)>=top_k:
                break
        return merged
