# HỢP ĐỒNG GIAO TIẾP MODULE 6 VÀ MODULE 7 (M6-M7 CONTRACT V1.4)

**Mục đích:** Đặc tả tiêu chuẩn dữ liệu đầu ra của Module 6 (Semantic LLM Extractor) để đảm bảo tương thích 100% với màng lọc Validation của Module 7 (Legal Ontology Builder). Mọi dữ liệu vi phạm hợp đồng này sẽ bị M7 từ chối (REJECT) hoặc cách ly (QUARANTINE).

---

## 1. TIÊU CHUẨN LỚP THỰC THỂ (ENTITY TYPES)
Module 6 BẮT BUỘC chỉ được phân loại thực thể vào 1 trong 7 nhóm Literal sau:
1. `SUBJECT` (Chủ thể): Người, tổ chức, cơ quan nhà nước (VD: "Người sử dụng đất", "Nhà nước", "Tổ chức kinh tế").
2. `ACTION` (Hành vi): Hành động, quyền, nghĩa vụ, thủ tục (VD: "Chuyển nhượng", "Công chứng", "Bồi thường").
3. `OBJECT` (Khách thể): Vật chất, tài sản, văn bản, tiền bạc (VD: "Đất đai", "Giấy chứng nhận", "Hợp đồng").
4. `CONDITION` (Điều kiện): Trạng thái, thời hạn, tiền đề (VD: "Trong thời hạn sử dụng đất", "Có Giấy chứng nhận").
5. `EXCEPTION` (Ngoại lệ): Sự loại trừ (VD: "Trừ trường hợp thừa kế").
6. `REFERENCE` (Dẫn chiếu): Điều khoản, văn bản pháp luật (VD: "Điều 26 Luật này").
7. `PENALTY` (Chế tài): Xử phạt (VD: "Phạt tiền", "Thu hồi").

## 2. TIÊU CHUẨN LỚP QUAN HỆ (RELATION TYPES) & MA TRẬN RÀNG BUỘC
Module 6 chỉ được sử dụng 8 loại Relation sau và phải tuân thủ nghiêm ngặt Hướng mũi tên (Domain -> Range):

| Relation Type | Nguồn (Domain) | Đích (Range) |
| :--- | :--- | :--- |
| `ALLOW` | `SUBJECT` | `ACTION` |
| `REQUIRE` | `SUBJECT`, `ACTION` | `ACTION` |
| `PROHIBIT` | `SUBJECT` | `ACTION` |
| `HAS_CONDITION` | `SUBJECT`, `ACTION` | `CONDITION` |
| `HAS_EXCEPTION` | `ACTION`, `CONDITION` | `EXCEPTION` |
| `REFERENCE_TO` | * (Tất cả) | `REFERENCE` |
| `HAS_OBJECT` | `ACTION`, `SUBJECT` | `OBJECT` |
| `HAS_PENALTY` | `ACTION` | `PENALTY` |

**⚠️ CHÚ Ý QUAN TRỌNG:**
- KHÔNG BAO GIỜ gán `ALLOW`, `REQUIRE`, `PROHIBIT` xuất phát từ `OBJECT` (Hợp đồng, sổ đỏ không có quyền hay nghĩa vụ).

---

## 3. 8 QUY TẮC BÓC TÁCH NGỮ NGHĨA (DÀNH CHO PROMPT M6)

1. **Cấm gán Quyền/Nghĩa vụ cho OBJECT (Action-Object Fallacy):** `OBJECT` chỉ được làm Target của `HAS_OBJECT`.
2. **Dịch ngược Câu Bị Động (Passive Voice Inversion):** Khi văn bản ở thể bị động (VD: "Người dân được Nhà nước bồi thường"), KHÔNG gán "Nhà nước" làm Source của `ALLOW`. Phải lật lại: `(Người dân) --ALLOW--> (Bồi thường)` VÀ `(Nhà nước) --REQUIRE--> (Bồi thường)`.
3. **Suy luận Chủ thể Ẩn (Implicit Subject Resolution):** Khi gặp khoản liệt kê chỉ có hành vi (VD: "- Được chuyển nhượng"), BẮT BUỘC tìm ngược lên câu mở đoạn để xác định Chủ thể. KHÔNG để rỗng Source.
4. **Tách bạch Đối tượng và Hành động (Relation Chaining):** Không gộp "Chuyển nhượng quyền sử dụng đất" thành 1 Action. Phải rã ra: `(Chủ thể) --ALLOW--> (Chuyển nhượng)` VÀ `(Chuyển nhượng) --HAS_OBJECT--> (Quyền sử dụng đất)`.
5. **Gán CONDITION:** Cấu trúc "X khi Y" / "X nếu Y" -> `(Action X) --HAS_CONDITION--> (Condition Y)`.
6. **Gán EXCEPTION:** Cấu trúc "trừ trường hợp Y" -> `(Action/Condition) --HAS_EXCEPTION--> (Exception Y)`.
7. **Gán REFERENCE:** Cấu trúc "theo quy định tại Y" -> `(*) --REFERENCE_TO--> (Reference Y)`.
8. **Bằng chứng nguyên văn (Verbatim Evidence):** Trường `evidence` phải trích NGUYÊN VĂN từ văn bản gốc, không tóm tắt hay bịa chữ.

---

## 4. FEW-SHOT EXAMPLES (DÙNG ĐỂ HUẤN LUYỆN M6)

### Ví dụ 1: Xử lý Câu Bị Động
**Văn bản:** "Nhà nước thu hồi đất thì người sử dụng đất được bồi thường."
- ❌ **SAI:** `(Nhà nước) --ALLOW--> (Bồi thường)`
- ✅ **ĐÚNG:** `(Người sử dụng đất) --ALLOW--> (Bồi thường)` VÀ `(Thu hồi) --HAS_CONDITION--> (Nhà nước thu hồi đất)`

### Ví dụ 2: Tách Đối tượng & Hành động
**Văn bản:** "Hợp đồng chuyển nhượng quyền sử dụng đất phải được công chứng."
- ❌ **SAI:** `(Hợp đồng) --REQUIRE--> (Công chứng)`
- ✅ **ĐÚNG:** `(Người sử dụng đất) --REQUIRE--> (Công chứng)` VÀ `(Công chứng) --HAS_OBJECT--> (Hợp đồng chuyển nhượng)`

### Ví dụ 3: Chủ thể Ẩn
**Văn bản:** "Điều 27. Quyền của công dân: Được tham gia quản lý nhà nước."
- ✅ **ĐÚNG:** `(Công dân) --ALLOW--> (Tham gia quản lý nhà nước)`

---

## 5. CẤU TRÚC JSON OUTPUT YÊU CẦU (PYDANTIC SCHEMA)

Module 6 phải trả về JSON tuân thủ schema sau:

```json
{
  "entities": [
    {
      "id": "e1",
      "text": "Người sử dụng đất",
      "entity_type": "SUBJECT",
      "evidence": "Người sử dụng đất được chuyển nhượng"
    }
  ],
  "relations": [
    {
      "source": "e1",
      "relation_type": "ALLOW",
      "target": "e2",
      "evidence": "Người sử dụng đất được chuyển nhượng"
    }
  ]
}