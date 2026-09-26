# BẢN TÓM TẮT MODULE 6: MÁY TRÍCH XUẤT NGỮ NGHĨA (SEMANTIC EXTRACTOR) - KIẾN TRÚC HYPERGRAPH V8

## 1. Giới thiệu chức năng
Module 6 (LLM Semantic Extractor) là bộ não đóng vai trò Trích xuất tri thức (Information Extraction - IE) của toàn bộ hệ thống. 
Nếu Module 1-4 là "Xây bộ khung xương" và Module 5 là "Người phân loại", thì Module 6 đóng vai trò **"Phẫu thuật viên vi phẫu"**, chuyên bóc tách từng thớ thịt (thực thể pháp lý) và mạch máu (quan hệ pháp lý) từ những đoạn văn bản thô cứng của luật.

Đặc biệt ở **Phiên bản V8**, hệ thống đã được nâng cấp lên mô hình **Hypergraph (Siêu đồ thị)** tuân thủ triết lý NORM (Normative Requirements).

---

## 2. Kiến trúc 6 Nhãn Thực Thể & 7 Nhãn Quan Hệ

Mô hình V8 khai thác toàn bộ 6 nhãn thực thể (Entity Types) và 7 nhãn quan hệ (Relation Types) theo lý thuyết pháp luật NORM.

### 🏷️ 6 Thực Thể (Entities)
1. **`SUBJECT`**: Chủ thể pháp luật (Người sử dụng đất, Cơ quan nhà nước,...).
2. **`OBJECT`**: Đối tượng pháp lý chịu sự tác động (Quyền sử dụng đất, Tài sản, Đất đai,...).
3. **`ACTION`**: Hành vi pháp lý (Chuyển nhượng, Thu hồi, Đăng ký,...).
4. **`REFERENCE`**: Dẫn chiếu chéo (khoản 1 Điều 37, điểm a khoản này,...).
5. **`CONDITION`**: Điều kiện tiên quyết.
6. **`EXCEPTION`**: Trường hợp ngoại lệ.

### 🔗 7 Quan Hệ (Relations)
1. **`ALLOW`**: Cấp quyền (SUBJECT -> ALLOW -> ACTION).
2. **`HAS_OBJECT`**: Ràng buộc đối tượng (ACTION -> HAS_OBJECT -> OBJECT).
3. **`HAS_CONDITION`**: Điều kiện (ACTION/SUBJECT -> HAS_CONDITION -> CONDITION).
4. **`REQUIRE`**: Nghĩa vụ (SUBJECT -> REQUIRE -> ACTION).
5. **`PROHIBIT`**: Bị cấm (SUBJECT -> PROHIBIT -> ACTION).
6. **`REFERENCE_TO`**: Trỏ đến điều khoản khác.
7. **`HAS_EXCEPTION`**: Ngoại lệ.

---

## 3. Bước Đột Phá: Kiến Trúc Hypergraph (NORM)

Khác với Text-to-Text hay Triples đơn giản, Module 6 V8 bóc tách văn bản thành mạng lưới Hypergraph thông qua các "Biến số đại diện" (Local IDs) như `e1`, `e2`, `e3`.

Ví dụ: "Tổ chức kinh tế được Nhà nước cho thuê đất thu tiền một lần thì có quyền chuyển nhượng quyền sử dụng đất"

**Entities:**
- `e1`: "Tổ chức kinh tế" (SUBJECT)
- `e2`: "Nhà nước cho thuê đất thu tiền một lần" (CONDITION)
- `e3`: "chuyển nhượng" (ACTION)
- `e4`: "quyền sử dụng đất" (OBJECT)

**Relations:**
- `e1 -> HAS_CONDITION -> e2`
- `e1 -> ALLOW -> e3`
- `e3 -> HAS_OBJECT -> e4`

👉 **Sự thay đổi:** 
Nhờ việc tách rời **Hành vi (ACTION)** và **Đối tượng (OBJECT)** ra làm 2 thực thể độc lập, GraphRAG sau này có khả năng trả lời các câu hỏi siêu phức tạp như: *"Những hành vi nào có thể tác động lên [Quyền sử dụng đất]?"* hoặc *"Ai có quyền thực hiện hành vi [Chuyển nhượng]?"*

---

## 4. Báo Cáo Chất Lượng Đầu Ra (Bản V8 - Mới nhất)

Toàn bộ 179 đoạn văn (Candidate Nodes) vừa được chạy qua Module 6 cho ra kết quả bóc tách cực kỳ đồ sộ với độ chính xác Grounding tuyệt đối (100%):

- **Tổng số Thực thể:** 916
- **Tổng số Mối quan hệ:** 782
- **Thực thể xuất hiện nhiều nhất:** `SUBJECT` (285) và `OBJECT` (246)
- **Quan hệ xuất hiện nhiều nhất:** `ALLOW` (296) và `HAS_OBJECT` (225)
- **Tỉ lệ Grounded:** 100% (Zero Hallucination).

> ⚠️ **Lưu ý tương thích:** Do cấu trúc siêu đồ thị (Hypergraph) của Module 6 vừa được Lâm nâng cấp (thêm `OBJECT`, `HAS_OBJECT`, `REFERENCE_TO`), Module 7 hiện tại đang cảnh báo lỗi vì chưa được cấu hình để "chấp nhận" các luồng dữ liệu mới mẻ này. Đây là vấn đề thuộc Module 7 và cần được khắc phục ở bước kế tiếp.
