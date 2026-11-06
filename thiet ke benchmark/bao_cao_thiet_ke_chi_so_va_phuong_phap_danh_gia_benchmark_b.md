# Báo cáo thiết kế hệ thống chỉ số và phương pháp đánh giá Benchmark B

## 1. Mục tiêu đánh giá

Benchmark B đánh giá hai hệ thống hỏi–đáp pháp luật trên Chương III Luật Đất đai 2024:

- LightRAG, xây dựng graph index từ clean text;
- Hybrid Parser/UKG, truy hồi trên đồ thị pháp lý đã phân cấp và hợp nhất.

Mục tiêu không chỉ là kiểm tra hệ thống có tìm thấy đúng Điều luật hay không, mà còn tách bốn năng lực:

1. truy hồi đúng căn cứ;
2. bảo toàn cấu trúc Điều–Khoản–Điểm;
3. theo được chuỗi dẫn chiếu chéo;
4. sinh câu trả lời đủ sự kiện, điều kiện, ngoại lệ và đúng phạm vi chủ thể.

Ba câu `INSUFFICIENT_CORPUS` được đánh giá theo khả năng nhận biết thiếu căn cứ, không chấm như câu hỏi có đầy đủ gold evidence.

## 2. Nguyên tắc chấm điểm

### 2.1. Đơn vị đánh giá

Benchmark sử dụng ba đơn vị locator:

```text
Điều       LD2024:A46
Khoản      LD2024:A46:K1
Điểm       LD2024:A46:K1:Da
```

Đơn vị retrieval cấp Điều là `article_id` dạng `31/2024/qh15#46`. Đơn vị evidence chi tiết là canonical locator. Vì LightRAG và Hybrid có representation nội bộ khác nhau, hai hệ thống được chuẩn hóa về locator trước khi tính metric.

### 2.2. Quy tắc mẫu số

Mỗi metric được ghi cùng:

- `value`: giá trị trung bình trên các câu đủ điều kiện;
- `n_eligible`: số câu metric có ý nghĩa;
- `n_scored`: số câu thực sự có output quan sát được;
- `n_not_measured`: không đo được do hệ thống không xuất đủ dữ liệu;
- `n_not_applicable`: không áp dụng theo loại câu hỏi.

`N/A` không được đổi thành 0. Ví dụ, LightRAG chưa xuất `reference_paths` theo contract chung thì Chain Exact Match của LightRAG phải là `N/A`, không phải 0.

## 3. Thiết kế chỉ số truy hồi

### 3.1. Recall@5

Với mỗi câu có tập gold article (G_q) và danh sách Điều được hệ thống trả về (R_q):

```text
Recall@5(q) = |Gq ∩ top5(Rq)| / |Gq|
```

Trong đó:

- (G_q) là `relevant_articles` của câu hỏi;
- (R_q) là thứ tự các article ID do adapter hệ thống xuất;
- chỉ tối đa 5 kết quả đầu được tính.

Metric này đo khả năng tìm đúng phạm vi Điều luật, chưa chứng minh hệ thống tìm đúng Khoản hoặc Điểm.

### 3.2. MRR@5

```text
RR@5(q) = 1 / rank(first relevant article)
```

Nếu không có Điều đúng trong top 5, `RR@5 = 0`. MRR là trung bình RR trên tập câu đủ điều kiện.

### 3.3. Các lớp truy hồi của Hybrid

Hybrid được tách thành ba lớp để không nhầm lẫn giữa “đã tìm thấy” và “đã đưa vào prompt”:

- `anchor_recall_at_5`: recall của các node/article mỏ neo ban đầu;
- `expanded_evidence_recall`: recall sau khi mở rộng evidence;
- `generation_context_recall`: recall của evidence thực sự được đưa vào context sinh câu trả lời.

LightRAG chỉ được chấm các lớp mà adapter có thể quan sát được. Nếu phiên bản SDK không trả chunks/context đủ để align, kết quả là `not_measured`.

## 4. Chỉ số cấu trúc pháp luật

### 4.1. Exact Locator Recall@5

Với `acceptable_evidence_sets`, hệ thống được phép có nhiều tập evidence hợp lệ. Tính recall locator trên từng tập và lấy tập có kết quả tốt nhất:

```text
ExactLocatorRecall@5(q) = max_s |gold_s ∩ found_top5| / |gold_s|
```

