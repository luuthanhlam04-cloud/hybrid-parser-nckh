# Tóm tắt kiến trúc hiện hành — Module 10: Retrieval, Evidence Fusion và Answer Generation

**Phiên bản tài liệu:** M10 trên nhánh `main`, sau khi đồng bộ cơ chế Jev + `AUTO_FUSION`
**Phạm vi:** Truy vấn UKG Neo4j và sinh câu trả lời cho Chương III Luật Đất đai 2024
**Cập nhật:** 06/11/2026

## 1. Vai trò của M10

Module 10 là tầng truy vấn của Hybrid Parser/UKG. M10 nhận câu hỏi pháp lý bằng ngôn ngữ tự nhiên, truy hồi evidence từ UKG, mở rộng cấu trúc pháp lý và dẫn chiếu, sau đó tạo context có provenance cho LLM sinh câu trả lời.

M10 **không** tạo, sửa hoặc ghi thêm cạnh tri thức vào Neo4j khi truy vấn. Những dẫn chiếu rõ trong nguyên văn được dựng read-only ở thời điểm truy vấn và luôn mang provenance `EXPLICIT_TEXT_REFERENCE`. Một reference path do M10 xuất ra không phải là quan hệ `REFERENCE_TO` đã tồn tại sẵn trong UKG M8/M9.

M10 vẫn giữ Mode A và Mode B để phục vụ đối chứng; chế độ vận hành chính hiện tại là `AUTO_FUSION`.

| Chế độ | Mục đích |
|---|---|
| `A` | Truy hồi quy phạm `GLOBAL_NORM` từ anchor và cấu trúc norm. |
| `B` | Duyệt K-hop tổng quát trên đồ thị; dùng cho so sánh/baseline. |
| `AUTO` | Alias tương thích ngược, được chuẩn hóa thành `AUTO_FUSION`. |
| `AUTO_FUSION` | Luồng chính: anchor + norm + typed reference + hierarchy + physical evidence + Jev gate + evidence fusion. |

> Khác với kiến trúc cũ, `AUTO_FUSION` **không** chạy Mode A rồi chỉ chuyển Mode B khi Mode A rỗng. Mode A luôn chạy cùng các nhánh evidence cần thiết khác.

## 2. Kiến trúc thành phần

```text
Câu hỏi
  │
  ├─ AnchorSearch
  │    ├─ vector search trên Neo4j
  │    └─ lexical search trên physical graph
  │
  ├─ QuestionRouter
  │    ├─ rule signals
  │    └─ Jev Decisions API hoặc conservative fallback
  │
  ├─ GraphQuery
  │    ├─ GLOBAL_NORM (Mode A)
  │    ├─ typed explicit-reference traversal
  │    ├─ parent / child / exception expansion
  │    └─ physical evidence fallback
  │
  ├─ Evidence Fusion + Answerability Gate
  │    ├─ canonical locator, deduplication, ranking
  │    ├─ Jev relevance/sufficiency gate hoặc fallback
  │    └─ tối đa một targeted expansion
  │
  ├─ ContextPruner + AnswerPathBuilder
  │    ├─ minimal typed paths
  │    ├─ facet-aware child filtering
  │    └─ answer paths có source/type/target/provenance
  │
  ├─ ContextAssembler
  │    └─ context có locator và evidence provenance
  │
  └─ AnswerGenerator
       └─ `openai/gpt-4o-mini` qua OpenRouter
```

## 3. Thành phần mã nguồn

| File | Trách nhiệm hiện hành |
|---|---|
| `run_m10.py` | CLI, kết nối Neo4j/OpenRouter, mặc định `AUTO_FUSION`, `top_k=5`. |
| `anchor_search.py` | Vector anchor từ Neo4j kết hợp lexical anchor từ physical graph. |
| `question_router.py` | Kết hợp rule signal và xác suất Jev để kích hoạt facet truy hồi. |
| `jev_client.py` | Client OpenRouter Decisions API, validation response, retry tối đa 3 lần và event logging khi được cấp event log. |
| `graph_query.py` | Cypher cho norm, K-hop, typed reference, hierarchy, exception và physical evidence. |
| `evidence_fusion.py` | Chuẩn hóa canonical locator, tạo `EvidenceCandidate`, deduplicate và pre-rank evidence. |
| `answerability_gate.py` | Jev đánh giá relevance/sufficiency; lỗi Jev chuyển sang fail-safe fallback. |
| `context_pruning.py` | Prune typed path và chọn child theo parent/facet/hành vi. |
| `answer_path_builder.py` | Dựng `answer_paths`, có Jev root ranking nhưng luôn có deterministic fallback. |
| `context_assembler.py` | Render evidence có locator/provenance và áp budget context. |
| `answer_generator.py` | Prompt grounded answer; model mặc định `openai/gpt-4o-mini`. |
| `m10_pipeline.py` | Orchestrator toàn bộ lifecycle, ghi output JSONL. |

