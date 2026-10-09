import os
import sys
import json
from typing import Dict, Any

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from systems.base_system import BaseRAGSystem
from core.pydantic_schemas import BenchmarkQuestion, SystemResponse, RetrievalResult

class LightRAGWrapper(BaseRAGSystem):
    """
    Adapter cho LightRAG (GraphRAG).
    Yêu cầu: pip install lightrag (hoặc setup theo nhánh repo này).
    """
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        print("[LightRAG] Khởi tạo hệ thống GraphRAG...")
        # LƯU Ý KHI LÊN KAGGLE: Khởi tạo LightRAG ở đây
        """
        from lightrag import LightRAG
        from lightrag.utils import EmbeddingFunc
        from sentence_transformers import SentenceTransformer
        
        # Load embedding model
        model = SentenceTransformer('BAAI/bge-m3', device='cuda')
        async def embedding_func(texts: list[str]) -> list[list[float]]:
            return model.encode(texts, normalize_embeddings=True).tolist()
            
        # Khởi tạo LightRAG instance
        self.rag = LightRAG(
            working_dir="./lightrag_workspace",
            embedding_func=EmbeddingFunc(
                embedding_dim=1024, # BGE-M3 dim
                max_token_size=8192,
                func=embedding_func
            ),
            # Cấu hình LLM calls (GPT-4o-mini hoặc Qwen)
        )
        """
        pass
        
    def index_corpus(self, corpus_path: str, index_dir: str):
        print(f"[LightRAG] Bắt đầu xây dựng đồ thị tri thức (Graph Index) từ {corpus_path}...")
        # LƯU Ý KHI LÊN KAGGLE: Uncomment block dưới
        """
        with open(corpus_path, "r", encoding="utf-8") as f:
            corpus = json.load(f)
            
        texts = [doc['text'] for doc in corpus]
        
        # Gọi hàm insert để xây Graph
        self.rag.insert(texts)
        print("[LightRAG] Xây dựng đồ thị hoàn tất!")
        """
        pass
        
    def retrieve_and_answer(self, query_data: BenchmarkQuestion, top_k: int = 5) -> SystemResponse:
        # LƯU Ý KHI LÊN KAGGLE: Đổi thành code search thật
        """
        # Search mode: hybrid (local + global graph search)
        answer = self.rag.query(query_data.question, param={"mode": "hybrid"})
        
        # Mapping lại context (Giả sử LighRAG trả về chunks)
        # fake_results = [...] 
        """
        
        fake_results = [
            RetrievalResult(article_id="01/vbhn-vpqh#1", score=0.99, text="Trích đoạn mẫu từ Graph..."),
        ]
        
        return SystemResponse(
            question_id=query_data.question_id,
            retrieved_docs=fake_results[:top_k],
            generation="Đây là câu trả lời sinh ra từ LightRAG qua quá trình duyệt Đồ thị.",
            metadata={"latency_ms": 1500, "steps": "graph_traversal"}
        )
