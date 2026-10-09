# HƯỚNG DẪN INDEXING DỮ LIỆU TỪ A ĐẾN Z (CHO NGƯỜI MỚI BẮT ĐẦU)

Tài liệu này hướng dẫn chi tiết cách hệ thống `Benchmark Harness` "tiêu hóa" (Index) tập dữ liệu pháp luật để chuẩn bị cho quá trình tìm kiếm (Retrieval).

## 1. Dữ liệu Đầu vào (Input Data) đã chuẩn bị sẵn
Tập dữ liệu của chúng ta đã được chuyển vào thư mục chuẩn của bộ Harness:
- **Corpus (Kho tri thức):** `benchmark_harness/data/corpus_final.json` (Hiện có 2.087 mục).
- **Benchmark (Bộ đề thi):** `benchmark_harness/data/benchmark_rewritten.json` (512 câu hỏi QA).

Quá trình **Indexing** bản chất là biến file text `corpus_final.json` thành các dạng cấu trúc dữ liệu tối ưu để máy tính có thể tìm kiếm cực nhanh.

---

## 2. Trạng thái triển khai và chạy BM25

Trong repository hiện tại, BM25 là baseline retrieval đã có thể chạy thật. Vector
và Hybrid wrapper trong Harness vẫn là khung tích hợp, chưa phải hệ thống benchmark
hoàn chỉnh; phần Graph/LightRAG cần API và cấu hình riêng.

Cài các dependency cho baseline từ thư mục gốc repository:

```powershell
python -m pip install -r benchmark_harness/requirements.txt
```

Tạo sparse index từ corpus (mặc định `benchmark_harness/data/corpus_final.json`):

```powershell
python benchmark_harness/run_retrieval_benchmark.py index
```

Index đã token hóa được lưu tại `benchmark_harness/.cache/bm25/index.json`.
Mỗi lần chạy tiếp, Harness xác minh hash corpus và tái sử dụng index; nếu corpus
thay đổi thì index được tạo lại. Để chủ động tạo lại:

```powershell
python benchmark_harness/run_retrieval_benchmark.py index --rebuild-index
```

Chạy retrieval benchmark trên toàn bộ benchmark (mặc định 512 câu), tính
Recall@5/MRR@5 và latency, xuất từng kết quả ra
`benchmark_harness/results/bm25_results.csv`:

```powershell
python benchmark_harness/run_retrieval_benchmark.py benchmark
```

Chạy nhanh một phần để kiểm tra:

```powershell
python benchmark_harness/run_retrieval_benchmark.py benchmark --limit 50
```

Chỉ số này đo **retrieval**, chưa gọi LLM để sinh câu trả lời hay chấm RAG
end-to-end. Nếu ground-truth article ID không có trong corpus, lệnh benchmark sẽ
dừng và báo lỗi thay vì tính điểm trên dữ liệu sai.

`baseline_bm25.py` vẫn là entry point tương thích. Có thể thay
`python benchmark_harness/run_retrieval_benchmark.py` bằng
`python baseline_bm25.py` trong cả hai lệnh `index` và `benchmark`; gọi file này
không kèm subcommand sẽ chạy benchmark như phiên bản baseline cũ.

## 3. Benchmark Vector và Hybrid trên Kaggle

Các lệnh sau benchmark **retrieval-only**: Vector dùng cosine similarity trên
embedding BGE-M3; Hybrid kết hợp BM25 (PyVi) và BGE-M3 bằng Reciprocal Rank
Fusion (RRF), mặc định lấy 50 ứng viên từ mỗi bộ truy xuất và `rrf_k=60`.
Không gọi LLM, không sinh câu trả lời, và không dùng cross-encoder reranker.

Trên Kaggle, bật Internet để tải model BGE-M3 và chọn GPU accelerator. Từ thư
mục gốc repository:

```bash
python -m pip install -r benchmark_harness/requirements-vector.txt
python benchmark_harness/run_retrieval_benchmark.py index --system hybrid --device cuda --batch-size 8
python benchmark_harness/run_retrieval_benchmark.py benchmark --system vector --device cuda --batch-size 8 --output /kaggle/working/vector_results.csv
python benchmark_harness/run_retrieval_benchmark.py benchmark --system hybrid --device cuda --batch-size 8 --candidate-k 50 --rrf-k 60 --output /kaggle/working/hybrid_results.csv
```

Index embedding dùng chung cho hai benchmark, được lưu tại
`benchmark_harness/.cache/dense_bge_m3/index.npz`. Chạy mỗi benchmark trên đủ 512
câu; dùng `--limit 5` để smoke-test. Mỗi CSV có file `.summary.json` đi kèm, ghi
rõ model, thiết bị, phương pháp fusion, latency và cấu hình không reranker.
Nếu notebook Kaggle được mở ở thư mục khác, chuyển vào thư mục repository trước
khi chạy hoặc truyền đường dẫn `--corpus`, `--benchmark`, `--index` và
`--dense-index` tường minh.

## 4. Quy trình Indexing dự kiến cho 3 Hệ thống

