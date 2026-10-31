# Báo cáo audit gold Benchmark B

Ngày audit: 2026-10-31  
Nguồn đối chiếu: Luật Đất đai số 31/2024/QH15, Chương III, Điều 26–48 trong corpus đóng băng của dự án.  
Nguồn gold: `benchmark_B_v02.json`  
Kết quả: `benchmark_B_v03_ai_reviewed.json`

Bảng ký duyệt từng câu: `benchmark_B_v03_human_signoff.csv`

## Phạm vi audit

Đã đọc và đối chiếu đủ 50 câu hỏi, 148 gold-location occurrences (105 locator duy nhất), 129 atomic facts, 13 exception annotations, 8 forbidden claims và toàn bộ reference chains. Tất cả locator đều tồn tại trong locator map và khớp physical node ID hiện tại.

Bản kết quả được ghi đúng provenance là `AI_ASSISTED_VERIFIED_PENDING_HUMAN_SIGNOFF`. Đây là bản đề xuất đã audit, chưa được ghi giả thành human review. File v0.2 được giữ nguyên để đối chiếu.

## Các sửa đổi

1. B041 chuyển từ `multi_hop` thành `single_hop`: câu hỏi liệt kê trực tiếp quyền tại khoản 1 Điều 33 và không có reference chain.
2. B042 chuyển từ `multi_hop` thành `single_hop`: câu hỏi lấy trực tiếp quyền tại khoản 3 Điều 41 và không có reference chain.
3. B043 chuyển từ `multi_hop` thành `conditional`: câu hỏi tổng hợp ba điểm của khoản 8 Điều 45, có ngoại lệ nhưng không đi theo dẫn chiếu nội bộ.
4. B022 được viết chính xác phạm vi địa lý của lệnh cấm: khu vực rừng phòng hộ, phân khu bảo vệ nghiêm ngặt và phân khu phục hồi sinh thái thuộc rừng đặc dụng.
5. Atomic facts được gắn vai trò để xác định đúng mẫu số metric: `REQUIRED_FACT`, `REQUIRED_CONDITION`, `SUBJECT_SCOPE`.
6. Atomic facts của B048–B050 được gắn các locator `scope_boundary`; trước đó `evidence_any_of` để trống.
7. Reference edges được phân loại lại theo ngữ nghĩa: `INHERITS_RIGHTS_OBLIGATIONS`, `REQUIRES_CONDITION_FROM`, `EXCEPTION_REFERENCE`, `DIRECT_REFERENCE`, `PARENT_CHILD_CONTEXT`.
8. Exception và forbidden-claim annotations được gắn supporting locators từ candidate locators đã đối chiếu.

Thống kê chain sau audit:

- `PARENT_CHILD_CONTEXT`: 31 occurrences, 16 cạnh duy nhất.
- `INHERITS_RIGHTS_OBLIGATIONS`: 20 occurrences, 14 cạnh duy nhất.
- `REQUIRES_CONDITION_FROM`: 14 occurrences, 5 cạnh duy nhất.
- `EXCEPTION_REFERENCE`: 3 bước.
- `DIRECT_REFERENCE`: 2 bước.

## Cấu hình retrieval đã chốt

LightRAG sử dụng:

```text
graph top_k = 5
chunk_top_k = 5
max_total_tokens = 10.000
max_entity_tokens = 2.000
max_relation_tokens = 2.000
rerank = false
```

Năm chunks × 1.200 token dùng tối đa xấp xỉ 6.000 token; 4.000 token còn lại dành cho entity/relation context. Runner từ chối `top_k` khác 5 để các lần chạy không âm thầm đổi cấu hình.

## Human sign-off còn thiếu

Một thành viên nhóm nghiên cứu phải đọc bản candidate và ký tên thật trước khi dùng nhãn `HUMAN_REVIEWED` trong báo cáo. Sau khi hoàn tất, chạy:

Trước hết, mở `datasets/benchmarks/benchmark_B_v03_human_signoff.csv`, điền `APPROVED` hoặc `REJECTED` cho đủ 50 dòng cùng tên người review, ngày và ghi chú sửa nếu có. Sau đó mới chạy:

```powershell
python -m benchmark_b.signoff_gold --reviewer "Họ tên người review" --review-date 2026-10-31 --confirm-reviewed-all-50
```

Lệnh tạo `datasets/benchmarks/benchmark_B_v03.json`, chuyển các trạng thái đủ điều kiện sang `REVIEWED` và lưu tên người ký. Không chạy lệnh này nếu người ký chưa thực sự đọc toàn bộ 50 câu.

Cho đến khi ký, pipeline benchmark chính thức vẫn phải dùng v0.2 hoặc bản candidate với các metric human-dependent ở trạng thái `not_measured`. Không được trình bày bản AI-assisted là human-reviewed.

## Kiểm tra

- Candidate có đủ 50 câu; 50/50 question status và 129/129 fact status là `AI_ASSISTED_VERIFIED_PENDING_HUMAN_SIGNOFF`.
- 39 semantic chain steps chờ human sign-off; 31 parent-child steps giữ nhãn `STRUCTURAL`.
- Sign-off guard đã được kiểm tra: CSV còn `PENDING` bị từ chối và không sinh file `benchmark_B_v03.json`.
- Pytest vòng 1 sau thay đổi: **20 passed**.
- Pytest vòng 2 sau bổ sung sign-off guard: **20 passed**.
- `git diff --check`: đạt.
