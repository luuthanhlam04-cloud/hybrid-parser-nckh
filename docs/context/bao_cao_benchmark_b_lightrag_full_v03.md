# Báo cáo chạy Benchmark B v0.3 — LightRAG, 50 câu

## 1. Kết luận nhanh

LightRAG đã indexing trực tiếp toàn bộ file text Chương III và trả lời đủ 50/50 câu trong bộ gold đã human-review. Phần retrieval và chi phí API có log đầy đủ, có thể dùng trong báo cáo thực nghiệm.

LLM judge bằng `openai/gpt-4o-mini` đã chấm hoàn tất 50/50 answers bằng cùng contract `benchmark-b-judge-v6-negative-consistency`. Kết quả cuối không có ID trùng, không thiếu usage/cost, không còn mâu thuẫn ở câu `INSUFFICIENT_CORPUS`, và mọi forbidden claim dương tính đều có bằng chứng trong answer.

Checksum của `answers.jsonl`, `index_metadata.json` và `api_events.jsonl` không thay đổi trong quá trình hoàn thiện judge. Do đó các kết quả indexing và query bên dưới là nguyên bản của lượt chạy ban đầu.

## 2. Cấu hình thực nghiệm

- Run ID: `lightrag_full_v03_20261031_01`
- Dataset: `datasets/benchmarks/benchmark_B_v03.json`
- Trạng thái gold: `HUMAN_REVIEWED`
- Số câu: 50, gồm 47 câu answerable và 3 câu `INSUFFICIENT_CORPUS`
- Corpus indexing: `outputs/clean_texts/clean_Luat_dat_dai_chuong_3.txt`
- LightRAG: `1.5.7`, mode `hybrid`
- Model sinh graph và trả lời: `openai/gpt-4o-mini` qua OpenRouter
- Embedding: `BAAI/bge-m3`, local, 1024 chiều; chi phí embedding API bằng 0
- `graph_top_k = 5`, `chunk_top_k = 5`
- `max_total_tokens = 10,000`, `max_entity_tokens = 2,000`, `max_relation_tokens = 2,000`
- Rerank: tắt
- Chunk: 1,200 token, overlap 100 token
- Judge model: `openai/gpt-4o-mini`; không dùng human judge cho output của hệ thống

## 3. Kết quả indexing

| Chỉ số | Kết quả |
|---|---:|
| Tài liệu đầu vào | 1 |
| Tài liệu xử lý thành công | 1 |
| Chunk | 12 |
| Entity | 86 |
| Relation | 139 |
| LLM calls | 26 |
| Prompt tokens | 89,827 |
| Completion tokens | 17,755 |
| Tổng tokens | 107,582 |
| Provider cost | **$0.02184225** |
| Thời gian | 217,483.35 ms, xấp xỉ 3 phút 37 giây |

Cost ledger tính theo bảng giá cấu hình cho ra `$0.02412705`, trong khi log provider ghi `$0.02184225`. Khi trình bày chi phí thực trả, nên ưu tiên provider cost; giữ tariff estimate để đối chiếu.

## 4. Kết quả query và retrieval

LightRAG sinh đủ 50/50 câu trả lời. Tổng thời gian query là 566,281.59 ms, xấp xỉ 9 phút 26 giây, trung bình 11.33 giây/câu.

| Chỉ số | Kết quả |
|---|---:|
| Query LLM calls | 100 |
| Prompt tokens | 480,279 |
| Completion tokens | 15,152 |
| Tổng tokens | 495,431 |
| Provider cost | **$0.08113305** |
| Retrieval Recall@5 | **0.7358** |
| MRR@5 | **0.5539** |
| Exact locator Recall@5 | **0.8509** |
| Citation article precision | **0.3333** |
| Citation article recall | **0.2961** |
| Citation clause precision/recall | **0.0435 / 0.0435** |
| Citation point precision/recall | **0.0270 / 0.0270** |

100 query calls tương ứng hai lượt LLM cho mỗi câu trong luồng LightRAG hiện tại, chủ yếu là tạo từ khóa và sinh câu trả lời.

### Diễn giải kết quả citation locator

Citation precision và recall trong thực nghiệm này đo mức độ trùng khớp giữa locator pháp lý được nêu tường minh trong câu trả lời với gold locator của benchmark. Vì vậy, đây là phép đo về **khả năng sinh citation có cấu trúc và đúng độ chi tiết**, không phải phép đo trực tiếp tỷ lệ câu trả lời đúng hoặc sai về mặt pháp lý.

