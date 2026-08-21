# Tổng kết Module 3 - Validation Engine (Quality Gate)

Module 3 đóng vai trò là "Chốt chặn chất lượng" (Quality Gate) cho hệ thống Hybrid Parser của GraphRAG Văn bản Pháp luật Việt Nam. Nhiệm vụ chính của module là rà soát toàn bộ mảng node JSON từ Module 2, phát hiện và phân loại lỗi cấu trúc, lọc bỏ các node lỗi nghiêm trọng, và sinh ra báo cáo chất lượng chi tiết.

**Nguyên tắc tối thượng:** Chỉ phát hiện, lọc và báo cáo — TUYỆT ĐỐI KHÔNG tự sửa dữ liệu (No Auto-repair).

## 1. Công nghệ và Nguyên tắc thiết kế
- **Ngôn ngữ & Thư viện:** Python 3, `pydantic` (tái sử dụng `LegalNode` từ Module 2 để validate schema), `json` (đọc/ghi), `re` (trích xuất marker cho sequence check).
- **Nguyên tắc:**
  - **Single Responsibility:** Mỗi file đảm nhận đúng một trách nhiệm kiểm tra riêng biệt (Schema, Integrity, Sequence, Report).
  - **100% Deterministic:** Chạy 2 lần với cùng input cho ra kết quả giống hệt nhau. Không có yếu tố ngẫu nhiên.
  - **Fail-Safe Filtering:** Chỉ các node dính lỗi ERROR mới bị loại bỏ (quarantine). Các node dính WARNING vẫn được giữ lại nguyên vẹn.

## 2. Luồng dữ liệu (Data Flow)

```
raw_nodes.json (Module 2)
       │
       ▼
  ┌─────────────────┐
  │  validator.py    │  ← Orchestrator
  │  (Pipeline)      │
  └─────┬───────────┘
        │
        ├──► schema_validator.py    → Kiểm tra Pydantic schema
        ├──► integrity_checker.py   → Rà soát Orphan, BrokenParent, Duplicate, Cycle, Empty
        ├──► sequence_checker.py    → Kiểm tra nhảy số (GapIndex)
        └──► report_generator.py    → Tính metrics, ghi report
        │
        ▼
  ┌─────────────────────────────────────┐
  │ validated_nodes.json (node sạch)     │
  │ validation_report.json (báo cáo)     │
  └─────────────────────────────────────┘
```

## 3. Vai trò và Workflow của từng file

- **`schema_validator.py`**:
  - *Vai trò:* Tuyến phòng thủ đầu tiên. Kiểm tra từng raw dict có khớp Pydantic `LegalNode` schema hay không.
  - *Workflow:* Duyệt qua từng phần tử trong mảng JSON, gọi `LegalNode.model_validate()`. Nếu fail, bắn issue `SchemaViolation` (ERROR) và loại node đó khỏi pipeline.

- **`integrity_checker.py`**:
  - *Vai trò:* Bộ rà soát toàn vẹn đồ thị (DAG Integrity Checker). Đây là lõi kiểm tra quan trọng nhất.
  - *Workflow:* Thực hiện 5 phép kiểm tra tuần tự:
    1. **DuplicateNodeID (VAL-001, ERROR):** Quét toàn bộ mảng node, dùng `Dict` để đếm tần suất xuất hiện của từng ID. Nếu ID xuất hiện > 1 lần → ERROR.
    2. **OrphanNode (VAL-002, ERROR):** Kiểm tra node con (SECTION, ARTICLE, CLAUSE, POINT) có `parent_id = None` hay không. Cho phép ngoại lệ: PART, CHAPTER, TEXT ở top-level.
    3. **BrokenParent (VAL-003, ERROR):** Thu thập tập hợp `all_ids`, rồi kiểm tra `parent_id` của mỗi node có nằm trong tập hợp đó không. Nếu không tồn tại → ERROR.
    4. **CyclicDependency (VAL-004, ERROR):** Sử dụng thuật toán **DFS ngược (Ancestor Walk)**: Từ mỗi node, đi ngược lên theo chuỗi `parent_id`. Nếu gặp lại chính node đang duyệt → phát hiện chu trình (cycle). Dùng `Set` để tránh báo trùng.
    5. **EmptyNode (VAL-005, WARNING):** Kiểm tra trường `text` rỗng hoặc chỉ chứa whitespace. Đây là cảnh báo nhẹ (vd: các node CHAPTER/SECTION chỉ có title).

