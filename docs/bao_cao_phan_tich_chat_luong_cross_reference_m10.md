# Báo cáo phân tích chất lượng Cross-Reference của M10

Ngày: 31/10/2026  
Nhánh: `benmark_b`  
Phạm vi: M10 Hybrid Parser/UKG với `AUTO_FUSION`, Jev routing và hai tầng lọc context.

## 1. Mục đích

Báo cáo này phân tích nguyên nhân khiến chất lượng dẫn chiếu chéo của M10 chưa ổn định, dù hệ thống thường truy xuất được văn bản căn cứ đúng. Phạm vi tập trung vào ba câu đại diện của Benchmark B:

- `B026`: dẫn chiếu một bước về quyền chuyển đổi.
- `B030`: dẫn chiếu kết hợp với bước đi xuống điểm pháp lý.
- `B034`: chuỗi dẫn chiếu nhiều tầng về quyền bán tài sản và điều kiện bán.

Báo cáo không xem `Chain Exact Match` là đại diện duy nhất cho độ đúng pháp lý. Cần phân biệt giữa khả năng tìm được evidence đúng và khả năng tái dựng chính xác chuỗi dẫn chiếu.

## 2. Kết luận chính

Nguyên nhân chính không phải là UKG hoàn toàn thiếu dữ liệu. Evidence đúng đã xuất hiện trong expanded/context retrieval. Điểm yếu tập trung ở bốn khâu:

1. Hệ thống đang xếp hạng edge riêng lẻ thay vì xây dựng và chấm điểm path hoàn chỉnh.
2. Gold chain chứa cả explicit reference edge và hierarchy step, nhưng runtime đang xuất hai loại này chưa thống nhất.
3. Auxiliary anchors làm candidate pool chứa nhiều nhánh pháp lý cùng chủ đề nhưng không thuộc chuỗi trả lời.
4. Giới hạn `max_paths` đang giới hạn số edge record, chưa giới hạn số path hoàn chỉnh.

Vì vậy, đây chủ yếu là vấn đề `path reconstruction / path reporting` và path ranking; không nên kết luận đơn giản rằng hệ thống không truy hồi được quy định pháp luật cần thiết.

## 3. Số liệu pilot

Run nghiệm thu cuối:

`outputs/benchmark_b/hybrid/hybrid_minpath_3q_20261031_03`

| Chỉ số | Kết quả |
|---|---:|
| Số câu | 3 |
| Expanded evidence recall | 1,0000 |
| Generation context recall | 1,0000 |
| Evidence unresolved | 0 |
| Context evidence | 38 |
| Context evidence trung bình/câu | 12,67 |
| Chain-step precision | 0,2222 |
| Chain-step recall | 0,5000 |
| Chain-step F1 | 0,3000 |
| Chain Exact Match | 0,0000 |
| Reference-target recall | 0,6111 |
| Edge-label accuracy | 0,6667 |

So với pilot trước khi pruning, context giảm từ 165 xuống 38 evidence, trong khi expanded/context recall vẫn đạt 1,0. Điều này cho thấy hai tầng lọc đã giảm nhiễu context, nhưng chưa giải quyết đầy đủ việc xây dựng chain.

## 4. Phân tích theo câu hỏi

### 4.1. B026 — Chuỗi đúng có mặt nhưng bị path nhiễu cạnh tranh

Gold chain:

```text
LD2024:A28:K1:Da → LD2024:A37:K1:Db
```

Đây là dẫn chiếu về việc cá nhân được nhận chuyển đổi quyền sử dụng đất nông nghiệp và quy định thực chất nằm tại điểm b khoản 1 Điều 37.

Candidate pool đồng thời chứa các cạnh khác như:

```text
LD2024:A45:K3:Db → LD2024:A47
LD2024:A45:K7 → LD2024:A45:K6
```

Các cạnh này có từ khóa liên quan đến “điều kiện”, “chuyển đổi” hoặc “phương án sử dụng đất”, nên được xem là liên quan khi chấm riêng từng edge. Tuy nhiên, chúng không thuộc answer path của B026.

