# 🚀 HƯỚNG DẪN CHẠY THỰC NGHIỆM ĐA TẦNG PHỄU RAG TRÊN KAGGLE GPU (T4 / P100) — PHIÊN BẢN V2 HOÀN CHỈNH

Tài liệu này hướng dẫn chi tiết quy trình đưa gói thực nghiệm lên Kaggle GPU để đo kiểm 100% bằng số liệu phần cứng thực tế (không dùng ước tính hay offset), tích hợp đối sánh **Ma trận 6 Cấu hình ($3 \times 2$)**, **Khảo sát quét tỷ lệ dung hợp (Weighted RRF Sweep)**, đo kiểm LightRAG Approximate Retrieval và đánh giá Citation thực nghiệm toàn diện bằng **LLM-as-a-Judge đa luồng** (`gpt-4o-mini`).

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
4. **Khảo sát Quét Tỷ Lệ Dung Hợp (Hybrid Fusion Ratio Sweep):**
   - Quét 11 tỷ lệ $\alpha \in [0.0, 1.0]$ với bước nhảy $0.1$ trên toàn bộ 512 câu hỏi.
   - Chứng minh thực nghiệm hiện tượng Negative Fusion khi dung hợp cào bằng 1:1, giải thích cơ sở toán học vì sao hệ số ưu tiên Dense (0.8 hoặc 1.0) là tối ưu toàn cục.
5. **Đánh giá Citation Toàn Diện bằng LLM-as-a-Judge Đa Luồng:**
   - Hỗ trợ đánh giá Full 512 câu (hoặc mẫu 50 câu) qua OpenRouter API `gpt-4o-mini`.
   - Cơ chế đa luồng (`ThreadPoolExecutor`, 8 workers) rút ngắn thời gian chạy từ 20 phút xuống còn ~2-3 phút.
   - Cơ chế an toàn: Tự động retry khi gặp lỗi 429 và lưu Checkpoint định kỳ mỗi 25 câu ra đĩa chống mất mát dữ liệu khi timeout/đứt mạng.
6. **Đo kiểm LightRAG Approximate Retrieval:**
   - So sánh đa chiều trên Full 512 câu và Tập kiểm soát công bằng 205 câu (Fair Subset - 100% tài liệu liên quan có mặt trong VDB).

---

## 📁 1. DANH MỤC CÁC TẬP TIN TRONG GÓI (`kaggle_ablation_package.zip`)

| Tên File | Dung Lượng | Vai Trò & Chức Năng |
| :--- | :--- | :--- |
| **`kaggle_funnel_benchmark.ipynb`** | ~55 KB | **Jupyter Notebook chính** chia sẵn các khung code tuần tự, sẵn sàng chạy 1-chạm hoặc tương tác. |
| **`run_kaggle_ablation.py`** | ~52 KB | Script Python thực thi tự động hóa toàn diện 6 cấu hình, alpha sweep, LLM judge đa luồng, checkpoint và xuất báo cáo. |
| **`structure_aware_parser.py`** | ~8 KB | Module M1-M3 Regex Parser v2 bóc tách tiêu đề thực và kế thừa ngữ cảnh. |
| **`baseline_bm25_rewritten_results.csv`** | ~125 KB | Baseline Naive BM25 (512 câu) để hoàn thiện ma trận đối soát đối xứng. |
| **`final_benchmark_results_VECTOR.csv`** | 53 KB | Baseline Naive Vector (512 câu) để so sánh đối chiếu. |
| **`final_benchmark_results_HYBRID.csv`** | 54 KB | Baseline Naive Hybrid RRF (512 câu) để so sánh đối chiếu. |
| **`final_benchmark_results_LIGHTRAG_verified.csv`** | 50 KB | Dữ liệu đo kiểm LightRAG 512 câu đã xác minh (kèm 10 câu retry). |
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
- Tạo một Kaggle Dataset mới hoặc tải trực tiếp file `kaggle_ablation_package.zip` lên thư mục `/kaggle/working`.

### Bước 3: Thực thi
- **Lựa chọn 1 (Khuyên dùng - 1 Chạm Toàn Diện):**
  Chạy lệnh trong cell notebook (truyền API key OpenRouter để chạy LLM Judge Full 512 câu):
  ```bash
  # Điền API Key OpenRouter của bạn
  API_KEY="sk-or-v1-..."
  
  # Chạy script tự động hóa toàn diện
  !python run_kaggle_ablation.py --api_key "$API_KEY" --judge_sample_size 512 --judge_workers 8
  ```
  *(Nếu không có API Key hoặc muốn chạy nhanh phần retrieval trên GPU mà bỏ qua LLM Judge, chỉ cần chạy: `!python run_kaggle_ablation.py --skip_llm_judge`)*

- **Lựa chọn 2 (Chạy tương tác từng cell):**
  Chạy lần lượt từ Khung 1 đến Khung 11 của notebook `kaggle_funnel_benchmark.ipynb` để quan sát trực quan output, kiểm tra cấu trúc chunks vi mô và xem kết quả từng bước.

---

## 📦 3. KẾT QUẢ ĐẦU RA SẼ NHẬN ĐƯỢC (TỰ ĐỘNG ĐÓNG GÓI TRONG `kaggle_benchmark_results.zip`)

Sau khi chạy xong, trong thư mục `/kaggle/working/` sẽ tự động đóng gói toàn bộ artifacts vào `kaggle_benchmark_results.zip`:
1. `six_configurations_ablation_matrix.csv`: Bảng ma trận $3 \times 2$ đầy đủ số liệu Recall@5, MRR@5, Citation, Latency P95.
2. `tier1_fair_subset_205_matrix.csv`: Bảng đối soát trên tập kiểm soát công bằng 205 câu.
3. `hybrid_fusion_ratio_sweep.csv`: Bảng dữ liệu quét 11 tỷ lệ dung hợp $\alpha \in [0.0, 1.0]$.
4. `results_ablation_bm25_parser.csv`: Chi tiết 512 câu của Cấu hình 4 (Parser BM25 + MaxP).
5. `results_ablation_vector_parser.csv`: Chi tiết 512 câu của Cấu hình 5 (Parser Dense + MaxP).
6. `results_ablation_hybrid_parser.csv`: Chi tiết 512 câu của Cấu hình 6 (Parser Hybrid RRF + MaxP).
7. `results_lightrag_approx_retrieval.csv`: Chi tiết 512 câu của LightRAG Approximate.
8. `parser_citation_llm_judge_512.json`: Toàn bộ 512 generation IDs, điểm citation, context precision, faithfulness và chi phí token.
9. `parser_citation_llm_judge_50.json`: Lát cắt 50 câu tương thích ngược.
10. `full_llm_judge_audit_trail.json`: Nhật ký kiểm toán thẩm định LLM đầy đủ cho cả Parser Dense và Parser Hybrid.
11. `runtime_performance_and_cost_report.json` & `.md`: Báo cáo thời gian indexing, độ trễ phân vị và VRAM GPU.
12. `kaggle_benchmark_results.zip`: Gói nén toàn bộ các file trên để bạn tải về máy tính chỉ với 1 cú click từ tab Output của Kaggle!