- **`sequence_checker.py`**:
  - *Vai trò:* Bộ kiểm tra tính liên tục của chuỗi đánh số.
  - *Workflow:*
    - Nhóm node theo `(parent_id, type)` để xác định các chuỗi cùng cha cùng loại.
    - Trích xuất marker từ `title` bằng regex: `"1."` → `1`, `"a)"` → `a`, `"Chương III"` → `III`.
    - Xây dựng dãy kỳ vọng (expected) từ phần tử đầu đến phần tử cuối, rồi dùng **phép trừ tập hợp (Set Difference)** so với dãy thực tế (actual) để tìm phần tử bị thiếu.
    - Hỗ trợ 3 loại chuỗi:
      - **Số La Mã (Chương):** I, II, III, IV... (hỗ trợ tới L).
      - **Số Tự Nhiên (Mục, Điều, Khoản):** 1, 2, 3...
      - **Bảng Chữ Cái Tiếng Việt (Điểm):** `a, b, c, d, đ, e, g, h, i, k, l, m, n, o, p, q, r, s, t, u, v, x, y` — Bắt buộc có chữ `đ`, bỏ qua `f, j, w, z` theo chuẩn pháp luật VN.
    - Kết quả: GapIndex (VAL-006, WARNING) kèm thông điệp mô tả chính xác phần tử bị thiếu nằm giữa 2 phần tử nào, thuộc parent nào.

- **`report_generator.py`**:
  - *Vai trò:* Bộ tính toán metrics và sinh báo cáo.
  - *Workflow:* Nhận toàn bộ danh sách issues, phân loại ERROR/WARNING, tính `structural_integrity_score` theo công thức `(1 - fatal_errors_count / total_nodes_received) * 100`, rồi ghi ra file `validation_report.json`.

- **`validator.py`**:
  - *Vai trò:* Nhạc trưởng (Orchestrator) điều phối toàn bộ pipeline.
  - *Workflow:*
    1. Đọc `raw_nodes.json`.
    2. Gọi `schema_validator` → lọc node lỗi schema.
    3. Gọi `integrity_checker` → phát hiện lỗi toàn vẹn đồ thị.
    4. Gọi `sequence_checker` → phát hiện nhảy số.
    5. Tổng hợp tất cả issues, lọc bỏ node ERROR → ghi `validated_nodes.json`.
    6. Gọi `report_generator` → ghi `validation_report.json`.
  - Cung cấp thêm method `validate_nodes()` cho phép unit test gọi trực tiếp với danh sách `LegalNode` mà không cần đọc/ghi file.

## 4. Phân cấp lỗi và Chính sách xử lý

| Rule ID | Loại lỗi | Severity | Hành động |
|---------|----------|----------|-----------|
| VAL-000 | SchemaViolation | ERROR | Loại bỏ khỏi `validated_nodes.json` |
| VAL-001 | DuplicateNodeID | ERROR | Loại bỏ khỏi `validated_nodes.json` |
| VAL-002 | OrphanNode | ERROR | Loại bỏ khỏi `validated_nodes.json` |
| VAL-003 | BrokenParent | ERROR | Loại bỏ khỏi `validated_nodes.json` |
| VAL-004 | CyclicDependency | ERROR | Loại bỏ khỏi `validated_nodes.json` |
| VAL-005 | EmptyNode | WARNING | Giữ lại trong `validated_nodes.json` |
| VAL-006 | GapIndex | WARNING | Giữ lại trong `validated_nodes.json` |

## 5. Kết quả Audit trên dữ liệu thật (Luật Đất Đai - Chương III)

```
=== VALIDATION ENGINE RESULTS ===
Structural Integrity Score : 100.0%
Fatal Errors               : 0
Warnings                   : 25 (EmptyNode — các node CHAPTER/SECTION/ARTICLE chỉ có title)
Validated                  : 224/224 node
```

Kết quả này chứng minh:
- **Hybrid ID từ Module 2 hoạt động hoàn hảo:** 0 DuplicateNodeID, 0 BrokenParent → Lỗi KL-02 đã được xử lý triệt để.
- **Cây phân cấp hoàn toàn hợp lệ:** 0 OrphanNode, 0 CyclicDependency → mọi quan hệ cha-con đều khớp chính xác.
- **25 EmptyNode (WARNING)** là hành vi bình thường: Các node cấp CHAPTER, SECTION, ARTICLE thường chỉ mang tiêu đề mà không có nội dung text riêng.

## 6. Tổng kết Chiến dịch Hợp nhất (Merge M1 + M2 + M3 + C2) - Cột mốc Checkpoint v1

Chiến dịch hợp nhất đã kết nối thành công 3 Module (Preprocessing, Physical Parser, Validation Engine) cùng với nhánh nghiên cứu phục hồi đứt gãy (C2) thành một Physical Pipeline v1 hoàn chỉnh và chốt chặn (Frozen).

### A. Quá trình thực thi & Số liệu
1. **M1 → M2 (Production Core):**
   - **Đầu vào:** `Luat_dat_dai_chuong_3.docx` (288 paragraphs).
   - **Đầu ra:** Chính xác **222 nodes** (1 Chapter, 5 Section, 23 Article, 84 Clause, 109 Point).
   - **Chất lượng:** Thuật toán *Hybrid ID* (kết hợp `law_code` + `parent_id` + offset/char_start) đã triệt tiêu 100% tình trạng đụng độ ID. Không ghi nhận lỗi Fatal Error nào.
