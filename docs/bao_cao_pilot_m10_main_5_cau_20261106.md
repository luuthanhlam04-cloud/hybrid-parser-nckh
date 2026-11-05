# Báo cáo pilot M10 AUTO_FUSION trên `main` — 5 câu Chương III Luật Đất đai

**Ngày chạy:** 06/11/2026  
**Chế độ:** `AUTO_FUSION`, `top_k=5`  
**Answer model:** `openai/gpt-4o-mini` qua OpenRouter  
**Router/gate:** Jev theo cấu hình môi trường  
**Nguồn dữ liệu:** Neo4j UKG hiện hành và Chương III Luật Đất đai 2024.

## 1. Phạm vi và điều kiện chạy

Pilot kiểm tra năm dạng câu hỏi: điều kiện trực tiếp, liệt kê điều kiện con, dẫn chiếu nhiều bước, phân định chủ thể và câu hỏi ngoài phạm vi corpus. Aura Neo4j đã xác nhận `verify_connectivity()` thành công trước khi chạy.

Các output mới được ghi bởi pipeline tại:

`outputs/evaluation/m10_live_pilot_20261106.jsonl`

Câu `PILOT_01` được chạy bằng entry point `run_m10.py`; output mặc định được nối vào `outputs/evaluation/m10_answers.jsonl`. File lịch sử này đã có bản ghi cũ không kết thúc bằng dòng mới, nên cần parse theo JSON stream thay vì đọc từng dòng khi audit.

## 2. Kết quả tổng hợp

| ID | Dạng kiểm tra | Đánh giá nội dung | Kết luận |
|---|---|---|---|
| PILOT_01 | Điều kiện bán tài sản gắn liền với đất thuê | Lẫn Điều 45, thiếu Điều 46 khoản 1 điểm b | Không đạt |
| PILOT_02 | Điều kiện/phương án tại Điều 45 khoản 6 | Đúng điều kiện khung nhưng chỉ liệt kê điểm b, bỏ a/c/d/đ | Không đạt |
| PILOT_03 | Dẫn chiếu khu công nghiệp → Điều 34 → Điều 46 | Có kết luận quyền bán và nhiều điều kiện đúng, nhưng lẫn Điều 45 và không bảo toàn chain nguồn | Đạt một phần |
| PILOT_04 | Chủ thể tại Điều 41 khoản 2 điểm đ | Kết luận và điều kiện đúng | Đạt |
| PILOT_05 | Câu ngoài corpus về mức thuế | Từ chối đúng, nêu đúng giới hạn Điều 46 | Đạt |

Tỷ lệ đánh giá thủ công trong pilot: **2/5 đạt, 1/5 đạt một phần, 2/5 không đạt**. Đây là kết quả chẩn đoán, không phải metric Benchmark B chính thức.

## 3. Đối chiếu từng câu

### PILOT_01 — Điều kiện bán tài sản gắn liền với đất thuê

**Câu hỏi:** “Điều kiện để bán tài sản gắn liền với đất thuê là gì?”

Hệ thống truy hồi được Điều 46 và sinh bốn ý, trong đó có:

- Điều 46 khoản 1 điểm a: tài sản được tạo lập hợp pháp và đã đăng ký;
- Điều 46 khoản 2 điểm b: tiền bồi thường, hỗ trợ, tái định cư đã ứng trước chưa khấu trừ hết.

Tuy nhiên, câu trả lời:

- bỏ sót Điều 46 khoản 1 điểm b: hoàn thành xây dựng đúng quy hoạch chi tiết và dự án đầu tư đã được phê duyệt/chấp thuận, nếu có;
- đưa Điều 45 khoản 1 điểm a, b thành điều kiện chung, trong khi Điều 45 không phải tập điều kiện chung cho mọi trường hợp bán tài sản theo Điều 46;
- không phân biệt trường hợp chỉ bán tài sản với trường hợp bán cả tài sản và quyền thuê trong hợp đồng thuê đất.

**Đánh giá:** không đạt về condition coverage và subject/scope.

### PILOT_02 — Tổ chức kinh tế nhận chuyển nhượng đất nông nghiệp

**Câu hỏi:** “Tổ chức kinh tế nhận chuyển nhượng quyền sử dụng đất nông nghiệp phải đáp ứng điều kiện gì?”

Hệ thống nêu đúng điều kiện khung: có phương án sử dụng đất nông nghiệp được UBND cấp huyện chấp thuận. Tuy nhiên, Điều 45 khoản 6 quy định năm nội dung chính của phương án: địa điểm/diện tích/mục đích; kế hoạch sản xuất kinh doanh; vốn đầu tư; thời hạn sử dụng; tiến độ sử dụng đất.

Câu trả lời chỉ nêu kế hoạch sản xuất, kinh doanh nông nghiệp (điểm b), bỏ bốn nhóm nội dung còn lại.

**Đánh giá:** không đạt khi câu hỏi yêu cầu danh sách đầy đủ; lỗi child evidence coverage.

### PILOT_03 — Thuê lại đất trong khu công nghiệp, trả tiền hằng năm

**Câu hỏi:** “Người gốc Việt Nam định cư ở nước ngoài thuê lại đất trong khu công nghiệp và trả tiền thuê đất hằng năm có được bán tài sản gắn liền với đất không? Điều kiện là gì?”

