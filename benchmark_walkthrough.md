# Hướng Dẫn Kỹ Thuật (Walkthrough) - Benchmark Harness 
*(Cập nhật theo kiến trúc End-to-End RAG mới nhất - 512 câu hỏi)*

Hệ thống Benchmark đã được khởi tạo toàn vẹn kiến trúc (Skeleton & Logic Flow) theo **Adapter Pattern**. Đây là hướng dẫn để Team Dev hiểu cách "cắm" (plug-in) các hệ thống RAG vào và cách luồng dữ liệu di chuyển.

## 1. Khung Kiến Trúc (Architecture Diagram)

```text
[Dataset 512 câu] --> run_harness.py (Orchestrator)
                            |
           +----------------+----------------+
           |                |                |
      [Vector RAG]     [Hybrid RAG]     [LightRAG]
       Wrapper          Wrapper          Wrapper
           |                |                |
           +----------------+----------------+
                            |
                   SystemResponse DTO 
          (Chứa Top-K Retrieved Docs & LLM Generation)
                            |
                   LLM Judge (evaluator.py)
                            |
       +--------------------+--------------------+
       |                    |                    |
  Retrieval (T1)      Semantic (T2)       Legal (T3)
   (MRR, Recall)     (Precision, Faith)  (Citation)
                            |
              [Per-10-Question Checkpoint]
                checkpoint_results.csv
```

**Chiến lược Dữ liệu (Full 512 Questions):**
- Toàn bộ 512 câu hỏi đều được đưa vào đánh giá End-to-End (Cả Khả năng truy xuất lẫn Khả năng sinh câu trả lời).
- Sử dụng mô hình `gemini-3.5-flash-lite` (hoặc `gpt-4o-mini`) làm LLM-as-a-Judge tự động chấm điểm chống ảo giác và độ chính xác của ngữ cảnh.

## 2. Cách "Cắm" 1 Hệ thống Baseline Vào Harness

Team Dev **KHÔNG CẦN** sửa bất cứ file nào trong thư mục `core/` hay `run_harness.py`. Bạn chỉ cần vào thư mục hệ thống của mình (ví dụ: `systems/hybrid_rag/`) và điền logic vào file `wrapper.py` đã được tạo sẵn.

Class này bắt buộc phải kế thừa `BaseRAGSystem` và nhả ra `SystemResponse`.

```python
from typing import Dict, Any
import os
import sys

# Import chuẩn từ core
from systems.base_system import BaseRAGSystem
from core.pydantic_schemas import BenchmarkQuestion, SystemResponse, RetrievalResult

class HybridRAGWrapper(BaseRAGSystem):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        # TODO: Load BGE-M3, BM25, FAISS tại đây...
        
    def index_corpus(self, corpus_path: str, index_dir: str):
        # TODO: Code băm vector và lưu file index tại đây...
        pass
        
    def retrieve_and_answer(self, query_data: BenchmarkQuestion, top_k: int = 5) -> SystemResponse:
        """
        Nhận vào object câu hỏi, BẮT BUỘC trả ra SystemResponse
        """
        # 1. Chạy Retrieval (BM25 + Dense + Reranker)
        # 2. Gọi LLM sinh câu trả lời (Generation)
        
        results = [
            RetrievalResult(article_id="01/vbhn-vpqh#1", score=0.95, text="Toàn văn điều 1..."),
        ]
        
        return SystemResponse(
            question_id=query_data.question_id,
            retrieved_docs=results[:top_k],
            generation="Đây là câu trả lời sinh ra bởi RAG.",
            metadata={"latency_ms": 250, "steps": "bm25+dense->rrf->rerank"}
        )
```

## 3. Cấu hình Hybrid RAG (Chuẩn ViDRILL - VLSP 2025)
Team phụ trách nhánh `Hybrid_RAG` cần lưu ý tuân thủ đúng cấu hình đã chốt:
- **BM25** (Sparse) + **BGE-M3** (Dense).
- Gộp điểm bằng **RRF** (Reciprocal Rank Fusion).
- Lọc lại bằng **BGE Reranker v2-m3** (Cross-Encoder).
- **TẮT** HyDE và **TẮT** Query Rewriting để đảm bảo tính tái lập (Reproducibility) và tránh Ảo giác pháp lý.

## 4. Cách Chạy Trên Kaggle GPU

1. Đưa toàn bộ thư mục `benchmark_harness/` lên Kaggle.
2. Cài đặt các thư viện lõi của team bạn (VD: `pip install sentence-transformers faiss-gpu`).
3. Khởi chạy Orchestrator:
```bash
python run_harness.py
```

Hệ thống sẽ tự động in ra màn hình tiến trình chạy từng câu, chấm điểm và tự động tổng hợp **Báo Cáo 5 Dòng** cuối cùng:
```text
BÁO CÁO NHANH (QUICK REPORT)
- Tổng số câu đã chạy: 512
- Recall@5 trung bình: 0.85
- MRR@5 trung bình: 0.72
- Thời gian chạy thực tế: ... giây
- Trạng thái: PASS
```
