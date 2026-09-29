# CONTRACT M7 → M8 (Adapter Contract V1.0)

> **Mục đích:** Định nghĩa ranh giới trách nhiệm và giao thức dữ liệu giữa Module 7 (Canonicalization Authority) và Module 8 (Fusion Engine).
> **Nguyên tắc:** Không merge code khi chưa có contract này. Contract này là nguồn duy nhất giải quyết tranh luận về schema.

---

## 1. Vai trò và ranh giới

| Module | Vai trò | KHÔNG làm |
| :--- | :--- | :--- |
| **M7** | Canonicalization Authority: chuẩn hóa, kiểm tra constraint, build NormAssertion, quarantine | Tự tạo thông tin không có căn cứ trong văn bản (R1: No Semantic Amplification) |
| **M8** | Fusion Engine: tích hợp M4+M7 → UKG, resolve tham chiếu về M4, quality gate | Tự phân loại ngữ nghĩa mới, thay đổi nhãn M7, tạo node Document nếu M4 không có |

---

## 2. Schema NormAssertion (M7 → M8)

```json
{
  "id": "NORM_DOC_CHUONG3_ARTICLE27_0",
  "modality": "REQUIRE",
  "subject_status": "RESOLVED | UNRESOLVED",
  "subject_ids": ["mention_id_1"],
  "action_ids": ["mention_id_2"],
  "object_ids": ["mention_id_3"],
  "condition_ids": [],
  "exception_ids": [],
  "consequence_ids": [],
  "condition_groups": [],
  "provenance_node_id": "physical_node_id",
  "evidence": "trích dẫn văn bản gốc",
  "status": "VALID | QUARANTINED",
  "norm_completeness": "COMPLETE | PARTIAL"
}
```

### Phân loại `norm_completeness`:
- **`COMPLETE`**: `subject_ids` không rỗng VÀ `action_ids` không rỗng.
- **`PARTIAL`**: `subject_ids` rỗng (subject chưa xác định được) nhưng `action_ids` không rỗng. `subject_status` = `UNRESOLVED`.
- **`QUARANTINED`**: Vi phạm invariant — không được phép vào `active_norms`, chỉ lưu trong `quarantine`.

---


## 3. Source=None Policy (Hai tầng độc lập — Gate 1 và Gate 2)

> [!IMPORTANT]
> Gate 1 chạy **TRƯỚC** NormBuilder. `norm_id` chưa tồn tại tại thời điểm này. Gate 1 chỉ hỏi: *"source có phải LocalMention hợp lệ không?"*
> Gate 2 chạy **SAU** NormBuilder. Mới có `norm_ids` để kiểm tra. Gate 2 hỏi: *"cấu trúc cuối cùng có đúng Ontology không?"*

### Tầng Gate 1 — Kiểm tra M6/Local Graph

| RelationType | Source bắt buộc? | Hành vi khi `source_mention_id = None` |
| :--- | :---: | :--- |
| `ALLOW`, `REQUIRE`, `PROHIBIT` | **Không** | Cho phép — đây là Partial Norm (`UNRESOLVED`) |
| `HAS_OBJECT` | **Có** (LocalMention) | Drop: `GATE1_MISSING_MANDATORY_SOURCE` |
| `HAS_CONDITION`, `HAS_EXCEPTION`, `HAS_CONSEQUENCE` | **Có** (LocalMention) | Drop |
| `HAS_SUBJECT`, `HAS_ACTION`, `DENOTES` | N/A | NormBuilder tạo nội bộ — không xuất hiện trong M6 output |

### Tầng Gate 2 — Kiểm tra Final M7 Graph (Invariant I1)

| RelationType | Source bắt buộc là gì? | Hành vi khi sai |
| :--- | :---: | :--- |
| `HAS_CONDITION`, `HAS_EXCEPTION`, `HAS_CONSEQUENCE` | **NormAssertion ID** (∈ `norm_ids`) | Reject edge, ghi `validation_report` |
| `HAS_EXCEPTION` đệ quy | Exception mention type | Cho phép |
| `HAS_SUBJECT`, `HAS_ACTION`, `HAS_OBJECT` | **NormAssertion ID** | Reject nếu sai |