Chẩn đoán: lỗi ranking/pruning ở cấp path; không phải lỗi thiếu edge đúng.

### 4.2. B030 — Explicit reference đúng nhưng thiếu hierarchy step trong path

Gold chain:

```text
LD2024:A41:K1
→ LD2024:A33:K1
→ LD2024:A33:K1:Dđ
```

Runtime đã tìm được explicit reference:

```text
LD2024:A41:K1 → LD2024:A33:K1
```

Đồng thời context có thông tin về điểm đ khoản 1 Điều 33, là nơi quy định quyền thế chấp. Tuy nhiên, sau khi loại `PARENT_CHILD_CONTEXT` khỏi `reference_paths` để tránh làm nhiễu metric, bước:

```text
LD2024:A33:K1 → LD2024:A33:K1:Dđ
```

không còn được biểu diễn trong answer path.

Chẩn đoán: lỗi biểu diễn chain, không phải lỗi truy xuất evidence. Hierarchy step cần được giữ nếu nó là bước đi xuống nhánh trả lời, nhưng phải tách khỏi các cạnh phân cấp không liên quan.

### 4.3. B034 — Chuỗi nhiều tầng bị cắt và trộn nhánh

Gold yêu cầu hai biến thể điều kiện:

```text
LD2024:A43:K2:Db
→ LD2024:A34:K1
→ LD2024:A34:K1:Dc
→ LD2024:A46
→ LD2024:A46:K1
→ LD2024:A46:K1:Da
```

và tương tự với điểm `Db`.

Runtime lại có xu hướng chọn các cạnh độc lập như:

```text
LD2024:A34:K2 → LD2024:A34:K1
LD2024:A46:K5 → LD2024:A45:K1
LD2024:A46:K2:Da → LD2024:A46:K1
```

Một số cạnh có liên quan pháp lý nhưng không tạo thành chuỗi từ chủ thể ban đầu đến hai điều kiện cần trả lời.

Chẩn đoán: lỗi kết hợp giữa edge-level scoring, candidate noise và giới hạn path chưa được định nghĩa theo path hoàn chỉnh.

## 5. Các nguyên nhân kỹ thuật

### 5.1. Scoring hiện tại là edge-level

Điểm hiện tại chủ yếu dựa trên:

- lexical overlap giữa câu hỏi và source/target text;
- source hoặc target có cùng Article với anchor;
- hop distance;
- relation type.

Điểm này không biết một edge có nối tiếp edge trước đó hay có dẫn tới facet cần trả lời hay không.

### 5.2. Auxiliary anchors làm mở rộng phạm vi quá rộng

Traversal hiện có thể bắt đầu từ top anchor và auxiliary lexical anchors. Cơ chế này tốt cho recall nhưng đưa vào candidate pool các Điều/Khoản cùng chủ đề. Nếu không có chain-level penalty, các nhánh này cạnh tranh với path chính.

### 5.3. Explicit reference và hierarchy chưa có contract thống nhất

Có ba loại bước cần phân biệt:

```text
EXPLICIT_REFERENCE
PARENT_CHILD_ANSWER_STEP
PARENT_CHILD_CONTEXT_ONLY
```

Chỉ hai loại đầu nên xuất hiện trong `answer_paths`. Loại thứ ba chỉ phục vụ context và hierarchy audit.

### 5.4. `max_paths` chưa phản ánh path hoàn chỉnh

Giới hạn ba record không tương đương với ba chuỗi. Một câu multi-hop có thể cần nhiều edge và hierarchy step trong cùng một chuỗi. Do đó phải giới hạn:

```text
max_complete_paths = 3
max_explicit_hops_per_path = 2 hoặc 3
max_answer_children_per_target = 2 hoặc 5 tùy facet
```

### 5.5. Evaluator đang nhạy với cách biểu diễn chain

Nếu runtime chỉ có explicit edge nhưng gold có thêm hierarchy step, `Chain Exact Match` sẽ bằng 0 dù context có đúng node đích. Đây là lý do metric chain cần chấm trên `answer_paths` đã chuẩn hóa, không trực tiếp trên danh sách raw edges.