Đây là metric ở cấp Điều–Khoản–Điểm, nghiêm ngặt hơn Recall@5 cấp Điều.

### 4.2. Parent Context Coverage

Đo tỷ lệ locator cha bắt buộc có trong evidence/context:

```text
ParentCoverage(q) = |required_parents ∩ context_locators| / |required_parents|
```

Ví dụ, nếu câu hỏi cần khoản 1 làm ngữ cảnh cho điểm a, hệ thống phải truy hồi khoản 1 hoặc một evidence được đánh dấu ancestor hợp lệ.

### 4.3. Child Evidence Coverage

Đo tỷ lệ điểm con bắt buộc được thu thập:

```text
ChildCoverage(q) = |required_children ∩ context_locators| / |required_children|
```

Metric này quan trọng với câu hỏi yêu cầu liệt kê các điểm a, b, c hoặc điều kiện nằm dưới một khoản.

### 4.4. Hierarchical Context Completeness

Đây là metric tổng hợp đề xuất dùng trong báo cáo, không thay thế hai metric thành phần:

```text
HCC(q) = mean(ParentCoverage(q), ChildCoverage(q))
```

Nếu câu hỏi không yêu cầu parent hoặc child, thành phần không áp dụng phải loại khỏi mẫu số. Trong output hiện tại, `hierarchy_parent_context` và `hierarchy_child_evidence` là hai trường được evaluator ghi trực tiếp; HCC có thể tính ở bước tổng hợp từ hai trường này.

## 5. Chỉ số dẫn chiếu chéo

Các metric chain chỉ áp dụng cho 18 câu có `accepted_chain_sets`. Không áp dụng cho câu không chứa dẫn chiếu hoặc câu insufficient-corpus.

### 5.1. Reference-target Recall

Gọi (T_g) là tập target locator trong chain gold và (T_p) là tập target locator do hệ thống xuất:

```text
ReferenceTargetRecall = |Tg ∩ Tp| / |Tg|
```

Metric này chỉ kiểm tra tìm đúng node đích; chưa kiểm tra thứ tự và nhãn cạnh.

### 5.2. Chain-step Precision, Recall và F1

Một chain step là bộ ba có thứ tự:

```text
(source, relation_type, target)
```

Với (E_g) là tập bước gold và (E_p) là tập bước dự đoán:

```text
Precision = |Eg ∩ Ep| / |Ep|
Recall    = |Eg ∩ Ep| / |Eg|
F1        = 2PR / (P + R)
```

Các bước hierarchy có nhãn `PARENT_CHILD_CONTEXT`; các bước dẫn chiếu pháp lý có thể mang `DIRECT_REFERENCE`, `REQUIRES_CONDITION_FROM`, `EXCEPTION_REFERENCE` hoặc `INHERITS_RIGHTS_OBLIGATIONS`.

### 5.3. Edge-label Accuracy

Đo tỷ lệ nhãn quan hệ chính xác trên các cặp source–target mà gold yêu cầu. Chỉ đúng locator nhưng sai loại cạnh không được tính là đúng hoàn toàn.

Ví dụ, `PARENT_CHILD_CONTEXT` không tương đương với `REQUIRES_CONDITION_FROM`; một cạnh phân cấp được dùng để render context không tự động là một bước dẫn chiếu pháp lý.

### 5.4. Chain Exact Match

Chain Exact Match bằng 1 khi tập `answer_paths` của hệ thống khớp đầy đủ một accepted chain set:

- đủ mọi path bắt buộc;
- đúng thứ tự các step;
- đúng source, target và relation type;
- không có path/step thừa ngoài accepted set.

Đây là metric nghiêm ngặt nhất. Hệ thống có thể có evidence recall cao nhưng Chain Exact Match bằng 0 nếu làm mất thứ tự, sai nhãn cạnh hoặc đưa quá nhiều path cạnh tranh.

## 6. Chỉ số chất lượng câu trả lời pháp lý

### 6.1. Atomic Fact Coverage

Mỗi câu có một tập atomic fact đã annotation. Judge chấm từng fact:

- `1`: nêu đúng và đủ;
- `0.5`: đúng nhưng thiếu phần quan trọng;
- `0`: thiếu hoặc sai.

```text
AtomicFactCoverage(q) = mean(fact_decisions)
```

### 6.2. Condition Coverage

