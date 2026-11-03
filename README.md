# 🏛️ HỆ THỐNG THỰC NGHIỆM RAG FUNNEL BENCHMARK (NCKH)
**Hướng dẫn Điều hướng & Cấu trúc Thư mục Thực nghiệm**  
*Phiên bản:* v2.0 Hoàn thiện  
*Mục đích:* Tài liệu chuẩn hóa dành cho thành viên nhóm nghiên cứu đọc hiểu cấu trúc dữ liệu, vận hành benchmark trên Kaggle, và khai thác số liệu viết Luận văn Tốt nghiệp.

---

## 🧭 1. SƠ ĐỒ CẤU TRÚC THƯ MỤC TỔNG QUAN

```
Benchmark/
├── 📁 01_raw_data/              # [DỮ LIỆU GỐC] Toàn văn 2.087 điều luật & 512 câu hỏi benchmark chuẩn
│   ├── corpus_final.json              # Ngữ liệu 2.087 điều luật đầy đủ (3.35 MB)
│   ├── benchmark_rewritten.json       # Tập 512 câu hỏi benchmark kèm nhãn ground-truth
│   ├── benchmark_dataset_final.json   # Dataset benchmark mở rộng
│   └── vmteb_corpus.parquet           # Ngữ liệu gốc VMTEB Parquet (34.7 MB)
│
├── 📁 02_baselines/             # [ĐỐI CHUẨN] Kết quả đo kiểm của các mô hình cơ sở
│   ├── final_benchmark_results_VECTOR.csv         # Baseline Naive Vector (Recall 0.9141)
│   ├── final_benchmark_results_HYBRID.csv         # Baseline Naive Hybrid (Recall 0.9316)
│   ├── baseline_bm25_rewritten_results.csv        # Baseline Naive BM25 (Recall 0.7051)
│   ├── final_benchmark_results_LIGHTRAG_verified.csv # Kết quả LightRAG 512 câu đã xác minh
│   └── backup_lightrag_512.csv                    # Bản sao lưu LightRAG
│
├── 📁 03_lightrag_artifacts/    # [TÀI NGUYÊN LIGHTRAG] Vector DB & bản đồ ánh xạ trích xuất từ LightRAG
│   ├── lightrag_workspace_500.zip     # Workspace gốc của LightRAG (36.6 MB)
│   ├── lightrag_vdb_matrix.npy        # Ma trận 519 vector (1024-d, normalized)
│   ├── lightrag_chunk_to_article_id.json # Ánh xạ chunk ID sang Article ID
│   ├── lightrag_vdb_chunk_ids.json    # Danh sách ID chunks trong VDB
│   └── lightrag_retry_cost_log.json   # Nhật ký chi phí retry 10 câu API
│
├── 📁 04_archive_v1_failure/    # [HỒ SƠ THẤT BẠI V1] Dữ liệu phục vụ Failure Mode Analysis trong luận văn
│   ├── FAILURE_MODE_ANALYSIS_V1.md    # Phân tích nguyên nhân sụt giảm Recall & Context Orphanage
│   ├── results_ablation_vector_parser.csv  # Kết quả Vector Parser V1 (Recall 0.8906)
│   ├── results_ablation_hybrid_parser.csv  # Kết quả Hybrid Parser V1 (Recall 0.8652)
│   ├── tier1_fair_subset_205_matrix.csv    # Ma trận đối soát tập 205 câu V1
│   ├── runtime_performance_and_cost_report.json # Báo cáo độ trễ V1 (P95 61.88ms)
│   └── kaggle_benchmark_results.zip        # Gói kết quả tải về nguyên bản từ Kaggle đợt 1
│
├── 📁 05_kaggle_execution/      # 🚀 [GÓI THỰC THI CHÍNH V2] Gói chạy 1-Click trên Kaggle GPU T4/P100
│   ├── kaggle_ablation_package.zip    # ⭐ FILE NÉN 2.49 MB UPLOAD TRỰC TIẾP LÊN KAGGLE
│   ├── kaggle_funnel_benchmark.ipynb  # Jupyter Notebook chuẩn bị sẵn 25 ô lệnh
│   ├── run_kaggle_ablation.py         # Script tự động hóa toàn bộ 6 cấu hình v2
│   ├── structure_aware_parser.py      # Module Parser v2 (Kế thừa tiêu đề, loại bỏ orphan)
│   ├── README_KAGGLE.md               # Hướng dẫn chi tiết 3 bước chạy trên Kaggle
│   └── requirements.txt               # Danh sách thư viện Python cần thiết
│
├── 📁 06_tools_and_audits/      # [CÔNG CỤ KIỂM TOÁN] Các script kiểm tra rò rỉ & tính toán thống kê
│   ├── leakage_check.py               # Kiểm tra rò rỉ dữ liệu giữa tập câu hỏi và corpus
│   ├── strict_audit.py                # Kiểm toán tính toàn vẹn của benchmark
│   ├── verify_benchmark.py            # Xác minh nhãn ground-truth
│   ├── run_ttest.py                   # Tính kiểm định Paired t-test và Wilcoxon
│   └── calc_exact_metrics.py          # Tính Recall@5, MRR@5 theo định nghĩa toán học
│
├── 📁 07_benchmark_b_pending/   # ⏳ [BENCHMARK 2] Dữ liệu đợt 2 (Đang xếp hàng chờ chạy)
│   ├── funnel_evaluation/             # Khung đánh giá đa tầng cũ & Tier 3 Benchmark B
│   └── README_BENCHMARK_B.md          # Ghi chú hướng dẫn mở rộng cho đợt 2
│
├── 📁 08_empirical_results/     # 🏆 [KẾT QUẢ THỰC NGHIỆM ĐỘC LẬP TỪ KAGGLE T4]
│   ├── six_configurations_ablation_matrix.csv  # Ma trận 6 cấu hình hoàn chỉnh (512 queries)
│   ├── tier1_fair_subset_205_matrix.csv        # Đối chuẩn công bằng với LightRAG (205 queries)
│   ├── results_ablation_vector_parser.csv      # Kết quả Cấu hình đề xuất (Recall 0.9316, Citation 0.9070)
│   ├── results_ablation_hybrid_parser.csv      # Kết quả Hybrid RRF Parser (Recall 0.8770, Citation 0.8391)
│   ├── results_ablation_bm25_parser.csv        # Kết quả BM25 Parser (Recall 0.7402, Citation 0.6973)
│   ├── results_lightrag_approx_retrieval.csv   # Kết quả đo kiểm LightRAG trên 512 câu
│   ├── parser_citation_llm_judge_50.json       # Kết quả xác minh LLM Judge (Mean Citation: 0.9000, Chi phí: $0.006210 USD)
│   └── runtime_performance_and_cost_report.json # Báo cáo độ trễ GPU P95 (0.762 ms) & chi phí $0
│
├── 📁 docs/                     # 📚 [TOÀN BỘ TÀI LIỆU KỸ THUẬT & NGHIÊN CỨU]
│   ├── empirical_benchmark_evaluation_report.md # 🏆 BÁO CÁO PHÂN TÍCH THỰC NGHIỆM KAGGLE CHUYÊN SÂU
│   ├── llm_judge_audit_trail.md       # 🔍 BÁO CÁO KIỂM TOÁN THẨM ĐỊNH THỰC NGHIỆM LLM-AS-A-JUDGE (50 Giao dịch OpenRouter)
│   ├── system_architecture.md         # 🏛️ ĐẶC TẢ KIẾN TRÚC HỆ THỐNG PHỄU RAG ĐA TẦNG (Bản vẽ kỹ thuật & sơ đồ)
│   ├── dataset_analysis_and_defense_strategy.md # ⚖️ PHÂN TÍCH CHUYÊN SÂU 205/512 CÂU & CẨM NANG DEFEND TRƯỚC HỘI ĐỒNG
│   ├── research_notes_benchmark_system.md # Master Technical Blueprint & Cẩm nang Nghiên cứu
│   ├── benchmark_walkthrough.md       # Báo cáo tổng quan quy trình đo kiểm
│   ├── data_audit_report.md           # Báo cáo kiểm toán dữ liệu
│   ├── leakage_report.txt             # Báo cáo kiểm định không rò rỉ dữ liệu
│   ├── verify_benchmark_report.txt    # Báo cáo xác minh nhãn ground-truth
│   ├── benchmark.docx / benchmark.txt # Tài liệu benchmark gốc
│   ├── indexing.docx / indexing.txt   # Tài liệu hướng dẫn indexing
│   └── context/                       # Ảnh chụp thảo luận và ghi chú nghiên cứu
│
└── 📦 kaggle_ablation_package.zip # Bản sao tiện ích tại root để nạp nhanh lên Kaggle
```

