# Báo cáo nâng cấp M10: Jev + AUTO-FUSION

## Bổ sung: minimal-path pruning và facet-aware child filtering

Ngày nghiệm thu: 31/10/2026.

### Thay đổi

- Thêm `src/retrieval/context_pruning.py` để chấm điểm và giới hạn tối đa 3 typed reference path cho mỗi câu hỏi.
- Children được nhóm theo parent, chấm theo hành vi, facet điều kiện/ngoại lệ/chủ thể và lexical overlap; mỗi parent giữ tối đa 5 children.
- Câu hỏi yêu cầu danh sách đầy đủ vẫn được phép lấy toàn bộ các mục liên quan trong đúng parent, thay vì lấy children từ mọi nhánh.
- Lưu `candidate_reference_paths`, `path_pruning_trace` và `child_pruning_trace` để kiểm toán cả bằng chứng được chọn và bị loại.
- Tách `PARENT_CHILD_CONTEXT` sang `hierarchy_context_edges`; trường này không còn làm nhiễu metric chuỗi dẫn chiếu pháp lý.

### Pilot ba câu dẫn chiếu

Tập nghiệm thu: `B026`, `B030`, `B034`; chế độ `AUTO_FUSION`; không chạy LLM Judge.

Run được chốt: `outputs/benchmark_b/hybrid/hybrid_minpath_3q_20261031_03`.

| Chỉ số | Trước pruning | Sau pruning |
|---|---:|---:|
| Expanded evidence recall | 1.0000 | 1.0000 |
| Generation context recall | 1.0000 | 1.0000 |
| Context evidence | 165 / 3 câu | 38 / 3 câu |
| Context evidence trung bình | 55.00 | 12.67 |
| Evidence unresolved | 0 | 0 |
| Chain-step precision | 0.0645 | 0.2222 |
| Chain-step recall | 0.8889 | 0.5000 |
| Chain-step F1 | chưa ghi nhận ở pilot cũ | 0.3000 |
| Chain Exact Match | 0.0000 | 0.0000 |
| Edge-label accuracy | 1.0000 | 0.6667 |
| Reference-target recall | 0.9444 | 0.6111 |

API query answer dùng 7.449 tokens, chi phí quan sát 0,0015435 USD. Jev dùng 9 calls, chi phí quan sát 0,000886368 USD. Judge không được chạy trong pilot này.

### Kết luận nghiệm thu

Hai tầng lọc giải quyết tốt vấn đề phình context: giảm khoảng 76,97% số evidence nhưng vẫn giữ 100% recall của evidence/context trên ba câu thử. Precision chuỗi dẫn chiếu tăng đáng kể so với pilot cũ.

Tuy nhiên, chuỗi dẫn chiếu chưa ổn định hoàn toàn. Việc giới hạn path làm giảm recall bước chuỗi và `Chain Exact Match` vẫn bằng 0. Vì vậy cấu hình hiện tại phù hợp để chạy development benchmark hoặc pilot mở rộng, nhưng trước khi coi kết quả 50 câu là kết quả nghiên cứu cuối cùng cần cải thiện nhận diện chuỗi nhiều hop theo quan hệ cha–con của locator mà không đưa cạnh phân cấp vào gold reference chain.

Ngày nghiệm thu: 31/10/2026  
Nhánh: `benmark_b`  
Phạm vi: M10, adapter Benchmark B, evaluator và instrumentation; không sửa dữ liệu M1–M9 hay ghi thay đổi vào Neo4j.

## 1. Kết luận ngắn

Hệ thống đã được nâng cấp từ cơ chế `AUTO` chọn loại trừ A/B sang `AUTO_FUSION`, trong đó Mode A luôn chạy đồng thời với lexical/vector anchor, hierarchy expansion, explicit-text typed reference traversal, Jev routing, Jev evidence gate và một vòng targeted expansion có giới hạn.

Các yêu cầu về fallback, provenance, locator, tách tầng retrieval, cost separation và chống gold leakage đã được triển khai. Pilot 10 câu chạy thành công ở tất cả nhóm câu hỏi và tăng anchor recall từ 0,5556 ở bản pilot đầu lên 0,9444; bản hoàn thiện sau đó đạt expanded/context recall 1,0. Tuy nhiên, tiêu chí chất lượng cross-reference chưa hoàn thiện tuyệt đối: `Chain Exact Match = 0` và còn nhiều đường dẫn thừa. Vì vậy hệ thống đủ để tiếp tục pilot/calibration, nhưng chưa nên chạy full 50 câu để lấy số liệu báo cáo chính thức nếu mục tiêu là công bố chain exact/precision ở trạng thái tốt nhất.

