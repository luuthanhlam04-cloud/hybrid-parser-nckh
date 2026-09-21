# Research Note: Module 7 — Ontology / Semantic Canonicalization (Knowledge Base)

**Ngày cập nhật:** 2026-09-21  
**Tác giả:** Lâm  
**Trạng thái:** ✅ Pipeline V1.0 hoàn chỉnh, đã chạy thử thành công (Frozen Schema)

---

# TẦNG A — TL;DR (Đọc 5 phút hiểu M7)

## §0. Snapshot
**Trạng thái hiện tại:** v1.0 (frozen schema)
**Số liệu mới nhất (2026-09-21):**
- 846 LocalMentions + 70 ReferenceMentions
- 102 NormAssertions
- 13 CanonicalConcepts (được sử dụng từ 32 concepts trong registry)
- 1141 Edges (32 QUARANTINED edges, 0 REJECTED)
- 0 bugs đang mở

**Người làm:** Lâm
**Người review:** [2 team members]
**Deadline freeze:** 2026-09-21

## §1. TL;DR cho người mới đọc lần đầu
Module 6 làm tốt một việc: nhờ LLM bóc tách entity thô (SUBJECT, ACTION, CONDITION...) từ từng điều khoản. Nhưng M6 *không thể* và *không nên* trả lời ba câu hỏi sau:
1. **"Nó là gì trong ontology pháp lý?"** — `"người dân tộc thiểu số"` và `"đồng bào DTTS"` đều là SUBJECT nhưng chúng là cùng một khái niệm pháp lý không?
2. **"Cùng khái niệm xuất hiện 50 điều khác nhau thì graph trông như thế nào?"** — Gom hết vào một node → siêu node mạng nhện. Tách hết → 50 node rời rạc đứt gãy.
3. **"Điều kiện của quy tắc này có bị trộn sang quy tắc khác không?"** — Cùng action "chuyển nhượng" xuất hiện trong 3 quy tắc với 3 bộ điều kiện khác nhau: nếu gắn điều kiện vào Action thì 3 bộ đó bị trộn lẫn.

M7 giải quyết cả ba bài toán đó bằng cách phân tách rõ Local Mention (token) và Canonical Concept (type), đồng thời sử dụng NormAssertion để gói gọn ngữ cảnh quy phạm (normative context).

## §2. Từ điển thuật ngữ (Glossary)
- **LocalMention (Token):** Một lần xuất hiện cụ thể của entity trong một điều khoản cụ thể, có ngữ cảnh riêng.
- **CanonicalConcept (Type):** Khái niệm pháp lý chung (dùng chung) mà nhiều Local Mention cùng nói đến. Không chứa cạnh normative.
- **NormAssertion:** Một quy phạm pháp lý đầy đủ, đóng vai trò như một context frame để nhóm các thành phần (Subject, Action, Object, Condition...) lại với nhau, tránh cross-context pollution.
- **QUARANTINED:** Trạng thái cách ly dành cho các node/edge vi phạm ràng buộc (ví dụ: gán sai Semantic Role, vi phạm Domain-Range). Tri thức được giữ lại cho audit, không bị xóa âm thầm.

---

# TẦNG B — DECISION LOG (Đọc để hiểu tại sao)

## §3. Bối cảnh M7 ra đời
Vấn đề cốt lõi M7 phải giải quyết là phân biệt Type-Token. Nếu không phân biệt, graph sẽ rơi vào một trong hai bệnh:
- **Supernode:** Gom tất cả mentions cùng loại vào một node → node đó có hàng trăm cạnh, normative relations từ nhiều context khác nhau bị trộn vào một chỗ.
- **Graph Fragmentation:** Mỗi mention là một node riêng → graph bị đứt gãy, không tra cứu được "DTTS" theo nghĩa khái niệm.

## §4. Decision Log
*(Các quyết định D01-D10 sẽ được điền chi tiết vào đây sau khi được review cấu trúc)*

