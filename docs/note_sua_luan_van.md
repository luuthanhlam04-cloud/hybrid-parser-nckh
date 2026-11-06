# NOTE HƯỚNG DẪN SỬA ĐỔI VÀ NÂNG CẤP LUẬN VĂN / BÁO CÁO NCKH
**Mã tài liệu:** `NOTE-REVISION-NCKH-2026`  
**Ngày lập:** 06/11/2026  
**Chủ đề:** Bổ sung phương pháp luận Phễu Đánh giá Phân tầng (Tiered Funnel Evaluation), giải quyết rủi ro Prompt Confounding, chuẩn hóa hệ thống Citation và điều chỉnh cấu trúc Chương 3.

---

## PHẦN I: ĐỀ XUẤT BỔ SUNG CHIẾN LƯỢC CHO TOÀN BỘ BÁO CÁO NCKH

```
                  MÔ HÌNH PHỄU ĐÁNH GIÁ PHÂN TẦNG (TIERED FUNNEL EVALUATION)
  ┌─────────────────────────────────────────────────────────────────────────────────┐
  │ GIAI ĐOẠN 1 & 2: Component-level Context Evaluation (Benchmark A: 512 câu)      │
  │ • Ngữ liệu diện rộng: 2.087 Điều luật (Dân sự, Hình sự, Lao động, Doanh nghiệp) │
  │ • Mục tiêu: Cô lập biến độc lập (Parser v2 + MaxP)                             │
  │ • Đo lường: Retrieval Recall@5 (0.9316) + Chunk Locator Precision (99.02%)      │
  │ • Kiểm soát: KHÔNG sinh answer tự do để triệt tiêu biến nhiễu LLM Stochasticity │
  └──────────────────────────────────────┬──────────────────────────────────────────┘
                                         │ Tiền đề: Ngữ cảnh đã sạch & đủ tọa độ
                                         ▼
  ┌─────────────────────────────────────────────────────────────────────────────────┐
  │ GIAI ĐOẠN 3: System-level End-to-End Task Evaluation (Benchmark B: 50 câu)      │
  │ • Ngữ liệu chuyên sâu: Chương III Luật Đất đai 2024 (Đồ thị UKG quan hệ đa bước)│
  │ • Mục tiêu: Đánh giá toàn trình từ Lập chỉ mục -> Đồ thị -> Sinh -> Giám khảo   │
  │ • Tạo sinh: Module M10 AnswerGenerator (System Prompt pháp lý chuyên biệt)      │
  │ • Đo lường: LLM Judge v6 với Signed Gold Rubric (Atomic facts, Exceptions, Bẫy) │
  └─────────────────────────────────────────────────────────────────────────────────┘
```

### 1. Bổ sung tại Chương 2 — Mục 2.1.3 (Nguyên tắc kiểm soát biến thực nghiệm)
* **Nội dung bổ sung:** Đưa vào khái niệm **Mô hình Phễu Đánh giá Phân tầng (Tiered Funnel Evaluation)**:
  * Hệ thống RAG gồm 2 khối lớn: *Khối Chuẩn bị Ngữ cảnh (Context Pipeline)* và *Khối Tạo sinh (Generation Pipeline)*.
  * Ở Giai đoạn 1 và 2, nghiên cứu tập trung tối ưu hóa Khối Chuẩn bị Ngữ cảnh trên tập ngữ liệu diện rộng (2.087 điều luật). Để đánh giá chính xác giá trị gia tăng của Parser v2 và giải thuật MaxP, nhóm **chủ động tách rời bước tạo sinh tự do** nhằm tránh việc tính bất định (stochasticity) của LLM và kỹ thuật viết prompt làm nhiễu kết quả đo lường.
  * Chỉ khi chất lượng ngữ cảnh và tọa độ định vị đã đạt độ tin cậy thực chứng (Citation đạt 99.02%), hệ thống mới tích hợp toàn trình ở Giai đoạn 3.

