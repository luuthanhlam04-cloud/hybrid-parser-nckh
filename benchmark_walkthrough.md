# Hướng Dẫn Kỹ Thuật (Walkthrough) - Benchmark Harness V6

Hệ thống Benchmark đã được khởi tạo toàn vẹn kiến trúc (Skeleton & Logic Flow). Đây là hướng dẫn để bạn hiểu cách cắm (plug-in) các hệ thống RAG vào và cách luồng dữ liệu di chuyển.

## 1. Khung Kiến Trúc (Architecture Diagram)

```text
[Dataset 200 câu] --> DatasetLoader (Filter Tiers)
                            |
                            v
[LLM Call] -------> CostTracker.check() --> [Raise nếu vượt Hard Limit]
                            |
                      Evaluator (Loop)
                            |
     +----------------------+----------------------+
     |                      |                      |
[Vector RAG]         [Hybrid RAG]            [LightRAG]
 (Tay súng 1)         (Tay súng 2)           (Tay súng 3)
     |                      |                      |
     +----------------------+----------------------+
                            |
                  RetrievalResult DTO
                            |
    +----------+----------+----------+----------+----------+
    |          |          |          |          |          |
  Tier 1    Tier 2    Tier 2.5    Tier 3    Tier 4
   (MRR)   (RAGAS)  (Correct)  (Citation)  (LSV)
    |          |          |          |          |
    +----------+----------+----------+----------+----------+
                            |
             [Per-Question Atomic Checkpoint]
             results/raw/{system}/{question_id}.json
```

**Chiến lược Dữ liệu (Stratified Reporting):**
- T1 (Context Inclusion, MRR): N = 165
- T2 (Context Precision): N = 165
- T2 (Faithfulness): N = 200
- T2.5 (Answer Correctness): N = 165
- T3 (Citation Accuracy): N = 200
- T4 (LSV Score): N = 200

## 2. Luồng Thực Thi Của Evaluator

Evaluator xử lý stratified reporting thông qua 4 bước:

1. **Load Data:** Tự động xin Loader 165 câu cho các Metric yêu cầu Gold Data và 200 câu cho các Metric Gold-free.
2. **Execute RAG:** Lấy Random Seed (`config.set_global_seed()`) để đảm bảo Deterministic. Gọi hàm `.retrieve()` và `.generate_answer()`.
3. **Thực thi các Tầng Đánh Giá (Metrics):**
   - **Tier 1 (Retrieval):** Tính MRR và Context Inclusion. Chạy trên 165 câu.
   - **Tier 2 (RAGAS):** Tính Faithfulness (chạy trên 200 câu) và Context Precision (chạy trên 165 câu).
   - **Tier 2.5 (Correctness):** LLM Judge chấm độ chính xác (chạy trên 165 câu).
   - **Tier 3 (Citation):** Đánh giá cấu trúc trích dẫn pháp lý (chạy trên 200 câu).
   - **Tier 4 (LSV):** Gọi LSV Extractor để lấy cấu trúc S-A-O-C và check với Ontology (trên 200 câu).
   *Lưu ý (Blinding Mechanism & Cost Tracker):* Trước khi gọi LLM (T2, T2.5, T4), Evaluator bắt buộc phải gọi `CostTracker.check_limit()` để tránh cháy ví. Khi truyền prompt, Evaluator chỉ đưa `{question}`, `{gold_answer}`, `{system_answer}` — TUYỆT ĐỐI KHÔNG truyền `system_name`.
4. **Per-Question Atomic Checkpoint (Option B):** Lưu lập tức kết quả của câu hỏi này thành 1 file JSON độc lập `results/raw/{system_name}/{question_id}.json` bằng cơ chế `os.replace()`. Folder này đóng vai trò checkpoint. Resume bằng cách scan folder, skip các câu đã có. CSV aggregated chỉ xuất sau khi toàn bộ chạy xong.

## 3. Cách "Cắm" 1 Hệ thống Baseline Vào Harness

Bạn chỉ cần tạo một class kế thừa từ `BaseRAGSystem` trong file `systems/vector_rag.py`. 

```python
from core.base_system import BaseRAGSystem, RetrievalResult, Chunk
import core.config as config

class MyVectorRAG(BaseRAGSystem):
    def index(self, corpus_path: str):
        config.set_global_seed() # Bắt buộc
        pass
        
    def retrieve(self, query_id: str, query: str) -> RetrievalResult:
        return RetrievalResult(
            query_id=query_id,
            chunks=[Chunk(text="Nội dung...", article_id="Điều 45")],
            latency_ms=120.5 # Báo cáo p50/p95 latency về sau
        )
        
    def generate_answer(self, query: str, retrieval: RetrievalResult) -> str:
        return "Theo Điều 45, ..."
```

## 4. Cách Chạy (Run Command)

```python
from core.evaluator import BenchmarkEvaluator
from systems.vector_rag import MyVectorRAG

# Khởi tạo Evaluator
harness = BenchmarkEvaluator(
    dataset_path="benchmark_dataset_final.json",
    results_dir="benchmark_harness/results/raw",
    ontology_path="benchmark_harness/schemas/ontology_m7.json"
)

# Chạy
system = MyVectorRAG()
harness.run_evaluation(system, "Vector_RAG_Baseline")
```

## 5. Báo Cáo Phân Tích (Aggregate.py)

Sau khi toàn bộ chạy xong, bạn chạy script độc lập:

```bash
python benchmark_harness/aggregate.py
```

Script này thực thi 2 nhiệm vụ học thuật cốt lõi:
1. **Listwise Deletion:** Gom tất cả file JSON lại, tìm các câu hỏi báo lỗi ("error" != null) và xóa câu hỏi đó khỏi Bảng điểm của CẢ 3 hệ thống. Điều này đảm bảo N_effective công bằng tuyệt đối.
2. **Percentile Latency:** Tính toán Descriptive Stats như `p50` và `p95` trên tập câu hỏi hợp lệ (bỏ qua những câu lỗi timeout) và xuất toàn bộ ra CSV cho bài báo khoa học.
