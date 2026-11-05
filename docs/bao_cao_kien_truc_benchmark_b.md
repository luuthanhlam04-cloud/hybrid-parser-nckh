# Báo cáo kiến trúc và workflow Benchmark B

## 1. Mục tiêu kiến trúc

Benchmark B vận hành hai pipeline độc lập:

1. **LightRAG**: baseline RAG đồ thị, tự lập index từ clean text và tự truy vấn.
2. **Hybrid Parser/UKG**: hệ thống có preprocessing, parse cấu trúc, extraction, ontology/fusion/Neo4j và M10 `AUTO_FUSION`.

Hai pipeline dùng cùng phạm vi pháp lý: clean text của Chương III Luật Đất đai 2024. Chúng có workspace/output/cost ledger riêng, không chia sẻ vector store, graph store, cache LLM hoặc câu trả lời.

## 2. Sơ đồ tổng thể

```text
clean_Luat_dat_dai_chuong_3.txt ──┬──> LightRAG index/workspace ──> query ──> answer/evidence
                                  │
                                  └──> M1–M9 Hybrid Parser ──> UKG + Neo4j + local embeddings
                                                                    │
50 câu Benchmark B ────────────────────────────────────────────────┴──> M10 AUTO_FUSION ──> answer/evidence/path
                                                                                              │
gold v0.3 (tách khỏi runtime) ────────────────────────────────────────────────────────────────┴──> evaluator + judge/review
```

Gold dataset chỉ được nạp sau khi có output để đánh giá. M10, LightRAG adapter và prompt runtime không nhận `gold_locations`, `accepted_chain_sets`, `reference_answer` hay atomic facts.

## 3. Workflow LightRAG

### 3.1 Indexing

Input trực tiếp của LightRAG là:

```text
outputs/clean_texts/clean_Luat_dat_dai_chuong_3.txt
```

Adapter nạp clean TXT thành một document source, sau đó LightRAG thực hiện chunking/indexing nội bộ:

| Cấu hình | Giá trị |
|---|---|
| Embedding | `BAAI/bge-m3`, 1024 dimensions, local |
| LLM | `openai/gpt-4o-mini` qua OpenRouter (mặc định, có thể cấu hình) |
| Chunk size | 1.200 tokens |
| Chunk overlap | 100 tokens |
| LLM cache | tắt |
| Workspace | `outputs/benchmark_b/lightrag/<run_id>/workspace` |

LightRAG gọi LLM trong pha `index` để trích xuất entity/relation theo cơ chế của SDK. Event log ghi usage do provider trả về; local embedding được ghi thời gian nhưng có chi phí API bằng 0 USD.

### 3.2 Query

Mỗi câu dùng mode `hybrid` của LightRAG với contract cố định:

| Tham số | Giá trị |
|---|---:|
| `graph_top_k` | 5 |
| `chunk_top_k` | 5 |
| Context total budget | 10.000 tokens |
| Entity budget | 2.000 tokens |
| Relation budget | 2.000 tokens |
| Rerank | tắt |
| Temperature | 0 |

Adapter lưu raw retrieval, answer, context/chunks nếu SDK trả về và alignment sang locator chuẩn. Nếu SDK không trả raw context đủ để align, retrieval metric được ghi `not_measured`, không chấm 0.

## 4. Workflow Hybrid Parser/UKG

### 4.1 Xây dựng UKG trước benchmark

Hybrid không tái build âm thầm khi chạy Benchmark B. Các artifact M1–M9 phải có sẵn:

```text
DOCX -> M1 preprocessing/clean text
     -> M2 parse cấu trúc Điều–Khoản–Điểm
     -> M5 local embeddings
     -> M6 LLM structured extraction
     -> M7 validation/ontology
     -> M8 fusion UKG
     -> M9 Neo4j ingestion
```

Runner `index --system hybrid` chỉ kiểm tra readiness và ghi metadata; nó không suy đoán hoặc tính lại chi phí M1–M9. Nếu nghiên cứu đo chi phí indexing Hybrid, phải chạy M6 extraction riêng trên cùng artifact đầu vào và dùng event log thực tế.

### 4.2 M10 AUTO_FUSION khi query

```text
Câu hỏi
  -> local vector anchor search
  -> Jev pre-retrieval routing (có fallback deterministic)
  -> Mode A: norm/semantic retrieval
  -> typed explicit-reference traversal + parent/child retrieval
  -> evidence fusion, answerability gate, bounded expansion
  -> context assembly có budget
  -> LLM answer generation
  -> answer, evidence, context evidence, reference paths, provenance
```

M10 giữ các lớp evidence riêng: anchor, expanded evidence, generation-context evidence, explicit reference edge, hierarchy step và `answer_path_trace`. Khi Jev lỗi, router/gate fallback deterministic thay vì dừng hoặc trả context rỗng.

## 5. Chuẩn hóa output để so sánh

Mỗi hệ thống phải ghi output theo contract chung:

```text
answers.jsonl
per_question_metrics.jsonl
structural_metrics.jsonl
metrics.json
api_events.jsonl / jev_api_events.jsonl
index_metadata.json
```

Evidence được chuẩn hóa thành `EvidenceItem`:

- `raw_source_id`, `text`, `rank`, `granularity`;
- `canonical_locators`;
- `alignment_status`: `EXACT`, `ANCESTOR_ONLY`, `ARTICLE_ONLY` hoặc `UNRESOLVED`;
- `stage`: retrieved, expanded hoặc generation_context.

Điều này giúp đối chiếu output của LightRAG và Hybrid trên cùng locator gold mà không ép hai hệ thống dùng cùng cấu trúc lưu trữ.

## 6. Đánh giá và chi phí

### 6.1 Các lớp metric

| Lớp | Metric/đối tượng |
|---|---|
| Retrieval cấp Điều | Recall@5, MRR@5, anchor recall. |
| Evidence | exact locator recall, expanded/context evidence recall, hierarchy context/child evidence. |
| Citation | Precision/Recall ở cấp Điều, Khoản, Điểm. |
| Dẫn chiếu | Reference-target recall, chain-step precision/recall/F1, edge-label accuracy, Chain Exact Match. |
| Nội dung | Atomic fact coverage, condition/exception coverage, subject scope, forbidden/unsupported claims, legal correctness. |
| Hành vi ngoài corpus | Abstention accuracy và refusal quality. |
| Vận hành | Latency, usage, cost từng pha. |

Không áp dụng chain metric cho câu không có gold chain; không áp dụng evidence-content metric cho `INSUFFICIENT_CORPUS`. Tất cả summary phải kèm mẫu số `scored`, `not_measured`, `not_applicable`.

### 6.2 Tách chi phí

| Hệ thống | Indexing | Query-time |
|---|---|---|
| LightRAG | LLM graph extraction từ clean TXT; local BGE-M3 không tính API cost. | LLM query/generation. |
| Hybrid Parser/UKG | Chỉ đo M6 LLM extraction nếu mục tiêu là token extraction; M5 embedding local, M7/M8/M9 không có LLM API cost. | LLM answer, Jev routing/gating và judge được ghi riêng. |

Cost ledger chỉ cộng token usage mà provider trả về. Với tariff mặc định GPT-4o-mini trong code: input 0,15 USD/1M token; output 0,60 USD/1M token. Nếu provider thiếu usage thì ghi `missing_usage_calls`; không thay bằng ước lượng và gọi đó là chi phí quan sát được.

## 7. Fairness và các giới hạn phải nêu trong báo cáo

1. Cùng **phạm vi luật sạch** không đồng nghĩa cùng representation: LightRAG ingest nguyên clean TXT, còn Hybrid dùng cấu trúc/UKG được xây từ cùng nguồn. Đây là chủ đích so sánh baseline text-to-graph với parser/UKG, nhưng phải công khai.
2. Chunk size/retrieval budget không thể đồng nhất tuyệt đối: LightRAG dùng chunk 1.200 token; Hybrid truy hồi node Điều–Khoản–Điểm và fusion context. Vì vậy nên báo cáo metric evidence/answer trên locator chuẩn, không chỉ so sánh số chunk.
3. Không dùng cache index/query cũ khi đo cost. Mỗi LightRAG indexing run dùng workspace mới và run ID riêng.
4. LightRAG chưa xuất `reference_paths` theo contract chung; Chain Exact Match của LightRAG phải ghi `N/A`, không phải 0. Không được kết luận Hybrid tốt hơn về multi-hop chỉ vì một bên có metric còn bên kia không có.
5. Citation mismatch cần được diễn giải là phép đo citation parser hiện tại; không suy ra trực tiếp rằng tỷ lệ câu trả lời sai pháp lý tương ứng.

## 8. Quy trình chạy khuyến nghị

```powershell
# 1. Kiểm tra gold và mapping
python -m benchmark_b.runner validate

# 2. LightRAG: index clean TXT vào workspace mới
python -m benchmark_b.runner index --system lightrag --run-id lightrag_vNN --fresh
python -m benchmark_b.runner run --system lightrag --run-id lightrag_vNN

# 3. Hybrid: UKG M1–M9 phải chuẩn bị trước
python -m benchmark_b.runner index --system hybrid --run-id hybrid_vNN
python -m benchmark_b.runner run --system hybrid --run-id hybrid_vNN --mode AUTO_FUSION

# 4. Khi cần chấm lại answer đã lưu mà không chạy retrieval/query lại
python -m benchmark_b.runner judge --answers outputs/benchmark_b/<system>/<run_id>/answers.jsonl
```

## 9. Câu văn gợi ý cho báo cáo nghiên cứu

> Benchmark B được triển khai theo hai pipeline độc lập. LightRAG xây dựng graph index từ clean text của Chương III Luật Đất đai 2024 và truy vấn với cấu hình cố định. Hybrid Parser/UKG sử dụng đồ thị pháp lý đã được phân cấp và hợp nhất, sau đó truy vấn bằng M10 AUTO_FUSION có provenance cho evidence và đường dẫn dẫn chiếu. Hai hệ thống được đánh giá trên cùng bộ gold locator độc lập với runtime; chi phí indexing, query, routing và judge được ghi tách pha. Do representation nội bộ khác nhau, nghiên cứu không đồng nhất chunk size một cách cưỡng ép mà so sánh trên evidence alignment, chất lượng câu trả lời và các metric cấu trúc có điều kiện áp dụng rõ ràng.