### 2. Bổ sung tại Chương 2 — Mục 2.8 (Thiết kế hệ thống chỉ số đánh giá)
* **Tách bạch rạch ròi 2 định nghĩa về Citation:**
  * **Chỉ số 1: Chunk-level Locator Precision (Đo ở Giai đoạn 2 trên Benchmark A):** Đo lường tỷ lệ các phân đoạn vi mô được truy hồi có gắn tiền tố kế thừa `[Luật > Điều > Khoản > Điểm]` khớp chính xác với Ground Truth. Chỉ số này phản ánh năng lực *chống mồ côi ngữ cảnh* của tầng tiền xử lý. Kiểm toán độc lập bằng LLM-as-a-Judge (`gpt-4o-mini`, 1.536 lượt gọi) xác lập: C4 (Parser BM25) đạt 0.9028, C5 (Parser Dense) đạt 0.9902, C6 (Parser Hybrid) đạt 0.9786; các baseline Naive (C1–C3) ghi nhận `N/A*` do không hỗ trợ toạ độ phân cấp về mặt thiết kế.
  * **Chỉ số 2: End-to-End Citation Accuracy & Claim Support (Đo ở Giai đoạn 3 trên Benchmark B):** Đo lường tỷ lệ các khẳng định trong câu trả lời văn bản thực tế của LLM được bảo chứng bởi các căn cứ pháp lý hợp lệ theo Gold Rubric.

### 3. Bổ sung tại Chương 3 — Mục Các yếu tố ảnh hưởng đến tính hợp lệ (Threats to Validity)
* **Thêm mục phân tích "Kiểm soát Thiên lệch do Prompt" (Prompt Confounding Analysis):**
  * Thừa nhận một cách khoa học: Trong bài toán RAG chuyên ngành, System Prompt đóng vai trò là một "giao diện phiên dịch" giữa đồ thị tri thức và mô hình ngôn ngữ.
  * Nhóm minh chứng tính khách quan bằng việc đối soát song song ở **Tầng Truy xuất thuần túy (Retrieval Metrics)**: Ngay cả khi chưa xét đến câu chữ của câu trả lời, đồ thị UKG đề xuất đã vượt trội LightRAG về năng lực truy hồi dẫn chiếu chéo và tổng hợp cha-con. Do đó, kết quả vượt trội của hệ thống là do **chất lượng biểu diễn tri thức của đồ thị**, không phải do mẹo vặt prompt engineering.

### 4. Bổ sung tại Phần Mở đầu và Kết luận của Luận văn
* Nhấn mạnh **Đóng góp 2 Nấc (Two-tier Scientific Contribution)**:
  * **Nấc 1 (Đóng góp về Xử lý Ngữ cảnh):** Giải quyết triệt để bài toán mồ côi ngữ cảnh và bão hòa từ vựng trên văn bản lập pháp Việt Nam thông qua bộ đôi giải thuật *Structure-Aware Regex Parser v2* và *Article-level MaxP*.
  * **Nấc 2 (Đóng góp về Biểu diễn Tri thức Đồ thị):** Giải quyết bài toán suy luận đa bước, xung đột quan hệ và bẫy ngoại lệ thông qua kiến trúc *Hybrid Parser/UKG 10 module (M1–M10)* được kiểm chứng bằng bộ Gold Rubric có chữ ký chuyên gia.

---

## PHẦN II: KỊCH BẢN PHÒNG THỦ VẤN ĐÁP HỘI ĐỒNG (BỔ SUNG)

### Câu hỏi 4: *"Tại sao ở Giai đoạn 1 và 2 nhóm chỉ đánh giá ở tầng ngữ cảnh truy xuất (Context/Locator Precision) mà không đo văn bản câu trả lời do LLM sinh ra? Liệu có phải nhóm né tránh đánh giá toàn trình (End-to-End)?"*
* **Đáp luận:**
  > *"Kính thưa Hội đồng, đề tài thiết kế nghiên cứu theo **Mô hình phễu 3 giai đoạn phân tầng chặt chẽ (Funnel Methodology)**:
  > 1. **Nguyên tắc cô lập biến độc lập (Component-level Evaluation):** Mục tiêu nghiên cứu của Giai đoạn 2 là kiểm chứng giả thuyết $H_2$ về năng lực của bộ phân tích cấu trúc (Parser v2) và cơ chế MaxP trong việc khắc phục hiện tượng mồ côi ngữ cảnh và bảo toàn tọa độ pháp lý. Nếu đưa bước tạo sinh văn bản vào 512 câu hỏi ở giai đoạn này, tính bất định ngẫu nhiên của LLM (Stochasticity, Temperature, Hallucination tự phát) và kỹ thuật viết Prompt sẽ trở thành các **biến gây nhiễu (Confounding Variables)** làm sai lệch kết quả đo lường thuật toán phân đoạn.
  > 2. **Nguyên lý 'Garbage In, Garbage Out':** Nếu tầng ngữ cảnh nạp vào bị ngợp dài (~2.898 tokens) hoặc mất tiêu đề Điều, LLM thông minh đến đâu cũng sẽ bị ảo giác hoặc trích dẫn chung chung. Parser v2 đảm bảo 99.02% phân đoạn vi mô mang đúng tọa độ pháp lý và thu gọn ngữ cảnh xuống ~580 tokens — đây là điều kiện tiên quyết bảo đảm chất lượng cho tầng tạo sinh.
  > 3. **Đánh giá Toàn trình ở Giai đoạn 3:** Nhóm hoàn toàn không né tránh đánh giá toàn trình. Ngay sau khi chứng minh được chất lượng tầng ngữ cảnh ở Giai đoạn 2, nhóm đã chuyển tiếp sang **Giai đoạn 3 (Benchmark B)** để vận hành toàn trình khép kín: từ truy hồi đồ thị UKG, sinh câu trả lời bằng M10 AnswerGenerator, đến thẩm định đa chiều bằng LLM Judge dựa trên Gold Rubric (atomic facts, exceptions, forbidden claims)."*