Tính trung bình các atomic fact có role `REQUIRED_CONDITION`. Không được coi câu trả lời chỉ nêu “theo Điều 46” là đạt nếu gold yêu cầu liệt kê các điều kiện cụ thể.

### 6.3. Exception Coverage

Đo tỷ lệ ngoại lệ bắt buộc được nêu đúng. Câu trả lời có kết luận đúng nhưng bỏ ngoại lệ quan trọng chỉ được điểm một phần hoặc bị giảm exception coverage.

### 6.4. Subject-Scope Accuracy

Đo việc câu trả lời gắn đúng quyền/nghĩa vụ với chủ thể và chế độ pháp lý tương ứng. Đây là metric quan trọng để phát hiện nhầm giữa:

- cá nhân và tổ chức kinh tế;
- người gốc Việt Nam định cư ở nước ngoài và tổ chức có vốn đầu tư nước ngoài;
- người bán, người mua và người thuê lại;
- thuê đất trả tiền hằng năm và trả tiền một lần.

### 6.5. Citation Precision/Recall

Citation parser trích locator từ chính câu trả lời người dùng nhìn thấy, sau đó so với locator gold:

```text
CitationPrecision = |predicted ∩ gold| / |predicted|
CitationRecall    = |predicted ∩ gold| / |gold|
```

Tính riêng ở ba mức Điều, Khoản và Điểm. Đây là độ chính xác của citation được sinh/parse, không phải trực tiếp là legal correctness. Một câu có nội dung đúng nhưng chỉ trích dẫn ở cấp Điều có thể có recall cấp Điểm thấp.

## 7. Chỉ số an toàn

### 7.1. Abstention Accuracy

Chỉ áp dụng cho câu `INSUFFICIENT_CORPUS`. Đạt 1 khi hệ thống nhận biết thiếu căn cứ trong corpus và không bịa thêm điều kiện, số liệu hoặc quy định ngoài dữ liệu.

### 7.2. Refusal Quality

Được judge chấm từ 0 đến 1:

- 1: từ chối rõ, nêu giới hạn corpus và không bịa;
- 0.5: nhận biết thiếu căn cứ nhưng giải thích chưa đầy đủ;
- 0: không từ chối hoặc bịa nội dung.

### 7.3. Unsupported-Claim Rate

Tỷ lệ các khẳng định pháp lý đáng kể trong câu trả lời không được gold rubric hỗ trợ. Giá trị càng thấp càng tốt.

### 7.4. Forbidden-Claim Rate

Trong implementation, đây là tỷ lệ forbidden claim xuất hiện trong câu trả lời, không phải tỷ lệ tuân thủ. Judge chỉ đánh dấu `is_present=true` khi câu trả lời thực sự khẳng định toàn bộ nội dung bị cấm. Khi claim không xuất hiện, evidence bắt buộc là `null`.

## 8. Kiến trúc LLM-as-a-Judge

Judge được chạy sau retrieval và generation, độc lập với quá trình chọn evidence:

```text
Gold v0.3 rubric + system answer
            ↓
      LLM Judge
            ↓
JSON judgment theo schema
            ↓
validation + normalization
            ↓
per_question_metrics.jsonl + metrics.json
```

Judge nhận:

- question ID và câu hỏi;
- `answerability`;
- `reference_answer`;
- atomic facts;
- required exceptions;
- forbidden claims;
- câu trả lời thực tế của hệ thống.

Judge không nhận output chain/evidence để tự thay thế deterministic structural evaluator. Chain metrics và citation locator được tính từ output/evidence theo evaluator riêng.

## 9. Cấu trúc prompt và JSON schema

### 9.1. Nguyên tắc prompt

System prompt yêu cầu Judge:

1. chỉ dùng gold rubric được cung cấp;
2. chấm nội dung, không chấm văn phong;
3. chấm atomic fact/exception theo thang 0, 0.5, 1;
4. chỉ đánh dấu forbidden claim khi câu trả lời thực sự khẳng định claim đó;
5. với forbidden claim xuất hiện, cung cấp đoạn quote liên tục từ câu trả lời;
6. tách rõ câu trả lời thiếu sót với câu trả lời sai;
7. xử lý riêng `INSUFFICIENT_CORPUS`;
8. trả đúng JSON, không markdown.

### 9.2. Schema output

