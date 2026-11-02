# 🚀 HƯỚNG DẪN CHẠY THỰC NGHIỆM ĐA TẦNG PHỄU RAG TRÊN KAGGLE GPU (T4 / P100) — PHIÊN BẢN V2 HOÀN CHỈNH

Tài liệu này hướng dẫn chi tiết quy trình đưa gói thực nghiệm lên Kaggle GPU để đo kiểm 100% bằng số liệu phần cứng thực tế (không dùng ước tính hay offset), tích hợp đối sánh **Ma trận 6 Cấu hình ($3 \times 2$)**, đo kiểm LightRAG Approximate Retrieval và đánh giá Citation thực nghiệm bằng LLM-as-a-Judge (`gpt-4o-mini`).

---

## 🎯 CÁC CẢI TIẾN TRỌNG TÂM CỦA PHIÊN BẢN V2

1. **Khắc phục Hiện tượng "Context Orphanage" (Mồ côi Ngữ cảnh):**
   - Tự động bóc tách tên thực tế của Điều luật từ dòng đầu tiên của trường văn bản khi metadata generic (`Điều X`), loại bỏ chunk rác `_p0`.
   - Kế thừa cấu trúc phân cấp pháp lý `[Luật: ... | Điều X: <Tên Điều>]` vào **100% các Khoản và Điểm** vi mô.
2. **Cơ chế Gom điểm Bài báo (Article-level MaxP Aggregation):**
   - Đảm bảo Top-5 kết quả trả về đại diện cho 5 Điều luật độc lập, tránh hiện tượng nhiều Khoản cùng 1 Điều chiếm hết Top-5 (giải quyết triệt để sụt giảm Recall ảo do trùng lặp).
3. **Ma trận Thực nghiệm Đối xứng 6 Cấu hình ($3 \times 2$):**
   - **Nhóm 1 (Naive Chunks - Điều thô):**
     1. Naive BM25 Only
     2. Naive Dense Only (BGE-M3)
     3. Naive Hybrid RRF ($k=60$)
   - **Nhóm 2 (Parser Chunks - Khoản/Điểm vi mô + MaxP):**
     4. Parser BM25 Only (MaxP)
     5. Parser Dense Only (BGE-M3 + MaxP)
     6. Parser Hybrid RRF ($k=60$ + MaxP)
4. **Đo kiểm Citation Thực nghiệm bằng LLM-as-a-Judge:**
   - Thay thế nhãn danh nghĩa "Preserved" bằng đo lường thực tế trên 50 câu hỏi qua OpenRouter API (`gpt-4o-mini`).
5. **Đo kiểm LightRAG Approximate Retrieval:**
   - So sánh đa chiều trên Full 512 câu và Tập kiểm soát công bằng 205 câu (Fair Subset - 100% tài liệu liên quan có mặt trong VDB).

---

## 📁 1. DANH MỤC CÁC TẬP TIN TRONG GÓI (`kaggle_package/`)

| Tên File | Dung Lượng | Vai Trò & Chức Năng |
| :--- | :--- | :--- |
| **`kaggle_funnel_benchmark.ipynb`** | ~45 KB | **Jupyter Notebook chính** chia sẵn 11 khung code tuần tự, sẵn sàng chạy 1-click hoặc tương tác. |
| **`run_kaggle_ablation.py`** | ~35 KB | Script Python thực thi tự động hóa toàn diện 6 cấu hình, checkpoint và xuất báo cáo. |
| **`structure_aware_parser.py`** | ~8 KB | Module M1-M3 Regex Parser v2 bóc tách tiêu đề thực và kế thừa ngữ cảnh. |
| **`baseline_bm25_rewritten_results.csv`** | ~40 KB | Baseline Naive BM25 (512 câu) để hoàn thiện ma trận đối soát đối xứng. |
| **`final_benchmark_results_VECTOR.csv`** | 53 KB | Baseline Naive Vector (512 câu) để so sánh đối chiếu. |
| **`final_benchmark_results_HYBRID.csv`** | 54 KB | Baseline Naive Hybrid RRF (512 câu) để so sánh đối chiếu. |
| **`final_benchmark_results_LIGHTRAG_verified.csv`** | 54 KB | Dữ liệu đo kiểm LightRAG 512 câu đã xác minh (kèm 10 câu retry). |
| **`lightrag_vdb_matrix.npy`** | 2.12 MB | Ma trận embedding gốc gồm 519 vector (1024-d, normalized) từ LightRAG VDB. |
| **`lightrag_chunk_to_article_id.json`** | 38 KB | Bản đồ ánh xạ 519 chunks của LightRAG về 500 Article ID tương ứng. |
| **`lightrag_vdb_chunk_ids.json`** | 26 KB | Danh sách thứ tự chunk ID trong ma trận vector của LightRAG. |
| **`corpus_final.json`** | 3.35 MB | Toàn văn 2.087 điều luật đầy đủ của Benchmark A. |
| **`benchmark_rewritten.json`** | 202 KB | Tập 512 câu hỏi benchmark kèm nhãn ground-truth và phân loại category. |
| **`requirements.txt`** | < 1 KB | Danh sách thư viện Python cần thiết (`sentence-transformers`, `rank-bm25`, `pyvi`, `requests`, `scipy`). |

