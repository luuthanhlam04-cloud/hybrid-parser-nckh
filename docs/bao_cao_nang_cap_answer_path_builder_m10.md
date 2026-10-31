# Báo cáo nâng cấp Answer-Path Builder cho M10

Ngày: 31/10/2026  
Nhánh: `benmark_b`  
Mục tiêu: khắc phục giới hạn `Chain Exact Match = 0` của M10 `AUTO_FUSION` mà không thay đổi gold, M1–M9 hoặc Neo4j.

## 1. Vấn đề ban đầu

Phiên bản Hybrid full v04 truy xuất evidence tốt nhưng báo cáo chain theo các explicit edge rời rạc. Khi gold yêu cầu chuỗi xen kẽ giữa dẫn chiếu rõ và bước Điều–Khoản–Điểm, evaluator không nhận được path hoàn chỉnh.

Kết quả v04 trên 18 câu có chain:

| Metric | v04 |
|---|---:|
| Chain-step precision | 0,3241 |
| Chain-step recall | 0,5080 |
| Chain-step F1 | 0,3499 |
| Reference-target recall | 0,5867 |
| Edge-label accuracy | 0,7222 |
| Chain Exact Match | 0,0000 |

## 2. Thay đổi triển khai

Thêm `src/retrieval/answer_path_builder.py` và mở rộng M10.

1. Đọc bounded descendants của anchor/reference target ở tối đa hai tầng bằng `retrieve_hierarchy_descendants`.
2. Dựng path theo thứ tự:

```text
explicit reference edge
→ PARENT_CHILD_CONTEXT cần thiết
→ explicit reference edge tiếp theo
→ leaf Điều/Khoản/Điểm trả lời
```

3. Child chỉ được thêm khi thuộc nhánh target và khớp action, condition hoặc facet của câu hỏi.
4. Xuất tách bốn artefact:

```text
reference_paths / answer_paths
explicit_reference_edges
selected_hierarchy_steps
answer_path_trace
```

5. Không đọc `gold_locations`, `accepted_chain_sets` hay bất kỳ trường gold nào trong runtime.

## 3. Pilot nghiệm thu

Run: `outputs/benchmark_b/hybrid/hybrid_answer_paths_pilot_20261031_01`  
Câu thử: `B012`, `B028`, `B030`, `B034`; không chạy Judge.

| Metric chain | Pilot answer-path builder |
|---|---:|
| Chain-step precision | 0,6250 |
| Chain-step recall | 0,7083 |
| Chain-step F1 | 0,6278 |
| Reference-target recall | 0,8125 |
| Edge-label accuracy | 1,0000 |
| Chain Exact Match | 0,2500 |

`B030` đạt Chain Exact Match = 1,0 với path:

```text
LD2024:A41:K1
→ LD2024:A33:K1
→ LD2024:A33:K1:Dđ
```

Đây là bằng chứng cơ chế answer-path đã có thể nối explicit reference với hierarchy step theo đúng contract gold.

## 4. Giới hạn còn lại

`B012`, `B028` và `B034` vẫn có nhánh root nhiễu, ví dụ path đi từ Điều 46 khoản 3 sang khoản 2 thay vì bắt đầu từ source clause/point theo câu hỏi. Vì vậy:

- Chưa chạy lại full 50 câu dưới version mới.
- Chưa thay thế kết quả chính thức `hybrid_full_v04_20261031`.
- Cần tăng root ranking theo subject context của parent và toàn bộ chain relevance, không chỉ edge text.

## 5. Kết luận

Answer-path builder đã giải quyết được lỗi kiến trúc làm Chain Exact Match luôn bằng 0: metric hiện có thể đạt giá trị dương mà không có gold leakage. Tuy nhiên, root selection cho câu điều kiện/multi-hop vẫn cần một vòng tối ưu trước khi chạy full v05 và dùng kết quả đó trong báo cáo nghiên cứu.

## 6. Bổ sung triển khai P1–P3 và nghiệm thu ngày 31/10/2026

Yêu cầu mở rộng gồm: (P1) giảm nhiễu root selection; (P2) không tự thêm hierarchy step không phục vụ câu trả lời; và (P3) chuẩn hóa path, hỗ trợ nhiều `accepted_chain_sets`.

### 6.1. Những thay đổi được giữ lại

1. **P2 — hierarchy có điều kiện:** với câu không yêu cầu liệt kê/điều kiện, M10 chỉ thêm `PARENT_CHILD_CONTEXT` khi child đạt ngưỡng relevance theo action/facet hoặc child là connector của một explicit reference quan sát được. Hệ thống không còn dùng child đầu tiên như một fallback cấu trúc.
2. **P3 — chuẩn hóa evaluator:** evaluator loại duplicate step liên tiếp, loại duplicate path, và chọn một `accepted_chain_set` exact-match trước khi so sánh F1 của các alternative hợp lệ. Thứ tự step vẫn được bảo toàn.
3. Runtime không đọc gold; phần `accepted_chain_sets` chỉ được dùng trong evaluator sau khi M10 đã tạo kết quả.

### 6.2. Kiểm thử

Đã chạy tối đa ba vòng pytest theo giới hạn đã đặt:

| Vòng | Lệnh/nhóm | Kết quả |
|---|---|---:|
| 1 | `test_answer_path_builder`, `test_benchmark_b_v02` | 24 passed |
| 2 | Bổ sung `test_m10_pipeline` | 26 passed, 1 failed do FakeGraphQuery chưa có API descendants mới |
| 3 | Cập nhật test double và chạy lại | **27 passed** |

Pilot tích hợp không Judge được chạy trên bốn câu `B012`, `B028`, `B030`, `B034`. Bản thử root-ranking P1 theo relation/specificity không đạt Chain Exact Match và có xu hướng thêm prefix path dư. Vì không đạt nghiệm thu, bản thử đó đã được **khôi phục**; không dùng nó làm kết quả chính thức.

| Run | Chain Exact | Chain-step F1 | Nhận định |
|---|---:|---:|---|
| `hybrid_answer_paths_pilot_20261031_01` | 0,2500 | 0,6278 | Bản builder ban đầu: chứng minh metric không còn bị khóa ở 0 |
| `hybrid_answer_paths_pilot_20261031_05` | 0,0000 | 0,3111 | Thử P1 đầu tiên không đạt |
| `hybrid_answer_paths_pilot_20261031_06` | 0,0000 | 0,3694 | Tăng step recall nhưng sinh prefix dư, không đạt exact-match |

### 6.3. Kết luận nghiệm thu

- P2 và P3 được giữ vì có unit test, không làm runtime đọc gold và làm path/evaluation chặt chẽ hơn.
- P1 **chưa đạt nghiệm thu**. Lý do không phải thiếu edge: trace cho thấy candidate pool chứa edge đúng, nhưng scoring hiện vẫn không phân biệt ổn định giữa path điều kiện trực tiếp và path điều kiện rộng hơn cùng Điều.
- Không chạy full 50 câu và không thay thế số liệu `hybrid_full_v04_20261031` bằng các run thử này.
- Hướng xử lý tiếp theo cần là path planner theo semantic roles của câu hỏi (subject, action, legal regime), rồi mới ranking complete path; không nên tăng trọng số edge/hierarchy đơn lẻ thêm nữa.
