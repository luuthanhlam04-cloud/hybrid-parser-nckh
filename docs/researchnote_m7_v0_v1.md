# TỔNG HỢP LỊCH SỬ M7 (V0.9 & V1.1)

---

# PHẦN 1: BẢN V0.9 (ARCHIVED)
# Research Note: Module 7 — Ontology / Semantic Canonicalization
**Ngày:** 19 tháng 9, 2026  
**Tác giả:** Lâm  
**Trạng thái:** ✅ Pipeline V1.0 hoàn chỉnh, đã chạy thử thành công  
**Topic:** Thiết kế và triển khai tầng Ontology Canonicalization — chuyển M6 semantic extraction thô thành Canonical Semantic Graph chuẩn hóa, sẵn sàng cho Module 8 (Fusion Engine) và Neo4j.

---

## 1. Bối cảnh & Lý do M7 tồn tại

Module 6 làm tốt một việc: nhờ LLM bóc tách entity thô (SUBJECT, ACTION, CONDITION...) từ từng điều khoản. Nhưng M6 *không thể* và *không nên* trả lời ba câu hỏi sau:

1. **"Nó là gì trong ontology pháp lý?"** — `"người dân tộc thiểu số"` và `"đồng bào DTTS"` đều là SUBJECT nhưng chúng là cùng một khái niệm pháp lý không?
2. **"Cùng khái niệm xuất hiện 50 điều khác nhau thì graph trông như thế nào?"** — Gom hết vào một node → siêu node mạng nhện. Tách hết → 50 node rời rạc đứt gãy.
3. **"Điều kiện của quy tắc này có bị trộn sang quy tắc khác không?"** — Cùng action "chuyển nhượng" xuất hiện trong 3 quy tắc với 3 bộ điều kiện khác nhau: nếu gắn điều kiện vào Action thì 3 bộ đó bị trộn lẫn.

M7 giải quyết cả ba bài toán đó.

---

## 2. Quá trình nghiên cứu thiết kế (Research Journey)

### 2.1 Vấn đề nền: Bài toán Type-Token

Vấn đề cốt lõi M7 phải giải quyết là phân biệt:
- **Token (Local Mention):** Một lần xuất hiện cụ thể của entity trong một điều khoản cụ thể, có ngữ cảnh riêng.
- **Type (Canonical Concept):** Khái niệm pháp lý chung mà nhiều Local Mention cùng nói đến.

Nếu không phân biệt, graph sẽ rơi vào một trong hai bệnh:
- **Supernode:** Gom tất cả mentions cùng loại vào một node → node đó có hàng trăm cạnh, normative relations từ nhiều context khác nhau bị trộn vào một chỗ.
- **Graph Fragmentation:** Mỗi mention là một node riêng → graph bị đứt gãy, không tra cứu được "DTTS" theo nghĩa khái niệm.

### 2.2 Tranh luận về Taxonomy Depth

Qua quá trình nghiên cứu (trao đổi với Gemini và phản biện lại bởi ChatGPT), đã có một tranh luận quan trọng về độ sâu taxonomy:

**Gemini đề xuất ban đầu:** MaxDepth = 2 (Root → Category → Subtype), sau đó bổ sung facets cho các đặc tính như EthnicMinority.

**Phản biện:** MaxDepth = 2 là luật cứng không có cơ sở kỹ thuật. Có trường hợp Depth 1 đủ, có trường hợp Depth 3 mới đủ, có trường hợp không nên subclass mà chỉ cần property/facet.

**Giải pháp chốt:** Thay bằng **Granularity Test** — chỉ tạo subtype khi sự phân biệt đó thay đổi ít nhất 1 trong 5 thứ:
1. Normative relation (quyền/nghĩa vụ/cấm đoán khác nhau)
2. Domain/Range của quan hệ
3. Competency Question mà graph cần trả lời
4. Canonical identity (có thể merge hay không)
5. Retrieval partition (GraphRAG phân vùng)

Nếu không thay đổi gì → property/facet, không phải class.

### 2.3 Tranh luận về vị trí Condition/Exception

Đây là lỗi architecture quan trọng nhất bị phát hiện trong quá trình nghiên cứu.

**Gemini (và nhiều bản spec ban đầu) đề xuất:**
```
LegalSubject ──ALLOW──> LegalAction
LegalAction ──HAS_CONDITION──> Condition
```

**Phản biện (ChatGPT reviewer):**
> Condition thường không bổ nghĩa cho Action mà bổ nghĩa cho normative assertion.  
> Ví dụ: Cùng action "chuyển nhượng" xuất hiện trong Rule 1 (ALLOW, condition C1), Rule 2 (PROHIBIT, condition C2), Rule 3 (REQUIRE, condition C3). Nếu gắn condition vào Action thì C1, C2, C3 bị trộn lẫn — không còn biết điều kiện nào thuộc quy tắc nào.