---

## 💻 2. QUY TRÌNH 3 BƯỚC CHẠY TRÊN KAGGLE GPU (T4 / P100)

### Bước 1: Tạo Kaggle Notebook mới
1. Đăng nhập vào [Kaggle](https://www.kaggle.com/) -> Nhấn **Create** -> **New Notebook**.
2. Tại thanh cấu hình bên phải (**Notebook options**):
   - **Accelerator:** Chọn **GPU T4 x2** (hoặc GPU P100).
   - **Internet:** Bật **Internet ON** (bắt buộc để tải model BGE-M3 từ HuggingFace và gọi OpenRouter API).

### Bước 2: Nạp mã nguồn & dữ liệu
Bạn có 2 cách cực kỳ đơn giản:
- **Cách A (Tải Notebook trực tiếp):** Nhấn **File** -> **Upload Notebook** -> Chọn file `kaggle_funnel_benchmark.ipynb`. Sau đó upload toàn bộ thư mục dữ liệu vào `/kaggle/working` hoặc tạo một Kaggle Dataset chứa các file `.json`, `.csv`, `.npy`.
- **Cách B (Upload file ZIP):** Tạo một Kaggle Dataset từ `kaggle_ablation_package.zip`, thêm dataset vào Notebook.

### Bước 3: Thực thi
- **Lựa chọn 1 (Khuyên dùng - 1 Chạm Toàn Diện):**
  Chạy lệnh trong cell đầu tiên:
  ```bash
  !python run_kaggle_ablation.py
  ```
  Quá trình chạy mất khoảng **2 - 4 phút** trên GPU T4. Toàn bộ 6 cấu hình, đo kiểm LightRAG và thẩm định LLM Judge sẽ tự động hoàn tất.

- **Lựa chọn 2 (Chạy tương tác từng cell):**
  Chạy lần lượt từ Khung 1 đến Khung 11 để quan sát trực quan output, kiểm tra cấu trúc chunks vi mô và xem độ trễ từng bước.

---

## 📦 3. KẾT QUẢ ĐẦU RA SẼ NHẬN ĐƯỢC (TỰ ĐỘNG ĐÓNG GÓI TRONG `kaggle_benchmark_results.zip`)

Sau khi chạy xong, trong thư mục `/kaggle/working/` sẽ xuất hiện các file:
1. `six_configurations_ablation_matrix.csv`: Bảng ma trận $3 \times 2$ đầy đủ số liệu Recall@5, MRR@5, Citation, Latency P95.
2. `tier1_fair_subset_205_matrix.csv`: Bảng đối soát trên tập kiểm soát công bằng 205 câu.
3. `results_ablation_bm25_parser.csv`: Chi tiết 512 câu của Cấu hình 4 (Parser BM25 + MaxP).
4. `results_ablation_vector_parser.csv`: Chi tiết 512 câu của Cấu hình 5 (Parser Dense + MaxP).
5. `results_ablation_hybrid_parser.csv`: Chi tiết 512 câu của Cấu hình 6 (Parser Hybrid RRF + MaxP).
6. `parser_citation_llm_judge_50.json`: Nhật ký đánh giá Citation thực nghiệm kèm phân bổ chi phí token.
7. `runtime_performance_and_cost_report.json` & `.md`: Báo cáo thời gian indexing, độ trễ phân vị và VRAM GPU.
8. `kaggle_benchmark_results.zip`: Gói nén toàn bộ các file trên để bạn tải về máy tính chỉ với 1 cú click!
