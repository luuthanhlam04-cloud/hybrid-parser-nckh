# Benchmark B: Hybrid Parser/UKG vs LightRAG

## Mục tiêu và phạm vi

Benchmark B đánh giá hai hệ thống độc lập trên đúng một phạm vi dữ liệu: Chương III, Luật Đất đai số 31/2024/QH15 (Điều 26--48). Bộ câu hỏi cố định là `datasets/benchmarks/benchmark_B_50_chuong_III.json`: 50 câu, gồm 47 câu trả lời được trong phạm vi và 3 câu buộc hệ thống thừa nhận thiếu căn cứ.

Đây là benchmark mới, tách riêng Benchmark A. Nó không được dùng để thay thế hay gộp điểm với benchmark ba pipeline Naive/Hybrid/LightRAG cũ.

## Tính công bằng

Hai pipeline nhận cùng corpus đầu vào do `benchmark_b.corpus` sinh từ `outputs/physical_graphs/physical_graph.json`: 23 document, mỗi document là một Điều và chứa `[ARTICLE_ID: 31/2024/qh15#<điều>]`. Manifest SHA-256 trong `outputs/benchmark_b/corpus/corpus_manifest.json` là bằng chứng hai pipeline dùng cùng input.

- Hybrid Parser/UKG dùng UKG và Neo4j hiện có. Điểm retrieval trong Benchmark B là **article projection của M10 anchors**, không phải tuyên bố rằng toàn bộ norm/evidence cuối cùng đã được đo.
- LightRAG dùng BGE-M3 local (1024 chiều), GPT-4o-mini qua OpenRouter, chunk 1.200 token với overlap 100 token, workspace riêng: `outputs/benchmark_b/lightrag/workspace`.
- Không có mock response. Thiếu package/API key/Neo4j thì pipeline dừng với lỗi rõ ràng, không tạo kết quả benchmark.
- `--fresh` chỉ xóa workspace LightRAG cô lập. Nó không được dùng với Hybrid Parser/UKG; M1--M9 của Hybrid phải được tái xây dựng bằng lệnh module hiện có nếu nghiên cứu cần đo chi phí toàn pipeline.

## Chạy pipeline

Trong nhánh `benmark_b`:

```powershell
python -m benchmark_b.runner validate
python -m benchmark_b.runner prepare-corpus

# Hybrid: readiness/index metadata, sau đó chạy 50 câu qua M10/Neo4j.
python -m benchmark_b.runner index --system hybrid
python -m benchmark_b.runner run --system hybrid --mode AUTO

# LightRAG: tạo index mới trong workspace riêng, sau đó chạy 50 câu.
# Cài package LightRAG tương thích với môi trường trước khi chạy.
python -m pip install lightrag-hku
python -m benchmark_b.runner index --system lightrag --fresh
python -m benchmark_b.runner run --system lightrag
```

Nếu bản LightRAG được cài cung cấp API khác với `LightRAG`, `QueryParam` hoặc `EmbeddingFunc`, lệnh dừng thay vì fallback. Ghi lại version (`python -m pip show lightrag-hku`) vào báo cáo thực nghiệm trước khi chạy chính thức.

## Output tách biệt

```text
outputs/benchmark_b/
  corpus/{chapter_iii_articles.json,corpus_manifest.json}
  hybrid/{index_metadata.json,answers.jsonl,per_question_metrics.jsonl,metrics.json,human_review.csv}
  lightrag/{workspace/,index_metadata.json,answers.jsonl,per_question_metrics.jsonl,metrics.json,human_review.csv}
```

Không so sánh cache/index cũ với index mới. Mỗi lần cần số đo indexing LightRAG mới, dùng `--fresh` và lưu `index_metadata.json` của run đó.

## Chỉ số được ghi

`metrics.json` báo Recall@5, MRR@5 và citation-article overlap theo cách xác định. Khi LightRAG version không trả context chứa header nguồn, retrieval score được ghi `null`/`not_measured`, **không phải 0**. `human_review.csv` là nơi chấm các yêu cầu pháp lý không thể suy ra an toàn bằng luật text matching: đầy đủ atomic facts, điều kiện/ngoại lệ, không có forbidden claim, chuỗi dẫn chiếu, và tính đúng pháp lý.

Cost ledger tách `index` và `query`; chỉ tính token provider trả về. Công thức với GPT-4o-mini mặc định là:

```text
input_cost  = prompt_tokens * 0.15 / 1,000,000
output_cost = completion_tokens * 0.60 / 1,000,000
```

BGE-M3 chạy local nên không có API embedding cost; thời gian của nó được ghi ở latency/index duration và không được đổi thành USD. Nếu provider không gửi `usage`, ledger ghi `missing_usage_calls`; không được thay bằng ước lượng rồi gọi là chi phí thực đo.

## Kiểm thử không tốn API

```powershell
python -m pytest tests/unit/test_benchmark_b.py -q
```

Các test chỉ kiểm tra dataset, corpus chung, cách tính ledger, xử lý `not_measured` và cách ly output. Chúng không gọi OpenRouter, Neo4j, tải embedding model hay chạy LightRAG.
