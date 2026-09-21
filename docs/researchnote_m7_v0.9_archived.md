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
