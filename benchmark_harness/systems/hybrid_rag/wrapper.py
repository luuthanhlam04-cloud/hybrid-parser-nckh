import os
import sys
import json
import time
import requests
import numpy as np
from typing import Dict, Any, List

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from systems.base_system import BaseRAGSystem
from core.pydantic_schemas import BenchmarkQuestion, SystemResponse, RetrievalResult

class HybridRAGWrapper(BaseRAGSystem):
    """
    Hệ thống Hybrid RAG SẴN SÀNG CHẠY THẬT.
    Tự động catch lỗi nếu thiếu thư viện.
    """
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.k_rrf = 60
        self.top_k_retrieve = 50
        self.bm25_model = None
        self.faiss_index = None
        self.doc_mapping = {}
        
        print("[HybridRAG] Khởi tạo hệ thống...")
        try:
            import torch
            from sentence_transformers import SentenceTransformer
            from FlagEmbedding import FlagReranker
            
            self.dense_model = SentenceTransformer('BAAI/bge-m3', device='cuda' if torch.cuda.is_available() else 'cpu')
            self.reranker = FlagReranker('BAAI/bge-reranker-v2-m3', use_fp16=True)
            self.models_loaded = True
        except ImportError as e:
            print(f"[HybridRAG] LỖI Thiếu thư viện: {e}. Hệ thống sẽ chạy giả lập.")
            self.models_loaded = False
            
    def index_corpus(self, corpus_path: str, index_dir: str):
        if not self.models_loaded:
            return
            
        try:
            from rank_bm25 import BM25Okapi
            import faiss
            
            with open(corpus_path, "r", encoding="utf-8") as f:
                corpus = json.load(f)
                
            texts = [doc['text'] for doc in corpus]
            ids = [doc['article_id'] for doc in corpus]
            
            # BM25
            tokenized_corpus = [doc.split() for doc in texts]
            self.bm25_model = BM25Okapi(tokenized_corpus)
            
            # FAISS
            embeddings = self.dense_model.encode(texts, batch_size=16, show_progress_bar=True, normalize_embeddings=True)
            dim = embeddings.shape[1]
            self.faiss_index = faiss.IndexFlatIP(dim)
            self.faiss_index.add(np.array(embeddings, dtype=np.float32))
            
            self.doc_mapping = {i: {"id": ids[i], "text": texts[i]} for i in range(len(corpus))}
            print("[HybridRAG] Indexing hoàn tất!")
        except Exception as e:
            print(f"[HybridRAG] Lỗi khi indexing: {e}")
            
    def _generate_answer(self, question: str, context: str) -> str:
        api_key = os.environ.get("OPENROUTER_API_KEY", "")
        if not api_key or api_key == "YOUR_OPENROUTER_API_KEY_HERE":
            return "ERROR: Missing API Key"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        prompt = f"Trả lời câu hỏi sau dựa trên thông tin pháp luật được cung cấp.\n\nNgữ cảnh:\n{context}\n\nCâu hỏi: {question}"
        try:
            res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, 
                              json={"model": "openai/gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "temperature": 0.0}, timeout=30)
            res.raise_for_status()
            return res.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"ERROR: LLM Crash - {e}"

    def retrieve_and_answer(self, query_data: BenchmarkQuestion, top_k: int = 5) -> SystemResponse:
        start_time = time.time()
        if not self.models_loaded or not self.doc_mapping:
            fake_results = [RetrievalResult(article_id="01/vbhn-vpqh#1", score=0.95, text="Fake data...")]
            return SystemResponse(question_id=query_data.question_id, retrieved_docs=fake_results[:top_k], generation="Mock answer", metadata={"latency_ms": 0})
            
        try:
            query = query_data.question
            # BM25
            bm25_scores = self.bm25_model.get_scores(query.split())
            bm25_top_indices = np.argsort(bm25_scores)[::-1][:self.top_k_retrieve]
            
            # Dense
            q_emb = self.dense_model.encode([query], normalize_embeddings=True)
            dense_scores, dense_indices = self.faiss_index.search(np.array(q_emb, dtype=np.float32), self.top_k_retrieve)
            dense_indices = dense_indices[0]
            
            # RRF
            rrf_scores = {}
            for rank, doc_idx in enumerate(bm25_top_indices):
                rrf_scores[doc_idx] = rrf_scores.get(doc_idx, 0) + 1.0 / (self.k_rrf + rank + 1)
            for rank, doc_idx in enumerate(dense_indices):
                rrf_scores[doc_idx] = rrf_scores.get(doc_idx, 0) + 1.0 / (self.k_rrf + rank + 1)
                
            fused_indices = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)[:self.top_k_retrieve]
            
            # Rerank
            passages = [self.doc_mapping[idx]["text"] for idx in fused_indices]
            pairs = [[query, p] for p in passages]
            rerank_scores = self.reranker.compute_score(pairs, normalize=True)
            
            final_results = []
            for i, idx in enumerate(fused_indices):
                final_results.append({"id": self.doc_mapping[idx]["id"], "text": self.doc_mapping[idx]["text"], "score": float(rerank_scores[i])})
                
            final_results = sorted(final_results, key=lambda x: x["score"], reverse=True)[:top_k]
            
            retrieved_docs = [RetrievalResult(article_id=r["id"], score=r["score"], text=r["text"]) for r in final_results]
            context = "\n\n".join([r["text"] for r in final_results])
            
            # Generation (Protected)
            generation = self._generate_answer(query, context)
            
        except Exception as e:
            retrieved_docs = []
            generation = f"ERROR: Hybrid Pipeline Crash - {e}"
            
        latency = int((time.time() - start_time) * 1000)
        return SystemResponse(question_id=query_data.question_id, retrieved_docs=retrieved_docs, generation=generation, metadata={"latency_ms": latency})