### Decision D01: Dùng DENOTES thay vì INSTANCE_OF
[Chờ viết]

### Decision D02: Dùng NormAssertion thay vì gắn Condition vào Action
[Chờ viết]

### Decision D03: Granularity Test thay vì MaxDepth=2 cho Taxonomy
[Chờ viết]

### Decision D04: Neo4j Multi-label là Projection Layer
[Chờ viết]

### Decision D05: Xử lý PERMISSION/OBLIGATION thành Modality Context
[Chờ viết]

### Decision D06: 100% Rule-based, 0 LLM
[Chờ viết]

### Decision D07: Boolean Logic v1 (Flat AND/OR)
[Chờ viết]

### Decision D08: Không Auto-cast, chỉ QUARANTINE hoặc UNRESOLVED
[Chờ viết]

### Decision D09: Reference Classifier thay vì Reference Resolver
[Chờ viết]

### Decision D10: Per-document Concept Scope
[Chờ viết]

## §5. Rejected Alternatives (Các phương án đã bị loại)
*(Sẽ bổ sung chi tiết sau)*
- ALT-01: MaxDepth = 2 cho Taxonomy
- ALT-02: Condition gắn vào Action
- ALT-03: Auto-cast SUBJECT → OBJECT
...

## §6. Key Insights (Kiến thức rút ra cho luận văn)
*(Sẽ bổ sung chi tiết sau)*

---

# TẦNG C — WORKING NOTES (Đọc để làm việc)

## §7. Kiến trúc hiện tại (Reference)
Kiến trúc 6 lớp, không lớp nào thay thế lớp khác:

```
Layer 1: SEMANTIC VOCABULARY
         LegalSubject | LegalAction | LegalObject
         LegalConsequence | Condition | Exception | Reference
         (ALLOW/REQUIRE/PROHIBIT là modality, không phải entity class)
              ↓
Layer 2: CONTROLLED TAXONOMY
         Subtype theo Granularity Test — không hard-code depth
         Lưu trong configs/taxonomy_registry.yaml
              ↓
Layer 3: LOCAL SEMANTIC MENTION
         ID: <physical_node_id>#<MENTION_TYPE>#<index>
         Chứa: raw_text, semantic_type, subtype, provenance_node_id, evidence
              ↓
Layer 4: CANONICAL CONCEPT HUB
         MERGE semantics — mỗi canonical concept có một ID duy nhất
         LocalMention ──DENOTES──> CanonicalConcept
         CanonicalConcept KHÔNG chứa normative edges
              ↓
Layer 5: NORM / ASSERTION
         NormAssertion giữ đúng normative context
         Condition/Exception/Consequence thuộc NormAssertion, không phải Action
              ↓
Layer 6: NEO4J PROJECTION
         Multi-label chỉ là query layer
         (:LegalSubject:DomesticEntity:EthnicMinority)
```

## §8. Pipeline & File Structure

### Pipeline (100% rule-based, 0 LLM)
```
M6 semantic_extraction.json
        │
        ▼
[ entity_normalizer ]         Semantic Role Audit (VALID / CORRECTED / QUARANTINED / UNRESOLVED)
        │
        ▼
[ relation_normalizer ]       ALLOW/REQUIRE/PROHIBIT → NormativeModality context
        │
        ▼
[ canonical_mapper ]          DENOTES edges, MERGE semantics cho Concept Hub
        │
        ▼
[ norm_builder ]              Quyết định: simple edge hay NormAssertion?
        │
        ▼
[ reference_classifier ]      Phân loại 4 scopes, PENDING_M8
        │
        ▼
[ ontology_validator ]        Domain-Range matrix, QUARANTINED + log (không âm thầm xóa data)
        │
        ▼
canonical_semantic_graph.json
```