### Hệ thống 1: Sparse Indexing (Cho BM25 & Hybrid)
- **Bản chất:** Lập chỉ mục từ vựng (Giống như mục lục ở cuối cuốn sách).
- **Cách hoạt động:**
  1. Đọc từng Điều luật trong `corpus_final.json`.
  2. Dùng thư viện `pyvi` hoặc `underthesea` để "cắt từ" tiếng Việt (Tokenization). VD: "Luật Đất đai" -> `["Luật", "Đất đai"]`.
  3. Đếm tần suất xuất hiện của các từ (TF-IDF cải tiến) bằng thuật toán BM25.
- **Lưu trữ:** Tạo ra một object bộ nhớ (hoặc file `.pkl`) chứa tần suất từ vựng. Quá trình này rất nhẹ, mất khoảng 1-2 giây.

### Hệ thống 2: Hybrid RAG (Chuẩn ViDRILL - VLSP 2025)
- **Bản chất:** Kết hợp thế mạnh của Sparse (Từ khóa) và Dense (Ngữ nghĩa), sau đó dùng mô hình Reranker để lọc lại độ chính xác cao nhất.
- **Công cụ:** BM25 + Embedding `BAAI/bge-m3` + Reranker `BAAI/bge-reranker-v2-m3` (chạy trên GPU Kaggle).
- **Thiết kế nghiêm ngặt:** TUYỆT ĐỐI BỎ HyDE (Hypothetical Document Embeddings) và BỎ Query Rewriting để tránh Ảo giác pháp lý và giữ độ Reproducibility (khả năng tái lập kết quả) chuẩn học thuật.
- **Công cụ:** Mô hình Embedding `BAAI/bge-m3` (chạy trên GPU Kaggle).
- **Cách hoạt động:**
  1. Load mô hình `BAAI/bge-m3` lên VRAM GPU.
  2. Băm nhỏ văn bản (Chunking). Tuy nhiên, vì một điều luật tiếng Việt khá ngắn (thường < 512 tokens), ta có thể lấy luôn `article_text` làm 1 chunk.
  3. Bơm từng chunk vào mô hình để sinh ra các mảng số (ví dụ: mảng 1024 chiều).
  4. Lưu trữ tất cả các mảng số này vào một CSDL Vector (như `FAISS` hoặc `ChromaDB`).
- **Lưu trữ:** Sẽ sinh ra thư mục `benchmark_harness/vector_index/`. Quá trình này mất khoảng 2-5 phút trên GPU.

### Hệ thống 3: Graph Indexing (Cho LightRAG)
- **Bản chất:** Rút trích Thực thể (Entity) và Mối quan hệ (Relationship) để tạo Đồ thị Tri thức (Knowledge Graph).
- **Công cụ:** Gọi API `GPT-4o-mini`.
- **Cách hoạt động:**
  1. Chia `corpus_final.json` thành các block văn bản.
  2. Gửi từng block lên API GPT-4o-mini kèm theo Prompt yêu cầu: "Hãy trích xuất các chủ thể pháp luật (ví dụ: Người sử dụng đất, Cơ quan có thẩm quyền) và mối quan hệ giữa chúng (ví dụ: cấp giấy phép, xử phạt)".
  3. API trả về danh sách các Node (Thực thể) và Edge (Quan hệ).
  4. Ghi các Node và Edge vào một Graph Database (ví dụ: `NanoGraphRAG` hoặc `NetworkX`).
  5. Đồng thời, dùng Embedding `BAAI/bge-m3` để vector hóa các Node và Edge đó nhằm hỗ trợ tìm kiếm ngữ nghĩa trên đồ thị.
- **Lưu trữ:** Sẽ sinh ra thư mục `benchmark_harness/graph_index/`. Quá trình này tốn API và mất thời gian lâu nhất (khoảng 30 phút - 1 tiếng tùy Rate Limit).

---

## 5. Kiến trúc Harness và Đánh giá RAG End-to-End (Tầng 1 -> 4)
Thay vì chỉ đánh giá Retrieval thuần túy (chỉ lấy top-5 ID), hệ thống đã được chốt hạ **Đánh Giá RAG End-to-End**. Điều này có nghĩa là cả 3 hệ thống (Vector, Hybrid, LightRAG) đều BẮT BUỘC phải tích hợp 1 module LLM Generator (GPT-4o-mini) ở cuối phễu để sinh ra câu trả lời cuối cùng.

Kiến trúc code thực tế đã được xây dựng theo **Adapter Pattern**:
```text
benchmark_harness/
├── core/
│   ├── pydantic_schemas.py  # Ép kiểu dữ liệu nghiêm ngặt 8 trường (SystemResponse, EvaluationScore)
│   └── evaluator.py         # LLM Judge tự động chấm điểm Faithfulness, Context Precision...
├── systems/
│   ├── base_system.py       # Interface chuẩn
│   ├── hybrid_rag/wrapper.py# Nơi Team Dev nhúng code FAISS/BM25
│   ├── vector_rag/wrapper.py
│   └── light_rag/wrapper.py
└── run_harness.py           # Vòng lặp Orchestrator chạy trên Kaggle
```

Nhờ kiến trúc này, khi đưa lên Kaggle, Team Dev chỉ việc điền logic Model vào các file `wrapper.py`, sau đó chạy `python run_harness.py`. Quá trình chấm điểm, lưu checkpoint (mỗi 10 câu), và xuất báo cáo CSV sẽ diễn ra hoàn toàn tự động.
