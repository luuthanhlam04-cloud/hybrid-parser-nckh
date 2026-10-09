import os
import sys
import json
import time
from typing import Dict, Any

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from systems.base_system import BaseRAGSystem
from core.pydantic_schemas import BenchmarkQuestion, SystemResponse, RetrievalResult

class LightRAGWrapper(BaseRAGSystem):
    """
    Hệ thống LightRAG SẴN SÀNG CHẠY THẬT.
    """
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.model_loaded = False
        
        try:
            from lightrag import LightRAG, QueryParam
            from lightrag.utils import EmbeddingFunc
            from lightrag.llm import openrouter_model_if_cache, openrouter_embedding
            from sentence_transformers import SentenceTransformer
            
            # Load embedding model
            self.emb_model = SentenceTransformer('BAAI/bge-m3', device='cuda')
            
            async def embedding_func(texts: list[str]) -> list[list[float]]:
                return self.emb_model.encode(texts, normalize_embeddings=True).tolist()
                
            os.makedirs("./lightrag_workspace", exist_ok=True)
            self.rag = LightRAG(
                working_dir="./lightrag_workspace",
                embedding_func=EmbeddingFunc(
                    embedding_dim=1024,
                    max_token_size=8192,
                    func=embedding_func
                ),
                llm_model_func=openrouter_model_if_cache,
                llm_model_name="openai/gpt-4o-mini",
                llm_model_max_async=4
            )
            self.model_loaded = True
        except ImportError:
            print("[LightRAG] LỖI: Thiếu thư viện lightrag. Chạy giả lập.")
            
    def index_corpus(self, corpus_path: str, index_dir: str):
        if not self.model_loaded:
            return
            
        print(f"[LightRAG] Đang xây dựng đồ thị từ {corpus_path}...")
        try:
            with open(corpus_path, "r", encoding="utf-8") as f:
                corpus = json.load(f)
            texts = [doc['text'] for doc in corpus]
            self.rag.insert(texts)
            print("[LightRAG] Xây dựng đồ thị hoàn tất!")
        except Exception as e:
            print(f"[LightRAG] Lỗi khi insert: {e}")
            
    def retrieve_and_answer(self, query_data: BenchmarkQuestion, top_k: int = 5) -> SystemResponse:
        start_time = time.time()
        
        if not self.model_loaded:
            fake_results = [RetrievalResult(article_id="01/vbhn-vpqh#1", score=0.99, text="Fake Graph...")]
            return SystemResponse(question_id=query_data.question_id, retrieved_docs=fake_results[:top_k], generation="Mock Graph Answer", metadata={"latency_ms": 0})
            
        try:
            from lightrag import QueryParam
            import re
            
            # Query trực tiếp từ Graph
            answer = self.rag.query(query_data.question, param=QueryParam(mode="hybrid"))
            
            # LightRAG query() mặc định chỉ trả về String answer, không trả list chunks.
            # Cố gắng dùng Regex để bóc tách article_id (ví dụ '01/vbhn-vpqh#1') nếu LLM có trích dẫn.
            found_ids = re.findall(r'[0-9a-zA-Z_]+/[a-zA-Z0-9_-]+#[0-9]+', str(answer))
            found_ids = list(set(found_ids))
            
            retrieved_docs = []
            if found_ids:
                for aid in found_ids[:top_k]:
                    retrieved_docs.append(RetrievalResult(article_id=aid, score=1.0, text="Extracted from LightRAG answer"))
            else:
                print("LIGHTRAG_CANNOT_EXTRACT_CHUNKS")
                
            generation = str(answer)
        except Exception as e:
            retrieved_docs = []
            generation = f"ERROR: LightRAG Crash - {e}"
            
        latency = int((time.time() - start_time) * 1000)
        return SystemResponse(question_id=query_data.question_id, retrieved_docs=retrieved_docs, generation=generation, metadata={"latency_ms": latency})
