# Research Note: Module 7 — Ontology / Semantic Canonicalization (Knowledge Base) v1.2

**Ngày cập nhật:** 2026-09-24  
**Tác giả:** Lâm, Minh, Dương (Tổng hợp và tối ưu)  
**Trạng thái:** ✅ Pipeline V1.2 hoàn chỉnh, đã tích hợp các tinh hoa từ 3 phiên bản M7.

---

# TẦNG A — TL;DR (Snapshot & Luồng Logic)

## §0. Snapshot
**Trạng thái hiện tại:** v1.2 (Đã tích hợp các module filter/quarantine tối ưu)
**Số liệu mới nhất (v1.2):**
- 816 LocalMentions (Active nodes) + 70 ReferenceMentions
- 102 NormAssertions
- 13 CanonicalConcepts
- 1109 Edges (Active edges)
- Quarantine: 30 mentions (29 orphans + 1 unresolved text rỗng), 32 edges
- NodeQualityFilter blocked: 16 garbage nodes.

**Kiến trúc lõi:** Dựa trên Semantic Architecture của Lâm (Type-Token separation, NormAssertion), kết hợp Graph Hygiene của Dương (NodeQualityFilter, Evidence Validation, Orphan Handling) và Alias Handling của Minh (Boot-time Alias Collision Detection).

## §1. Luồng logic hoạt động M7 hiện tại (Pipeline v1.2)

Pipeline hiện tại tuân thủ nghiêm ngặt nguyên tắc **Single Source of Truth** và **Preserve Data (Không xóa dữ liệu, chỉ Quarantine)**:

```text
M6 semantic_extraction.json
        │
        ▼
[ node_quality_filter ]       (TỪ DƯƠNG) Lọc rác đầu vào (text rỗng, evidence rỗng, orphan relations). Block ngay các garbage nodes tránh crash.
        │
        ▼
[ entity_normalizer ]         Semantic Role Audit (VALID / CORRECTED / QUARANTINED / UNRESOLVED).
                              (TỪ MINH) Kèm Boot-time Alias Collision Detection để phát hiện conflict cấu hình.
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
[ orphan_quarantine ]         (TỪ DƯƠNG - ADAPTED) Quét các mention không có active edge (degree = 0). 
                              Chuyển vào Quarantine thay vì xóa vật lý.
        │
        ▼
canonical_semantic_graph.json
```

---

# TẦNG B — ĐÁNH GIÁ 3 PHIÊN BẢN M7 & BÀI TOÁN TÍCH HỢP

Qua quá trình phát triển song song, nhóm có 3 bản M7 mang 3 triết lý thiết kế khác nhau:

## §2. Phân tích 3 triết lý M7
1. **Lâm (Semantic-First):** 
   - **Mạnh:** Kiến trúc tốt nhất. Phân tách rõ Ràng LocalMention (Token) và CanonicalConcept (Type). Dùng NormAssertion để bảo toàn Context (Condition/Exception) không bị cross-pollution.
   - **Yếu:** Thiếu các lớp bảo vệ (Graph Hygiene) khi dữ liệu đầu vào từ LLM (M6) quá bẩn.
2. **Minh (Coverage-First):**
   - **Mạnh:** Xử lý Entity Canonicalization cực tốt. Sử dụng Fuzzy Match có class-constraint và Boot-time Alias Collision Detection để phát hiện các khái niệm chồng chéo.
   - **Yếu:** Gộp chung Type/Token khiến Normative Context bị vỡ nát. Merge evidence thành chuỗi string làm mất hoàn toàn Provenance (nguồn gốc).
3. **Dương (Quality-First):**
   - **Mạnh:** Sanitation (vệ sinh đồ thị) cực tốt. Dùng NodeQualityFilter và EdgeQualityFilter để chặn đứng placeholder text, null, NaN. 
   - **Yếu:** Triết lý "Orphan Pruning" - xóa thẳng tay các node độ bậc 0 (degree 0). Điều này vi phạm nguyên lý bảo toàn chứng cứ pháp lý (một khái niệm hiếm có thể đứng một mình nhưng vẫn hợp lệ).

## §3. Quyết định tích hợp (The Best of Both Worlds)

Kết luận cốt lõi: **Không tạo ra một "quái vật Frankenstein".** Giữ nguyên kiến trúc của Lâm làm base (vì nó giải quyết đúng bài toán Semantic/Legal GraphRAG), và chỉ cấy ghép các component xử lý luồng dữ liệu (pipeline components) của Minh và Dương.