**Giải pháp chốt:** NormAssertion node để giữ toàn bộ normative context trong cùng một frame:
```
NormAssertion
  ├── HAS_SUBJECT  → LocalMention (LegalSubject)
  ├── HAS_ACTION   → LocalMention (LegalAction)
  ├── HAS_CONDITION → Condition        ← đúng: gắn vào Norm
  ├── HAS_EXCEPTION → Exception        ← đúng: gắn vào Norm
  └── HAS_CONSEQUENCE → LegalConsequence
```

### 2.4 Tranh luận về INSTANCE_OF vs DENOTES

**Gemini đề xuất ban đầu:**
```
LocalSubject ──INSTANCE_OF──> CanonicalConcept
```

**Phản biện:** INSTANCE_OF đúng nếu LocalSubject là instance của class. Nhưng nếu nó chỉ là một lần xuất hiện/cụm từ trong văn bản, DENOTES sát nghĩa hơn — phân biệt rõ giữa lexical mention và canonical concept trong semantic modeling. Sự khác biệt này quyết định sau này concept và mention có bị trộn vào nhau hay không.

> **Lưu ý:** DENOTES không phải một property chuẩn của SKOS (SKOS dùng các quan hệ như `skos:broader`, `skos:narrower`, `skos:exactMatch`...). Đây là quan hệ nội bộ của mô hình M7, lấy cảm hứng từ sự phân biệt lexical mention/concept trong semantic modeling; không phải SKOS property chuẩn.

**Giải pháp chốt:**
```
LocalMention ──DENOTES──> CanonicalConcept
```

### 2.5 Tranh luận về Neo4j Multi-label

**Gemini đề xuất:** Multi-label là ontology hierarchy, có thể "nhanh hơn property 10 lần".

**Phản biện:** Neo4j label ≠ ontology hierarchy. Label là cách vật hóa classification để truy vấn thuận tiện, không phải bản thân semantic model. Về hiệu năng, phải benchmark trên workload thực tế — với corpus ~222 nodes hiện tại, chưa phải bottleneck cần tối ưu.

**Giải pháp chốt:** Multi-label là Layer 6 (Neo4j Projection), tách hoàn toàn khỏi ontology model. Neo4j labels được materialize từ semantic classification theo nhu cầu truy vấn; không được coi là canonical ontology definition.

---

## 3. Kiến trúc Chốt Cuối (Architecture Freeze)

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
         VD: doc_chuong-iii_dieu-48_khoan-2_p520#SUBJECT#1
         Chứa: raw_text, semantic_type, subtype, provenance_node_id, evidence
              ↓
Layer 4: CANONICAL CONCEPT HUB
         MERGE semantics — mỗi canonical concept có một ID duy nhất
         trong ontology namespace/version hiện tại (LO2024.Ch3.*)
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

---

## 4. Cấu trúc Triển Khai

### Pipeline (100% rule-based, 0 LLM)

```
M6 semantic_extraction.json
        │
        ▼
[ entity_normalizer ]         Semantic Role Audit
                              VALID / CORRECTED / UNRESOLVED
                              PERMISSION/OBLIGATION → skip (không tạo entity class)
        │
        ▼
[ relation_normalizer ]       ALLOW/REQUIRE/PROHIBIT → NormativeModality context
                              PERMISSION/OBLIGATION entity → modality extraction
        │
        ▼
[ canonical_mapper ]          DENOTES edges
                              MERGE semantics cho Concept Hub
        │
        ▼
[ norm_builder ]              Quyết định: simple edge hay NormAssertion?
                              Tiêu chí: cần context frame riêng để bảo toàn
                              association giữa modality, subject, action/object
                              và modifiers (condition/exception/consequence/joint subject)
                              v1 triggers: condition | exception | consequence | joint subject
                              Boolean logic v1: flat AND/OR
        │
        ▼
[ reference_resolver ]        Relative: "khoản này", "điểm b khoản này"
                              Absolute: "Điều 27", "khoản 2 Điều 48"
                              Unresolved → FLAG, không silent drop
        │
        ▼
[ ontology_validator ]        Tầng 1: Structural invariants
                              Tầng 2: Domain-Range matrix
                              REJECT + log (không âm thầm xóa data)
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
├── reference_resolver.py       Physical Graph traversal
├── ontology_validator.py       Domain-Range + invariant checks
├── ontology_builder.py         Pipeline orchestrator
└── configs/
    ├── taxonomy_registry.yaml  Controlled taxonomy (Granularity Test)
    ├── concept_registry.yaml   Canonical Concepts (GENERATED_DRAFT corpus Ch3)
    ├── mapping_rules.yaml      Phrase trigger → subtype + concept_id
    ├── relation_rules.yaml     Modality normalization + domain-range
    └── reference_rules.yaml   9 regex patterns cho references
```

---

## 5. Domain-Range Matrix (Invariant)