## 2. Kiến trúc đã triển khai

Luồng truy vấn mới:

1. Top-5 anchor kết hợp 4 lexical anchors từ physical graph và tối đa 1 vector anchor từ Neo4j.
2. Rule router phát hiện yêu cầu liệt kê, dẫn chiếu, ngoại lệ, chủ thể, so sánh và multi-hop.
3. Jev `typesafe/jev-1.14` gọi qua `POST /api/alpha/decisions` để trả xác suất routing kiểu `noul`.
4. Mode A luôn truy hồi `GLOBAL_NORM`; không còn điều kiện “Mode A có record thì bỏ Mode B”.
5. Typed traversal đọc các dẫn chiếu hiển thị trong văn bản vật lý và tạo cạnh read-only với:
   - `source_locator`;
   - `relation_type`;
   - `target_locator`;
   - `direction=OUTGOING`;
   - `provenance=EXPLICIT_TEXT_REFERENCE`.
6. Các nhánh parent, child, exception và physical fallback được hợp nhất thành `EvidenceCandidate`.
7. Deterministic pre-ranking giới hạn candidates trước khi gửi Jev.
8. Jev evidence/sufficiency gate giữ evidence liên quan và xác định facet còn thiếu.
9. Targeted expansion chạy tối đa một vòng; tổng số Jev calls không vượt 3/câu.
10. Context render locator chuẩn Điều–Khoản–Điểm, có token budget 10.000.
11. GPT-4o-mini sinh câu trả lời từ context đã chốt.

Do UKG M8/M9 hiện không có cạnh `REFERENCE_TO`, M10 không bịa hoặc ghi cạnh mới vào Neo4j. Cạnh dẫn chiếu được dựng từ cụm dẫn chiếu hiện hữu trong nguyên văn và được ghi provenance rõ ràng. Target ngoài Điều 26–48 được đánh dấu `EXTERNAL_REFERENCE`; target không ánh xạ được không được giả lập thành node nội bộ.

## 3. Thành phần mã nguồn

Các file mới:

- `src/retrieval/jev_client.py`: Decisions API, validation, timeout, retry tối đa 3 và event logging.
- `src/retrieval/routing_contracts.py`: `QuestionNeeds`, `RoutingDecision`.
- `src/retrieval/question_router.py`: rule signals, Jev probabilities và conservative fallback.
- `src/retrieval/evidence_fusion.py`: locator, evidence contract, deduplication và pre-ranking.
- `src/retrieval/answerability_gate.py`: relevance/sufficiency gate và fail-safe.
- `tests/unit/test_jev_auto_fusion.py`: test Jev, router, fallback, locator, budget, cost và gold leakage.

Các file chính đã sửa:

- `src/retrieval/m10_pipeline.py`;
- `src/retrieval/graph_query.py`;
- `src/retrieval/anchor_search.py`;
- `src/retrieval/context_assembler.py`;
- `src/retrieval/answer_generator.py`;
- `benchmark_b/systems/hybrid_ukg.py`;
- `benchmark_b/alignment.py`;
- `benchmark_b/evaluation.py`;
- `benchmark_b/events.py`;
- `benchmark_b/runner.py`;
- `.env.example`, `requirements.txt`, `run_m10.py`.

## 4. Provenance và output contract

Mỗi kết quả `AUTO_FUSION` có thêm:

- `routing_trace`;
- `anchor_records`;
- `auxiliary_reference_anchors`;
- `expanded_evidence`;
- `context_evidence`;
- `reference_paths`;
- `answerability_trace`;
- `context_budget`;
- `retrieval_stage_counts`.

Mỗi evidence có `canonical_locator` hoặc `alignment_status=UNRESOLVED`. Locator được suy ra từ physical node ID, không tra trong gold question. `d` và `đ` được giữ riêng (`Dd` và `Dđ`).

Adapter benchmark xuất riêng:

- `anchor_article_ids`;
- `expanded_article_ids`;
- `context_article_ids`.

Evaluator báo riêng:

- `anchor_recall_at_5`;
- `expanded_evidence_recall`;
- `generation_context_recall`.

## 5. Cost instrumentation

Jev events được ghi tại:

`outputs/benchmark_b/hybrid/<run_id>/jev_api_events.jsonl`

Các phase chi phí không bị trộn:

- `query_cost_ledger`: GPT-4o-mini trả lời M10;
- `jev_cost_ledger`: Jev routing/gating;
- `llm_judge`: Judge v6, chỉ có khi bật Judge;
- M6 indexing extraction tiếp tục là ledger riêng ở lệnh `extract-m6`.

Event log hỗ trợ cả tên usage của Chat Completions (`prompt_tokens`, `completion_tokens`) và Decisions API (`input_tokens`, `output_tokens`). API key không được ghi vào log.

## 6. Kết quả pytest — giới hạn đúng 3 vòng

| Vòng | Phạm vi | Kết quả | Xử lý |
|---|---|---:|---|
| 1/3 | `tests/unit` | 127 pass, 3 fail | Sửa 2 lỗi mới: overlap locator điểm/khoản và uncertainty trace; xác định 1 test M9 cũ không khớp cơ chế batch hiện tại. |
| 2/3 | `tests/unit` | 129 pass, 1 fail | Chỉ còn assertion M9 cũ kỳ vọng `execute_write` trong khi implementation dùng `session.run`. |
| 3/3 | toàn bộ `tests` | 134 pass, 4 fail | Bốn lỗi live Neo4j quality cũ: thiếu 5 conditions Điều 45 khoản 1, thiếu exception, không có `REFERENCE_TO`, lỗi dữ liệu subject/action. Dừng pytest theo giới hạn đã thỏa thuận. |

Test M9 được cập nhật để kiểm tra đúng batch size qua cả `execute_write` và `session.run`; mã M9 không bị thay đổi.

Bốn lỗi vòng cuối là lỗi snapshot M6–M9 đã tồn tại và cũng giải thích vì sao M10 cần explicit-text traversal. Không chạy vòng pytest thứ tư. Các thay đổi sau vòng 3 được nghiệm thu bằng pilot thực tế, không được tính là một vòng pytest mới.

## 7. Pilot và số liệu

### 7.1 Pilot 10 nhóm câu hỏi — run 04

Run:

`outputs/benchmark_b/hybrid/hybrid_jev_auto_fusion_pilot_20261031_04`

Tập câu: B001, B009, B011, B019, B021, B026, B030, B034, B041, B048.

| Chỉ số | Kết quả |
|---|---:|
| Questions completed | 10/10 |
| Anchor Recall@5 | 0,9444 |
| MRR@5 | 0,8611 |
| Expanded evidence recall | 1,0000 |
| Generation context recall | 1,0000 |
| Context evidence `UNRESOLVED` | 0/124 |
| Jev calls | 28, không quá 3/câu |
| Jev provider cost | $0,002688252 |
| GPT-4o-mini query cost | $0,004565400 |
| Judge cost | N/A — pilot dùng `--skip-judge` |

Tất cả nhóm đều chạy được và tạo answer/provenance: direct, multi-condition, exception/prohibition, one-hop, multi-hop, parent-child và insufficient corpus.

### 7.2 Cross-reference acceptance — run 05

Run:

`outputs/benchmark_b/hybrid/hybrid_jev_crossref_acceptance_20261031_05`

Tập câu: B026, B030, B034.

| Chỉ số | Kết quả |
|---|---:|
| Expanded evidence recall | 1,0000 |
| Generation context recall | 1,0000 |
| Chain step recall | 0,8889 |
| Reference target recall | 0,9444 |
| Edge label accuracy | 1,0000 |
| Chain step precision | 0,0645 |
| Chain Exact Match | 0,0000 |
| Context evidence `UNRESOLVED` | 0/165 |
| Jev calls | 8 |
| Jev cost | $0,000751884 |
| GPT-4o-mini query cost | $0,003562500 |

B030 đã trả đúng target dẫn chiếu: điểm đ khoản 1 Điều 33, gồm tổ chức tín dụng, tổ chức kinh tế khác và cá nhân. B034 đã truy hồi đúng Điều 43 → Điều 34 → Điều 46 và hai điều kiện tại điểm a, b khoản 1 Điều 46.