### Câu hỏi 5: *"Hệ thống Prompt có sự khác biệt giữa các hệ thống (ví dụ: Hybrid UKG có System Prompt tiếng Việt chuyên sâu 8 điều răn, còn LightRAG dùng prompt mặc định tiếng Anh). Liệu kết quả vượt trội của Hybrid UKG ở Giai đoạn 3 có bị nhiễu do Prompt Engineering (Prompt Confounding Bias) không?"*
* **Đáp luận:**
  > *"Kính thưa Hội đồng, sự khác biệt về System Prompt được nhóm giải trình trên ba cơ sở phương pháp luận:
  > 1. **Prompt là một bộ phận kiến trúc của Domain RAG:** Trong kỹ nghệ hệ thống thông tin chuyên ngành, System Prompt của Module M10 (Retrieval & Answering) không phải là mẹo vặt bề mặt, mà là **bộ phận hợp thành của Kiến trúc Hệ thống (Architectural Component)**. M10 chịu trách nhiệm định dạng ngữ cảnh đồ thị kèm các ràng buộc suy luận pháp lý đặc thù Việt Nam (phân định chủ thể, tách biệt ngoại lệ, chuẩn hóa locator).
  > 2. **Bản chất của phép đối chuẩn Out-of-the-Box:** Mục tiêu đối chuẩn ở Giai đoạn 3 là so sánh giữa một **Kiến trúc GraphRAG tổng quát đóng gói sẵn (Generic Out-of-the-Box GraphRAG đại diện là LightRAG)** với một **Kiến trúc Chuyên ngành được tối ưu hóa cho Pháp luật Việt Nam (Domain-Specific Hybrid UKG)**. Việc giữ nguyên cấu hình mặc định của LightRAG phản ánh trung thực năng lực thực tế của các giải pháp mã nguồn mở quốc tế khi áp dụng trực tiếp vào ngữ liệu pháp luật Việt Nam.
  > 3. **Bằng chứng từ Tầng Truy xuất (Retrieval-level Evidence):** Ngay ở tầng truy xuất thuần túy — hoàn toàn không chịu tác động của prompt tạo sinh — LightRAG đã bộc lộ hạn chế sâu sắc: Retrieval Recall@5 chỉ đạt 0.7358 (so với 0.88–0.92 của hệ thống đề xuất), và nhóm câu hỏi tổng hợp cha-con chỉ đạt 0.5000. Điều này chứng minh rằng kể cả khi được cung cấp cùng một System Prompt hoàn hảo, LightRAG vẫn thất bại ở tầng tạo sinh vì đồ thị của nó vốn đã bị khuyết thiếu căn cứ pháp lý ngay từ đầu."*

---

## PHẦN III: GHI CHÚ ĐIỀU CHỈNH CẤU TRÚC VÀ SỐ LIỆU

1. **Về việc bỏ cột "Cite lý thuyết" (Deterministic Proxy) tại Bảng 3.1:**
   * Nên loại bỏ các giá trị Proxy ước tính (`0.6637*`, `0.8793*`, `0.9133*`, `0.6973*`) hoặc để `N/A*` đối với C1–C4.
   * *Lý do:* Tránh hiểu nhầm và tránh việc số Proxy 91.33% ở C3 vô tình phóng đại năng lực của Naive RAG, làm mờ nhạt mức tăng thực chất của Parser.
2. **Về việc điều chỉnh thứ tự mục Chương 3:**
   * Bỏ mục 3.9 cũ (Thảo luận lặp lại kết quả và chi phí API).
   * Lùi **3.10** (Threats to Validity) $\rightarrow$ **Mục 3.9**.
   * Lùi **3.11** (Tổng kết Chương 3) $\rightarrow$ **Mục 3.10**.

