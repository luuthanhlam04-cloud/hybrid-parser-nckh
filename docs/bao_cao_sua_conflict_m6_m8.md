# Báo cáo xử lý cảnh báo conflict từ M6 đến M8

Ngày: 30/10/2026 · Nhánh: `minh_hybrid_parser`

## Baseline

Trước khi sửa: M6 có 180 extracted nodes; M7 có 834 active mentions, 103 norms, 966 active edges, 49 quarantined edges; M8 có 739 nodes và 3 `POTENTIAL_LEGAL_CONFLICT` trong 2 cụm (chuyển nhượng và thế chấp). Ba dòng đó là ứng viên rà soát, chưa phải kết luận pháp luật mâu thuẫn.

## Phase 1 — Chỉnh 5 extraction của M6

Script `scripts/correct_m6_conflict_nodes.py` sửa có kiểm tra ID và evidence:

| Node | Thay đổi | Mục đích |
|---|---|---|
| Điều 32 khoản 2 | Thêm `e10` CONDITION “được Nhà nước giao đất không thu tiền sử dụng đất”, nối với `e4`–`e9` | Giới hạn phạm vi lệnh cấm |
| Điều 33 khoản 1 điểm đ | Thêm `e8` CONDITION lấy nguyên văn khoản cha; nối với `e2` | Ghi nhận giao đất có thu tiền/thuê trả một lần |
| Điều 34 khoản 1 điểm b | Đổi `e4.text` thành “Thế chấp tài sản thuộc sở hữu của mình gắn liền với đất”; thêm condition thuê đất trả tiền hằng năm | Phân biệt đối tượng thế chấp |
| Điều 37 khoản 1 điểm g | Đổi `e4/e5` từ SUBJECT sang CONDITION bên nhận thế chấp; giữ `e7` là chủ thể thực hiện | Ngăn gán quyền cho bên nhận |
| Điều 45 khoản 8 điểm c | Giữ condition chung theo nguyên văn, chuẩn hóa text của `e11` | Tránh tạo hai trích dẫn không có trong văn bản |

Phương án trước từng đề xuất tách điều kiện Điều 45 thành hai câu riêng. Kiểm tra văn bản vật lý cho thấy câu nguồn chỉ có một cụm chung, nên đã giữ một condition và xử lý phạm vi ở M8. M6 vẫn có **180 nodes**, metadata hiện có được giữ nguyên; các relation mới đều có endpoint tồn tại và evidence xuất hiện trong văn bản vật lý hoặc khoản cha.

## Phase 2 — Canonical mapping của M7

Thêm `LO2024.ACTION.ATTACHED_ASSET_MORTGAGE` trong concept registry và rule cụ thể đứng trước rule “thế chấp” chung. Điều 34 khoản 1 điểm b không còn bị gom thành `LAND_MORTGAGE` (thế chấp quyền sử dụng đất).

Sau khi chạy `run_ontology_builder.py`:

| Chỉ số | Trước | Sau |
|---|---:|---:|
| Assembled mentions | 834 | 837 |
| Assembled norms | 103 | 103 |
| Assembled edges | 1015 | 1017 |
| Active edges | 966 | 968 |
| Quarantined edges | 49 | 49 |
| Partial norms | 6 | 6 |
| Endpoint/norm/reference owner gãy | 0 | 0 |

Final M7 gate: conservation pass, 0 domain-range violation, 0 provenance violation.

## Phase 3 — Phân loại conflict ở M8

`ConflictResolver` nay xét từng cặp ALLOW/REQUIRE ↔ PROHIBIT, giữ provenance và nội dung điều kiện của mỗi vế. Quy tắc hẹp:

- cùng điều kiện và cùng object rõ ràng, không có exception → `POTENTIAL_LEGAL_CONFLICT`;
- hai chế độ giao đất có thu tiền và không thu tiền khác nhau → `CONTEXTUAL_DIFFERENCE`;
- câu cấm “pháp luật không cho phép” → `REVIEW_REQUIRED`;
- điều kiện thiếu/không chứng minh được cùng phạm vi hoặc có exception cần đọc → `REVIEW_REQUIRED`.

