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
