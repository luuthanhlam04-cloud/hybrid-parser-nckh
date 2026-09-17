# Tóm tắt Module 7: Legal Ontology Builder

Tài liệu này tóm tắt kiến trúc, luồng xử lý, và các thành phần cốt lõi của **Module 7: Legal Ontology Builder**. Module 7 có nhiệm vụ chuyển đổi đầu ra trích xuất dạng thô từ LLM (Module 6) thành một Đồ thị Tri thức Pháp lý (Canonical Semantic Graph) chuẩn tắc, tuân thủ chặt chẽ theo thiết kế **Hohfeldian V1.3** và triết lý **Edge-Level Provenance** (ngữ cảnh nằm trên cạnh).

---

## 1. Thành phần và Nội dung các file mã nguồn

Hệ thống được chia thành các file rõ ràng, đảm bảo nguyên tắc SOLID và dễ dàng bảo trì:

### Cấu hình (Configs)
- **`docs/implementation/ONTOLOGY_SPEC_V1.3.md`**: Bản đặc tả kiến trúc cốt lõi. Khẳng định hệ thống chỉ có 6 Core Classes (`LEGAL_SUBJECT`, `LEGAL_ACTION`, `CONDITION`, `EXCEPTION`, `PENALTY`, `LEGAL_DOCUMENT_REF`) và 7 loại Relations. Đặt ra quy tắc Edge-Level Provenance (Thực thể phải siêu nhẹ, bằng chứng lưu ở cạnh) và Human-in-the-loop (cơ chế cách ly).
- **`src/ontology/configs/ontology_schema.yaml`**: Lưu trữ ma trận Domain-Range của 7 loại quan hệ (ALLOW, REQUIRE, PROHIBIT...). Ma trận này là "chốt chặn" để loại bỏ các quan hệ phi logic (VD: ALLOW trỏ vào SUBJECT).
- **`src/ontology/configs/taxonomy_aliases.yaml`**: Từ điển Seed Taxonomy. Định nghĩa các thực thể chuẩn (Canonical Entity) và các từ khóa đồng nghĩa (aliases). Được dùng làm "chân lý" để Normalize các thực thể trích xuất được từ LLM. Hiện đã được nâng cấp lên 361 dòng với rất nhiều từ khóa cho Luật Đất đai.

### Động cơ lõi (Core Engines)
- **`src/ontology/canonical_mapper.py`**: Chịu trách nhiệm nạp (load) 2 file YAML cấu hình lên bộ nhớ và cung cấp hàm API nội bộ để truy xuất dữ liệu taxonomy, domain/range constraints.
- **`src/ontology/entity_normalizer.py`**: Chịu trách nhiệm chuẩn hóa thực thể. Sử dụng kỹ thuật 2-Tier Matching:
  - *Tier 1 (Exact Match)*: Khớp chính xác hoàn toàn.
  - *Tier 2 (Fuzzy Match)*: Khớp mờ sử dụng thư viện `thefuzz` (thuật toán Levenshtein).
  - *Fallback (Quarantine Mode)*: Nếu không khớp, thực thể bị gán ID `unassigned.[tên]` và đẩy vào log cách ly, đồng thời tự động ép kiểu lớp (M6 to M7 mapping) để giữ cho cạnh không bị vứt bỏ.
- **`src/ontology/relation_normalizer.py`**: Chuẩn hóa quan hệ. Nhận đầu vào là các ID cục bộ (e1, e2) của M6, ánh xạ chúng sang Canonical ID của M7. Đặc biệt, nó **tiêm toàn bộ ngữ cảnh cục bộ** (gồm `source_node_id`, `evidence`) vào cấu trúc của Cạnh để thực thi Edge-Level Provenance.
- **`src/ontology/ontology_validator.py`**: Bộ kiểm duyệt quan hệ. Đối chiếu Cạnh với ma trận từ `ontology_schema.yaml`. Bất kỳ cạnh nào vi phạm Domain (nguồn sai lớp) hoặc Range (đích sai lớp) đều bị thẳng tay loại bỏ (REJECT).