---


## 4. Merge Policy (NormFuser)

| Trường hợp | Hành vi V1 | Lý do |
| :--- | :--- | :--- |
| `PARTIAL + PARTIAL` cùng semantic core **và** cùng context (condition/exception/consequence) | **Merge được** | Hash giống → cùng quy phạm |
| `PARTIAL + PARTIAL` khác condition/exception | **Không merge** | Context khác → có thể là hai quy phạm khác nhau về phạm vi |
| `FULL + FULL` cùng semantic core | **Merge được** | Deduplication tiêu chuẩn |
| `PARTIAL + FULL` | **KHÔNG merge (V1)** | Tránh vi phạm R1 (No Semantic Amplification) |
| Khác `exception_ids` | **Không merge** | Hash khác → tự động không merge |
| Khác `consequence_ids` | **Không merge** | Hash khác → tự động không merge |

### Hash Key chuẩn (dùng trong NormFuser):
```python
# Dùng tuple thay vì string join — tránh collision khi ID chứa ký tự "_"
hash_key_tuple = (
    modality,
    tuple(sorted(subject_ids)),    # [] cho Partial Norm
    tuple(sorted(action_ids)),
    tuple(sorted(condition_ids)),
    tuple(sorted(exception_ids)),
    tuple(sorted(consequence_ids)),
)
# PARTIAL + PARTIAL: subject_ids=[] ở cả hai → tuple([])==tuple([]) → hash giống
# Nếu condition khác nhau → hash khác → không merge (bảo toàn context)
```

### Partial Norm trong NormFuser — KHÔNG dùng phantom node:
- Cờ nhận diện: `norm_status="PARTIAL"` và `subject_status="UNRESOLVED"`
- `source=None` trong relation — **KHÔNG bao giờ dùng string `"UNRESOLVED"` như endpoint**
- Lý do: `"UNRESOLVED"` như node ID tạo phantom node `(:Unknown)` trong Neo4j

---

## 5. Provenance Requirements

- Mọi `NormAssertion` xuất M7 **bắt buộc** có `provenance_node_id` trỏ về Physical Node của M4.
- Mọi `SemanticEdge` **bắt buộc** có `evidence` không rỗng.
- Khi Adapter map sang M8, phải giữ nguyên `source_node_id` — không được xóa hoặc override.

---

## 6. Quarantine Semantics

- Quarantine ≠ Delete. Mọi phần tử bị Quarantine phải được giữ lại trong `quarantine` list của output JSON.
- Lý do Quarantine phải được ghi rõ (`audit_note`).
- Mục đích: audit sau, đo `recall` thực sự của hệ thống.

---

## 7. Invariants (Không được vi phạm)

```
I1: ∀ edge ∈ active_edges:
    edge.relation_type ∈ {HAS_CONDITION, HAS_EXCEPTION, HAS_CONSEQUENCE}
    ⟹ edge.source_id ∈ norm_ids

I2: ∀ norm ∈ active_norms:
    norm.subject_status = "UNRESOLVED" ⟹ norm.subject_ids = []
    norm.subject_status = "RESOLVED"   ⟹ len(norm.subject_ids) > 0

I3: ∀ norm ∈ active_norms:
    norm.norm_completeness = "COMPLETE" ⟺ (len(subject_ids) > 0 AND len(action_ids) > 0)

I4: NormFuser merge kết quả phải idempotent:
    merge(merge(A, B), B) = merge(A, B)
```

---

## 8. Edge → Norm Ownership

Bất kỳ `HAS_CONDITION`, `HAS_EXCEPTION`, `HAS_CONSEQUENCE` edge nào đều phải có parent Norm. Không có "orphan structural edge". Adapter M8 khi đọc file M7 phải kiểm tra invariant I1 trước khi xử lý.
