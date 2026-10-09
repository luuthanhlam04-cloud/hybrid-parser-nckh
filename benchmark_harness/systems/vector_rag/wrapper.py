import os
import sys
import json
import time
import requests
import numpy as np
from typing import Dict, Any

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from systems.base_system import BaseRAGSystem
from core.pydantic_schemas import BenchmarkQuestion, SystemResponse, RetrievalResult

class VectorRAGWrapper(BaseRAGSystem):
    """
    Hệ thống Vector RAG SẴN SÀNG CHẠY THẬT trên Kaggle.
    Tự động catch lỗi nếu thiếu thư viện khi chạy local.
    """
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.index = None
        self.doc_mapping = {}
        self.model_loaded = False
        
        try:
            import torch
            from sentence_transformers import SentenceTransformer
            print("[VectorRAG] Loading Dense Model (BGE-M3)...")
            self.model = SentenceTransformer('BAAI/bge-m3', device='cuda' if torch.cuda.is_available() else 'cpu')
            self.model_loaded = True
        except ImportError:
            print("[VectorRAG] LỖI: Thiếu thư viện sentence_transformers. Hệ thống sẽ chạy ở chế độ giả lập (Mock).")
            
    def index_corpus(self, corpus_path: str, index_dir: str):
        if not self.model_loaded:
            print("[VectorRAG] Model chưa load, bỏ qua indexing.")
            return
            
        print(f"[VectorRAG] Đang index tập dữ liệu {corpus_path}...")
        try:
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
            print("[VectorRAG] Indexing hoàn tất!")
        except ImportError:
            print("[VectorRAG] LỖI: Thiếu thư viện faiss, bỏ qua indexing.")

    def _generate_answer(self, question: str, context: str) -> str:
        api_key = os.environ.get("OPENROUTER_API_KEY", "")
        if not api_key or api_key == "YOUR_OPENROUTER_API_KEY_HERE":
            return "ERROR: Missing API Key"
            
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        prompt = f"Trả lời câu hỏi sau dựa trên thông tin pháp luật được cung cấp.\n\nNgữ cảnh:\n{context}\n\nCâu hỏi: {question}"
        
        payload = {
            "model": "openai/gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0
        }
        try:
            print("Calling OpenRouter...")
            res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=30)
            res.raise_for_status()
            return res.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"ERROR: LLM Crash - {e}"

    def retrieve_and_answer(self, query_data: BenchmarkQuestion, top_k: int = 5) -> SystemResponse:
        start_time = time.time()
        
        if not self.model_loaded or not self.index:
            fake_results = [RetrievalResult(article_id="01/vbhn-vpqh#1", score=0.95, text="Fake context...")]
            return SystemResponse(question_id=query_data.question_id, retrieved_docs=fake_results[:top_k], generation="Mock answer due to missing libs", metadata={"latency_ms": 0})
            
        try:
            q_emb = self.model.encode([query_data.question], normalize_embeddings=True)
            scores, indices = self.index.search(np.array(q_emb, dtype=np.float32), top_k)
            
            results = []
            context_texts = []
            for i, idx in enumerate(indices[0]):
                doc_info = self.doc_mapping[int(idx)]
                results.append(RetrievalResult(article_id=doc_info["id"], score=float(scores[0][i]), text=doc_info["text"]))
                context_texts.append(doc_info["text"])
                
            context = "\n\n".join(context_texts)
            generation = self._generate_answer(query_data.question, context)
            
        except Exception as e:
            # Vẫn trả về danh sách trống và lý do lỗi để không làm sập tiến trình
            results = []
            generation = f"ERROR: Pipeline Crash - {e}"
            
        latency = int((time.time() - start_time) * 1000)
        return SystemResponse(question_id=query_data.question_id, retrieved_docs=results, generation=generation, metadata={"latency_ms": latency})
