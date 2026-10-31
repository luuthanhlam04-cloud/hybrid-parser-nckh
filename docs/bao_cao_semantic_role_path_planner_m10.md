# Báo cáo nâng cấp Semantic-role Path Planner cho M10

Ngày thực hiện: 31/10/2026  
Phạm vi: tái dựng `answer_paths` của M10 `AUTO_FUSION` cho truy vấn có dẫn chiếu chéo.  
Không dùng `reference_chain`, `accepted_chain_sets`, locator gold hoặc `question_id` của Benchmark B trong runtime.

## 1. Mục tiêu và nguyên tắc

Mục tiêu là thay cơ chế chọn từng cạnh độc lập bằng một planner theo vai trò ngữ nghĩa của câu hỏi:

```text
chủ thể + hành vi mục tiêu + chế độ pháp lý
    -> root explicit reference phù hợp
    -> hierarchy child nằm trong nhánh trả lời
    -> explicit reference tiếp theo (nếu có)
    -> các leaf điều kiện/ngoại lệ cần thiết
```

`answer_paths` là **proof path có thứ tự** để evaluator kiểm tra. Evidence hỗ trợ vẫn được giữ trong context cho LLM, nhưng không tự động biến thành một nhánh dẫn chiếu độc lập.

## 2. Thay đổi đã thực hiện

### 2.1 Semantic query profile

`src/retrieval/answer_path_builder.py` bổ sung hồ sơ câu hỏi gồm:

- action mục tiêu; ưu tiên action sau các tín hiệu vận hành như `muốn`, `có quyền`, `được`, `cần`, không coi mọi hành vi trong tình huống là hành vi được hỏi;
- role/chế độ pháp lý, với biến thể bề mặt cho `tổ chức kinh tế`, `doanh nghiệp/tổ chức có vốn đầu tư nước ngoài`, thuê/nộp tiền hằng năm và khu/cụm/khu công nghệ cao;
- facet `CONDITION`, `EXCEPTION`, `RIGHT_ORIGIN`;
- phân biệt bán tài sản riêng với bán kèm quyền thuê trong hợp đồng.

Role không chỉ được cộng điểm: nếu candidate source thiếu role đặc thù mà câu hỏi yêu cầu, candidate bị phạt. Mục đích là hạn chế nhầm một hậu quả chung hoặc quyền của chủ thể khác thành nhánh áp dụng.

### 2.2 Complete-path construction

Planner chỉ sử dụng:

- cạnh dẫn chiếu explicit đã quan sát từ UKG;
- cạnh cha–con đã truy hồi từ đồ thị;
- text của các node truy hồi;
- routing decision và evidence đã chọn.

Các guard mới:

- câu hỏi `RIGHT_ORIGIN` không ưu tiên root chỉ là clause “khi có đủ các điều kiện”; 
- nếu một child thể hiện đúng action mục tiêu, không mở thêm child “quyền/nghĩa vụ chung” chỉ vì child đó có cạnh ra;
- khi một clause là danh sách điều kiện hoàn chỉnh, giữ các leaf điều kiện cần thiết;
- với trường hợp bán kèm quyền thuê, proof path đi theo cạnh explicit từ điểm điều kiện sang khoản điều kiện chung;
- Jev chỉ adjudicate các root candidate đã quan sát. Điểm deterministic theo subject/action/regime vẫn chiếm 95%, Jev chiếm 5%; nếu Jev lỗi, planner fallback hoàn toàn deterministic.

### 2.3 Provenance

Mỗi root candidate trong `answer_path_trace` ghi:

- `source`, `relation_type`, `target`;
- semantic components;
- xác suất Jev (nếu có);
- `root_selection_source` và cờ `selected_as_root`.

Output tách rõ `answer_paths`, `explicit_reference_edges` và `selected_hierarchy_steps`.

### 2.4 Điều chỉnh evaluator đã có liên quan

`benchmark_b/structural_metrics.py` chuẩn hóa bước trùng liên tiếp và chọn accepted chain set theo `(exact match, F1)`. Điều này tránh phạt một đường đi chỉ vì representation lặp cùng node liên tiếp, nhưng **không** nới lỏng điều kiện Chain Exact Match.

## 3. Kiểm thử

### Unit test

Theo giới hạn đã thống nhất tối đa ba vòng `pytest`, không chạy thêm pytest trong lượt này. Trạng thái pytest hợp lệ gần nhất trước các chỉnh sửa semantic planner là:

```text
29 passed in 1.86s
```

Sau thay đổi cuối cùng đã chạy:

```text
python -m py_compile src/retrieval/m10_pipeline.py src/retrieval/answer_path_builder.py
```

Kết quả: thành công.

### Integration pilot

Pilot dùng bốn câu cross-reference đại diện B012, B028, B030, B034, mode `AUTO_FUSION`, `--skip-judge`. Đây không phải kết quả full 50 câu và không dùng để báo cáo hiệu năng cuối cùng.

| Lần chạy | Chain Exact | Step Precision | Step Recall | Step F1 | Target Recall | Label Accuracy |
|---|---:|---:|---:|---:|---:|---:|
| Baseline full v04 (18 câu chain) | 0,00% | 32,41% | 50,80% | 34,99% | 58,67% | 72,22% |
| Semantic/Jev pilot trước guard | 0,00% | 52,38% | 70,83% | 52,90% | 81,25% | 100,00% |
| Semantic-role guard tốt nhất trong lượt này | **25,00%** | **75,00%** | **62,50%** | **66,11%** | 72,92% | **100,00%** |

Kết quả tốt nhất lưu ở:

```text
outputs/benchmark_b/hybrid/hybrid_semantic_role_guard_pilot_20261031_05
```

Các đường đi khớp hoàn toàn có thể quan sát được ở B030:

```text
Điều 41 khoản 1
-> INHERITS_RIGHTS_OBLIGATIONS -> Điều 33 khoản 1
-> PARENT_CHILD_CONTEXT -> điểm đ khoản 1 Điều 33
```

Một thử nghiệm bổ sung parent context cho mọi source edge đã làm metric giảm về Chain Exact 0%; nguyên nhân là context parent tạo nhiễu candidate/root ranking. Wiring đó đã được hoàn nguyên, không nằm trong luồng M10 cuối cùng.

Một refinement hẹp hơn chỉ cấp parent context cho source là POINT cũng cho Chain Exact 0% ở pilot xác nhận. Nó cũng đã được hoàn nguyên; kết quả tốt nhất nêu trong bảng là cấu hình được giữ lại.

## 4. Đánh giá trung thực

Kết quả chứng minh rằng representation `answer_paths` có thể khớp hoàn toàn một số chuỗi và semantic-role planning tăng đáng kể precision/F1 trên pilot. Tuy nhiên, **25% trên bốn câu không đủ để tuyên bố hệ thống đã giải quyết bài toán truy vấn dẫn chiếu chéo**.

Các vấn đề còn lại:

1. Một số candidate root ở điều kiện/hậu quả gần câu hỏi vẫn vượt qua nhánh quyền áp dụng thực sự.
2. Benchmark contract yêu cầu tập path đúng tuyệt đối. Một proof path có thêm nhánh hợp lệ về nội dung vẫn bị tính Chain Exact = 0.
3. Câu multi-hop như B034 cần chọn đúng root theo chế độ áp dụng trước, sau đó mới mở nhánh Điều 34 -> Điều 46; hiện planner vẫn có thể khởi động quá muộn tại Điều 46.
4. Cần chạy lại pytest sau khi người dùng cho phép reset giới hạn ba vòng, rồi đánh giá full 18 câu có chain trước khi quyết định chạy 50 câu.

## 5. Khuyến nghị nghiệm thu tiếp theo

Không nên đưa Chain Exact Match hiện tại vào báo cáo nghiên cứu như một claim thành công. Bước kỹ thuật đúng tiếp theo là một **root applicability classifier** nhỏ, có contract đầu ra `applicable_subject`, `target_action`, `legal_regime`, `right_origin/condition`, rồi chỉ cho answer-path planner xét các root thỏa contract đó. Classifier phải dùng text/UKG runtime và được đo tách riêng; không được học locator gold.

Tiêu chí để đủ an toàn cho claim nghiên cứu:

- chạy pytest sạch sau khi được phép;
- pilot 18 câu chain có Chain Exact Match khác 0 và ổn định qua nhiều nhóm (quyền kế thừa, điều kiện, ngoại lệ, multi-hop);
- sau đó mới chạy full Benchmark B 50 câu;
- báo cáo song song Chain Exact, step F1, target recall và ví dụ audit, không thay thế metric này bằng evidence recall.
