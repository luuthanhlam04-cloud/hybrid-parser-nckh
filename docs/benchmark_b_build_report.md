# Báo cáo xây dựng Benchmark B

Ngày tạo: 2026-10-30  
Nhánh: `benmark_b` (tạo từ `minh_hybrid_parser`, commit gốc `3cf5d795`)

## Phase 1 — Cố định tập benchmark và phạm vi

- Dùng bộ `datasets/benchmarks/benchmark_B_50_chuong_III.json`, không sửa nội dung pháp lý/gold answer.
- Kiểm tra thành công: 50 câu hỏi duy nhất; 47 câu `ANSWERABLE_IN_CHAPTER_III`; 3 câu `INSUFFICIENT_CORPUS`; phủ đủ 23 Điều (26--48).
- Trạng thái legal gold vẫn là `REQUIRES_HUMAN_LEGAL_REVIEW`; pipeline không tuyên bố bộ gold đã được thẩm định pháp lý độc lập.

## Phase 2 — Chuẩn hóa input công bằng

- Thêm `benchmark_b.corpus`, sinh đúng 23 document article-level từ `outputs/physical_graphs/physical_graph.json`.
- Mỗi document có header `ARTICLE_ID` để truy nguyên và giữ `physical_evidence_node_ids`.
- Sinh `corpus_manifest.json` với SHA-256. Hybrid Parser/UKG và LightRAG phải dùng manifest này cho cùng một run.
- Edge case đã xử lý: Điều 47 có văn bản trực tiếp tại ARTICLE thay vì có node khoản con; document Điều 47 giờ giữ node Điều 47 làm evidence, không rỗng.

## Phase 3 — Hai pipeline độc lập

- `HybridUKGSystem`: dùng M10/Neo4j/UKG hiện có, output ở `outputs/benchmark_b/hybrid/`. Nó không tự chạy lại M1--M9 hay xóa graph hiện hữu.
- `LightRAGSystem`: kế thừa cấu hình cốt lõi của wrapper cũ (BGE-M3 1024 chiều, GPT-4o-mini, hybrid query) nhưng sửa ba lỗi benchmark cũ: không có mock answer, không dùng `./lightrag_workspace` dùng chung, và ghi token/cost ledger từ API usage.
- Workspace LightRAG tách riêng: `outputs/benchmark_b/lightrag/workspace/`; chỉ `index --system lightrag --fresh` mới cho phép tạo index mới và xóa workspace đó.
- Không chạy index/query thật trong phase xây dựng: việc đó cần OpenRouter, model embedding và LightRAG cài đặt đúng phiên bản; kết quả test không được nhầm là kết quả nghiên cứu.

## Phase 4 — Đo lường và review

- Output mỗi hệ: `answers.jsonl`, `per_question_metrics.jsonl`, `metrics.json`, `human_review.csv`.
- Retrieval metrics chỉ tính khi hệ thống xuất được nguồn article. Nếu không trích được source từ LightRAG, kết quả là `not_measured`/`null`, tuyệt đối không gán 0.
- Cost tách `index`/`query`; chỉ tính usage API thực trả về. BGE-M3 local có chi phí API bằng 0, nhưng thời gian local vẫn ghi latency.
- `human_review.csv` buộc reviewer kiểm tra atomic facts, điều kiện/ngoại lệ, forbidden claims và chuỗi dẫn chiếu; không dùng keyword overlap để khẳng định đáp án pháp lý đúng.

## Phase 5 — Kiểm thử

- Vòng 1: 4/5 đạt, phát hiện Điều 47 không có evidence child.
- Đã sửa Phase 2.
- Vòng 2: **5/5 đạt** với `python -m pytest tests/unit/test_benchmark_b.py -q`.
- Kiểm tra cú pháp: `python -m compileall -q benchmark_b` đạt.
- Không cần đến vòng test thứ ba. Cảnh báo duy nhất là deprecation warning từ dependency `anyio`, không phải lỗi Benchmark B.
