# Báo cáo Benchmark B — Hybrid Parser/UKG Full 50 câu

Ngày chạy: 31/10/2026  
Nhánh: `benmark_b`  
Run ID: `hybrid_full_v04_20261031`  
Hệ thống: Hybrid Parser/UKG, M10 `AUTO_FUSION`  
Dataset: `datasets/benchmarks/benchmark_B_v03.json` (`HUMAN_REVIEWED`)  
Answer model và Judge model: `openai/gpt-4o-mini`

## 1. Phạm vi và tính tái lập

Run dùng fixed gold v0.3 gồm 50 câu hỏi, `top_k=5`, chế độ `AUTO_FUSION`, M5 embedding local và UKG M1–M9 đã có sẵn. Không chạy lại indexing M1–M9 trong benchmark này.

File kết quả chính:

- `outputs/benchmark_b/hybrid/hybrid_full_v04_20261031/answers.jsonl`: 50 answer.
- `outputs/benchmark_b/hybrid/hybrid_full_v04_20261031/judge_decisions.jsonl`: 50 quyết định Judge.
- `outputs/benchmark_b/hybrid/hybrid_full_v04_20261031/metrics.json`: báo cáo tổng hợp.
- `outputs/benchmark_b/hybrid/hybrid_full_v04_20261031/structural_metrics.jsonl`: metric cấu trúc theo từng câu.

Kiểm tra hoàn tất:

| Điều kiện | Kết quả |
|---|---:|
| Answer sinh thành công | 50/50 |
| Judge decision hợp lệ | 50/50 |
| Dataset trạng thái `HUMAN_REVIEWED` | Có |
| Context evidence `UNRESOLVED` | 0 |
| Gold truyền vào runtime M10 | Không |

## 2. Kết quả retrieval và evidence

| Metric | Giá trị |
|---|---:|
| Retrieval Recall@5 | 0,9184 |
| Retrieval MRR@5 | 0,8848 |
| Anchor Recall@5 | 0,9184 |
| Expanded evidence recall | 0,9770 |
| Generation-context recall | 0,9557 |
| Citation article overlap | 0,9078 |
| Context evidence items | 382 |
| Context evidence trung bình/câu | 7,64 |

Theo loại câu, retrieval recall@5 đạt 1,0 ở `DIRECT_RIGHT_OBLIGATION`, `EXCEPTION_PROHIBITION`, `PARENT_CHILD_SYNTHESIS` và `LEGAL_SCENARIO`. Hai nhóm cần chú ý là:

- `CROSS_REF_ONE_HOP`: 0,7500.
- `CROSS_REF_MULTI_HOP`: 0,7917.
- `SUBJECT_DISAMBIGUATION`: 0,8000.

## 3. Kết quả Judge và chất lượng trả lời

Judge dùng `openai/gpt-4o-mini`, prompt `benchmark-b-judge-v6-negative-consistency`, không dùng human review trong run này.

| Metric Judge | Giá trị | Số câu đủ điều kiện |
|---|---:|---:|
| Legal correctness | 0,8777 | 50 |
| Atomic fact coverage | 0,8686 | 47 |
| Unsupported claim rate | 0,0807 | 50 |
| Condition coverage | 0,7066 | 19 |
| Exception coverage | 0,6786 | 14 |
| Subject-scope accuracy | 0,8889 | 18 |
| Abstention accuracy | 1,0000 | 3 |
| Refusal quality | 1,0000 | 3 |
| Forbidden claim rate | 0,4286 | 7 |

`Forbidden claim rate` chỉ áp dụng cho 7 câu có annotation forbidden claim. Đây là chỉ số cần được nêu cùng tập áp dụng, không được diễn giải thành tỷ lệ lỗi trên toàn bộ 50 câu. Nó là hạng mục nên ưu tiên kiểm tra thủ công nếu dùng kết quả cho kết luận pháp lý mạnh.

## 4. Citation, hierarchy và cross-reference