Điểm yếu còn lại là context và path noise: 52–57 context evidence/câu trong run 05. Recall cao nhưng precision thấp; vì thế chưa được phép diễn giải `Chain Exact Match = 0` thành lỗi source/type/target. Nó phản ánh output đang chứa nhiều path hợp lệ nhưng dư và path composition chưa khớp đúng tập chain tối thiểu của gold.

## 8. Bảng nghiệm thu 9 yêu cầu

| # | Yêu cầu | Trạng thái | Bằng chứng |
|---:|---|---|---|
| 1 | Jev lỗi có fallback | PASS | Unit test timeout/exception; route ghi `FAILED_FALLBACK_USED`, giữ evidence và conservative fusion. |
| 2 | Mode A không chặn Mode B | PASS | `AUTO_FUSION` luôn gọi Mode A và typed traversal; unit test có Mode A record vẫn thấy reference path. |
| 3 | Path giữ source/type/target | PASS về contract/provenance | Edge label accuracy 1,0; mỗi step có source, relation type, target, direction, hop và provenance. Chain precision còn thấp do path dư. |
| 4 | Render Điều–Khoản–Điểm đúng | PASS | Locator/render test giữ riêng `d` và `đ`; context dùng `[LD2024:...]` và tên căn cứ pháp lý. |
| 5 | Expanded/context đo riêng | PASS | Ba trường article IDs và ba recall metrics riêng. |
| 6 | Context evidence mapped hoặc UNRESOLVED | PASS | Run 04: 124/124 mapped; run 05: 165/165 mapped; contract vẫn cho phép đánh dấu `UNRESOLVED`. |
| 7 | Query, Jev, Judge cost tách riêng | PASS | `cost_separation` có ba ledger; Judge là `null` khi skip. |
| 8 | Không gold leakage | PASS | M10 chỉ nhận question/question_id; source scan và unit test cấm các field gold trong `src/retrieval`. |
| 9 | Pilot vượt qua toàn bộ nhóm | PARTIAL | 10/10 chạy, recall context 1,0 và có provenance; nhưng Chain Exact Match 0 và path precision thấp, nên chưa đạt chuẩn chất lượng cuối để chạy full 50. |

## 9. Việc cần làm trước full benchmark 50 câu

1. Thêm path pruning sau Jev: chỉ giữ minimal connected subgraph giữa anchor chính và evidence được đưa vào context.
2. Không force toàn bộ children của mọi reference target; chỉ force target branch có semantic relevance cao hoặc phù hợp facet hỏi.
3. Tách `retrieval context` và `path metric output`: context có thể chứa evidence bổ trợ, nhưng `reference_paths` chỉ nên xuất chuỗi tối thiểu đã dùng để trả lời.
4. Thay encoder `Qwen/Qwen2.5-0.5B` bằng sentence embedding model phù hợp hoặc giữ lexical-vector fusion như cấu hình chính thức. Không gọi cache hiện tại là BGE-M3 khi metadata thực tế ghi Qwen.
5. Sau khi pruning, chạy development pilot độc lập; không điều chỉnh threshold trực tiếp theo điểm của 50 câu gold.
6. Khi các chỉ số chain ổn định, chạy full 50 với Judge v6 và chốt manifest/hash/config.

## 10. Nguồn kỹ thuật Jev

- OpenRouter Decisions endpoint: `https://openrouter.ai/api/alpha/decisions`.
- Model pin: `typesafe/jev-1.14`.
- OpenRouter model page tại thời điểm triển khai ghi giá $0,042/M input tokens, output $0/M và context 262K.
- Jev chỉ trả typed probabilities; policy và side effects vẫn do code quyết định.

## 11. Cảnh báo vận hành

- Neo4j hiện cảnh báo `db.index.vector.queryNodes` đã deprecated.
- Snapshot không có relationship `HAS_CONSEQUENCE` và property `name`; query vẫn chạy nhờ `OPTIONAL MATCH/coalesce`, nhưng console nhiễu.
- Snapshot không có native `REFERENCE_TO`; provenance hiện là `EXPLICIT_TEXT_REFERENCE`, không được mô tả sai thành cạnh M9 đã lưu.
- Không nên dùng run 01/02 làm số liệu nghiên cứu. Run 01 là run lỗi Cypher; run 02 là baseline trước lexical fusion.