Kết quả chạy `run_fusion.py`:

| Chỉ số | Trước | Sau |
|---|---:|---:|
| UKG nodes | 739 | 744 |
| Semantic edges | 1198 | 1223 |
| `POTENTIAL_LEGAL_CONFLICT` xuất cho M9 | 3 | 0 |
| Cặp norm được giữ để rà soát | chưa tách | 15 |
| SHACL conforms | có | `true` |

15 cặp rà soát trong `outputs/unified_graphs/fusion_conflict_reviews.json`: 2 khác chế độ giao đất, 4 có điều kiện cấm chung cần đối chiếu, 8 có exception cần đọc phạm vi, 1 chưa đủ điều kiện để kết luận. Những cặp này không được tuyên bố là xung đột đã xác nhận và không nằm trong `fusion_conflicts.json`/`UKG.conflicts` mà M9 dùng. Hai cảnh báo chuyển nhượng cũ hiện nằm trong 4 cặp điều kiện cấm chung; cảnh báo thế chấp cũ được giới hạn theo chế độ giao đất và loại tài sản.

## Phase 4 — Kiểm thử

Tạo `tests/unit/test_m8_conflict_scope.py`: kiểm tra điều kiện khác nhau, cấm có điều kiện, object khác nhau, cặp cùng phạm vi, provenance và tính lặp lại của script M6. Chạy **2 vòng pytest** (giới hạn tối đa 3): vòng 1 `13 passed in 0.39s`; sau khi thêm gate so sánh object, vòng 2 `14 passed in 0.38s` khi chạy cùng test M7 integrity và NormFuser. `git diff --check` không phát hiện lỗi whitespace.

## Giới hạn còn lại

Số conflict bằng 0 chỉ nói rằng không có cặp nào vượt ngưỡng cảnh báo hiện tại; không chứng minh Luật Đất đai không có xung đột. M7 hiện gom tất cả subject/action/condition trong một extraction node thành một norm, nên có thể gán điều kiện riêng của một chủ thể sang chủ thể khác (đặc biệt Điều 28 khoản 1 điểm c), và condition group có thể biểu diễn các phương án “hoặc” như một nhóm AND. Cần cải tiến NormBuilder theo từng relation và biểu diễn OR trước khi dùng hệ thống để kết luận pháp lý tự động. Danh sách 15 cặp review cần người đọc nguồn luật xác nhận.

Các file output được tái sinh từ pipeline: `outputs/canonical_graphs/canonical_semantic_graph.json`, `outputs/unified_graphs/unified_knowledge_graph.json`, `outputs/unified_graphs/fusion_conflicts.json`, `outputs/unified_graphs/fusion_conflict_reviews.json` và `outputs/unified_graphs/fusion_shacl_report.json`.

## Phase 5 — Materialize review findings cho M9

Theo yêu cầu truy vấn trên Neo4j, 15 review findings được materialize vào UKG
thành 15 node `REVIEW_FINDING` (ID `REVIEW_001` đến `REVIEW_015`). Mỗi node
được nối bằng `REVIEW_POSITIVE_NORM` và `REVIEW_PROHIBITIVE_NORM` tới hai
`GLOBAL_NORM`, đồng thời nối bằng `REVIEW_SOURCE_NODE` tới các node vật lý
nguồn. Các cạnh pháp lý gốc không bị đổi thành conflict.

UKG sau khi tái sinh có 759 nodes và 2.541 edges; trong đó có 15 node review,
15 cạnh `REVIEW_POSITIVE_NORM`, 15 cạnh `REVIEW_PROHIBITIVE_NORM` và 30 cạnh
`REVIEW_SOURCE_NODE`. SHACL vẫn đạt. M9 sẽ ingest các node/cạnh này cùng UKG;
file `fusion_conflict_reviews.json` tiếp tục là bản báo cáo chi tiết để đối
chiếu.

Test bổ sung cho materialization đạt `5 passed`.
