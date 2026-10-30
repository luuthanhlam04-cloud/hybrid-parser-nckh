"""A real, isolated LightRAG adapter derived from the old benchmark wrapper.

Unlike the legacy wrapper, this module has no simulated answers.  It stores its
workspace below outputs/benchmark_b/lightrag and records provider-reported usage.
"""

from __future__ import annotations

import asyncio
import json
import os
import shutil
import time
from pathlib import Path
from typing import Any

from benchmark_b.costs import CostLedger
from .base import BenchmarkSystem


class LightRAGSystem(BenchmarkSystem):
    name = "lightrag"

    def __init__(self, output_dir: str | Path, *, model: str | None = None) -> None:
        super().__init__(output_dir)
        self.workspace = self.output_dir / "workspace"
        self.model = model or os.getenv("BENCHMARK_B_LIGHTRAG_MODEL", "openai/gpt-4o-mini")
        self.ledger = CostLedger(self.model)
        self.rag: Any | None = None
        self._phase = "index"

    def readiness(self) -> dict[str, Any]:
        try:
            import lightrag  # noqa: F401
            import sentence_transformers  # noqa: F401
            available = True
            error = None
        except ImportError as exc:
            available = False
            error = str(exc)
        key_present = bool(os.getenv("OPENROUTER_API_KEY") or os.getenv("LLM_API_KEY"))
        return {"system": self.name, "ready": available and key_present, "lightrag_importable": available, "api_key_present": key_present, "dependency_error": error, "workspace": str(self.workspace)}

    def _require_dependencies(self) -> None:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("LLM_API_KEY")
        if not api_key:
            raise RuntimeError("LightRAG benchmark requires OPENROUTER_API_KEY or LLM_API_KEY in .env.")
        os.environ["OPENROUTER_API_KEY"] = api_key
        try:
            from lightrag import LightRAG, QueryParam  # noqa: F401
            from lightrag.utils import EmbeddingFunc  # noqa: F401
            from sentence_transformers import SentenceTransformer  # noqa: F401
        except ImportError as exc:
            raise RuntimeError("LightRAG is not installed. Install the LightRAG package documented in docs/benchmark_b_pipeline.md; benchmark results are never mocked.") from exc

    def _build_rag(self) -> Any:
        self._require_dependencies()
        if self.rag is not None:
            return self.rag
        from lightrag import LightRAG
        from lightrag.utils import EmbeddingFunc
        from sentence_transformers import SentenceTransformer
        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            device = "cpu"
        encoder = SentenceTransformer("BAAI/bge-m3", device=device)

        async def embedding_func(texts: list[str]) -> list[list[float]]:
            return encoder.encode(texts, normalize_embeddings=True).tolist()

        async def completion_func(prompt: str, system_prompt: str | None = None, history_messages: list[dict[str, str]] | None = None, **kwargs: Any) -> str:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])
            messages: list[dict[str, str]] = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.extend(history_messages or [])
            messages.append({"role": "user", "content": prompt})
            response = await client.chat.completions.create(model=self.model, messages=messages, temperature=0.0)
            self.ledger.add_usage(self._phase, getattr(response, "usage", None))
            content = response.choices[0].message.content
            if not isinstance(content, str) or not content.strip():
                raise RuntimeError("LightRAG completion model returned an empty response.")
            return content

        self.workspace.mkdir(parents=True, exist_ok=True)
        self.rag = LightRAG(
            working_dir=str(self.workspace),
            embedding_func=EmbeddingFunc(embedding_dim=1024, max_token_size=8192, func=embedding_func),
            llm_model_func=completion_func,
            llm_model_name=self.model,
            llm_model_max_async=4,
            chunk_token_size=1200,
            chunk_overlap_token_size=100,
        )
        return self.rag

    @staticmethod
    def _run(value: Any) -> Any:
        if asyncio.iscoroutine(value):
            return asyncio.run(value)
        return value

    def index(self, corpus: list[dict[str, Any]], *, fresh: bool = False) -> dict[str, Any]:
        if fresh and self.workspace.exists():
            shutil.rmtree(self.workspace)
            self.rag = None
        if self.workspace.exists() and any(self.workspace.iterdir()) and not fresh:
            raise RuntimeError("LightRAG workspace already exists. Use --fresh for a new indexing run or preserve it for query-only evaluation.")
        started = time.perf_counter()
        rag = self._build_rag()
        self._phase = "index"
        texts = [document["text"] for document in corpus]
        self._run(rag.insert(texts))
        metadata = {
            "system": self.name,
            "workspace": str(self.workspace),
            "fresh_index": fresh,
            "corpus_article_count": len(corpus),
            "corpus_article_ids": [document["article_id"] for document in corpus],
            "index_duration_ms": round((time.perf_counter() - started) * 1000, 2),
            "embedding": {"model": "BAAI/bge-m3", "dimensions": 1024, "execution": "local"},
            "chunking": {"token_size": 1200, "overlap_tokens": 100},
            "package_provenance": self._package_provenance(),
            "cost_ledger": self.ledger.to_dict(),
        }
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "index_metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return metadata

    @staticmethod
    def _package_provenance() -> dict[str, str | None]:
        try:
            import lightrag
            return {"module": "lightrag", "version": getattr(lightrag, "__version__", None)}
        except ImportError:
            return {"module": "lightrag", "version": None}

    @staticmethod
    def _article_ids_from_context(context: str) -> list[str] | None:
        import re
        matches = re.findall(r"\[ARTICLE_ID:\s*([^\]]+)\]", context or "")
        if not matches:
            return None
        return list(dict.fromkeys(matches))

    def answer(self, question: dict[str, Any], *, top_k: int) -> dict[str, Any]:
        self._phase = "query"
        rag = self._build_rag()
        from lightrag import QueryParam
        started = time.perf_counter()
        context = self._run(rag.query(question["question"], param=QueryParam(mode="hybrid", top_k=top_k, only_need_context=True)))
        evidence = self._article_ids_from_context(str(context))
        answer = self._run(rag.query(question["question"], param=QueryParam(mode="hybrid", top_k=top_k)))
        return {
            "question_id": question["question_id"],
            "system": self.name,
            "answer": str(answer),
            "retrieved_article_ids": evidence[:top_k] if evidence is not None else None,
            "retrieval_evidence": "article_headers_in_context" if evidence is not None else "not_available_from_installed_lightrag_version",
            "latency_ms": round((time.perf_counter() - started) * 1000, 2),
            "model": self.model,
            "usage": self.ledger.to_dict(),
            "mode": "hybrid",
        }