### File Structure
```
src/ontology/
├── schemas.py                  Pydantic models (LocalMention, NormAssertion, ...)
├── entity_normalizer.py        Semantic Role Audit + taxonomy lookup
├── relation_normalizer.py      Modality normalization
├── canonical_mapper.py         DENOTES edges + Concept Hub management
├── norm_builder.py             NormAssertion construction
├── reference_classifier.py     Phân loại 4 scopes cho References
├── ontology_validator.py       Domain-Range + invariant checks
├── ontology_builder.py         Pipeline orchestrator
└── configs/
    ├── taxonomy_registry.yaml  Controlled taxonomy (Granularity Test)
    ├── concept_registry.yaml   Canonical Concepts (LO2024 namespace)
    ├── mapping_rules.yaml      Phrase trigger → subtype + concept_id + FLAG rules
    ├── relation_rules.yaml     Modality normalization + domain-range
    └── reference_rules.yaml    Regex patterns cho references
```

## §9. Domain-Range Matrix
> **Lưu ý đọc bảng:** Các node semantic thực tế trong graph là **LocalMention**. Neo4j mới materialize chúng thành labels.

### Simple norm (direct edge)
| Relation | Source | Target |
|----------|--------|--------|
| `ALLOW` | `LocalMention [LegalSubject]` | `LocalMention [LegalAction]` |
| `REQUIRE` | `LocalMention [LegalSubject]` | `LocalMention [LegalAction]` |
| `PROHIBIT` | `LocalMention [LegalSubject]` | `LocalMention [LegalAction]` |
| `HAS_OBJECT` | `LocalMention [LegalAction]` hoặc `NormAssertion` | `LocalMention [LegalObject]` |
| `DENOTES` | `LocalMention` | `CanonicalConcept` |
| `PROVENANCE` | `LocalMention` / `NormAssertion` | `Physical Node ID` |

### Complex norm (NormAssertion)
| Relation | Source | Target |
|----------|--------|--------|
| `HAS_SUBJECT` | `NormAssertion` | `LocalMention [LegalSubject]` |
| `HAS_ACTION` | `NormAssertion` | `LocalMention [LegalAction]` |
| `HAS_OBJECT` | `NormAssertion` | `LocalMention [LegalObject]` |
| `HAS_CONDITION` | `NormAssertion` | `LocalMention [Condition]` |
| `HAS_EXCEPTION` | `NormAssertion` | `LocalMention [Exception]` |
| `HAS_CONSEQUENCE` | `NormAssertion` | `LocalMention [LegalConsequence]` |

## §10. Semantic Contract (R1-R9)
| Rule | Phát biểu | Trạng thái |
|------|-----------|----------|
| **R1** | `CanonicalConcept` không mang normative edges (`ALLOW/REQUIRE/PROHIBIT/HAS_CONDITION...`) | ✅ |
| **R2** | Mọi `LocalMention` phải có `provenance_node_id` trỏ về một `PhysicalNode` cụ thể | ✅ |
| **R3** | `LocalMention` chỉ được DENOTES tới `CanonicalConcept`, không dùng INSTANCE_OF | ✅ |
| **R4** | Normative context không được đặt trên `CanonicalConcept` | ✅ |
| **R5** | `Condition/Exception/Consequence` thuộc `NormAssertion` khi chúng là modifiers của một specific norm | ✅ |
| **R6** | M7 chỉ phân loại scope reference, không resolve tới Physical Node | ✅ |
| **R7** | Neo4j labels là projection layer, không phải canonical ontology definition | ✅ |
| **R8** | M6 extraction labels phải qua Semantic Role Audit, sai role → QUARANTINED | ✅ |
| **R9** | Unresolved semantic/reference cases phải được giữ trạng thái `UNRESOLVED` hoặc `QUARANTINED` + logged; không được silently drop | ✅ |