> **Lưu ý đọc bảng:** Các node semantic thực tế trong graph là **LocalMention** — không phải class node `LegalSubject` hay `LegalAction` standalone. `LegalSubject` trong bảng dưới đây là viết tắt của `LocalMention [semantic_type=LegalSubject]`. Neo4j mới materialize chúng thành labels `(:LegalSubject:DomesticEntity:EthnicMinority)`. Không để nhầm class với instance node.

```
Ontology Type       LegalSubject / LegalAction / ...
      ↓
Local Mention       LocalMention [semantic_type=LegalSubject]
      ↓
Neo4j Label         (:LegalSubject:Authority:CentralAuthority)
```

### Simple norm (direct edge)

| Relation | Source | Target |
|----------|--------|--------|
| `ALLOW` | `LocalMention [LegalSubject]` | `LocalMention [LegalAction]` |
| `REQUIRE` | `LocalMention [LegalSubject]` | `LocalMention [LegalAction]` |
| `PROHIBIT` | `LocalMention [LegalSubject]` | `LocalMention [LegalAction]` |
| `HAS_OBJECT` | `LocalMention [LegalAction]` hoặc `NormAssertion` | `LocalMention [LegalObject]` |
| `DENOTES` | `LocalMention` | `CanonicalConcept` |
| `REFERENCES` | `LocalMention [Reference]` hoặc reference-bearing Mention | `Physical Node ID` |
| `PROVENANCE` | `LocalMention` / `NormAssertion` | `Physical Node ID` |

> **REFERENCES ≠ PROVENANCE:** `REFERENCES` = mention này *nói đến* node vật lý nào (dẫn chiếu). `PROVENANCE` = mention này *xuất phát từ* node vật lý nào (nguồn gốc). Hai relation này phân biệt rõ và không thể dùng thay thế nhau.

### Complex norm (NormAssertion)

| Relation | Source | Target |
|----------|--------|--------|
| `HAS_SUBJECT` | `NormAssertion` | `LocalMention [LegalSubject]` |
| `HAS_ACTION` | `NormAssertion` | `LocalMention [LegalAction]` |
| `HAS_OBJECT` | `NormAssertion` | `LocalMention [LegalObject]` |
| `HAS_CONDITION` | `NormAssertion` | `LocalMention [Condition]` |
| `HAS_EXCEPTION` | `NormAssertion` | `LocalMention [Exception]` |
| `HAS_CONSEQUENCE` | `NormAssertion` | `LocalMention [LegalConsequence]` |

> **Về HAS_CONDITION:** Trong mô hình M7 đã chọn, `HAS_CONDITION` được gắn vào `NormAssertion` để bảo toàn association giữa điều kiện và quy phạm cụ thể — không mặc định gắn trực tiếp vào `LegalAction`. Điều này là design rule của M7 dựa trên bài toán cross-context pollution, không phải tuyên bố rằng mọi ontology pháp lý đều cấm `Action → Condition`.

---

## 6. Kết Quả Chạy Thử (Run Results)

**Input:** `semantic_extraction.json` (179 nodes từ M6 minh_fix_bug)  
**Chạy:** `python -X utf8 run_ontology_builder.py`

```
══════════════════════════════════════════════════
MODULE 7 — VALIDATION REPORT
══════════════════════════════════════════════════
  LocalMentions  : 916
    VALID        : 555   (60.6%)
    CORRECTED    : 331   (36.1%)
    UNRESOLVED   : 30    ( 3.3%)
  NormAssertions : 102   (tất cả structural VALID)
  CanonicalConc. : 13    concepts được DENOTES tới
  Edges          : 1182
    REJECTED     : 32
  References     : 41/70 resolved
    UNRESOLVED   : 29    ← chưa có Physical Graph M4
══════════════════════════════════════════════════
```

> **Diễn giải đúng kết quả (quan trọng cho evaluation sau này):**
> - **331 CORRECTED** = rule-based correction đã chạy và apply rule. Chưa phải bằng chứng 331 case đều đúng về mặt pháp lý; cần golden set để xác nhận precision.
> - **102 NormAssertions VALID** = structural validation pass (schema, provenance đầy đủ). Không có nghĩa 102 quy phạm đã được xác nhận đúng hoàn toàn về ngữ nghĩa pháp lý.
> - **32 REJECTED** = validator phát hiện 32 violations theo constraint hiện hành. Đây là candidate violations cần manual review; chưa kết luận chắc chắn 100% là lỗi M6 cho đến khi golden set xác nhận.
> - **41/70 resolved** = Reference Resolver xử lý được 41/70 references mà không có Physical Graph. Không phải upper bound thực tế.

### Ví dụ LocalMention output (từ canonical_semantic_graph.json)