2. **M3 Validation:**
   - Score đạt **100.0%**.
   - Phát hiện **1 Warning (GapIndex)**: Hệ thống báo lỗi thiếu Điểm "e" dưới Khoản 1 Điều 37.
3. **M1(TXT) → M2 → M3 (Compatibility Test):**
   - Đứt gãy 100% cấp độ Khoản (Clause) khi parse qua đường TXT (còn 37 nodes).
   - M3 **không crash**, báo cáo Score 100%. Node Điểm (Point) được chấp nhận mồ côi cấp Khoản và nối thẳng vào Điều (Article) nhờ M2 thiết lập `implicit_parent = True`.
4. **C2 (Research - Phục hồi đứt gãy):**
   - F1-Score của tập H2 duy trì chính xác ở mức **0.521**.
   - Chứng minh Hybrid ID không phá vỡ Logic matching dựa trên nội dung (text-based matching) của Module nghiên cứu.

### B. Các phát hiện & Sửa lỗi (Bugs Fixed)
- **Lỗi thiếu Pydantic Schema:** Script cũ của Module 3 gọi `LegalNode.model_validate()` nhưng khai báo Schema chưa được đồng bộ. Đã tự động tái tạo `class LegalNode(BaseModel)` chuẩn hóa theo hợp đồng (Data Contract) của M2.
- **Xử lý Technical Debt (Single Source of Truth):** 
  - Trước hợp nhất: Module 3 tự dùng Regex quét `node.title` để tìm marker (ví dụ `a)`, `1.`), rất dễ sai sót.
  - Sau hợp nhất: Module 3 ưu tiên lấy `node.marker` và `node.number` (vốn đã được M1 bóc tách cực kỳ chính xác từ thẻ XML `w:lvlText` của DOCX).
  - *Kết quả tuyệt vời:* Nhờ loại bỏ Regex mò mẫm, M3 đã bóc trúng phóc việc văn bản gốc bị khuyết mất Điểm "e" (nhảy từ đ → g).

### C. Trade-offs (Sự đánh đổi)
1. **TXT Degradation vs. Robustness:** Chấp nhận mất dữ liệu cấp Khoản trên file TXT (do giới hạn không có metadata) thay vì cố viết Regex quá phức tạp. Bù lại, hệ thống M3 có tính chống chịu (Robustness) cao, không sụp đổ khi nhận cây đồ thị bị thoái hóa.
2. **PDF Out of Scope:** Giới hạn scope v1 chỉ tập trung xử lý DOCX/TXT. PDF được gác lại để tránh loãng nguồn lực cho đến khi các parser PDF (như LlamaParse, MinerU) ổn định hơn.
3. **No Auto-repair:** Quyết định không tự động sửa lỗi chuỗi (như tự thêm điểm "e" ảo). Việc giữ nguyên bản gốc để con người/LLM quyết định ở phase sau quan trọng hơn việc "làm đẹp" dữ liệu.

### D. Vấn đề bỏ ngỏ (Open Issues)
- **Khả năng khái quát (Generalization):** Rule hiện tại parse rất mượt Luật Đất Đai. Liệu các Nghị định, Thông tư có cấu trúc lỏng lẻo hơn (VD: các Phụ lục, Bảng biểu) có làm M2 sinh ra quá nhiều rác (Orphan) không?
- **Đồng bộ Annotation C2:** Reference Annotation hiện tại là "cross-checked đại diện". Trong tương lai cần một Ground Truth do con người (Lawyers) gắn nhãn thủ công để đánh giá C2 chính xác hơn.

### E. Câu hỏi mở rộng (Chuyển tiếp sang Phase Semantic Extraction)
Khi Physical Pipeline đã đóng băng (Frozen), bài toán chuyển từ "Bóc tách Cấu trúc" sang "Hiểu Ngữ nghĩa". Các câu hỏi lớn được đặt ra:
1. **Ontology Design:** Trong Luật Đất đai, những Thực thể (Entity) nào đáng giá nhất để trích xuất? (Cơ quan quản lý, Thẩm quyền, Đối tượng chịu thuế, Hành vi cấm...).
2. **Cross-reference Resolution:** Làm sao để nhận diện một cụm từ "Tại khoản 2 Điều này" và nối nó thành Edge `REFERENCES` tới đúng ID của node đích trên đồ thị?
3. **LLM Chunking Strategy:** 1 Node Vật lý có nên là 1 Node Ngữ nghĩa? Hay cần gộp (Merge) các Điểm nhỏ (Point) lên Khoản (Clause) để đủ context cho LLM hiểu?