## §11. Run Results
| Ngày | Version | Mentions | Norms | Concepts | Edges | Notes |
|------|---------|----------|-------|----------|-------|-------|
| 2026-09-19 | v0.5 | 916 | 102 | 13 | 1182 (32 REJECTED) | Bản đầu |
| 2026-09-21 | v1.0 | 846+70 | 102 | 13 | 1141 (32Q) | Fix Bug 2 (QUARANTINED edges) |
| 2026-09-21 | v1.0-fix | 846+70 | 102 | 13 | 1141 (32Q) | Fix Bug 1 (mapping rules), 7 nodes QUARANTINED |

## §12. Bug Log

### Bug B01: Validator xoá edges thay vì QUARANTINE
**Phát hiện:** 2026-09-21
**Mức độ:** Nghiêm trọng (vi phạm Decision D08)
**Triệu chứng:** 32 edges vi phạm domain-range bị xoá khỏi output
**Root cause:** ontology_validator.py filter `valid_edges` thay vì set status
**Fix:** Thêm trường `status` vào SemanticEdge, set "QUARANTINED" khi vi phạm
**Trạng thái:** ✅ Fixed
**Bài học:** Validator phải "flag" không phải "delete"

### Bug B02: mapping_rules.yaml cũ, không có FLAG rules
**Phát hiện:** 2026-09-21
**Mức độ:** Nghiêm trọng
**Triệu chứng:** 0 QUARANTINED mentions
**Root cause:** File config chưa update, trỏ về CONCEPT_STATE cũ
**Fix:** Update mapping_rules.yaml, thêm FLAG rules cho SUBJECT→OBJECT với negative_triggers hợp lý
**Trạng thái:** ✅ Fixed

## §13. Open Problems (Chưa giải quyết)
- **Tiêu chí NormAssertion:** Hiện dùng "có condition/exception/consequence". Cần thực nghiệm xem có trường hợp simple norm nhưng vẫn cần NormAssertion để giữ context không?
- **PERMISSION/OBLIGATION trong M6:** M6 fix của Minh đã bổ sung `HAS_OBJECT` và Hohfeldian relations. Cần kiểm tra kỹ lại các entity type `PERMISSION` và `OBLIGATION` có thực sự chỉ là modality hay đôi khi cần là first-class entity (normative position).
- **Joint norm:** Khi A và B cùng liên đới nghĩa vụ (joint and several liability) — hai mũi tên `REQUIRE` cùng trỏ vào Norm chưa đủ để biểu diễn; cần cơ chế `JOINT/COLLECTIVE`.

## §14. Idea Backlog (Ý tưởng cho v2)
### Idea 1: Hybrid Lexicon (embedding + rule-based)
**Nguồn:** Gemini đề xuất, ChatGPT phản biện, chưa implement
**Mô tả:** Dùng LLM/Embedding để match alias khi rule-based không hit
**Tại sao chưa làm:** v1 ưu tiên deterministic. Cần benchmark trước khi thêm AI vào M7
**Khi nào làm:** M7 v2, sau khi có benchmark 3 phiên bản

### Idea 2: Recursive Exception (depth > 2)
**Nguồn:** Phát hiện khi scan corpus
**Mô tả:** Cho phép Exception of Exception of Exception
**Tại sao chưa làm:** Chưa gặp case thực tế trong Ch3-LDD
**Khi nào làm:** Khi mở rộng sang luật khác

## §15. Evolution Log
*(Timeline tiến hóa của schema - Cần bổ sung thêm)*

## §16. Liên kết & Tài nguyên
- **M6 Output (Input của M7):** `outputs/semantic_graphs/semantic_extraction.json`
- **M7 Output:** `outputs/canonical_graphs/canonical_semantic_graph.json`
- **Log:** `outputs/m7_run.log`
- **Audit CSV:** `outputs/m7_audit_log.csv`
- **Run script:** `run_ontology_builder.py`
- **Source:** `src/ontology/`
- **Tài liệu nghiên cứu gốc:** `tong_hop_context_ontology.txt` (NCKH/)
- **Implementation Plan:** `implementation_plan.md`