```json
{
  "id": "doc_chuong-iii_muc-1_dieu-26_khoan-4_p521#SUBJECT#1",
  "mention_type": "SUBJECT",
  "raw_text": "Nhà nước",
  "semantic_type": "LegalSubject",
  "subtype": "CentralAuthority",
  "canonical_concept_id": "CONCEPT_STATE",
  "provenance_node_id": "doc_chuong-iii_muc-1_dieu-26_khoan-4_p521",
  "evidence": "Được Nhà nước hướng dẫn và giúp đỡ trong việc cải tạo, phục hồi đất nông nghiệp.",
  "status": "CORRECTED",
  "audit_note": "[RULE_MAP_S04] Auto-corrected: 'Nhà nước' → subtype=CentralAuthority, concept=CONCEPT_STATE",
  "neo4j_labels": ["LegalSubject", "Authority", "CentralAuthority"]
}
```

---

## 7. Vấn Đề Phát Hiện & Hướng Xử Lý

### A. 32 Edges bị Reject — Candidate M6 Extraction Violations

Validator phát hiện 32 violations theo domain-range constraints hiện hành:
- `ALLOW → OBJECT` (vi phạm: ALLOW chỉ đến LocalMention [LegalAction])
- `HAS_OBJECT` từ LocalMention [SUBJECT] (vi phạm: phải từ LegalAction hoặc NormAssertion)

**Ví dụ bị reject:**
```
doc_..._dieu-27_khoan-3_diem-b_p2794#SUBJECT#1 ──ALLOW──> #OBJECT#1
→ ALLOW target có semantic_type=LegalObject nhưng cần LegalAction
```

**Hypothesis (chưa confirmed):** M6 có thể đã gán ALLOW thẳng tới danh sách các quyền (OBJECT) thay vì hành vi (ACTION). Cần golden set / manual review để xác nhận đây thực sự là M6 error hay là edge case hợp lệ nằm ngoài domain-range hiện tại.

**Hướng xử lý tiếp:** Sau khi xác nhận bằng golden set → bổ sung rule trong `relation_normalizer` để auto-correct pattern `ALLOW → OBJECT` thành `ALLOW → ACTION + HAS_OBJECT → OBJECT`.

### B. 29 Unresolved References — Thiếu Physical Graph M4

Reference Resolver cần Physical Graph để traverse cây `parent_id`. Hiện tại chưa cung cấp `physical_graph.json`.

**Hướng xử lý tiếp:** Chạy lại `run_ontology_builder.py` với `physical_graph_path` trỏ đúng vào file M4 output.

```python
physical_graph_path = "outputs/physical_graphs/physical_graph.json"
```

### C. 30 UNRESOLVED Mentions — Semantic Role Conflict

Pattern điển hình: M6 gán SUBJECT cho "hợp đồng chuyển nhượng" (grammatical subject ≠ LegalSubject). Validator đã flag đúng nhưng không auto-correct vì confidence MEDIUM.

**Hướng xử lý tiếp:** Review thủ công 30 mentions. Nếu pattern lặp lại nhiều lần → bổ sung rule FLAG → CORRECT với confidence cụ thể hơn.

---

## 8. Semantic Contract — Invariant Bất Biến

Phần này định nghĩa M7 như một **semantic contract** chứ không chỉ là tài liệu code. Các invariant dưới đây phải luôn đúng trong bất kỳ version nào của pipeline.

### R1–R9: Modeling Rules

| Rule | Phát biểu | Trạng thái |
|------|-----------|----------|
| **R1** | `CanonicalConcept` không mang normative edges (`ALLOW/REQUIRE/PROHIBIT/HAS_CONDITION...`) | ✅ 0 violations |
| **R2** | Mọi `LocalMention` phải có `provenance_node_id` trỏ về một `PhysicalNode` cụ thể | ✅ Pydantic enforce |
| **R3** | `LocalMention` chỉ được DENOTES tới `CanonicalConcept`, không dùng INSTANCE_OF | ✅ Validated |
| **R4** | Normative context (`modality + condition + exception + consequence`) không được đặt trên `CanonicalConcept` | ✅ Enforced |
| **R5** | `Condition/Exception/Consequence` thuộc `NormAssertion` khi chúng là modifiers của một specific norm (M7 design rule, không phải chân lý phổ quát của mọi ontology) | ✅ 102 norms đúng |
| **R6** | `REFERENCES ≠ PROVENANCE`: `REFERENCES` = mention dẫn chiếu đến node vật lý nào; `PROVENANCE` = mention xuất phát từ node vật lý nào | ✅ Phân biệt trong schema |
| **R7** | Neo4j labels là projection layer, không phải canonical ontology definition | ✅ Layer 6 tách biệt |
| **R8** | M6 extraction labels (SUBJECT/ACTION/...) không được tự động coi là canonical semantic role; phải qua Semantic Role Audit | ✅ entity_normalizer |
| **R9** | Unresolved semantic/reference cases phải được giữ trạng thái `UNRESOLVED` + logged; không được silently drop | ✅ 30+29 flagged |

---

## 9. Quyết Định Thiết Kế Quan Trọng (Design Decisions)