### Điều phối & Chạy thử
- **`src/ontology/ontology_builder.py`**: Trái tim của Module 7. Dùng generator (O(1) memory) để duyệt qua các Node đầu vào, reset ID cục bộ, gọi các Normalizer và Validator, sau đó gom nhóm (Aggregate) thực thể, và xuất ra đồ thị Canonical hoàn chỉnh.
- **`run_ontology_builder.py`**: Script thực thi toàn bộ pipeline, đọc từ `semantic_extraction.json` và xuất ra `canonical_semantic_graph.json`.
- **`tests/unit/test_ontology_v1_3.py`**: Kịch bản kiểm thử Pytest đảm bảo code tuyệt đối tuân thủ V1.3:
  - Test 01: Entity siêu nhẹ (không chứa evidence/source_node_id).
  - Test 02: Không có class rác (Chỉ cho phép 6 Core Classes).
  - Test 03: Edge-Level Provenance (Quan hệ bắt buộc phải chứa evidence).
  - Test 04: Domain-Range Matrix hợp lệ.
  - Test 05: Tính năng Quarantine (phải có các thực thể unassigned).

---

## 2. Luồng Workflow (Quy trình xử lý)

Workflow của Module 7 tuân thủ theo nguyên tắc 100% Rule-based (không gọi LLM), diễn ra như sau:

1. **Khởi tạo**: Đọc `ontology_schema.yaml` và `taxonomy_aliases.yaml` vào RAM thông qua `CanonicalMapper`.
2. **Luồng Streaming**: Đọc file `semantic_extraction.json` theo từng Node. ID mapping cục bộ (`local_to_canonical`) được reset mới mỗi khi bắt đầu một Node để tránh loạn ID.
3. **Chuẩn hóa Thực thể (Entity)**:
   - Các thực thể thô được đưa vào `EntityNormalizer`.
   - Nếu tìm thấy trong Taxonomy -> Lấy Canonical ID chuẩn.
   - Nếu không tìm thấy -> Gán `unassigned.xxx` (Quarantine), tự động map fallback type sang class của V1.3, và ghi log ra `unresolved_entities.log`.
   - Các thực thể chuẩn hóa được gom lại. *Chỉ lưu trữ thông tin cơ bản (ID, class, tên)*.
4. **Chuẩn hóa Quan hệ (Relation) & Bơm Ngữ cảnh**:
   - `RelationNormalizer` đổi ID nguồn/đích sang Canonical ID.
   - Tiêm thông tin nguồn gốc (`source_node_id`, `evidence`) vào chính Cạnh đó.
5. **Kiểm duyệt (Validation)**:
   - `OntologyValidator` kiểm tra Cạnh. Nếu nguồn và đích không hợp lệ theo `ontology_schema.yaml` -> Loại bỏ và tăng biến đếm `rejected_edges`.
6. **Tổng hợp & Ghi file**: Xuất ra file `canonical_semantic_graph.json` chứa tập Thực thể phẳng và tập Quan hệ mang ngữ cảnh.

---

## 3. Các Vấn đề Gặp phải & Giải pháp

Trong quá trình triển khai, đã phát sinh 2 vấn đề lớn về kiến trúc và cách giải quyết như sau:

### Vấn đề 1: Đụng độ Type giữa Module 6 (Cũ) và Module 7 (Mới) làm sập cơ chế Quarantine
- **Tình trạng**: Ở M6, LLM trả về các type tự do như `SUBJECT`, `ACTION`. Khi rơi vào Quarantine, thực thể giữ nguyên type cũ. Kết quả là `OntologyValidator` của M7 (chỉ chấp nhận `LEGAL_SUBJECT`, `LEGAL_ACTION`) đã **từ chối 100%** các Cạnh nối với thực thể Quarantine vì lỗi sai Domain-Range.
- **Giải pháp**: Tại hàm `_quarantine` trong `entity_normalizer.py`, tôi đã lập tức thiết lập một bộ `m6_to_m7_map` để ngầm ánh xạ type (VD: `SUBJECT` -> `LEGAL_SUBJECT`, `OBLIGATION` -> `LEGAL_ACTION`). Nhờ đó, các thực thể lạ vẫn bị cách ly, nhưng các cạnh hợp logic của chúng không bị loại bỏ oan. Số cạnh Rejected giảm mạnh ngay lập tức.