| Metric | Giá trị | Số câu đủ điều kiện |
|---|---:|---:|
| Citation precision — Điều | 0,8369 | 47 |
| Citation recall — Điều | 0,9078 | 47 |
| Citation precision — Khoản | 0,7757 | 46 |
| Citation recall — Khoản | 0,8170 | 46 |
| Citation precision — Điểm | 0,6797 | 37 |
| Citation recall — Điểm | 0,6374 | 37 |
| Hierarchy parent context | 0,8984 | 32 |
| Hierarchy child evidence | 0,7360 | 37 |
| Chain-step precision | 0,3241 | 18 |
| Chain-step recall | 0,5080 | 18 |
| Chain-step F1 | 0,3499 | 18 |
| Reference-target recall | 0,5867 | 18 |
| Edge-label accuracy | 0,7222 | 18 |
| Chain Exact Match | 0,0000 | 18 |

Kết quả cho thấy evidence và citation ở cấp Điều/Khoản tương đối tốt, trong khi path dẫn chiếu chéo vẫn là giới hạn chính. `Chain Exact Match = 0` không nên được diễn giải rằng hệ thống luôn tìm sai nội dung: expanded/context evidence recall cao cho thấy nhiều căn cứ cần thiết đã vào context. Tuy nhiên, cơ chế hiện tại chưa tái dựng được chuỗi dẫn chiếu hoàn chỉnh theo contract gold, đặc biệt khi chain xen kẽ explicit reference và bước Điều–Khoản–Điểm.

Vì vậy, kết quả full run này có thể dùng để báo cáo retrieval, evidence coverage, answer quality và citation theo cấp pháp lý; chỉ số cross-reference chain cần được báo cáo như một hạn chế hiện hữu, không dùng để khẳng định hệ thống đã giải quyết hoàn chỉnh truy hồi chuỗi dẫn chiếu.

## 5. Chi phí API của full run

| Pha | Calls | Input tokens | Output tokens | Chi phí quan sát (USD) |
|---|---:|---:|---:|---:|
| Query answer GPT-4o-mini | 50 | 75.348 | 12.139 | 0,018586 |
| Jev routing/gating | 137 | 311.466 | 40.492 | 0,013082 |
| LLM Judge GPT-4o-mini — toàn bộ attempt | 53 | 72.866 | 8.564 | 0,015780 |
| Tổng Query + Jev + Judge | 240 | 459.680 | 61.195 | **0,047447** |

M5 embedding chạy local nên được ghi nhận là chi phí API bằng 0. Bảng này không cộng historical indexing cost của M6 hoặc chi phí local compute/Neo4j.

## 6. Sự cố Judge và cách phục hồi

Lần chạy đầu đã sinh đủ 50 answer nhưng dừng tại Judge câu `B010`: model trả giá trị không-null cho `correctly_abstained` dù câu hỏi là answerable. Runner đã retry ba lần và dừng theo cơ chế chống lặp vô hạn.

Đã bổ sung chuẩn hóa an toàn tại Judge: ở câu không thuộc `INSUFFICIENT_CORPUS`, hai trường không áp dụng `correctly_abstained` và `refusal_quality` được ép về `null` trước validation. Việc này không thay đổi answer, `fact_decisions`, `exception_decisions`, `legal_correctness` hoặc forbidden-claim decisions.

Judge sau đó được resume trên chính `answers.jsonl`:

- Reuse 9 quyết định đã hợp lệ.
- Gọi mới 41 câu chưa có quyết định.
- Ledger tổng cộng 53 Judge attempt, bao gồm ba retry schema không hợp lệ từ lần đầu.
- Không chạy lại M10, Jev hoặc sinh lại answer.

## 7. Kết luận

Full benchmark 50 câu đã hoàn tất với đầy đủ answer, Judge decision, metric cấu trúc và cost ledger. Hybrid Parser/UKG cho kết quả tốt về retrieval, evidence coverage, citation Điều/Khoản và legal correctness do Judge chấm.

Hạn chế chính còn lại là cross-reference path reconstruction: chain precision/recall còn thấp và Chain Exact Match bằng 0 trên 18 câu có chain metric. Đây là giới hạn đã biết của phiên bản `AUTO_FUSION` hiện tại, cần được nêu rõ nếu dùng số liệu trong báo cáo nghiên cứu.

Để cải thiện riêng hạng mục này, hướng tiếp theo là `answer-path construction`: chấm complete path thay vì edge rời rạc, nối explicit reference với hierarchy step liên quan và đánh giá trên `answer_paths` đã chuẩn hóa.