| Quyết định | Lý do |
|-----------|-------|
| 100% rule-based, 0 LLM | Chi phí, tốc độ, deterministic — phù hợp với downstream GraphRAG pipeline |
| Không materialize OWL/RDF | M7 implementation hiện tại dùng Pydantic + YAML registry + Neo4j-oriented graph vì phù hợp với scope và downstream architecture. OWL/RDF không nằm trong scope implementation hiện tại (không phải claim "OWL/RDF không cần thiết"). |
| Taxonomy từ YAML (không hard-code Python) | Dễ mở rộng mà không phải sửa code |
| NormAssertion khi cần context frame riêng | Tránh cross-context pollution; v1 triggers: condition/exception/consequence/joint subject |
| Boolean logic v1: flat AND/OR | Nested logic xuất hiện ít trong corpus hiện tại, để extension sau |
| PERMISSION/OBLIGATION → modality context | M6 có entity type PERMISSION/OBLIGATION; M7 không tạo entity class cho chúng mà extract modality (ALLOW/REQUIRE) để gán vào NormAssertion |
| Neo4j multi-label là projection | Không coi label là ontology; labels được materialize theo nhu cầu truy vấn thực tế |

---

## 10. Open Questions (Cần Nghiên Cứu Tiếp)

- **Tiêu chí NormAssertion:** Hiện dùng "có condition/exception/consequence". Cần thực nghiệm xem có trường hợp simple norm nhưng vẫn cần NormAssertion để giữ context không?
- **PERMISSION/OBLIGATION trong M6:** M6 fix của Minh đã bổ sung `HAS_OBJECT` và Hohfeldian relations. Cần kiểm tra kỹ lại các entity type `PERMISSION` và `OBLIGATION` có thực sự chỉ là modality hay đôi khi cần là first-class entity (normative position).
- **Recursive Exception:** `Exception ──HAS_EXCEPTION──> Exception` — corpus thực tế có xuất hiện không? Nếu có, cần implement traversal.
- **Joint norm:** Khi A và B cùng liên đới nghĩa vụ (joint and several liability) — hai mũi tên `REQUIRE` cùng trỏ vào Norm chưa đủ để biểu diễn; cần cơ chế `JOINT/COLLECTIVE`.

---

## 11. Liên Kết

- **M6 Output (Input của M7):** `outputs/semantic_graphs/semantic_extraction.json`
- **M7 Output:** `outputs/canonical_graphs/canonical_semantic_graph.json`
- **Log:** `outputs/m7_run.log`
- **Run script:** `run_ontology_builder.py`
- **Source:** `src/ontology/`
- **Tài liệu nghiên cứu gốc:** `tong_hop_context_ontology.txt` (NCKH/)
- **Implementation Plan:** [implementation_plan.md](../../.gemini/antigravity-ide/brain/a01860be-518f-47e3-8979-05f94accb929/implementation_plan.md)

---
---

# PHẦN 2: BẢN V1.1
# Research Note: Module 7 — Ontology / Semantic Canonicalization
(Knowledge Base)

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
- 0 bugs đang mở. 3 known limitations (xem §13).
- Validation: Gate 1 (entity-level) + Gate 2 (graph-level)

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
Kiến trúc 4 tầng logic (thay thế mô hình 6 lớp cũ):

