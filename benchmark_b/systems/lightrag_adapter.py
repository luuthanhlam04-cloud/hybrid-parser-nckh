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
import hashlib
from pathlib import Path
from typing import Any

from benchmark_b.costs import CostLedger
from benchmark_b.events import EventLog
from .base import BenchmarkSystem


class LightRAGSystem(BenchmarkSystem):
    name = "lightrag"
    GRAPH_TOP_K = 5
    CHUNK_TOP_K = 5
    MAX_TOTAL_TOKENS = 10_000
    MAX_ENTITY_TOKENS = 2_000
    MAX_RELATION_TOKENS = 2_000

    def __init__(self, output_dir: str | Path, *, model: str | None = None) -> None:
        super().__init__(output_dir)
        self.workspace = self.output_dir / "workspace"
        self.model = model or os.getenv("BENCHMARK_B_LIGHTRAG_MODEL", "openai/gpt-4o-mini")
        self.ledger = CostLedger(self.model)
        self.rag: Any | None = None
        self._phase = "index"
        self.events = EventLog(self.output_dir / 'api_events.jsonl', self.name)
        self._loop = asyncio.new_event_loop()
        self._initialized = False

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
        api_key = os.getenv("OPENROUTER_LIGHTRAG_BENCHMARK_KEY") or os.getenv("OPENROUTER_API_KEY") or os.getenv("LLM_API_KEY")
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

        async def embedding_func(texts: list[str]):
            return encoder.encode(texts, normalize_embeddings=True, batch_size=8, show_progress_bar=False)

        async def completion_func(prompt: str, system_prompt: str | None = None, history_messages: list[dict[str, str]] | None = None, **kwargs: Any) -> str:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"], max_retries=0)
            messages: list[dict[str, str]] = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.extend(history_messages or [])
            messages.append({"role": "user", "content": prompt})
            response = None
            for attempt in range(1,4):
                started = time.perf_counter()
                try:
                    response = await client.chat.completions.create(model=self.model, messages=messages, temperature=0.0)
                except Exception as exc:
                    self.events.record(phase=self._phase,operation='graph_index_llm_unclassified' if self._phase=='index' else 'query',attempt_no=attempt,started=started,error=exc)
                    if attempt == 3: raise
                else:
                    self.events.record(response,phase=self._phase,operation='graph_index_llm_unclassified' if self._phase=='index' else 'query',attempt_no=attempt,started=started)
                    break
            await client.close()
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
            enable_llm_cache=False,
            enable_llm_cache_for_entity_extract=False,
            default_embedding_timeout=300,
        )
        return self.rag

    def _run(self, value: Any) -> Any:
        if asyncio.iscoroutine(value):
            return self._loop.run_until_complete(value)
        return value

    def _initialize(self):
        rag = self._build_rag()
        if not self._initialized:
            self._run(rag.initialize_storages())
            self._initialized = True
        return rag

    def close(self):
        if self.rag is not None and self._initialized:
            self._run(self.rag.finalize_storages())
        if not self._loop.is_closed():
            # The SDK keeps queue workers alive after storage finalization.
            # Drain their cancellation before closing this adapter's own loop.
            async def cancel_workers():
                pending = [task for task in asyncio.all_tasks() if task is not asyncio.current_task()]
                for task in pending:
                    task.cancel()
                if pending:
                    await asyncio.gather(*pending, return_exceptions=True)
            self._run(cancel_workers())
            self._loop.run_until_complete(self._loop.shutdown_asyncgens())
            self._loop.close()

    def index(self, corpus: list[dict[str, Any]], *, fresh: bool = False) -> dict[str, Any]:
        if self.workspace.exists() and any(self.workspace.iterdir()):
            raise RuntimeError('Workspace exists: choose a new --run-id; fresh runs never overwrite previous data.')
        started = time.perf_counter()
        rag = self._initialize()
        self._phase = "index"
        texts = [document["text"] for document in corpus]
        self._run(rag.ainsert(texts, ids=[d['article_id'] for d in corpus], file_paths=[d['article_id'] for d in corpus]))
        status_counts = self._run(rag.doc_status.get_status_counts())
        if status_counts.get('processed', 0) != len(corpus):
            raise RuntimeError(f'Incomplete LightRAG index: {status_counts}; expected {len(corpus)} processed documents.')
        metadata = {
            "system": self.name,
            "workspace": str(self.workspace),
            "fresh_index": fresh,
            "input_source": corpus[0].get("source_path") if corpus else None,
            "input_sha256": hashlib.sha256(Path(corpus[0]["source_path"]).read_bytes()).hexdigest() if corpus and corpus[0].get("source_path") else None,
            "corpus_document_count": len(corpus),
            "document_status_counts": status_counts,
            "corpus_document_ids": [document["article_id"] for document in corpus],
            "physical_graph_sha256": __import__('benchmark_b.prepare',fromlist=['sha']).sha('outputs/physical_graphs/physical_graph.json'),
            "clean_text_sha256": __import__('benchmark_b.prepare',fromlist=['sha']).sha('outputs/clean_texts/clean_Luat_dat_dai_chuong_3.txt'),
            "index_duration_ms": round((time.perf_counter() - started) * 1000, 2),
            "embedding": {"model": "BAAI/bge-m3", "dimensions": 1024, "execution": "local"},
            "chunking": {"token_size": 1200, "overlap_tokens": 100},
            "package_provenance": self._package_provenance(),
            "cost_ledger": self.ledger.to_dict(),
            "extraction_api_summary": self.events.summary(),
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
        rag = self._initialize()
        from lightrag import QueryParam
        started = time.perf_counter()
        if not hasattr(rag,'aquery_llm'):
            raise RuntimeError('Install a LightRAG SDK exposing aquery_llm for single-call source/answer capture.')
        if top_k != self.GRAPH_TOP_K:
            raise ValueError(f'Benchmark B fixes LightRAG top_k={self.GRAPH_TOP_K}; received {top_k}.')
        query_config = QueryParam(
            mode='hybrid',
            top_k=self.GRAPH_TOP_K,
            chunk_top_k=self.CHUNK_TOP_K,
            max_total_tokens=self.MAX_TOTAL_TOKENS,
            max_entity_tokens=self.MAX_ENTITY_TOKENS,
            max_relation_tokens=self.MAX_RELATION_TOKENS,
            enable_rerank=False,
            stream=False,
        )
        raw = self._run(rag.aquery_llm(question['question'], param=query_config))
        from benchmark_b.prepare import MAP
        from benchmark_b.alignment import align
        mapping=json.loads(MAP.read_text(encoding='utf-8'))
        chunks=(raw.get('data') or {}).get('chunks',[])
        aligned=[align(str(c.get('chunk_id') or c.get('id') or i),str(c.get('content') or c.get('text') or ''),i,mapping,article_scope=str(c['file_path']).split('#')[-1] if '#' in str(c.get('file_path','')) else None) for i,c in enumerate(chunks,1)]
        llm=raw.get('llm_response') or {}
        answer=llm.get('content') or llm.get('response') or ''
        if not answer: raise RuntimeError('LightRAG returned no non-streaming answer; raw API shape requires review.')
        evidence=list(dict.fromkeys('31/2024/qh15#'+loc.split(':')[1][1:] for e in aligned for loc in e['canonical_locators'])) if aligned else None
        return {
            "question_id": question["question_id"],
            "system": self.name,
            "evidence": aligned if chunks else None,
            "context_evidence": None,
            "reference_paths": None,
            "raw_retrieval": raw,
            "answer": str(answer),
            "retrieved_article_ids": evidence[:top_k] if evidence is not None else None,
            "retrieval_evidence": "article_headers_in_context" if evidence is not None else "not_available_from_installed_lightrag_version",
            "latency_ms": round((time.perf_counter() - started) * 1000, 2),
            "model": self.model,
            "usage": self.ledger.to_dict(),
            "mode": "hybrid",
            "retrieval_config": {
                "graph_top_k": self.GRAPH_TOP_K,
                "chunk_top_k": self.CHUNK_TOP_K,
                "max_total_tokens": self.MAX_TOTAL_TOKENS,
                "max_entity_tokens": self.MAX_ENTITY_TOKENS,
                "max_relation_tokens": self.MAX_RELATION_TOKENS,
                "rerank": False,
            },
        }
