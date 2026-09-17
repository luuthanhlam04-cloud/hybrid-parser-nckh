# Tổng kết Module 5 — Semantic Router (Cổng định tuyến ngữ nghĩa)

Module 5 đóng vai trò là **Cổng định tuyến ngữ nghĩa (Decision Layer)**, đánh dấu sự chuyển tiếp từ Tuyến Tĩnh (Static Structural Pipeline) sang Tuyến Động (Semantic Intelligence Pipeline). Nhiệm vụ cốt lõi của Module này là phân loại các node pháp lý, từ đó chỉ chọn lọc các node thực sự chứa cấu trúc ngữ nghĩa phức tạp (Cross-reference, Exception, Condition...) để chuyển sang LLM, giúp tiết kiệm triệt để chi phí Token/API mà vẫn bảo đảm độ phủ tri thức.

## 1. Công nghệ & Nguyên tắc thiết kế (Tech Stack)

- **Lớp Mô hình Nhúng (Embedding Layer):** 
  - Mô hình **Qwen3-Embedding-0.6B** được tích hợp qua thư viện `SentenceTransformers`. 
  - Tạo ra các vector nhúng (Dense Vector) 1024-dim từ nội dung văn bản (text) của từng `LegalNode`. Việc sinh các Anchor Vectors (vector neo) được tiến hành ngay trên môi trường local.
- **Thuật toán Đo lường và Chấm điểm (Scoring Algorithms):**
  - **Semantic Pattern Match (Regex):** Nhận diện nhanh các từ khóa pháp lý mang tính chất dẫn chiếu, ngoại lệ hoặc điều kiện (VD: "trừ trường hợp...", "quy định tại khoản...").
  - **Vector Similarity (Cosine Similarity):** Đo lường khoảng cách từ văn bản đến các "Mỏ neo ngữ nghĩa" để phát hiện những quan hệ pháp lý ngầm định mà Regex không thể bắt được.
- **Cơ chế phân loại 3 nhánh (Three-way Classification):**
  - `REJECT`: Node thuần túy mang tính thủ tục hành chính, không đưa vào luồng LLM.
  - `RULE_ONLY`: Các tiêu đề chương, mục chỉ giữ vai trò cấu trúc đồ thị tĩnh.
  - `LLM_CANDIDATE`: Gán nhãn các Node mang ngữ nghĩa phức tạp để chuyển sang Module 6.

## 2. Các vấn đề gặp phải và Hướng xử lý (Challenges & Solutions)

### A. Sự đánh đổi giữa Recall và Precision trong thuật toán Max-Fusion (EXP-C)
- **Vấn đề:** Khi kết hợp tín hiệu Embedding vào Regex (Fusion), hệ thống bắt được những biến thể ngữ nghĩa bị ẩn mà Regex bỏ qua, giúp **Recall** tăng mạnh (từ 54.8% lên 67.7%). Tuy nhiên, hệ lụy là việc nhiễu thông tin khiến **Precision** giảm sâu (từ 1.0 xuống 0.677), nghĩa là có rất nhiều node vô nghĩa bị lọt qua.
- **Hướng xử lý (Kiến trúc):** Quyết định thiết kế là **Chấp nhận sự đánh đổi (Ưu tiên Recall hơn Precision)**. Module 5 đóng vai trò như một màng lọc thô (Gatekeeper). Việc phân loại nhầm (False Positive) có thể được khắc phục bằng cách thiết kế Prompt chặt chẽ ở Module 6 (LLM). Tuy nhiên, nếu Module 5 bỏ sót node quan trọng (False Negative), kiến thức pháp luật đó sẽ bị mất vĩnh viễn trên đồ thị. Do đó, ưu tiên Recall là lựa chọn đúng đắn.

### B. Hạn chế của Ngưỡng cố định (Fixed Threshold) trong Embedding
- **Vấn đề:** Quá trình thử nghiệm Baseline Embedding-only (EXP-B) với ngưỡng Cosine Similarity được chốt cứng ở mức `0.75` mang lại kết quả cực kỳ thấp (F1 Score chỉ 0.392). Đặc tính của các LLM Embeddings là các vector thường có xu hướng hội tụ sát nhau, nên một ngưỡng cố định không đủ độ linh hoạt để áp dụng cho mọi câu văn.
- **Hướng xử lý tương lai:** Đề xuất mở rộng nghiên cứu sang **Adaptive Threshold** (Ngưỡng thích ứng động dựa trên Z-score hoặc Top-K), hoặc huấn luyện một mô hình phân loại cực nhẹ (Lightweight Classifier như Logistic Regression) lấy đầu vào là Vector 1024-dim, thay thế hoàn toàn phép tính Cosine cứng nhắc.

### C. Đảm bảo tính Độc lập & Khả năng Kiểm thử
- **Vấn đề:** Nếu gom toàn bộ logic Regex, Embedding, và điều phối vào một file, hệ thống sẽ rất khó để kiểm thử (Test) hoặc thay thế Mô hình nhúng sau này.
- **Hướng xử lý:** Mã nguồn được tách bạch thành nhiều thành phần: `SemanticRouter` (Main Orchestrator), `RoutingEngine` (Xử lý Scoring & Fusion), `EmbeddingEngine` (Đóng gói thao tác tải vector), và `candidate_selector.py`. Điều này đã giúp Module 5 pass toàn bộ 41/41 Unit Tests một cách dễ dàng và sẵn sàng hỗ trợ các mode độc lập.

