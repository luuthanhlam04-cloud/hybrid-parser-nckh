# Báo cáo hoàn thiện Module 7

Ngày thực hiện: 29/10/2026  
Nhánh: `minh_hybrid_parser`  
Đầu vào M6: `outputs/semantic_graphs/semantic_extraction.json`  
Metadata M6 được giữ nguyên: `openai/gpt-4o-mini`, `180` candidates.

## 1. Mục tiêu

Sửa pipeline M7 thay vì vá thủ công `canonical_semantic_graph.json`, tập trung vào:

1. bảo toàn Partial Norm;
2. cascade quarantine và dependency closure;
3. loại false positive khi SUBJECT chứa từ “hợp đồng” hoặc “văn bản”;
4. orphan detection có xét norm/reference/canonical mapping;
5. bảo toàn hoặc cách ly reference ownership có lý do;
6. chuẩn hóa modifier edge về NormAssertion;
7. tính lại Validation Report sau toàn bộ pipeline;
8. chặn export nếu final graph còn invariant bị gãy;
9. bổ sung test hồi quy và kiểm tra deterministic.

## 2. Baseline trước khi sửa

| Chỉ số | Baseline |
|---|---:|
| Active mentions | 755 |
| Quarantine mentions | 79 |
| Norms | 101 |
| References | 118 |
| Active edges | 963 |
| Quarantine edges | 52 |
| Endpoint treo | 4 |
| Norm chứa mention ID không còn active | 4 |
| Reference không có owner active hợp lệ | 35 |

Ngoài ra, `NodeQualityFilter` đã loại 5 relation `source:null` như orphan source,
làm mất Partial Norm trước khi NormBuilder xử lý.

## 3. Phase 1 — Partial Norm và dependency closure

### Thay đổi

- `NodeQualityFilter` cho phép `source:null` duy nhất với
  `ALLOW/REQUIRE/PROHIBIT`, `source_status=UNRESOLVED`, target là ACTION và
  evidence không rỗng.
- Relation cấu trúc có `source:null` vẫn bị loại.
- `NormAssertion` có thêm `norm_completeness=COMPLETE|PARTIAL`.
- NormBuilder tạo Partial Norm với `subject_ids=[]` và
  `subject_status=UNRESOLVED`.
- Evidence của norm được gom theo thứ tự ổn định, không dùng thứ tự của `set`.
- Thêm dependency closure: xóa ID không còn active khỏi norm; norm mất subject
  thành PARTIAL; norm mất action bị quarantine; edge phụ thuộc bị cascade vào
  quarantine.

### Kết quả

| Chỉ số | Trước | Sau |
|---|---:|---:|
| Relation bị NodeQualityFilter loại | 6 | 1 |
| Relation `source:null` bị loại | 5 | 0 |
| Norms được tạo | 101 | 103 |
| Partial Norm active | 0 | 6 |

Sáu Partial Norm hiện tại:

- Điều 27 khoản 3 điểm a;
- Điều 28 khoản 3;
- Điều 29 khoản 2;
- Điều 33 khoản 3 điểm a;
- Điều 41 khoản 2 điểm d;
- Điều 46 khoản 5.

## 4. Phase 2 — Role audit, orphan và reference ownership

### Thay đổi

- SUBJECT có head noun `người`, `cá nhân`, `tổ chức`, `đại diện`, `cơ quan`,
  `nhà nước`, `ủy ban`, `bên` được ưu tiên là LegalSubject. Substring
  “hợp đồng” hoặc “văn bản” bên trong cụm không còn tự động làm node bị cách ly.
- Orphan audit xét đồng thời active edge, ID nội bộ của norm, reference owner và
  canonical mapping.
- Mention hợp lệ nhưng chưa liên kết được giữ active với nhãn audit
  `UNLINKED_EVIDENCE`, không bị gọi nhầm là orphan lỗi.
- Reference owner sai/mất được rebind trong cùng provenance khi có căn cứ; nếu
  không có căn cứ thì reference được đưa vào quarantine thay vì giữ active với
  owner giả.

### Kết quả sau Ontology Validator

| Chỉ số | Kết quả |
|---|---:|
| Active mentions | 834 |
| Quarantine mentions | 0 |
| Active edges | 966 |
| Quarantine edges | 49 |

Orphan audit cuối:

- 115 mentions là reference owner;
- 601 mentions là norm component;
- 51 mentions là unlinked evidence hợp lệ và vẫn được giữ active;
- 0 true orphan.

Reference cuối:

- 115 reference active có owner hợp lệ;
- 3 reference bị quarantine với lý do `MISSING_REFERENCE_OWNER` vì node nguồn
  không có mention/norm nào đủ căn cứ để rebind:
  - hai dẫn chiếu Điều 26 và Điều 31 tại Điều 41 khoản 3 điểm a;
  - dẫn chiếu khoản 1 Điều này tại Điều 46 khoản 2 điểm a.

