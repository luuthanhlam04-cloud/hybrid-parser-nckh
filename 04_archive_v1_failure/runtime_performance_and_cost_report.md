# BÁO CÁO THỰC CHỨNG HIỆU NĂNG, ĐỘ TRỄ VÀ CHI PHÍ (5 HỆ THỐNG)

- **Phần cứng:** Tesla T4 (VRAM đỉnh: 10288.92 MB)
- **Parsing M1-M3:** 0.052s | **BM25 Build:** 10.801s | **Dense Encode:** 279.262s

## 1. Phân Bố Độ Trễ Truy Xuất Thực Tế Trên GPU (Retrieval Latency):

| Cấu hình | Mean (ms) | Median (ms) | P95 (ms) | P99 (ms) |
| :--- | :--- | :--- | :--- | :--- |
| vector_parser | 0.75 | 0.665 | 0.783 | 0.876 |
| hybrid_parser | 43.462 | 43.052 | 61.878 | 69.519 |
| lightrag_approx | 0.08 | 0.057 | 0.104 | 0.252 |

## 2. Bảng Đối So Sánh Độ Trễ & Chi Phí Toàn Diện Cả 5 Hệ Thống:

| Hệ thống | Độ trễ Truy xuất | Độ trễ End-to-End API | Chi phí Truy vấn API | Chi phí Indexing |
| :--- | :--- | :--- | :--- | :--- |
| **1. Naive Vector (Baseline)** | ~1.2 ms (Local) | 3968.3 ms | $0.2255 | $0.00 (Local Offline) |
| **2. Naive Hybrid (Baseline)** | ~3.5 ms (Local) | 3693.1 ms | $0.2108 | $0.00 (Local Offline) |
| **3. Vector + Parser (Ours)** | 0.75 ms (P95: 0.783 ms) | N/A (Pure Retrieval) | $0.0000 (Local GPU) | $0.00 (Local GPU) |
| **4. Hybrid + Parser (Ours)** | 43.462 ms (P95: 61.878 ms) | N/A (Pure Retrieval) | $0.0000 (Local GPU) | $0.00 (Local GPU) |
| **5. LightRAG (Generic GraphRAG)** | 0.08 ms (P95: 0.104 ms) | 3674.3 ms | $0.1130 | $3.00 (API 500 docs) |

> Toàn bộ quá trình truy xuất của Hệ thống Đề xuất chạy 100% nội bộ trên GPU, không tốn bất kỳ chi phí API nào.