### Vấn đề 2: Xung đột giữa "Gộp mảng ngữ cảnh" và "Thực thể siêu nhẹ" (Edge-Level Provenance)
- **Tình trạng**: Ban đầu có sự nhầm lẫn giữa việc gộp ngữ cảnh (`source_node_ids`, `evidences`) vào Entity. Khi code chạy và đưa các mảng này vào Entity, Unit Test `test_01_entity_schema_super_lightweight` đã bắn ra cờ lỗi đỏ chót (Failed), vì nó cấm Entity chứa các trường bằng chứng để giữ Node siêu nhẹ.
- **Giải pháp**: Xóa bỏ hoàn toàn mảng `source_node_ids` và `evidences` khỏi Entity trong `ontology_builder.py`. Tuân thủ 100% quy tắc V1.3: "Nodes act as Identity Hubs. They DO NOT store source documentation". Mọi thông tin chứng cứ cục bộ chỉ được tiêm vào cạnh (Edge-level) qua `RelationNormalizer`. Sau khi sửa, 5/5 test cases đã PASS Xanh toàn bộ.

### Kết quả mở rộng thực tế
Khi chạy với Taxonomy cũ (10 items), có tới 616 thực thể bị Quarantine. Tuy nhiên, sau khi mở rộng `taxonomy_aliases.yaml` thành hơn 361 dòng, số lượng thực thể bị Quarantine giảm xuống chỉ còn 214, minh chứng cho sự hiệu quả vượt trội của việc kết hợp Alias Dictionary và Human-in-the-loop.

---

## 4. Tại sao dự án BẮT BUỘC phải có `canonical_id`?

Luật pháp Việt Nam dù rất chuẩn mực nhưng vẫn có sự đa dạng trong cách dùng từ (Biến thể từ vựng - Synonyms).
Ví dụ, khi đọc Luật Đất đai 2024, bạn sẽ thấy các cụm từ sau nằm rải rác ở các điều khoản khác nhau:
- "người gốc Việt Nam định cư ở nước ngoài"
- "người Việt Nam định cư ở nước ngoài"
- "cá nhân là người gốc Việt Nam định cư ở nước ngoài"

❌ **Nếu KHÔNG có canonical_id (Lỗi của Đồ thị sơ cấp)**:
Hệ thống sẽ tạo ra 3 Node (3 vòng tròn) khác nhau trên Neo4j. Đồ thị của bạn sẽ bị "bùng nổ" (Entity Explosion). Khi người dùng hỏi: *"Việt kiều có quyền gì?"*, hệ thống tìm kiếm sẽ bị phân tán, có thể chỉ tìm thấy Node 1 mà bỏ sót quyền lợi nằm ở Node 2 và 3.

✅ **Khi CÓ canonical_id (Sức mạnh của Module 7)**:
Module 7 sẽ nhận diện cả 3 cụm từ này và "gắn" cho chúng chung một mã định danh (như CCCD): `subject.land_user.foreign.overseas_vietnamese`.
Trên Neo4j, hệ thống sẽ gộp (merge) chúng lại thành DUY NHẤT 1 NODE. Mọi mũi tên quyền/nghĩa vụ từ 3 cụm từ kia đều sẽ trỏ chung về 1 Node khổng lồ này.

---

## 5. Ví dụ Luồng Workflow Thực tế trong Hệ thống

Hãy đi theo vòng đời của một khái niệm từ lúc nó nằm trên mặt giấy cho đến khi trả lời được câu hỏi của người dùng.

