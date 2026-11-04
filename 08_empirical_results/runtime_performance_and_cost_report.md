# BÁO CÁO THỰC CHỨNG HIỆU NĂNG TÍNH TOÁN, ĐỘ TRỄ VÀ CHI PHÍ (NCKH RAG v2)

- **Thiết bị:** Tesla T4 (VRAM: 14.56 GB)
- **Thời gian Parse M1-M3:** 0.100s (127264 chunks/s)
- **Thời gian Build BM25:** 12.497s
- **Thời gian Encode BGE-M3:** 60.354s (VRAM đỉnh: 2654.22 MB)

## 1. Phân Bố Độ Trễ Truy Xuất Thực Tế (Retrieval Latency):

| Hệ thống | Mean (ms) | Median (ms) | P95 (ms) | P99 (ms) | Min (ms) | Max (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| bm25_parser_latency_ms | 46.701 | 46.117 | 65.007 | 78.056 | 16.598 | 109.423 |
| vector_parser_latency_ms | 0.825 | 0.755 | 0.865 | 0.945 | 0.658 | 31.139 |
| hybrid_parser_latency_ms | 42.941 | 42.35 | 60.835 | 69.712 | 11.613 | 80.977 |
| lightrag_approx_latency_ms | 0.073 | 0.061 | 0.087 | 0.237 | 0.055 | 1.98 |

## 2. Ma trận 6 Cấu hình Thực nghiệm Ablation:

| Chunking            | Retrieval   |   Recall@5 |   MRR@5 |   Citation | P95_Latency     |
|:--------------------|:------------|-----------:|--------:|-----------:|:----------------|
| 1. Naive (Điều thô) | BM25 Only   |     0.7051 |  0.5794 |     0.6637 | ~2.5 ms         |
| 1. Naive (Điều thô) | Dense Only  |     0.9141 |  0.8129 |     0.8793 | 3968.3 ms (API) |
| 1. Naive (Điều thô) | Hybrid RRF  |     0.9316 |  0.8796 |     0.9133 | 3693.2 ms (API) |
| 2. Parser (Vi mô)   | BM25 Only   |     0.7402 |  0.6052 |     0.6973 | 65.007 ms       |
| 2. Parser (Vi mô)   | Dense Only  |     0.9316 |  0.8602 |     0.9902 | 0.865 ms        |
| 2. Parser (Vi mô)   | Hybrid RRF  |     0.873  |  0.7615 |     0.9786 | 60.835 ms       |

> Toàn bộ quá trình truy xuất của Hệ thống Đề xuất chạy 100% nội bộ trên GPU, không tốn bất kỳ chi phí API nào.