## 4. Luồng truy vấn AUTO_FUSION

### 4.1. Anchor retrieval

M10 mã hóa câu hỏi bằng encoder đã lưu trong metadata cache M5. Hệ thống lấy tối đa năm anchor qua vector index Neo4j. Với corpus Chương III mặc định, vector result được dung hợp với lexical anchor lấy từ physical graph để giảm bỏ sót thuật ngữ pháp lý định danh cao.

Với câu có dấu hiệu dẫn chiếu, M10 có thể lấy tối đa mười lexical auxiliary anchor. Auxiliary anchor không thuộc Anchor Recall@5; chúng chỉ phục vụ mở rộng reference branch.

### 4.2. Định tuyến nhu cầu câu hỏi

`QuestionRouter` nhận rule signals và có thể gọi Jev `typesafe/jev-1.14` qua OpenRouter Decisions API. Router đánh giá các facet:

- cần parent context;
- cần liệt kê toàn bộ children;
- cần reference traversal;
- cần multi-hop;
- cần exception;
- cần phân giải chủ thể;
- cần so sánh.

Nếu Jev timeout, lỗi HTTP, lỗi schema hoặc bị tắt, router không dừng truy vấn. Hệ thống chuyển sang `CONSERVATIVE_FUSION_FALLBACK`, giữ parent/reference/subject expansion cần thiết theo rule.

### 4.3. Thu thập evidence

AUTO_FUSION thu thập đồng thời:

1. **Norm evidence:** Mode A đọc `GLOBAL_NORM`, vai trò chủ thể, hành vi, đối tượng, điều kiện, ngoại lệ và hệ quả.
2. **Typed reference evidence:** phân tích dẫn chiếu hiển thị trong văn bản vật lý. Cạnh có `source_locator`, `relation_type`, `target_locator`, hướng và provenance.
3. **Hierarchy evidence:** parent context hoặc child evidence cấp Điều–Khoản–Điểm khi cần.
4. **Exception evidence:** nội dung ngoại lệ, cấm hoặc hạn chế.
5. **Physical evidence:** nguyên văn node vật lý gần anchor để tránh trả lời chỉ dựa trên entity/relation trừu tượng.

Target nằm ngoài Chương III được đánh dấu `EXTERNAL_REFERENCE`. Target không ánh xạ được giữ `UNRESOLVED`; M10 không tự tạo node hoặc nội dung giả.

### 4.4. Dung hợp, gate và mở rộng có giới hạn

`EvidenceCandidate` đưa các nguồn evidence về contract chung gồm text, canonical locator, source type, provenance, parent locator và reference metadata. Candidate được deduplicate và pre-rank trước khi gửi Jev.

`AnswerabilityGate` đánh giá evidence nào hỗ trợ trực tiếp câu trả lời, context đã đủ chủ thể/điều kiện/ngoại lệ/reference target hay chưa. Nếu thiếu facet, M10 thực hiện **tối đa một** vòng targeted expansion. Thiết kế giới hạn tổng số Jev call không vượt ba lần trên mỗi câu hỏi.

Nếu Jev gate thất bại, M10 giữ candidate đã có thay vì trả context rỗng hoặc tự sinh điểm gate.

### 4.5. Pruning và answer-path construction

`ContextPruner` chấm typed reference path và chọn số path có giới hạn. Children được nhóm theo parent và đánh giá theo hành vi, chủ thể, điều kiện, ngoại lệ và lexical overlap. Mục tiêu là giảm context noise mà không lấy children từ nhánh pháp lý không liên quan.

`AnswerPathBuilder` tạo các output tách biệt:

- `explicit_reference_edges`;
- `selected_hierarchy_steps`;
- `answer_paths`;
- `answer_path_trace`.

`PARENT_CHILD_CONTEXT` được tách khỏi cạnh dẫn chiếu tường minh để không làm nhiễu metric reference-chain, nhưng vẫn được lưu khi cần audit.

### 4.6. Context assembly và answer generation

Mỗi evidence render vào context gồm locator chuẩn Điều–Khoản–Điểm, loại evidence, provenance, reference edge (nếu có) và nguyên văn. `assemble_fusion()` dùng budget ước lượng tối đa **10.000 token**; `max_chars=16.000` vẫn áp dụng cho renderer legacy Mode A/B.

`AnswerGenerator` gửi question và context sang `openai/gpt-4o-mini`. Prompt yêu cầu:

- chỉ dùng căn cứ trong context;
- nêu locator khi context có locator;
- không dùng node ID hay `UNRESOLVED` làm citation;
- nêu giới hạn corpus nếu câu hỏi vượt phạm vi dữ liệu.