Schema strict yêu cầu:

```json
{
  "question_id": "Bxxx",
  "fact_decisions": {"fact_id": 0.0},
  "exception_decisions": {"exception_id": 0.5},
  "forbidden_claim_checks": {
    "claim_id": {"is_present": false, "evidence": null}
  },
  "unsupported_claim_rate": 0.0,
  "legal_correctness": 0.0,
  "correctly_abstained": null,
  "refusal_quality": null,
  "rationale": "..."
}
```

Với câu insufficient-corpus, `correctly_abstained` là boolean và `refusal_quality` là số; với câu answerable, hai trường này là `null`.

## 10. Validation kết quả Judge

Sau mỗi lần gọi, hệ thống kiểm tra:

- `question_id` đúng câu;
- đủ và đúng toàn bộ key fact/exception/forbidden claim;
- fact và exception chỉ thuộc `{0, 0.5, 1}`;
- tỷ lệ unsupported/legal correctness nằm trong `[0,1]`;
- forbidden evidence là quote align được với answer;
- claim không xuất hiện phải có evidence `null`;
- câu insufficient-corpus phải có kiểu abstention phù hợp;
- quyết định không bị trùng hoặc lệch thứ tự câu.

Mỗi câu được retry tối đa 3 lần khi API/schema validation thất bại. Sau lần thứ ba, pipeline dừng với lỗi rõ ràng; không tự tạo judgment thay thế.

Judge decisions được lưu tại:

```text
judge_decisions.jsonl
judge_summary.json
judge_api_events.jsonl
```

Event log ghi model, phase, token usage, latency, attempt và provider cost. Query cost, Jev cost và Judge cost được lưu trong các ledger riêng.

## 11. Đối chiếu atomic facts và forbidden claims

Quy trình chấm một câu:

```text
Answer
  ├── fact_decisions      → Atomic Fact Coverage
  ├── exception_decisions → Exception Coverage
  ├── forbidden checks    → Forbidden-Claim Rate
  ├── unsupported rate    → Unsupported-Claim Rate
  └── legal correctness   → đánh giá tổng thể
```

Fact coverage và exception coverage dùng trung bình các quyết định thành phần. Forbidden claim không được suy ra chỉ từ việc câu trả lời thiếu ngoại lệ; phải có khẳng định sai thực sự trong answer. Điều này hạn chế việc phạt nhầm câu trả lời hẹp nhưng không sai.

## 12. Kiểm chứng độ tin cậy

### 12.1. Kiểm chứng tự động

Trước khi chấp nhận `metrics.json`:

- kiểm tra đúng 50 câu và ID duy nhất;
- kiểm tra dataset là `HUMAN_REVIEWED`;
- kiểm tra locator map khớp physical graph SHA-256;
- kiểm tra mỗi câu có đúng một answer;
- kiểm tra context evidence có `EXACT` hoặc `UNRESOLVED`;
- kiểm tra không có gold field được truyền vào M10/LightRAG runtime;
- kiểm tra các metric có mẫu số hợp lệ;
- kiểm tra Judge decision khớp question order.

### 12.2. Kiểm chứng thủ công

Nên chọn mẫu phân tầng để audit:

- ít nhất một câu trong mỗi `benchmark_b_category`;
- tất cả câu `CROSS_REF_MULTI_HOP`;
- câu có Chain Exact = 0 nhưng evidence recall cao;
- câu citation mismatch cấp Khoản/Điểm;
- toàn bộ câu `INSUFFICIENT_CORPUS`;
- các câu có forbidden claim hoặc ngoại lệ quan trọng.

Mỗi case audit cần lưu:

1. câu hỏi;
2. answer người dùng nhìn thấy;
3. evidence/context thực tế;
4. gold locator và chain;
5. Judge decision;
6. phán quyết reviewer;
7. loại lỗi: retrieval, alignment, path reconstruction, generation hoặc evaluator.

## 13. Kiểm định và phân tích thống kê

### 13.1. So sánh theo cặp câu hỏi

Vì hai hệ thống trả lời cùng 50 câu, phân tích chính phải dùng paired comparison theo `question_id`, không coi hai hệ thống là hai mẫu độc lập.

Với mỗi metric:

```text
delta_q = score_hybrid(q) - score_lightrag(q)
```

Báo cáo:

- mean và median của delta;
- tỷ lệ câu Hybrid thắng/hòa/thua;
- 95% confidence interval;
- số câu eligible thực tế.

### 13.2. Khoảng tin cậy

Khuyến nghị:

- metric nhị phân như abstention/exact match: Wilson hoặc bootstrap theo câu;
- metric continuous như fact coverage/F1: paired bootstrap 10.000 lần trên question IDs đủ điều kiện;
- metric chain chỉ bootstrap trên 18 câu có gold chain, không kéo các câu N/A vào mẫu số.

### 13.3. Kiểm định giả thuyết

Với các điểm theo câu không phân phối chuẩn, dùng Wilcoxon signed-rank trên delta. Với kết quả thắng/thua nhị phân, có thể dùng McNemar cho các câu cùng điều kiện. Khi kiểm tra nhiều metric đồng thời, dùng hiệu chỉnh Holm hoặc nêu rõ đây là phân tích thăm dò.

Không nên chỉ báo cáo p-value. Cần kèm effect size, confidence interval và phân tích theo category vì 50 câu là kích thước mẫu nhỏ.

### 13.4. Phân tích lỗi

Báo cáo nên phân rã theo:

- direct right/obligation;
- multi-condition;
- one-hop và multi-hop cross-reference;
- parent-child synthesis;
- subject disambiguation;
- exception/prohibition;
- insufficient corpus.

Phân rã này giúp xác định Hybrid tốt hơn ở đâu, thay vì dùng một điểm trung bình để kết luận chung.

## 14. Giới hạn độc lập của LLM Judge

Trong thí nghiệm hiện tại, generator và Judge đều có thể dùng `openai/gpt-4o-mini`. Điều này **không bảo đảm tính độc lập tuyệt đối** vì:

- cùng họ model có thể chia sẻ thiên kiến diễn giải;
- Judge có thể ưu ái cách diễn đạt tương tự output do chính model tạo;
- rubric/reference answer vẫn do nhóm nghiên cứu thiết kế;
- Judge không thay thế human legal review.

Do đó, kết quả Judge phải được gọi là `LLM-judged legal correctness`, không phải ground truth pháp lý tuyệt đối.

Biện pháp giảm rủi ro:

1. Giữ deterministic retrieval/structure/citation evaluator độc lập với Judge.
2. Không cho Judge xem system provenance nếu metric cần đánh giá chính answer người dùng nhìn thấy.
3. Audit thủ công một mẫu phân tầng các câu Judge đã chấm.
4. Nếu tài nguyên cho phép, dùng model Judge khác generator hoặc chạy second-judge trên mẫu kiểm tra.
5. Báo cáo Judge model, prompt version, schema version và chi phí.

## 15. Cấu trúc báo cáo kết quả đề xuất

Mỗi bảng kết quả nên có dạng:

| Metric | LightRAG | Hybrid Parser | Hybrid–LightRAG | 95% CI | N scored | N/A | Ghi chú |
|---|---:|---:|---:|---:|---:|---:|---|

Các bảng chính:

1. Recall@5/MRR@5 cấp Điều;
2. exact locator và hierarchical coverage;
3. cross-reference metrics trên 18 câu eligible;
4. answer quality từ Judge/human audit;
5. safety metrics trên toàn bộ câu hoặc tập insufficient-corpus tương ứng;
6. latency/token/cost với index và query tách riêng;
7. breakdown theo category;
8. bảng lỗi đại diện có evidence và provenance.

## 16. Kết luận phương pháp

Thiết kế Benchmark B không dùng một metric duy nhất để đại diện cho “hệ thống hiểu luật”. Recall@5 chỉ phản ánh tìm được phạm vi Điều; exact locator và hierarchy metrics phản ánh cấu trúc; chain metrics phản ánh đường dẫn dẫn chiếu; atomic facts, exceptions và subject scope phản ánh nội dung câu trả lời; safety metrics phản ánh hành vi khi thiếu căn cứ.

LLM-as-a-Judge được dùng để chấm những thuộc tính khó tính bằng rule, nhưng phải bị giới hạn bởi gold rubric, JSON schema, validation, retry policy và manual audit. Đặc biệt, việc generator và Judge dùng cùng model làm giảm tính độc lập, vì vậy mọi kết luận về legal correctness cần được trình bày như kết quả có kiểm chứng, không phải chân lý pháp lý tuyệt đối.