```
TẦNG A: SEMANTIC MODEL (Lớp 1 & Lớp 3 cũ)
        Định nghĩa các LegalSubject, LegalAction, LegalObject...
        Mỗi node là một LocalMention đại diện cho 1 token trong text.
        (ALLOW/REQUIRE/PROHIBIT là modality, không phải entity class)
              ↓
TẦNG B: CONTEXT MODEL (Lớp 5 cũ)
        Dùng NormAssertion để giữ đúng normative context.
        Condition/Exception/Consequence thuộc về NormAssertion, không phải Action.
              ↓
TẦNG C: QUALITY / GROUNDING (Lớp 2 cũ + 2 Gates mới)
        Controlled Taxonomy (Granularity Test).
        Gate 1 (Pre-build): Semantic Role Audit (lọc rác entity).
        Gate 2 (Post-build): Domain-Range + Invariant checks.
              ↓
TẦNG D: OUTPUT CONTRACT (Lớp 4 & Lớp 6 cũ)
        Canonical Concept Hub (MERGE semantics). LocalMention ──DENOTES──> Concept.
        Neo4j Projection Layer (Multi-label query layer).
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
[ semantic_quality_gate ]     GATE 1: Tiền kiểm tra role conflict, semantic amplification
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
[ ontology_validator ]        GATE 2: Domain-Range matrix, QUARANTINED + log (không âm thầm xóa data)
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
├── semantic_quality_gate.py    Gate 1: Pre-build validation
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
| Relation | Source | Target | object_binding |
|----------|--------|--------|----------------|
| `ALLOW` | `LocalMention [LegalSubject]` | `LocalMention [LegalAction]` | |
| `REQUIRE` | `LocalMention [LegalSubject]` | `LocalMention [LegalAction]` | |
| `PROHIBIT` | `LocalMention [LegalSubject]` | `LocalMention [LegalAction]` | |
| `HAS_OBJECT` | `LocalMention [LegalAction]` hoặc `NormAssertion` | `LocalMention [LegalObject]` | `INTRINSIC / NORM_ARGUMENT / UNRESOLVED` |
| `DENOTES` | `LocalMention` | `CanonicalConcept` | |
| `PROVENANCE` | `LocalMention` / `NormAssertion` | `Physical Node ID` | |

### Complex norm (NormAssertion)
| Relation | Source | Target |
|----------|--------|--------|
| `HAS_SUBJECT` | `NormAssertion` | `LocalMention [LegalSubject]` |
| `HAS_ACTION` | `NormAssertion` | `LocalMention [LegalAction]` |
| `HAS_OBJECT` | `NormAssertion` | `LocalMention [LegalObject]` |
| `HAS_CONDITION` | `NormAssertion` | `LocalMention [Condition]` |
| `HAS_EXCEPTION` | `NormAssertion` | `LocalMention [Exception]` |
| `HAS_CONSEQUENCE` | `NormAssertion` | `LocalMention [LegalConsequence]` |

## §10. Semantic Contract (R1-R12)
| Rule | Phát biểu | Nguồn |
|------|-----------|-------|
| **R1** | `CanonicalConcept` không mang normative edges (`ALLOW/REQUIRE/PROHIBIT/HAS_CONDITION...`) | Note cũ |
| **R2** | Mọi `LocalMention` phải có `provenance_node_id` trỏ về một `PhysicalNode` cụ thể | Note cũ |
| **R3** | `LocalMention` chỉ được DENOTES tới `CanonicalConcept`, không dùng INSTANCE_OF | Note cũ |
| **R4** | Normative context không được đặt trên `CanonicalConcept` | Note cũ |
| **R5** | `Condition/Exception/Consequence` thuộc `NormAssertion` khi chúng là modifiers của một specific norm | Note cũ |
| **R6** | M7 chỉ phân loại scope reference, không resolve tới Physical Node | Note cũ |
| **R7** | Neo4j labels là projection layer, không phải canonical ontology definition | Note cũ |
| **R8** | M6 extraction labels phải qua Semantic Role Audit, sai role → QUARANTINED | Note cũ |
| **R9** | Unresolved semantic/reference cases phải được giữ trạng thái `UNRESOLVED` hoặc `QUARANTINED` + logged; không được silently drop | Note cũ |
| **R10** | **No Semantic Amplification** — M7 không tự tạo fact ngoài evidence | Thêm ngày 2026-09-21 |
| **R11** | **Quarantine Isolation** — Quarantine data tách khỏi Active data | Thêm ngày 2026-09-21 |
| **R12** | **Provenance ≠ Reference** — 2 relation khác nhau, không thay thế | Thêm ngày 2026-09-21 |

## §11. Run Results

### §11.1 Số liệu qua các version
| Ngày | Version | Mentions | Norms | Concepts | Edges | Notes |
|------|---------|----------|-------|----------|-------|-------|
| 2026-09-19 | v0.5 | 916 | 102 | 13 | 1182 (32 REJECTED) | Bản đầu |
| 2026-09-21 | v1.0 | 846+70 | 102 | 13 | 1141 (32Q) | Fix Bug 2 (QUARANTINED edges) |
| 2026-09-21 | v1.0-fix | 846+70 | 102 | 13 | 1141 (32Q) | Fix Bug 1 (mapping rules), 1 node QUARANTINED, 32 edges QUARANTINED |

### §11.2 Verification Log (2026-09-21)
- **Verify 1:** 1 quarantined mention (text rỗng)
- **Verify 2:** 19/32 concepts match — OK, do corpus Ch3-LDD chưa phủ hết (như Giao đất, Thu hồi đất).
- **Verify 3:** INTRINSIC = 0, UNRESOLVED = 48
- **Verify 4:** 331 CORRECTED, 100% là CONCEPT_MAP (sạch, không có role fix bẻ cong semantics)
- **Verify 5:** Gate 1 vs Gate 2 boundary rõ ràng, không duplicate.

### §11.3 3 Insights từ Verify
**Insight V1 — Gate 1 bắt được role conflict ở entity level qua keyword.**
> Khi verify bằng sample 20 active SUBJECT mentions, 100% là LegalSubject chuẩn. Case "hợp đồng as SUBJECT" bị bắt bởi Gate 1 rule-based (keyword `hợp đồng`) → set UNRESOLVED → Gate 2 đẩy vào Quarantine.
> **Ý nghĩa:** M7 v1 thực sự bảo vệ active graph khỏi grammatical-subject confusion, dù cơ chế là keyword-based, không phải semantic reasoning.

**Insight V2 — INTRINSIC wrapped in UNRESOLVED.**
> Khi sample 20 UNRESOLVED edges, nhiều case thực chất là INTRINSIC (VD: `Chuyển nhượng → QSDĐ`). Heuristic V1 quá conservative nên gom hết vào UNRESOLVED.
> **Ý nghĩa:** V1 an toàn (không suy diễn sai), nhưng M8 sẽ cần heuristic riêng để phân biệt INTRINSIC vs ambiguous.

**Insight V3 — 1 UNRESOLVED mention = Bug 1 đã được fix.**
> Mention UNRESOLVED duy nhất (text là "Người mua tài sản... trong hợp đồng thuê đất") chính là case Bug 1 — M6 gán SUBJECT cho grammatical subject. Gate 1 bắt đúng.
> **Ý nghĩa:** Bug 1 fix thực sự, không phải bug bị miss. Chỉ có 1 case trong corpus Ch3-LDD → không phải systemic issue.

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

### Bug B03: `neo4j_labels` hardcoded — architectural gap và DB coupling
**Phát hiện:** 2026-09-23
**Mức độ:** Design smell nghiêm trọng (không phải runtime bug, nhưng là silent inconsistency trap)

**Triệu chứng:**
- Output JSON có field `neo4j_labels` — nghe như M7 biết về Neo4j (DB coupling).
- Cụ thể hơn: `entity_normalizer.py` chứa dict hardcode `_TAXONOMY_TO_NEO4J_LABELS` với 16 entries, là bản copy thủ công của cây taxonomy.
- `taxonomy_registry.yaml` **chưa bao giờ được load** vào `EntityNormalizer` — file chỉ được load ở nơi khác, không phải nơi sinh labels.

**Root cause (3 tầng):**

*Tầng 1 — Tên field sai:*
`neo4j_labels` nghe như "nhãn dành riêng cho Neo4j" → M7 bị coi là coupling với database. Nhưng bản chất thông tin này là semantic path (đường dẫn phân cấp), không phải DB-specific.

*Tầng 2 — Architectural gap:*
`taxonomy_registry.yaml` định nghĩa cây phân cấp nhưng `entity_normalizer.py` không load file này. Người code biết phải dùng thông tin từ cây, nhưng thay vì load file, họ copy-paste thủ công vào dict Python → tạo ra 2 nguồn sự thật song song.

*Tầng 3 — Silent inconsistency trap:*
Khi thêm subtype mới vào `taxonomy_registry.yaml`, dict Python không tự update → type_hierarchy của subtype mới sẽ fallback về core label duy nhất, không có hierarchy. Không có warning, không có error. Chỉ phát hiện khi verify output kỹ.

**Phân tích: Ai chịu trách nhiệm sinh `type_hierarchy`?**
- M7 lo semantic canonicalization → M7 biết taxonomy → M7 nên output semantic path.
- M9 lo database → M9 đọc path → M9 quyết định dùng làm gì (Neo4j label, ArangoDB collection...).
- **Vậy M7 PHẢI output path, nhưng với tên semantic, không phải tên DB.**

**Insight từ bug này — Nguyên tắc "Single Source of Truth" trong kiến trúc:**
Đây là ví dụ điển hình của "shotgun surgery" anti-pattern: một quyết định thiết kế (taxonomy hierarchy) phải được thay đổi ở nhiều chỗ đồng thời (`taxonomy_registry.yaml` + `_TAXONOMY_TO_NEO4J_LABELS` dict). Nguyên tắc fix: bất kỳ thông tin nào chỉ được sống ở 1 chỗ — mọi nơi khác phải derive từ chỗ đó.

**Fix (2026-09-23):**
1. Xóa `_TAXONOMY_TO_NEO4J_LABELS` dict khỏi `entity_normalizer.py`.
2. Thêm load `taxonomy_registry.yaml` vào `_load_configs()` — `EntityNormalizer` lần đầu tiên thực sự đọc file taxonomy.
3. Thêm `_build_type_hierarchy()` + `_find_path_in_tree()` — DFS walk cây động.
4. Rename field `neo4j_labels` → `type_hierarchy` trong `schemas.py` và toàn bộ pipeline.
5. Chạy lại → số liệu giữ nguyên (845 nodes, 1109 edges, 102 norms). Output mới:
   - `"Nhà nước"` → `type_hierarchy: ["LegalSubject", "Authority", "CentralAuthority"]`
   - `"Đất nông nghiệp"` → `type_hierarchy: ["LegalObject", "PhysicalLand", "AgriculturalLand"]`

**Trạng thái:** ✅ Fixed
**Bài học:** Đừng trust field name nếu chưa đọc code. "neo4j_labels" nghe như coupling nhưng root cause là architectural gap (taxonomy_registry.yaml bị bypass). Fix tên field mà không fix cơ chế là chữa triệu chứng, không chữa bệnh.


## §13. Known Limitations (Báo cáo hội đồng)

**Limitation 1: M7 hiện chỉ bắt semantic role conflict ở edge level và rule-based entity level.**
- Dù đã có Gate 1 (rule-based) để lọc các "hợp đồng as SUBJECT", nhưng bản chất Gate 1 vẫn bị phụ thuộc vào danh sách từ khóa cố định (`hợp đồng`, `giấy chứng nhận`...). Case M6 gán SUBJECT sai từ một từ khóa lạ mà không sinh edge vi phạm domain-range sẽ không bị bắt.
- *Hướng giải quyết cho v2:* Cần rule entity-level role check thông minh hơn (dùng embedding) hoặc kết hợp context check chéo từ M8.

**Limitation 2: object_binding INTRINSIC chưa fire.**
- Do V1 heuristic quá conservative (thận trọng), mọi object nằm ngoài `NormAssertion` đều bị ép xuống trạng thái `UNRESOLVED` thay vì `INTRINSIC`, kể cả các quan hệ nội tại hiển nhiên như `Chuyển nhượng` -> `Quyền sử dụng đất`.
- *Hướng giải quyết cho v2:* Xây dựng một classifier phụ hoặc bảng từ điển quy định cặp động từ - tân ngữ nào là intrinsic.

**Limitation 3: 19/32 concepts chưa match.**
- Sự chênh lệch này là do corpus thử nghiệm (Chương 3 LĐĐ 2024) không cover hết toàn bộ các nhóm đối tượng (ví dụ: Giao đất, thu hồi đất là của Nhà nước - nằm ở các chương quản lý).
- *Hướng giải quyết cho v2:* Chấp nhận trong V1. Khi mở rộng sang toàn bộ luật, các concept này sẽ match đầy đủ.

## §14. Open Problems (Chưa giải quyết)
- **Tiêu chí NormAssertion:** Hiện dùng "có condition/exception/consequence". Cần thực nghiệm xem có trường hợp simple norm nhưng vẫn cần NormAssertion để giữ context không?
- **PERMISSION/OBLIGATION trong M6:** M6 fix của Minh đã bổ sung `HAS_OBJECT` và Hohfeldian relations. Cần kiểm tra kỹ lại các entity type `PERMISSION` và `OBLIGATION` có thực sự chỉ là modality hay đôi khi cần là first-class entity (normative position).
- **Joint norm:** Khi A và B cùng liên đới nghĩa vụ (joint and several liability) — hai mũi tên `REQUIRE` cùng trỏ vào Norm chưa đủ để biểu diễn; cần cơ chế `JOINT/COLLECTIVE`.

## §15. Idea Backlog (Ý tưởng cho v2)
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

## §16. Evolution Log
- **2026-09-15:** Prototype v0.1 (3 module cơ bản)
- **2026-09-17:** v0.5 (thêm NormAssertion, 3 status)
- **2026-09-19:** v1.0 (freeze schema, 4 status, 32 concept)
- **2026-09-21:** v1.0-fix (fix 2 bugs, 3 known limitations)
- **2026-09-21:** v1.0-frozen (verify 5 điểm, chính thức freeze)
- **2026-09-23:** v1.1 (Bug B03: xóa hardcoded dict, thêm DFS walk tree, rename `neo4j_labels` → `type_hierarchy` — single source of truth)
- **2026-09-24:** v1.1 — Fix Bug B04: REFERENCE_TO dead code trong relation_normalizer. Thêm explicit skip, xóa dead config. **Tạm freeze v1.1.**

### §16.1 Trạng thái Freeze v1.1 (2026-09-24)

**Số liệu chốt:**
- 846 LocalMentions, 70 ReferenceMentions, 102 NormAssertions, 13 CanonicalConcepts
- 1141 Edges (1109 active + 32 QUARANTINED)
- 58/70 References classified (12 AMBIGUOUS)

**Đã fix trong v1.1 (so với v1.0-frozen):**
- Bug B03: `neo4j_labels` → `type_hierarchy` (single source of truth từ taxonomy_registry.yaml)
- Bug B04: Dead code `REFERENCE_TO` trong relation_normalizer

**Tạm freeze để chờ:**
1. Nâng cấp mô hình M6 (GPT-4o-mini → model tốt hơn khi có ngân sách) — sẽ giảm số edges QUARANTINED do LLM skip tắt SUBJECT→OBJECT.
2. Tích hợp các cải tiến từ bản M7 của Dương (NodeQualityFilter, orphan pruning, evidence validation) và Minh (Fuzzy Matching, alias collision detection) — làm sau khi M8 ổn định.
3. Mở rộng corpus sang toàn bộ Luật Đất đai 2024 để đo số liệu chính thức cho luận văn.

## §17. Liên kết & Tài nguyên
- **M6 Output (Input của M7):** `outputs/semantic_graphs/semantic_extraction.json`
- **M7 Output:** `outputs/canonical_graphs/canonical_semantic_graph.json`
- **Log:** `outputs/m7_run.log`
- **Audit CSV:** `outputs/m7_audit_log.csv`
- **Run script:** `run_ontology_builder.py`
- **Source:** `src/ontology/`
- **Tài liệu nghiên cứu gốc:** `tong_hop_context_ontology.txt` (NCKH/)
- **Implementation Plan:** `implementation_plan.md`