## 5. Output, provenance và instrumentation

Kết quả M10 có câu trả lời cùng các trường phục vụ audit:

- `anchors`, `anchor_records`, `auxiliary_reference_anchors`;
- `routing_trace`;
- `expanded_evidence`, `context_evidence`;
- `reference_paths`, `answer_paths`;
- `explicit_reference_edges`, `selected_hierarchy_steps`;
- `candidate_reference_paths`, `path_pruning_trace`, `child_pruning_trace`, `answer_path_trace`;
- `answerability_trace`, `context_budget`, `retrieval_stage_counts`;
- `usage` của answer model.

Trong runner Benchmark B, query answer, Jev và LLM Judge có ledger chi phí riêng. Khi chạy trực tiếp bằng `run_m10.py`, output JSONL có `usage` answer model; muốn có Jev event ledger cần truyền event logger vào `JevClient` như adapter benchmark.

## 6. Cấu hình môi trường

```dotenv
OPENROUTER_API_KEY=...   # hoặc LLM_API_KEY
NEO4J_URI=...
NEO4J_USERNAME=...
NEO4J_PASSWORD=...
M10_LLM_MODEL=openai/gpt-4o-mini
JEV_ENABLED=true
JEV_MODEL=typesafe/jev-1.14
JEV_TIMEOUT_SECONDS=15
JEV_MAX_RETRIES=3
```

Trên Windows:

```powershell
$env:PYTHONUTF8=1
.\venv\Scripts\python.exe run_m10.py "Câu hỏi pháp lý" --mode AUTO_FUSION --top-k 5
```

## 7. Kiểm chứng thực tế và giới hạn hiện hành

Pilot live năm câu trên `main` ngày 06/11/2026 cho thấy pipeline chạy end-to-end, Aura Neo4j, Jev, evidence fusion và answer generation hoạt động. Đánh giá thủ công: **2 câu đạt, 1 câu đạt một phần, 2 câu không đạt**.

Điểm mạnh đã quan sát:

- từ chối đúng câu hỏi mức thuế nằm ngoài corpus;
- trả lời đúng trường hợp cho thuê lại tại Điều 41 khoản 2 điểm đ;
- context pilot không tạo evidence `UNRESOLVED`.

Giới hạn cần xử lý:

1. Câu hỏi liệt kê có thể chỉ giữ một point con thay vì toàn bộ point thuộc đúng parent branch.
2. Điều kiện Điều 45 và Điều 46 có thể bị trộn khi context chứa cả hai nhánh.
3. Phải phân biệt `bán tài sản` với `bán tài sản và quyền thuê`; Điều 46 khoản 2 không áp dụng cho mọi trường hợp.
4. `answer_paths` của câu cross-reference có thể mới giữ đoạn cuối tại target, chưa bảo toàn đủ anchor nguồn → reference target → answer child.
5. Neo4j hiện cảnh báo `db.index.vector.queryNodes` deprecated; snapshot còn thiếu `HAS_CONSEQUENCE` và property `name`, làm query log nhiễu.

Do đó M10 hiện phù hợp cho development/pilot và benchmark có nêu giới hạn. Chưa nên khẳng định đã giải quyết hoàn chỉnh câu multi-condition hoặc chain exact chỉ dựa trên AUTO_FUSION.

## 8. Khác biệt so với tài liệu M10 cũ

| Tài liệu cũ | Kiến trúc hiện hành |
|---|---|
| `AUTO`: Mode A có kết quả thì chặn Mode B | `AUTO` map thành `AUTO_FUSION`; Mode A luôn chạy cùng nguồn evidence khác. |
| Vector anchor thuần Neo4j | Vector + lexical fusion và auxiliary anchor cho reference query. |
| Context chủ yếu norm/neighbor | Evidence contract có locator, physical text, provenance và reference metadata. |
| Cắt ngữ cảnh chính bằng `max_chars=16.000` | Fusion context dùng budget 10.000 token; legacy A/B vẫn dùng hard char bound. |
| Không có Jev | Jev hỗ trợ router, evidence gate và root-path ranking; luôn có fallback. |
| Không có output chain rõ ràng | Có `answer_paths`, explicit edges, hierarchy steps và trace audit. |

## 9. Kết luận

M10 đã chuyển từ retrieval A/B đơn tuyến sang pipeline AUTO_FUSION có provenance, bounded expansion, Jev-assisted routing và answer-path audit. Nâng cấp giúp thu thập evidence cho câu hỏi cấu trúc và dẫn chiếu. Tuy nhiên, chất lượng câu trả lời vẫn phụ thuộc vào việc chọn đúng child branch, phân biệt phạm vi điều kiện và tái dựng chain tối thiểu. Những giới hạn này phải được nêu rõ khi báo cáo kết quả thực nghiệm.