## 6. Kiến trúc output nên chốt

M10 nên xuất ba lớp riêng:

```json
{
  "explicit_reference_edges": [],
  "selected_hierarchy_steps": [],
  "answer_paths": [],
  "candidate_reference_edges": [],
  "path_pruning_trace": []
}
```

Trong đó:

- `explicit_reference_edges`: toàn bộ cạnh dẫn chiếu được phát hiện và có provenance.
- `selected_hierarchy_steps`: các bước Điều–Khoản–Điểm thực sự được chọn để hoàn thiện câu trả lời.
- `answer_paths`: chuỗi đã nối hoàn chỉnh, dùng cho evaluator.
- `candidate_reference_edges`: ứng viên trước pruning, dùng audit.
- `path_pruning_trace`: lý do chọn hoặc loại từng edge/path.

## 7. Hướng khắc phục đề xuất

### Phase 1 — Chuẩn hóa graph path

- Xây đồ thị locator gồm explicit edges và hierarchy edges.
- Gắn loại cạnh rõ ràng.
- Không coi mọi parent-child edge là answer step.
- Cho phép nối `Điều → Khoản → Điểm` chỉ khi target branch phù hợp facet câu hỏi.

### Phase 2 — Xây complete answer paths

- Chọn 1–3 anchor chính làm root ưu tiên.
- Tạo path tới explicit target.
- Từ target, mở rộng children theo action/condition/exception facet.
- Tiếp tục explicit traversal nếu target text chứa dẫn chiếu tiếp theo.
- Loại path nếu bị ngắt, quay vòng hoặc rẽ sang branch không liên quan.

### Phase 3 — Chain-level scoring

Đề xuất:

```text
chain_score =
    0.30 × anchor_relevance
  + 0.25 × explicit_reference_relevance
  + 0.20 × answer_child_relevance
  + 0.15 × facet_coverage
  + 0.10 × path_connectivity
  - 0.15 × unrelated_branch_penalty
  - 0.10 × redundant_step_penalty
```

Chỉ giữ tối đa ba complete paths có score cao nhất và không trùng locator sequence.

### Phase 4 — Evaluator alignment

- Chấm chain trên `answer_paths`, không chấm trực tiếp raw context edges.
- Chấm `explicit_reference_edges` riêng.
- Chấm `selected_hierarchy_steps` riêng.
- Đánh dấu `N/A` nếu câu hỏi không yêu cầu chain.
- Không tính hierarchy context-only vào chain precision.

## 8. Tiêu chí nghiệm thu sau khi sửa

Trên tập development cross-reference:

- Expanded evidence recall ≥ 0,95.
- Generation context recall ≥ 0,95.
- Context trung bình ≤ 20 evidence/câu.
- Evidence unresolved = 0 hoặc được đánh dấu rõ.
- Chain-step precision ≥ 0,60.
- Chain-step recall ≥ 0,80.
- Có ít nhất một `Chain Exact Match` ở các câu một-hop.
- B034 phải tạo được complete path tới cả hai điều kiện tại điểm a và điểm b khoản 1 Điều 46.

Các ngưỡng này dùng để phát triển và nghiệm thu kỹ thuật, không thay thế human/LLM judge về tính đúng pháp lý của câu trả lời.

## 9. Kết luận

Chất lượng cross-reference hiện tại đã cải thiện rõ về độ gọn context và khả năng đưa evidence đúng vào generation context, nhưng chưa ổn định ở cấp chuỗi. Nguyên nhân cốt lõi là hệ thống đang tối ưu và báo cáo các edge rời rạc, trong khi bài toán cần chọn và tái dựng complete answer path có cả explicit reference và hierarchy step có điều kiện.

Do đó, hướng phù hợp là nâng cấp M10 theo mô hình `answer-path construction`, không cần sửa lại M6–M9 hoặc xây lại Neo4j ở giai đoạn này. Kết quả 50 câu chỉ nên được coi là development benchmark cho đến khi path contract và evaluator được chuẩn hóa.
