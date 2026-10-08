import os
import sys
import json
import numpy as np
from typing import Dict, Any

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from systems.base_system import BaseRAGSystem
from core.pydantic_schemas import BenchmarkQuestion, SystemResponse, RetrievalResult

class VectorRAGWrapper(BaseRAGSystem):
    """
    Adapter cho Vector RAG (Sẵn sàng chạy trên Kaggle GPU).
    Cần cài đặt: pip install sentence-transformers faiss-gpu
    """
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        print("[VectorRAG] Khởi tạo hệ thống (Loading BGE-M3 trên GPU)...")
        # Uncomment dòng dưới khi chạy trên Kaggle
        # from sentence_transformers import SentenceTransformer
        # self.model = SentenceTransformer('BAAI/bge-m3', device='cuda')
        self.index = None
        self.doc_mapping = {}
        
    def index_corpus(self, corpus_path: str, index_dir: str):
        print(f"[VectorRAG] Đang index tập dữ liệu {corpus_path}...")
        # LƯU Ý KHI LÊN KAGGLE: Uncomment block dưới
        """
        import faiss
        with open(corpus_path, "r", encoding="utf-8") as f:
            corpus = json.load(f)
            
        texts = [doc['text'] for doc in corpus]
        ids = [doc['article_id'] for doc in corpus]
        
        embeddings = self.model.encode(texts, batch_size=32, show_progress_bar=True, normalize_embeddings=True)
        
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(np.array(embeddings, dtype=np.float32))
        
        self.doc_mapping = {i: {"id": ids[i], "text": texts[i]} for i in range(len(corpus))}
        os.makedirs(index_dir, exist_ok=True)
        faiss.write_index(self.index, os.path.join(index_dir, "bge_m3.index"))
        with open(os.path.join(index_dir, "mapping.json"), "w") as f:
            json.dump(self.doc_mapping, f)
        """
        pass
        
    def retrieve_and_answer(self, query_data: BenchmarkQuestion, top_k: int = 5) -> SystemResponse:
        # LƯU Ý KHI LÊN KAGGLE: Đổi thành code search thật
        """
        q_emb = self.model.encode([query_data.question], normalize_embeddings=True)
        scores, indices = self.index.search(np.array(q_emb, dtype=np.float32), top_k)
        
        fake_results = []
        for i, idx in enumerate(indices[0]):
            doc_info = self.doc_mapping[int(idx)]
            fake_results.append(RetrievalResult(article_id=doc_info["id"], score=float(scores[0][i]), text=doc_info["text"]))
        """
        
        fake_results = [
            RetrievalResult(article_id="01/vbhn-vpqh#1", score=0.95, text="Trích đoạn mẫu..."),
        ]
        
        return SystemResponse(
            question_id=query_data.question_id,
            retrieved_docs=fake_results[:top_k],
            generation="Đây là câu trả lời sinh ra từ GPT-4o-mini (Vector RAG).",
            metadata={"latency_ms": 120}
        )