---

## 🎯 2. HƯỚNG DẪN DÀNH CHO TỪNG NHU CẦU CÔNG VIỆC

### A. Dành cho người phụ trách chạy Kaggle GPU:
1. Bạn chỉ cần làm việc duy nhất với thư mục **`05_kaggle_execution/`**.
2. Đọc file [`05_kaggle_execution/README_KAGGLE.md`](file:///c:/Users/luuth/NCKH/Benchmark/05_kaggle_execution/README_KAGGLE.md).
3. Đẩy file `kaggle_ablation_package.zip` (2.49 MB) lên Kaggle GPU T4, bật Internet ON và chạy:
   ```bash
   !python run_kaggle_ablation.py
   ```
4. Khi chạy xong, tải file `kaggle_benchmark_results.zip` về và giải nén nạp vào repo.

---

### B. Dành cho người viết Luận văn / Báo cáo NCKH:
- **Tài liệu tham khảo toàn diện:** Đọc ngay [`docs/research_notes_benchmark_system.md`](file:///c:/Users/luuth/NCKH/Benchmark/docs/research_notes_benchmark_system.md) — văn bản chứa đầy đủ giả thuyết phễu, phân tích Failure Mode V1, lý thuyết toán học (MaxP, RRF $k=60$) và sơ đồ thư mục.
- **Viết Chương 3 (Thiết kế Hệ thống):**
  - Trích dẫn file [`05_kaggle_execution/structure_aware_parser.py`](file:///c:/Users/luuth/NCKH/Benchmark/05_kaggle_execution/structure_aware_parser.py) (Module M1-M3 bóc tách và kế thừa ngữ cảnh).
  - Trích dẫn thuật toán Article-level MaxP Aggregation (Dai & Callan, SIGIR 2019) và RRF $k=60$ (Cormack et al., SIGIR 2009).
- **Viết Chương 4.2 (Bảng Kết quả Chính):**
  - Trích xuất bảng số liệu chính xác từ [`08_empirical_results/six_configurations_ablation_matrix.csv`](file:///c:/Users/luuth/NCKH/Benchmark/08_empirical_results/six_configurations_ablation_matrix.csv) và [`08_empirical_results/tier1_fair_subset_205_matrix.csv`](file:///c:/Users/luuth/NCKH/Benchmark/08_empirical_results/tier1_fair_subset_205_matrix.csv).
  - Đọc phân tích chi tiết tại [`docs/empirical_benchmark_evaluation_report.md`](file:///c:/Users/luuth/NCKH/Benchmark/docs/empirical_benchmark_evaluation_report.md).
  - Đối chiếu với baselines tại [`02_baselines/`](file:///c:/Users/luuth/NCKH/Benchmark/02_baselines/).
- **Viết Chương 4.3 (Failure Mode Analysis — Điểm nhấn Học thuật):**
  - Toàn bộ luận cứ nằm tại [`04_archive_v1_failure/FAILURE_MODE_ANALYSIS_V1.md`](file:///c:/Users/luuth/NCKH/Benchmark/04_archive_v1_failure/FAILURE_MODE_ANALYSIS_V1.md).
  - Phân tích 3 nguyên nhân: *Context Orphanage*, *Dedup Collapse*, và *Boundary Smearing của LightRAG*.
- **Viết Chương 4.4 (Phân tích Độ trễ & Chi phí):**
  - Sử dụng dữ liệu phân vị P50, P95, P99 từ `04_archive_v1_failure/runtime_performance_and_cost_report.json` và báo cáo v2 sau khi chạy.

---

### C. Dành cho người kiểm tra mã nguồn & dữ liệu:
- Kiểm tra tính rò rỉ: chạy script tại [`06_tools_and_audits/leakage_check.py`](file:///c:/Users/luuth/NCKH/Benchmark/06_tools_and_audits/leakage_check.py).
- Kiểm tra tính nhất quán nhãn: chạy [`06_tools_and_audits/verify_benchmark.py`](file:///c:/Users/luuth/NCKH/Benchmark/06_tools_and_audits/verify_benchmark.py).
- Xem xét kế hoạch Benchmark 2: tham khảo [`07_benchmark_b_pending/README_BENCHMARK_B.md`](file:///c:/Users/luuth/NCKH/Benchmark/07_benchmark_b_pending/README_BENCHMARK_B.md).