Theo cấu trúc văn bản, đây là câu cần đi từ Điều 43 khoản 2 điểm b đến khoản 1 Điều 34, sau đó tới Điều 46. Hệ thống trả lời có quyền bán và đưa được Điều 46 khoản 1 điểm a, b cùng Điều 46 khoản 2 điểm b.

Hạn chế:

- không nêu rõ căn cứ quyền từ Điều 43 khoản 2 điểm b → Điều 34 khoản 1 điểm c;
- đưa thêm Điều 45 khoản 1 điểm a, b như điều kiện chung;
- không tách rõ điều kiện áp dụng khi bán cả tài sản và quyền thuê so với tình huống bán tài sản đơn thuần;
- `answer_paths` trong output chỉ thể hiện các bước bên trong Điều 46, chưa thể hiện chuỗi nguồn từ Điều 43 sang Điều 34.

**Đánh giá:** đạt một phần. Evidence có mặt nhưng path reconstruction và scope chưa đầy đủ.

### PILOT_04 — Cho thuê lại quyền sử dụng đất của chủ thể FDI/Việt kiều

**Câu hỏi:** “Người gốc Việt Nam định cư ở nước ngoài được Nhà nước cho thuê đất trả tiền thuê đất hằng năm có được cho thuê lại quyền sử dụng đất không?”

Câu trả lời xác định đúng Điều 41 khoản 2 điểm đ: được cho thuê lại nếu đất đã xây dựng xong kết cấu hạ tầng, trong bối cảnh được phép đầu tư kinh doanh hạ tầng tại khu công nghiệp, cụm công nghiệp hoặc khu công nghệ cao. Hệ thống cũng nêu đúng nghĩa vụ của người thuê lại: sử dụng đúng mục đích và thực hiện nghĩa vụ tài chính.

**Đánh giá:** đạt. Cần lưu ý diễn đạt nên giữ điều kiện “trong trường hợp được phép đầu tư xây dựng kinh doanh kết cấu hạ tầng” ngay trong câu chính để chặt chẽ hơn.

### PILOT_05 — Mức thuế bán tài sản gắn liền với đất thuê

**Câu hỏi:** “Điều 46 quy định mức thuế phải nộp khi bán tài sản gắn liền với đất thuê là bao nhiêu?”

Hệ thống không bịa mức thuế, nêu rõ Điều 46 chỉ quy định điều kiện bán tài sản và corpus không chứa mức thuế cụ thể.

**Đánh giá:** đạt về abstention và an toàn.

## 4. Quan sát kỹ thuật

- Cả năm câu hoàn tất truy hồi và sinh đáp án; các evidence trong context đều có locator ánh xạ được.
- Các routing/gate trace cho bốn câu ghi `fallback_used=false`, nên Jev không làm gián đoạn pipeline trong lượt chạy này.
- Gate vẫn ghi thiếu `conditions` hoặc `overall_sufficiency` ở nhiều câu, nhưng pipeline chỉ thực hiện một lượt targeted expansion. Điều này chưa bảo đảm mọi điểm con bắt buộc được đưa vào context cuối.
- AUTO_FUSION thường kích hoạt nhiều facet cùng lúc. Điều này làm recall tốt hơn nhưng có nguy cơ đưa nhánh Điều 45/Điều 46 không đúng scope vào context.
- Neo4j phát warning vì `db.index.vector.queryNodes` đã deprecated và snapshot không có quan hệ `HAS_CONSEQUENCE`/thuộc tính `name`. Các warning không làm dừng pilot, nhưng cần xử lý để giảm nhiễu và tránh query phụ không có giá trị.

## 5. Kết luận và khuyến nghị

M10 AUTO_FUSION trên `main` đã chạy end-to-end trở lại sau khi Aura Neo4j kết nối được. Khả năng từ chối câu ngoài corpus và truy hồi trực tiếp theo chủ thể hoạt động tốt. Tuy nhiên, pilot chưa đạt chất lượng để kết luận hệ thống xử lý ổn định các câu nhiều điều kiện hoặc dẫn chiếu chéo.

Ưu tiên sửa trước khi chạy benchmark lớn:

1. Khi câu hỏi yêu cầu “các điều kiện/nội dung”, bắt buộc giữ đủ children của **đúng parent branch** (ví dụ toàn bộ điểm a–đ của Điều 45 khoản 6), thay vì để ranker chọn một điểm đại diện.
2. Thêm rule phân biệt `bán tài sản` với `bán tài sản và quyền thuê`; chỉ thêm Điều 46 khoản 2 điểm b trong trường hợp thứ hai.
3. Chặn đưa Điều 45 khoản 1 vào context/answer cho Điều 46, trừ trường hợp văn bản nguồn thực sự dẫn chiếu Điều 45.
4. Với câu cross-reference, `answer_paths` phải giữ cả anchor nguồn → explicit reference target → child evidence, thay vì chỉ lưu đoạn cuối tại Điều 46.
5. Ràng buộc prompt: khi context có Điều–Khoản–Điểm, câu trả lời phải phân biệt điều kiện chung, điều kiện bổ sung và trường hợp áp dụng; không được gom chúng thành một danh sách chung.