## 5. Phase 3 — Contract, report và final integrity gate

### Thay đổi

- Contract M6→M7 được bổ sung chính sách Partial Norm có kiểm soát.
- Modifier có norm cha được chuyển thành edge từ NormAssertion.
- Modifier không tìm được norm cha được cách ly với reason code rõ ràng:
  `UNATTACHED_CONDITION`, `UNATTACHED_EXCEPTION`.
- Validation Report được tính lại sau validator, dependency closure, orphan
  audit và reference repair.
- Final gate dừng export nếu còn endpoint treo, norm/reference gãy, duplicate,
  active/quarantine overlap, domain-range violation hoặc provenance sai.

### Số liệu cuối

| Chỉ số | Kết quả |
|---|---:|
| Input / active mentions | 834 / 834 |
| Quarantine mentions | 0 |
| Input / active norms | 103 / 103 |
| Partial norms | 6 |
| Input / active edges | 1015 / 966 |
| Quarantine edges | 49 |
| Input / active references | 118 / 115 |
| Quarantine references | 3 |
| Endpoint treo | 0 |
| Norm reference gãy | 0 |
| Active reference owner gãy | 0 |
| Active/quarantine overlap | 0 |
| Duplicate ID / edge | 0 / 0 |
| Domain-range violation trên active graph | 0 |
| Provenance violation | 0 |
| Conservation check | PASS |

Phân bố 49 cạnh quarantine:

- 31 `UNATTACHED_CONDITION`;
- 5 `UNATTACHED_EXCEPTION`;
- 13 `HAS_OBJECT` sai domain/range.

Các cạnh này không còn làm gãy active graph. Đây là lỗi/ngữ nghĩa chưa đủ căn
cứ từ output M6, nên M7 giữ lại trong quarantine để audit thay vì tự sửa bằng
suy diễn.

## 6. Phase 4 — Test và kiểm tra chạy lặp

Đã tạo `tests/unit/test_m7_integrity.py` với 8 test:

1. Partial Norm `source:null` được bảo toàn;
2. structural relation `source:null` bị từ chối;
3. SUBJECT chứa “hợp đồng/văn bản” không bị false positive;
4. HAS_CONDITION được re-anchor sang NormAssertion;
5. cascade dependency biến norm mất subject thành PARTIAL và bỏ edge treo;
6. reference owner không bị orphan quarantine;
7. unlinked evidence hợp lệ vẫn active;
8. finalizer idempotent và report khớp payload.

Kết quả pytest theo giới hạn tối đa 3 vòng:

- Vòng 1: chưa chạy test do `pytest` chưa có trong `venv`;
- Vòng 2: collection dừng do thiếu package `neo4j`;
- Vòng 3: `8 passed in 0.31s` cho bộ hồi quy M7.

`pytest` và `neo4j` đã được khôi phục/cài đúng trong `venv`. Toàn bộ suite dự án
không được chạy lại lần thứ tư để tuân thủ giới hạn người dùng; các test GraphRAG
toàn cục còn phụ thuộc một Neo4j service đang chạy và dữ liệu đã ingest.

Kiểm tra bổ sung không dùng pytest:

- chạy M7 hai lần bằng cùng một builder cho output giống nhau: PASS;
- M8 adapter đọc output mới: PASS;
- M8 adapter tạo 1.431 relations, trong đó 12 relation từ Partial Norm;
- không tạo source phantom `UNRESOLVED`: 0.

## 7. File đã thay đổi

- `src/ontology/node_quality_filter.py`
- `src/ontology/entity_normalizer.py`
- `src/ontology/norm_builder.py`
- `src/ontology/ontology_validator.py`
- `src/ontology/ontology_builder.py`
- `src/ontology/schemas.py`
- `src/ontology/graph_integrity.py` (mới)
- `tests/unit/test_m7_integrity.py` (mới)
- `docs/contracts/M6_M7_CONTRACT.md`
- `outputs/canonical_graphs/canonical_semantic_graph.json` (tái sinh từ M6)

`outputs/semantic_graphs/semantic_extraction.json` chỉ được đọc làm input; pipeline
không sửa metadata M6 đã chốt.

## 8. Kết luận

M7 hiện đạt các invariant an toàn để chuyển sang M8: không còn endpoint treo,
norm/reference gãy, overlap, duplicate, domain-range hoặc provenance violation
trên active graph. Partial Norm được giữ đúng contract và output deterministic.

Phần còn lại cần cải thiện ở M6 hoặc qua human review là 49 cạnh sai/thiếu ngữ
cảnh và 3 reference không có owner đủ căn cứ. M7 đã cách ly chúng rõ ràng thay
vì âm thầm xóa hoặc tự bịa quan hệ.