**Các component ĐÃ TÍCH HỢP (v1.2):**
1. **NodeQualityFilter (Dương):** Đặt ở vị trí đầu tiên của Pipeline. Xử lý triệt để các node rỗng, evidence rỗng, ID thiếu từ M6. Không overlap với Gate 1 (vì Gate 1 kiểm tra logic ngữ nghĩa, còn NodeQualityFilter kiểm tra tính toàn vẹn cấu trúc).
2. **Evidence Validation (Dương):** Đã tích hợp vào NodeQualityFilter. Cụ thể hóa bằng hàm quét exact-match danh sách placeholders (`n/a`, `unknown`, `...`, `không có`). Đã test không có false positive.
3. **Orphan Quarantine (Adapted từ Dương):** Dương sử dụng "Orphan Pruning" (xóa data). Trong v1.2, tính năng này được cấy vào cuối pipeline nhưng đổi thành **Orphan Quarantine** — Đẩy các LocalMention không có cạnh active vào QuarantineStore với lý do `ORPHAN_NO_ACTIVE_EDGE`. Tuân thủ nguyên tắc: *Quarantine, không Delete*.
4. **Boot-time Alias Collision Detection (Minh):** Bổ sung vào lúc khởi tạo `entity_normalizer.py`. Cảnh báo ngay lập tức nếu một Trigger (ví dụ: `"sổ đỏ"`) trỏ đến 2 rules khác nhau. Đã phát hiện và bóc tách thành công 2 conflict thật trong registry.

**Các component TỪ CHỐI / HOÃN tích hợp:**
1. **Edge Evidence Merge (Minh) — TỪ CHỐI:** Minh gom chung các evidence của cùng một cạnh xuất hiện ở nhiều điều khoản thành 1 string. Bị từ chối vì kiến trúc của Lâm đã giải quyết vấn đề này qua `LocalMention` và `provenance_node_id` riêng biệt. Gom chuỗi sẽ làm mất nguồn gốc vật lý (physical node provenance).
2. **Orphan Pruning (Xóa Data) (Dương) — TỪ CHỐI:** Vi phạm quy tắc R11 (Quarantine Isolation) và R10 (No Semantic Amplification). Data hiếm (xuất hiện 1 lần) không đồng nghĩa là data rác.
3. **Fuzzy Matching 2-Tier (Minh) — HOÃN LẠI:** Cần viết lại phần track top-2 trong cùng một class constraint pool để tránh false match. Sẽ tích hợp ở v2.0.

---

# TẦNG C — KEY INSIGHTS (BÀI HỌC RÚT RA DÀNH CHO LUẬN VĂN)

Qua quá trình cọ xát kiến trúc này, M7 đã đúc kết được các triết lý thiết kế cốt lõi cho một Legal Knowledge Graph:

## 1. Preserve Data ≠ Participate in Reasoning
Một hệ thống Knowledge Graph không bao giờ được âm thầm xóa bỏ (delete) thông tin sinh ra từ các hệ thống khai phá (LLM). Thay vào đó, nếu dữ liệu không thỏa mãn các Constraint/Shape (như SHACL), nó phải bị **Quarantine**. Node rác sẽ không tham gia vào suy luận (Reasoning) hay truy vấn RAG, nhưng nó được giữ lại để Audit, Debug và đo lường tỷ lệ Hallucination của LLM. (Sự khác biệt giữa Orphan Pruning của Dương và Orphan Quarantine của Lâm).

## 2. Hygiene là cần thiết, nhưng không thể thay thế Semantics
Dù bộ NodeQualityFilter của Dương làm sạch đồ thị rất tốt, nó không thể nhận biết được việc LLM gán `"hợp đồng chuyển nhượng"` (LegalObject) thành `LegalSubject`. Đó là lý do hệ thống cần **Defense in Depth**:
- Lớp 1: Structural Hygiene (NodeQualityFilter).
- Lớp 2: Semantic Quality Gate (Gate 1).
- Lớp 3: Domain-Range Validator (Gate 2).

## 3. Provenance (Nguồn gốc) > Evidence Merging
Trong pháp lý, "Luật Đất Đai quy định ở đâu?" quan trọng ngang với việc "Quy định điều gì?". Cách tiếp cận Type/Token của Lâm giữ được nguyên vẹn 100% Provenance của mỗi khái niệm (bằng cách sinh ra nhiều LocalMention, sau đó quy tụ qua `DENOTES` về CanonicalConcept). Nếu hợp nhất evidence sớm (như Minh làm), GraphRAG sẽ không thể cite (trích dẫn) chính xác Điều, Khoản nào đã sinh ra fact đó.

## 4. Bẫy "Single Source of Truth" trong Config
Bug B03 (Hardcode `neo4j_labels` bằng tay thay vì sinh động từ `taxonomy_registry.yaml`) là một anti-pattern (Shotgun Surgery). Việc tích hợp thêm Alias Collision Detection của Minh chính là liều thuốc giải cho căn bệnh này: Hệ thống phải tự validate bộ cấu hình của chính nó tại lúc boot (Boot-time validation) để chống lại các lỗi do con người gây ra khi quy mô taxonomy lên tới hàng nghìn entries.

---

*Tài liệu này đánh dấu sự kết thúc của Giai đoạn thiết kế và tối ưu cấu trúc M7. Module hiện tại đã được Frozen và sẵn sàng làm đầu vào cho Module 8 (Fusion Engine).*
