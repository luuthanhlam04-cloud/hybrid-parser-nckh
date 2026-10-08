"""BM25 index for the legal corpus used by the benchmark harness."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pyvi import ViTokenizer
from rank_bm25 import BM25Okapi


INDEX_SCHEMA_VERSION = 1
TOKENIZER_NAME = "pyvi.ViTokenizer"


@dataclass(frozen=True)
class IndexedDocument:
    article_id: str
    text: str
    tokens: list[str]


class BM25Index:
    """Build, persist, and query a BM25 index with Vietnamese word segmentation."""

    def __init__(self, documents: list[IndexedDocument]) -> None:
        if not documents:
            raise ValueError("The corpus must contain at least one document.")
        self.documents = documents
        self._bm25 = BM25Okapi([document.tokens for document in documents])

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return ViTokenizer.tokenize(text).lower().split()

    @classmethod
    def build_or_load(
        cls,
        corpus_path: str | Path,
        index_path: str | Path,
        *,
        force_rebuild: bool = False,
    ) -> tuple[BM25Index, bool]:
        corpus_file = Path(corpus_path)
        index_file = Path(index_path)
        corpus_bytes = corpus_file.read_bytes()
        corpus_digest = hashlib.sha256(corpus_bytes).hexdigest()

        if index_file.is_file() and not force_rebuild:
            payload = json.loads(index_file.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                raise ValueError(f"BM25 index must be a JSON object: {index_file}")
            if (
                payload.get("schema_version") == INDEX_SCHEMA_VERSION
                and payload.get("corpus_sha256") == corpus_digest
                and payload.get("tokenizer") == TOKENIZER_NAME
            ):
                documents = cls._load_documents(payload)
                return cls(documents), False

        corpus = json.loads(corpus_bytes.decode("utf-8"))
        if not isinstance(corpus, list) or not corpus:
            raise ValueError(f"Corpus must be a non-empty JSON array: {corpus_file}")

        documents = []
        seen_ids: set[str] = set()
        for position, item in enumerate(corpus):
            if not isinstance(item, dict):
                raise ValueError(f"Corpus item {position} must be a JSON object.")
            article_id = item.get("article_id")
            text = item.get("text")
            if not isinstance(article_id, str) or not article_id.strip():
                raise ValueError(f"Corpus item {position} has no valid article_id.")
            if article_id in seen_ids:
                raise ValueError(f"Duplicate article_id in corpus: {article_id}")
            if not isinstance(text, str) or not text.strip():
                raise ValueError(f"Corpus item {position} ({article_id}) has no text.")
            seen_ids.add(article_id)
            documents.append(
                IndexedDocument(
                    article_id=article_id,
                    text=text,
                    tokens=cls._tokenize(text),
                )
            )

        index_file.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": INDEX_SCHEMA_VERSION,
            "corpus_sha256": corpus_digest,
            "tokenizer": TOKENIZER_NAME,
            "documents": [
                {
                    "article_id": document.article_id,
                    "text": document.text,
                    "tokens": document.tokens,
                }
                for document in documents
            ],
        }
        temp_path: str | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=index_file.parent,
                prefix=f".{index_file.name}.",
                suffix=".tmp",
                delete=False,
            ) as stream:
                temp_path = stream.name
                json.dump(payload, stream, ensure_ascii=False)
            os.replace(temp_path, index_file)
            temp_path = None
        finally:
            if temp_path is not None:
                Path(temp_path).unlink(missing_ok=True)

        return cls(documents), True

    @staticmethod
    def _load_documents(payload: dict[str, Any]) -> list[IndexedDocument]:
        raw_documents = payload.get("documents")
        if not isinstance(raw_documents, list) or not raw_documents:
            raise ValueError("BM25 index has no documents.")

        documents = []
        seen_ids: set[str] = set()
        for position, item in enumerate(raw_documents):
            if not isinstance(item, dict):
                raise ValueError(f"BM25 index document {position} is invalid.")
            article_id = item.get("article_id")
            text = item.get("text")
            tokens = item.get("tokens")
            if (
                not isinstance(article_id, str)
                or not article_id.strip()
                or article_id in seen_ids
                or not isinstance(text, str)
                or not isinstance(tokens, list)
                or not all(isinstance(token, str) for token in tokens)
            ):
                raise ValueError(f"BM25 index document {position} is invalid.")
            seen_ids.add(article_id)
            documents.append(
                IndexedDocument(article_id=article_id, text=text, tokens=tokens)
            )
        return documents

    def retrieve(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string.")
        if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 1:
            raise ValueError("top_k must be a positive integer.")

        scores = self._bm25.get_scores(self._tokenize(query))
        ranked_indices = sorted(
            range(len(self.documents)),
            key=lambda index: (-float(scores[index]), index),
        )[:top_k]
        return [
            {
                "article_id": self.documents[index].article_id,
                "text": self.documents[index].text,
                "score": float(scores[index]),
            }
            for index in ranked_indices
        ]