## 3. Vai trò và Workflow của từng file trong Module 5

Mã nguồn được phân tách triệt để dựa trên nguyên tắc Single Responsibility (Đơn nhiệm) nhằm giúp hệ thống dễ bảo trì và dễ Unit Test. Dưới đây là chức năng chi tiết của từng tệp trong thư mục `src/semantic_router/`:

- **`semantic_router.py`** *(Main Orchestrator)*:
  - *Vai trò:* Là "nhạc trưởng" điều phối toàn bộ quá trình định tuyến. Khởi tạo và liên kết các module con lại với nhau.
  - *Workflow:* Đọc `physical_graph.json` → Lọc nhan đề (Type-based filter) → Gọi `RoutingEngine` để tính điểm Regex và Embedding → So sánh với ngưỡng từ `ThresholdController` → Ra quyết định (Route) → Gọi `CandidateSelector` xuất kết quả.

- **`routing_engine.py`** *(Xử lý Scoring & Fusion)*:
  - *Vai trò:* Trái tim thuật toán của Module 5. Định nghĩa danh sách các quy tắc ngữ nghĩa (Semantic Pattern Registry) và quản lý cơ chế kết hợp điểm (Fusion logic).
  - *Workflow:*
    1. Chạy `evaluate_regex`: Dò tìm từ khóa (VD: "trừ trường hợp") để trả về `regex_score` và phân loại (`category`).
    2. Chạy `embed_score`: Tính toán độ tương tự thông qua `EmbeddingEngine`.
    3. Chạy `fuse`: Kết hợp hai điểm số dựa trên chiến lược (EXP-A, B hoặc Max-Fusion EXP-C) để xuất ra `final_score`.

- **`embedding_engine.py`** *(Quản lý Vector Nhúng)*:
  - *Vai trò:* Quản lý vòng đời tải mô hình và cung cấp giao thức đo lường khoảng cách toán học (Iteration 1 dùng chế độ nạp Precomputed).
  - *Workflow:* Nạp `embeddings.npy` (chứa Vector 1024-dim) và `anchors.npy` (các Vector neo) lên RAM → Cung cấp phương thức `similarity()` áp dụng thuật toán `np.dot()` trên các Vector đã chuẩn hóa (chạy thuần Numpy, vô cùng nhanh).

- **`threshold_controller.py`** *(Kiểm soát Ngưỡng)*:
  - *Vai trò:* Quản lý ngưỡng quyết định (`threshold`).
  - *Workflow:* Trả về ngưỡng cắt (Cut-off). Phiên bản hiện tại sử dụng Fixed Threshold (VD: `0.75`), nhưng thiết kế đã sẵn sàng mở rộng sang Adaptive Threshold (ngưỡng thích ứng động) trong các chặng nghiên cứu sau.

- **`candidate_selector.py`** *(Trình định dạng & I/O)*:
  - *Vai trò:* Định dạng kết quả (`RoutingResult`) và xuất file JSON tương thích với đầu vào của Module 6.
  - *Workflow:* Tập hợp các Node → Tính toán tổng hợp Metadata (`total_evaluated`, `total_candidates`) → Ghi ra tệp `routing_candidates.json` theo đúng định dạng Data Contract.

## 4. Kết quả chạy thực tế trên Luật Đất Đai (Chương III)

Quá trình Benchmark được thực hiện với một tập Ground Truth (Golden Label) chứa 50 nodes được chọn ngẫu nhiên có phân tầng. Hệ thống đã tiến hành chạy 3 chiến lược định tuyến (EXP-A, B, C) với kết quả:

| Chiến lược | Precision | Recall | F1-Score | Quyết định |
| :--- | :--- | :--- | :--- | :--- |
| **EXP-A (Regex-only)** | 1.000 | 0.548 | 0.708 | Bỏ sót nhiều (Recall thấp) |
| **EXP-B (Embedding-only)** | 0.500 | 0.323 | 0.392 | Ngưỡng tĩnh 0.75 không hiệu quả |
| **EXP-C (Max-Fusion)** | 0.677 | **0.677** | 0.677 | **Được chọn (Cân bằng & Recall cao)** |

Dựa trên cấu hình `EXP-C`, tổng số node từ 222 (thuộc Module 4) khi đi qua Cổng định tuyến Module 5 đã lọc ra được **117 nodes** (`LLM_CANDIDATE`). Điều này giúp hệ thống giảm bớt gần 50% gánh nặng Token & chi phí API khi bước sang Module 6.

## 5. Vị trí trong toàn bộ Pipeline

```
M1 (Preprocessing)
   ▼
M2 (Regex Parser)
   ▼
M3 (Validation Engine)
   ▼
M4 (Physical Graph Builder)
   │  physical_graph.json (222 nodes)
   ▼
M5 (Semantic Router)  ← ĐÂY
   │  routing_candidates.json (117 LLM Candidates)
   ▼
M6 (LLM Structured Extraction)  ← Tương lai
   │  Truyền 117 nodes qua LLM API để bóc tách quan hệ (Relationships)
```

Module 5 đã khép lại bước chuyển giao quan trọng, bảo vệ tầng trích xuất của LLM khỏi lượng văn bản thủ tục khổng lồ, đồng thời đặt nền móng kiến trúc vững chắc cho các thực nghiệm tinh chỉnh ngưỡng đánh giá trong tương lai.
