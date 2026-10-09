import os
import sys
import json
import time
import asyncio
from typing import Dict, Any

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from systems.base_system import BaseRAGSystem
from core.pydantic_schemas import BenchmarkQuestion, SystemResponse

from lightrag import LightRAG, QueryParam
from lightrag.utils import EmbeddingFunc
from lightrag.llm.openai import openai_complete_if_cache
from sentence_transformers import SentenceTransformer

class LightRAGWrapper(BaseRAGSystem):
    """
    Hệ thống LightRAG SẴN SÀNG CHẠY THẬT.
    Tương thích với lightrag-hku.
    """
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        
        print("[LightRAG] Loading Dense Model (BGE-M3)...")
        self.emb_model = SentenceTransformer('BAAI/bge-m3', device='cuda')
        
        async def embedding_func(texts: list[str]) -> list[list[float]]:
            return self.emb_model.encode(texts, normalize_embeddings=True).tolist()
            
        async def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs) -> str:
            return await openai_complete_if_cache(
                "openai/gpt-4o-mini",
                prompt,
                system_prompt=system_prompt,
                history_messages=history_messages,
                api_key=os.environ.get("OPENROUTER_API_KEY", ""),
                base_url="https://openrouter.ai/api/v1",
                **kwargs
            )
            
        os.makedirs("./lightrag_workspace", exist_ok=True)
        self.rag = LightRAG(
            working_dir="./lightrag_workspace",
            embedding_func=EmbeddingFunc(
                embedding_dim=1024,
                max_token_size=8192,
                func=embedding_func
            ),
            llm_model_func=llm_model_func
        )
        
    def index_corpus(self, corpus_path: str, index_dir: str):
        print(f"[LightRAG] Đang xây dựng đồ thị từ {corpus_path}...")
        with open(corpus_path, "r", encoding="utf-8") as f:
            corpus = json.load(f)
        texts = [doc['text'] for doc in corpus]
        
        import asyncio
        asyncio.run(self.rag.initialize_storages())
        
        self.rag.insert(texts)
        print("[LightRAG] Xây dựng đồ thị hoàn tất!")
        
    def retrieve_and_answer(self, query_data: BenchmarkQuestion, top_k: int = 5) -> SystemResponse:
        start_time = time.time()
        
        # Query trực tiếp từ Graph
        answer = self.rag.query(query_data.question, param=QueryParam(mode="hybrid"))
        
        # LightRAG không giữ lại chunk ID ban đầu
        print("LIGHTRAG_CANNOT_EXTRACT_CHUNKS")
        retrieved_docs = []
        generation = str(answer)
            
        latency = int((time.time() - start_time) * 1000)
        return SystemResponse(question_id=query_data.question_id, retrieved_docs=retrieved_docs, generation=generation, metadata={"latency_ms": latency})