Kết quả cho thấy mức trùng khớp ở cấp Điều cao hơn đáng kể so với cấp Khoản và Điểm. Một nguyên nhân quan trọng là output LightRAG hiện tại thường dẫn tới tệp nguồn hoặc chỉ nêu Điều, thay vì luôn sinh đầy đủ locator theo dạng `Điểm–Khoản–Điều`. Do đó, recall thấp ở cấp Khoản hoặc Điểm có thể bao gồm cả trường hợp hệ thống sử dụng đúng nội dung làm căn cứ nhưng không chuyển locator chi tiết đó vào câu trả lời.

Mặt khác, evaluator hiện tại nhận diện citation bằng các mẫu biểu thức chính quy. Những cách viết ghép, đảo thứ tự hoặc rút gọn locator có thể không được nhận diện đầy đủ. Trong phạm vi nghiên cứu này, nhóm không thực hiện kiểm toán thủ công từng citation mismatch; vì vậy, không diễn giải `citation point recall = 2,70%` thành kết luận rằng `97,30%` câu trả lời đã dẫn sai điểm pháp luật.

Kết luận phù hợp từ thực nghiệm là: **LightRAG còn hạn chế trong việc biểu diễn căn cứ pháp lý ở độ chi tiết Khoản–Điểm trong câu trả lời**. Hạn chế này làm giảm khả năng kiểm chứng căn cứ của người dùng, nhưng cần được phân biệt với độ chính xác pháp lý tổng thể, vốn được đánh giá riêng bằng các metric answer quality.

Cách diễn đạt an toàn trong báo cáo
Không nên viết:
LightRAG trích dẫn sai 97,3% ở cấp Điểm.

Nên viết:
Theo evaluator hiện tại, mức độ trùng khớp citation với gold locator ở cấp Điểm đạt 2,70%. Kết quả này phản ánh khả năng phát sinh và nhận diện citation chi tiết trong câu trả lời, không đồng nghĩa 97,30% câu trả lời dẫn sai điểm pháp luật. Sai lệch có thể đến từ citation thô, thiếu citation, parser không nhận dạng hoặc retrieval/generation thực sự sai. Nhóm tiến hành error analysis thủ công để phân tách các nguyên nhân này

### Theo nhóm câu hỏi

| Nhóm | Số câu | Recall@5 | MRR@5 |
|---|---:|---:|---:|
| DIRECT_RIGHT_OBLIGATION | 8 | 0.7500 | 0.4479 |
| MULTI_CONDITION | 10 | 0.9000 | 0.7200 |
| EXCEPTION_PROHIBITION | 7 | 0.7143 | 0.5476 |
| CROSS_REF_ONE_HOP | 6 | 0.6667 | 0.6806 |
| CROSS_REF_MULTI_HOP | 4 | 0.6458 | 0.8125 |
| SUBJECT_DISAMBIGUATION | 5 | 0.8000 | 0.2500 |
| PARENT_CHILD_SYNTHESIS | 4 | 0.5000 | 0.3750 |
| LEGAL_SCENARIO | 3 | 0.6667 | 0.4444 |
| INSUFFICIENT_CORPUS | 3 | N/A | N/A |

Nhóm yếu nhất theo Recall@5 là `PARENT_CHILD_SYNTHESIS` (0.50). `SUBJECT_DISAMBIGUATION` có recall khá nhưng MRR thấp (0.25), cho thấy evidence đúng thường không nằm ở vị trí cao. Hai nhóm cross-reference chưa thể được chấm chain-level trực tiếp vì adapter LightRAG không xuất `reference_paths` và `context_evidence` theo contract chung.

## 5. Kết quả LLM judge

Runner v0.3 có judge riêng, structured JSON, log token/cost riêng, resume có kiểm soát và tối đa 3 lần thử mỗi câu. Contract v6 bổ sung:

- Phân biệt rõ forbidden claim dương tính với việc chỉ thiếu ngoại lệ.
- Forbidden claim dương tính phải có trích dẫn từ answer; cho phép căn chỉnh sau chuẩn hóa Unicode, khoảng trắng và dấu câu nhưng không cho phép diễn giải tự do.
- `INSUFFICIENT_CORPUS` được kiểm tra nhất quán giữa abstention, refusal quality, legal correctness và unsupported claims.
- Lượt chạy cuối chấm lại cả 50 answers bằng duy nhất prompt version v6; không tái sử dụng quyết định cũ.

