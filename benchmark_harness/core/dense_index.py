"""Dense and BM25+dense retrieval indexes for the legal benchmark."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

from .bm25_index import BM25Index, IndexedDocument


DENSE_INDEX_SCHEMA_VERSION = 1
DEFAULT_EMBEDDING_MODEL = "BAAI/bge-m3"


class DenseIndex:
    """Persist document embeddings and search them with cosine similarity."""

    def __init__(
        self,
        documents: list[IndexedDocument],
        embeddings: np.ndarray,
        encoder: Any,
    ) -> None:
        vectors = np.asarray(embeddings, dtype=np.float32)
        if vectors.ndim != 2 or vectors.shape[0] != len(documents):
            raise ValueError("Dense embedding rows must align with corpus documents.")
        if vectors.shape[1] < 1 or not np.isfinite(vectors).all():
            raise ValueError("Dense embeddings must be finite, non-empty vectors.")
        if not np.allclose(np.linalg.norm(vectors, axis=1), 1.0, atol=1e-3):
            raise ValueError("Dense document embeddings must be normalized.")
        self.documents = documents
        self.embeddings = vectors
        self.encoder = encoder

    @staticmethod
    def _load_encoder(
        model_name: str,
        device: str,
        local_files_only: bool,
    ) -> Any:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError(
                "Dense retrieval requires sentence-transformers; install "
                "benchmark_harness/requirements-vector.txt."
            ) from exc
        try:
            return SentenceTransformer(
                model_name,
                device=device,
                local_files_only=local_files_only,
            )
        except OSError as exc:
            if local_files_only:
                detail = "The model is not available in the local Hugging Face cache."
            else:
                detail = "The model could not be loaded or downloaded."
            raise RuntimeError(f"{detail} Model: {model_name!r}.") from exc

    @classmethod
    def build_or_load(
        cls,
        corpus_path: str | Path,
        index_path: str | Path,
        *,
        model_name: str = DEFAULT_EMBEDDING_MODEL,
        batch_size: int = 4,
        device: str = "auto",
        local_files_only: bool = False,
        force_rebuild: bool = False,
    ) -> tuple[DenseIndex, bool]:
        if (
            isinstance(batch_size, bool)
            or not isinstance(batch_size, int)
            or batch_size < 1
        ):
            raise ValueError("batch_size must be a positive integer.")
        if not model_name.strip():
            raise ValueError("model_name must be a non-empty string.")

        index_file = Path(index_path)
        corpus_file = Path(corpus_path)
        corpus_digest = hashlib.sha256(corpus_file.read_bytes()).hexdigest()
        payload: dict[str, Any] | None = None
        vectors: np.ndarray | None = None

        if index_file.is_file() and not force_rebuild:
            try:
                with np.load(index_file, allow_pickle=False) as cache:
                    payload = json.loads(str(cache["metadata"].item()))
                    if not isinstance(payload, dict):
                        raise ValueError("dense index metadata must be a JSON object.")
                    cached_ids = cache["article_ids"].tolist()
                    vectors = np.asarray(cache["embeddings"], dtype=np.float32)
            except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
                raise ValueError(f"Cannot read dense index {index_file}: {exc}") from exc

        cache_matches = (
            payload is not None
            and isinstance(payload, dict)
            and payload.get("schema_version") == DENSE_INDEX_SCHEMA_VERSION
            and payload.get("corpus_sha256") == corpus_digest
            and payload.get("model") == model_name
        )
        bm25_index, _ = BM25Index.build_or_load(
            corpus_file,
            index_file.parent / "bm25_validation_cache.json",
            force_rebuild=force_rebuild,
        )
        corpus_ids = [document.article_id for document in bm25_index.documents]
        if cache_matches and (
            cached_ids != corpus_ids
            or vectors is None
            or vectors.ndim != 2
            or vectors.shape[0] != len(corpus_ids)
            or payload.get("document_count") != len(corpus_ids)
            or payload.get("dimension") != vectors.shape[1]
            or payload.get("normalized") is not True
            or not np.isfinite(vectors).all()
        ):
            raise ValueError(f"Dense index metadata or embeddings are invalid: {index_file}")

        effective_device = device
        if device == "auto":
            try:
                import torch
            except ImportError as exc:
                raise RuntimeError(
                    "Dense retrieval requires PyTorch; install "
                    "benchmark_harness/requirements-vector.txt."
                ) from exc
            effective_device = "cuda" if torch.cuda.is_available() else "cpu"
        encoder = cls._load_encoder(model_name, effective_device, local_files_only)
        if cache_matches:
            return cls(bm25_index.documents, vectors, encoder), False

        texts = [document.text for document in bm25_index.documents]
        embeddings = np.asarray(
            encoder.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=True,
                normalize_embeddings=True,
                convert_to_numpy=True,
            ),
            dtype=np.float32,
        )
        dense_index = cls(bm25_index.documents, embeddings, encoder)

        index_file.parent.mkdir(parents=True, exist_ok=True)
        metadata = {
            "schema_version": DENSE_INDEX_SCHEMA_VERSION,
            "corpus_sha256": corpus_digest,
            "model": model_name,
            "device": effective_device,
            "document_count": len(corpus_ids),
            "dimension": int(embeddings.shape[1]),
            "normalized": True,
        }
        temp_path: str | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w+b",
                dir=index_file.parent,
                prefix=f".{index_file.name}.",
                suffix=".tmp",
                delete=False,
            ) as stream:
                temp_path = stream.name
                np.savez_compressed(
                    stream,
                    metadata=np.asarray(json.dumps(metadata)),
                    article_ids=np.asarray(corpus_ids),
                    embeddings=embeddings,
                )
            os.replace(temp_path, index_file)
            temp_path = None
        finally:
            if temp_path is not None:
                Path(temp_path).unlink(missing_ok=True)
        return dense_index, True

    def retrieve(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string.")
        if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 1:
            raise ValueError("top_k must be a positive integer.")

        query_vector = np.asarray(
            self.encoder.encode(
                [query.strip()],
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False,
            ),
            dtype=np.float32,
        )
        if query_vector.shape != (1, self.embeddings.shape[1]):
            raise ValueError(
                "Query embedding dimension does not match the document index: "
                f"{query_vector.shape} vs {(1, self.embeddings.shape[1])}."
            )
        if not np.isfinite(query_vector).all():
            raise ValueError("Query embedding contains non-finite values.")

        scores = self.embeddings @ query_vector[0]
        ranked_indices = sorted(
            range(len(self.documents)),
            key=lambda position: (-float(scores[position]), position),
        )[:top_k]
        return [
            {
                "article_id": self.documents[position].article_id,
                "text": self.documents[position].text,
                "score": float(scores[position]),
            }
            for position in ranked_indices
        ]


def reciprocal_rank_fusion(
    sparse_results: list[dict[str, Any]],
    dense_results: list[dict[str, Any]],
    *,
    top_k: int,
    rrf_k: int = 60,
) -> list[dict[str, Any]]:
    """Fuse sparse and dense rankings without score-scale assumptions."""
    if top_k < 1 or rrf_k < 1:
        raise ValueError("top_k and rrf_k must be positive integers.")

    fused_scores: dict[str, float] = {}
    documents: dict[str, dict[str, Any]] = {}
    for results in (sparse_results, dense_results):
        for rank, document in enumerate(results, start=1):
            article_id = document["article_id"]
            if article_id not in documents:
                documents[article_id] = document
            fused_scores[article_id] = fused_scores.get(article_id, 0.0) + (
                1.0 / (rrf_k + rank)
            )

    ranked_ids = sorted(
        fused_scores,
        key=lambda article_id: -fused_scores[article_id],
    )[:top_k]
    return [
        {
            **documents[article_id],
            "score": fused_scores[article_id],
        }
        for article_id in ranked_ids
    ]