### BƯỚC 1: Module 6 bóc tách thô (Raw Extraction)
Tại Điều 41, M6 bóc ra được:
- e1: "Người gốc Việt Nam định cư ở nước ngoài"
- Quan hệ: e1 $\xrightarrow{\text{ALLOW}}$ e2 ("thuê đất")

Tại Điều 43, M6 lại bóc ra được:
- e8: "Cá nhân là người gốc Việt Nam định cư ở nước ngoài"
- Quan hệ: e8 $\xrightarrow{\text{ALLOW}}$ e9 ("nhận chuyển nhượng đất trong KCN")

### BƯỚC 2: Module 7 Chuẩn hóa (Canonical Normalization)
Module 7 đọc file `taxonomy_aliases.yaml` (Từ điển đồng nghĩa) và phát hiện ra e1 và e8 thực chất là một. Nó gán cho cả hai mã CCCD: `subject.land_user.foreign.overseas_vietnamese`.
M7 xuất ra JSON chuẩn tắc:
```json
{
  "canonical_id": "subject.land_user.foreign.overseas_vietnamese",
  "ontology_class": "LEGAL_SUBJECT",
  "canonical_text": "Người gốc Việt Nam định cư ở nước ngoài",
  "aliases": ["Cá nhân là người gốc Việt Nam định cư ở nước ngoài"]
}
```

### BƯỚC 3: Đổ vào Neo4j (Graph Ingestion)
Lúc này, Neo4j tạo đúng 1 Node (1 vòng tròn) có mã là `subject.land_user.foreign.overseas_vietnamese`.
Và nó vẽ 2 mũi tên `ALLOW` cắm vào 2 Node hành vi (thuê đất và nhận chuyển nhượng). Mỗi mũi tên mang theo `source_node_id` (Dấu vết Điều 41 và Điều 43) nhờ cơ chế Edge-Level Provenance.

### BƯỚC 4: Luồng Truy vấn GraphRAG (Retrieval Workflow)
Giả sử hệ thống chatbot của nhóm bạn nhận được câu hỏi từ một user:
🗣️ **User hỏi:** *"Tôi là Việt kiều, tôi có được mua đất trong Khu công nghiệp không?"*

Luồng xử lý bằng canonical_id sẽ diễn ra mượt mà như sau:

**1. Semantic Router / Query Rewriter (Xử lý câu hỏi)**:
Hệ thống LLM đọc chữ "Việt kiều". Nó dò vào từ điển Ontology và dịch câu hỏi thành tham số hệ thống:
- Target_Entity = `subject.land_user.foreign.overseas_vietnamese`
- Target_Action = "nhận chuyển nhượng" (mua đất) / "khu công nghiệp"

**2. Graph Database Search (Câu lệnh Cypher)**:
Hệ thống bắn một câu lệnh vào Neo4j tìm đích danh cái "CCCD" đó:
```cypher
MATCH (s:CanonicalEntity {canonical_id: "subject.land_user.foreign.overseas_vietnamese"})
      -[rel:ALLOW]->
      (a:CanonicalEntity)
WHERE a.canonical_text CONTAINS "khu công nghiệp"
RETURN rel.source_node_id, rel.evidence
```

**3. Kết quả trả về từ Graph (Siêu tốc và Chính xác tuyệt đối)**:
Vì chúng ta truy vấn bằng ID (như tìm CCCD) chứ không phải tìm bằng Text rườm rà, Neo4j nhả kết quả trong 1 mili-giây:
- `source_node_id`: "doc_chuong-iii_dieu-43"
- `evidence`: "Cá nhân là người gốc Việt Nam định cư ở nước ngoài... được nhận chuyển nhượng đất trong KCN..."

**4. Khởi tạo câu trả lời cho User (Generation)**:
Hệ thống nạp evidence vào Prompt và LLM sẽ trả lời tự tin:
🤖 *"Chào bạn, theo quy định tại Điều 43 Luật Đất đai 2024, Người gốc Việt Nam định cư ở nước ngoài (Việt kiều) ĐƯỢC PHÉP nhận chuyển nhượng quyền sử dụng đất trong Khu công nghiệp."*