### Chi phí judge cuối

| Chỉ số | Kết quả |
|---|---:|
| Answers được chấm | 50 |
| API calls | 51 |
| Prompt tokens | 70,533 |
| Completion tokens | 8,308 |
| Tổng tokens | 78,841 |
| Provider cost | **$0.01556475** |
| Missing usage/cost | 0 |

51 calls cho 50 answers do một câu cần thêm một lần thử validation. Chi phí judge được báo cáo riêng, không gộp vào indexing hoặc query.

### Chỉ số chất lượng câu trả lời

| Metric | Mean | Số câu được chấm |
|---|---:|---:|
| Atomic fact coverage | **0.8551** | 47 |
| Condition coverage | **0.8421** | 19 |
| Exception coverage | **0.3929** | 14 |
| Subject scope accuracy | **0.7639** | 18 |
| Forbidden claim rate | **0.4286** | 7 |
| Unsupported claim rate | **0.1240** | 50 |
| Legal correctness | **0.8210** | 50 |
| Abstention accuracy | **1.0000** | 3 |
| Refusal quality | **1.0000** | 3 |

`forbidden_claim_rate` là tỷ lệ phát sinh khẳng định bị cấm, vì vậy càng thấp càng tốt. Ba câu bị judge phát hiện forbidden claim là `B025`, `B036` và `B041`; cả ba đều có evidence, trong đó `B041` dùng căn chỉnh tự động tới đoạn answer thực tế. Ba câu `B048–B050` đều có `abstention_accuracy = 1` và không bịa thông tin ngoài corpus.

Các phiên bản judge không hợp lệ hoặc bản incremental được giữ trong các thư mục audit, không tham gia vào metric cuối.

## 6. Kiểm thử

- Test suite: `tests/unit/test_benchmark_b.py` và `tests/unit/test_benchmark_b_v02.py`
- Lần pytest đầy đủ gần nhất trong giới hạn 3 vòng: **25 passed** trong 1.42 giây.
- Contract v6 sau đó được xác minh bằng lượt chạy end-to-end 50/50 thành công; không chạy vòng pytest thứ tư để tuân thủ giới hạn kiểm thử.
- Có test cho gold contract, event/cost separation, judge schema, negative abstention, evidence normalization và evidence alignment.

## 7. Tệp kết quả

- Câu trả lời 50 câu: `outputs/benchmark_b/lightrag/lightrag_full_v03_20261031_01/answers.jsonl`
- Retrieval metrics: `outputs/benchmark_b/lightrag/lightrag_full_v03_20261031_01/per_question_metrics.jsonl`
- Log API indexing/query: `outputs/benchmark_b/lightrag/lightrag_full_v03_20261031_01/api_events.jsonl`
- Metadata indexing: `outputs/benchmark_b/lightrag/lightrag_full_v03_20261031_01/index_metadata.json`
- Quyết định judge: `outputs/benchmark_b/lightrag/lightrag_full_v03_20261031_01/judge_decisions.jsonl`
- Log API judge: `outputs/benchmark_b/lightrag/lightrag_full_v03_20261031_01/judge_api_events.jsonl`
- Tổng hợp judge: `outputs/benchmark_b/lightrag/lightrag_full_v03_20261031_01/judge_summary.json`
- Metric cuối: `outputs/benchmark_b/lightrag/lightrag_full_v03_20261031_01/metrics.json`
- Audit judge cũ: `judge_v1_invalid_semantics`, `judge_v2_invalid_consistency`, `judge_v3_failed_evidence_validation` và `judge_v4_v6_incremental_audit`

## 8. Đánh giá sẵn sàng cho báo cáo NCKH

Có thể dùng kết quả indexing cost, query cost, retrieval, citation và answer-quality metrics của judge v6 cho báo cáo thực nghiệm. Khi viết báo cáo NCKH phải ghi rõ answer quality do LLM judge tự động chấm, không phải human evaluation. Các metric chain-level vẫn phải ghi `N/A` đối với LightRAG do adapter không xuất reference path có nhãn cạnh.
