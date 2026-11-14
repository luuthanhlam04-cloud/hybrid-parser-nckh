# BỘ TÀI LIỆU KỊCH BẢN VÀ THIẾT KẾ THUYẾT TRÌNH BẢO VỆ NCKH (15 PHÚT)
## PHIÊN BẢN CHUẨN HÓA: STORYTELLING KHOA HỌC & MINH BẠCH CÓ CHỌN LỌC (PRECISE CONFIDENCE)

**Đề tài:** Đánh giá và tối ưu hóa các kiến trúc RAG trên nền tảng dữ liệu cấu trúc đặc thù  
**Mã số đề tài:** 14-SV-2026-RIPT | **Lĩnh vực:** Khoa học Máy tính & Công nghệ Thông tin  
**Nhóm sinh viên thực hiện:** Lưu Thanh Lâm (Nhóm trưởng) • Ngô Thế Dương • Nguyễn Bình Minh  
**Giảng viên hướng dẫn:** TS. Nguyễn Mạnh Dũng  
**Đơn vị:** Viện Khoa học Kỹ thuật Bưu điện - Học viện Công nghệ Bưu chính Viễn thông (PTIT)  

---

# MỤC LỤC BỘ TÀI LIỆU
1. **PHẦN 1: BẢN THIẾT KẾ BỐ CỤC VÀ HIỂN THỊ 14 SLIDE (VISUAL BLUEPRINT)**  
   *(Chi tiết nội dung hiển thị, thông điệp cốt lõi mỗi slide, số liệu đối chuẩn chính xác và hệ thống Thẻ định vị dẫn chứng Evidence Signposts trích thẳng từ báo cáo bancuoi.docx).*
2. **PHẦN 2: KỊCH BẢN LỜI THOẠI STORYTELLING CHUYÊN SÂU 15 PHÚT (FULL SPOKEN SCRIPT)**  
   *(Toàn văn lời thoại chi tiết cho Lâm - Dương - Lâm - Minh từ 00:00 đến 15:00. Vận dụng triệt để nguyên tắc "Minh bạch có chọn lọc" và phong cách "Precise Confidence": tự tin, điềm đạm, chuẩn xác học thuật, tuyệt đối không khoa trương, không dùng từ ngữ drama, giải thích sâu sắc nguyên nhân kỹ thuật mà không vạch áo cho người xem lưng).*
3. **PHẦN 3: BẢN PHAO THỰC CHIẾN - Ý NEO TỰ SỰ & CỬ CHỈ SÂN KHẤU (ANCHOR CHEAT SHEET)**  
   *(Bảng tra cứu cầm tay 14 slide: ý neo xung đột - giải pháp, điểm chỉ laser chính xác, câu chốt chuyển giao micro nhịp nhàng).*
4. **PHẦN 4: HỒ SƠ PHÒNG THỦ VẤN ĐÁP (Q&A DEFENSE PLAYBOOK — 15 CÂU HỎI TRỌNG YẾU)**  
   *(Bộ 15 câu hỏi phản biện hóc búa nhất về phương pháp luận, số liệu và kiến trúc kèm câu trả lời mẫu đanh thép, chuẩn phòng thủ trong 20–30 giây, phân vai rõ ràng cho từng thành viên).*

---
---

# PHẦN 1: BẢN THIẾT KẾ BỐ CỤC VÀ HIỂN THỊ 14 SLIDE (VISUAL BLUEPRINT)

> **Nguyên tắc thiết kế thị giác học thuật:**
> * **1 Slide = 1 Luận điểm cốt lõi (One Slide, One Insight):** Tập trung vào bản chất khoa học, không nhồi nhét nhiều thông điệp phụ.
> * **Hệ màu chủ đạo:** Xanh thẫm học thuật (Navy Blue `#0A2540`) + Trắng nền `#FFFFFF` + Điểm nhấn Cam đất `#D9534F` + Xanh lục bảo `#00875A`.
> * **Thẻ định vị dẫn chứng (Evidence Signpost):** Góc dưới mỗi slide số liệu có nhãn định vị trang và bảng tương ứng trong báo cáo toàn văn (ví dụ: `[Dẫn chứng: Báo cáo toàn văn — Bảng 3.4 | Trang 92]`), giúp Thầy Cô đối soát tức thì.

---

### SLIDE 1 · BÌA BÁO CÁO (LÂM | 00:00 – 00:20)
* **Bố cục hiển thị:** Bố cục trung tâm trang trọng. Logo Học viện CNBCVT và Viện KHKT Bưu điện ở góc trên.
* **Nội dung hiển thị:**
  * Tên đề tài (Font đậm, cỡ lớn, căn giữa): **ĐÁNH GIÁ VÀ TỐI ƯU HÓA CÁC KIẾN TRÚC RAG TRÊN NỀN TẢNG DỮ LIỆU CẤU TRÚC ĐẶC THÙ**
  * Tên bài toán: *Hệ thống hỏi đáp và định vị quy phạm pháp luật Việt Nam*
  * Mã số đề tài: `14-SV-2026-RIPT`
  * Nhóm sinh viên thực hiện: **Lưu Thanh Lâm** (Nhóm trưởng) • **Ngô Thế Dương** • **Nguyễn Bình Minh**
  * Giảng viên hướng dẫn: **TS. Nguyễn Mạnh Dũng**
  * Đơn vị: Học viện Công nghệ Bưu chính Viễn thông — Hà Nội, 2026

---

### SLIDE 2 · BỐI CẢNH & THÁCH THỨC CĂN CỨ PHÁP LÝ (LÂM | 00:20 – 01:30)
* **Tiêu đề:** Thách thức của RAG trước yêu cầu kiểm chứng trong lĩnh vực pháp luật
* **Luận điểm cốt lõi:** *Trong pháp luật, một câu trả lời trôi chảy nhưng thiếu căn cứ xác thực hoặc sai lệch một điều khoản có thể làm thay đổi hoàn toàn hệ quả pháp lý.*
* **Bố cục hiển thị:** Chia 3 khối đối sánh:
  * *Khối 1 (Thực tiễn):* Nhu cầu người dân tra cứu pháp luật tăng cao $\rightarrow$ Đòi hỏi câu trả lời bắt buộc phải có căn cứ kiểm chứng xác thực đến cấp quy phạm cụ thể.
  * *Khối 2 (Giới hạn của RAG phổ thông):* RAG kết nối mô hình ngôn ngữ lớn với cơ sở dữ liệu ngoài, nhưng **chưa triệt tiêu được ảo giác**.
  * *Khối 3 (Cảnh báo thực nghiệm):* Nghiên cứu của Magesh và cộng sự (2025) trên tạp chí *Journal of Empirical Legal Studies* ghi nhận AI thương mại gặp tỷ lệ ảo giác pháp lý từ **17% đến 33%**.
* **Thẻ dẫn chứng:** `[Tham chiếu: Báo cáo toàn văn — Mục 1, Mở đầu | Trang 14]`.

---

### SLIDE 3 · ĐẶC THÙ VĂN BẢN LUẬT & KHOẢNG TRỐNG NGHIÊN CỨU (DƯƠNG | 01:30 – 02:25)
* **Tiêu đề:** Ba đặc thù văn bản luật Việt Nam & Khoảng trống của các kiến trúc RAG
* **Luận điểm cốt lõi:** *Văn bản luật có cấu trúc phả hệ đa tầng và mạng lưới dẫn chiếu, trong khi các kiến trúc RAG hiện hành chủ yếu được thiết kế cho văn bản phẳng phi cấu trúc.*
* **Bố cục hiển thị:** Đối chiếu song song 2 cột:
  * *Cột trái (3 Đặc thù kiến trúc):*
    1. **Cấu trúc phân cấp đa tầng nghiêm ngặt:** Luật $\rightarrow$ Chương $\rightarrow$ Mục $\rightarrow$ Điều $\rightarrow$ Khoản $\rightarrow$ Điểm. Mệnh đề cấp con phụ thuộc tuyệt đối vào chủ thể và điều kiện ở cấp cha.
    2. **Mạng lưới dẫn chiếu phức tạp:** Viện dẫn nội bộ và dẫn chiếu liên văn bản dày đặc.
    3. **Lệch pha ngôn ngữ:** Câu hỏi khẩu ngữ tự nhiên của người dân khác xa từ vựng lập pháp quy chuẩn.
  * *Cột phải (3 Khoảng trống nghiên cứu tương ứng):*
    1. **Gap 1:** Thiếu khung đối chuẩn thực nghiệm có kiểm soát biến số trên dữ liệu luật Việt Nam.
    2. **Gap 2:** Thiếu đánh giá thực nghiệm về tác động của phân đoạn cấu trúc vi mô so với cắt khối token thô truyền thống.
    3. **Gap 3:** Các thước đo RAG tổng quát hiện nay không đo lường được tính chính xác của trích dẫn căn cứ và chuỗi dẫn chiếu.
* **Thẻ dẫn chứng:** `[Tham chiếu: Báo cáo toàn văn — Mục 2, Mở đầu | Trang 15–16]`.

---

### SLIDE 4 · CƠ SỞ LÝ THUYẾT: BA TRƯỜNG PHÁI RAG CƠ SỞ (DƯƠNG | 02:25 – 03:20)
* **Tiêu đề:** Cơ sở lý thuyết — Ba trường phái RAG đối chuẩn cơ sở
* **Luận điểm cốt lõi:** *Khảo sát ba đại diện tiêu biểu cho ba nguyên lý truy xuất thông tin hiện đại để thiết lập đường cơ sở (Baseline).*
* **Bố cục hiển thị:** 3 cột kiến trúc trực quan:
  * *Cột 1 — Naive Vector RAG (Không gian Dense):* Sử dụng Bi-encoder biểu diễn câu hỏi và tài liệu trong không gian vector đa chiều, truy hồi Top-K dựa trên độ tương đồng Cosine.
  * *Cột 2 — Hybrid RAG (Dung hợp từ vựng & ngữ nghĩa):* Kết hợp tìm kiếm từ khóa chính xác BM25 và truy hồi Dense vector, dung hợp thứ hạng bằng thuật toán Reciprocal Rank Fusion (RRF), sau đó dùng Cross-Encoder để tái xếp hạng.
  * *Cột 3 — LightRAG (Đại diện GraphRAG):* Khai thác biểu diễn đồ thị thực thể và quan hệ hai tầng, hỗ trợ truy hồi ngữ cảnh rộng Local và Global.
* **Thẻ dẫn chứng:** `[Tham chiếu: Báo cáo toàn văn — Mục 2.4 | Bảng 2.3 | Trang 57]`.

---

### SLIDE 5 · HỆ THỐNG CÂU HỎI NGHIÊN CỨU (DƯƠNG | 03:20 – 04:05)
* **Tiêu đề:** Bốn câu hỏi nghiên cứu định hướng đề tài (RQ1 – RQ4)
* **Luận điểm cốt lõi:** *Lộ trình thực nghiệm ba giai đoạn nhằm từng bước giải mã và tối ưu hóa năng lực trích dẫn pháp lý.*
* **Bố cục hiển thị:** Bảng ma trận 4 câu hỏi nghiên cứu:
  * **RQ1 (Giai đoạn 1):** Ba kiến trúc RAG cơ sở thể hiện năng lực truy hồi và độ chính xác trích dẫn như thế nào trên văn bản luật Việt Nam khi áp dụng chiến lược cắt đoạn thô truyền thống?
  * **RQ2 (Giai đoạn 2):** Chiến lược phân đoạn cấu trúc vi mô (Parser v2) kết hợp tiền tố bất biến và thuật toán gom điểm Article MaxP có giải quyết được vấn đề trích dẫn và tối ưu hóa dung lượng ngữ cảnh không?
  * **RQ3 (Giai đoạn 3):** Kiến trúc đồ thị tri thức hợp nhất (Hybrid UKG) cải thiện khả năng định vị điều kiện và xử lý mệnh đề ngoại lệ pháp luật so với GraphRAG truyền thống như thế nào?
  * **RQ4 (Giai đoạn 3):** Đồ thị tri thức có khả năng giải quyết bài toán truy vết chuỗi quan hệ dẫn chiếu chéo đa bước trong văn bản quy phạm pháp luật hay không?
* **Thẻ dẫn chứng:** `[Tham chiếu: Báo cáo toàn văn — Mục 4, Mở đầu | Trang 17]`.

---

### SLIDE 6 · THIẾT KẾ THỰC NGHIỆM & HẠ TẦNG BENCHMARK (DƯƠNG | 04:05 – 05:15)
* **Tiêu đề:** Thiết kế thực nghiệm: Khung Benchmark Harness, Hai bộ dữ liệu & Quy trình kiểm chuẩn
* **Luận điểm cốt lõi:** *Thiết lập một sân chơi đối chuẩn công bằng: Đóng băng biến số ngoại lai, kiểm soát trùng lặp từ vựng và chuẩn hóa quy trình đánh giá.*
* **Bố cục hiển thị:** 3 khối thông tin khoa học:
  * *Khối 1 — Hạ tầng Harness & Đóng băng biến số:* Áp dụng mẫu thiết kế `BaseRAGAdapter` chuẩn hóa đầu vào/đầu ra; đóng băng toàn bộ biến ngoại lai: cùng ngữ liệu, cùng mô hình nhúng, cùng LLM, cùng tham số nhiệt độ $T=0$.
  * *Khối 2 — Hai bộ Benchmark độc lập:*
    * **Benchmark A (Quy mô rộng):** Ngữ liệu gồm **2.087 điều luật** thuộc 7 văn bản luật lớn. Tập câu hỏi gồm **512 câu hỏi** đã được biên tập lại có chọn lọc nhằm **giảm độ trùng lặp từ vựng Jaccard trung bình từ 0,68 xuống 0,31** (mô phỏng ngôn ngữ đời thường, hạn chế lợi thế so khớp từ khóa). Thiết lập tập đối chuẩn công bằng **Tier 1 gồm 205 câu hỏi trên 500 điều** đã lập chỉ mục cho LightRAG để đối đầu sòng phẳng về phạm vi dữ liệu.
    * **Benchmark B (Độ sâu ngữ nghĩa):** 50 câu hỏi phân tầng tại Chương III Luật Đất đai 2024, gắn nhãn vi mô tới từng Khoản, Điểm, Điều kiện, Ngoại lệ và Chuỗi dẫn chiếu.
  * *Khối 3 — Quy trình đánh giá kép:* Kết hợp kiểm toán tất định các chỉ số cấu trúc với thẩm định ngữ nghĩa bằng LLM-as-a-Judge có kiểm tra schema nghiêm ngặt.
* **Thẻ dẫn chứng:** `[Tham chiếu: Báo cáo toàn văn — Mục 2.2, 2.3, 2.7, 2.9 | Bảng 2.1, 2.2 | Trang 47, 50, 69, 76]`.

---

### SLIDE 7 · GIAI ĐOẠN 1: KẾT QUẢ ĐỐI CHUẨN & TRẢ LỜI RQ1 (LÂM | 05:15 – 06:40)
* **Tiêu đề:** Giai đoạn 1 — Khoảng cách giữa truy hồi và trích dẫn trên tập Tier 1 (N = 205 câu) & Trả lời RQ1
* **Luận điểm cốt lõi:** *Hiệu năng tìm kiếm tài liệu cao chưa đồng nghĩa với việc câu trả lời trích dẫn đúng căn cứ: Cắt đoạn thô làm đứt gãy phả hệ phân cấp.*
* **Bố cục hiển thị:** Bảng số liệu Bảng 3.4 kèm Hộp phân tích cơ chế:
  * *Bảng số liệu đối chuẩn (Tier 1 Fair Subset):*
    * Naive Vector RAG: Recall 0,9561 | Context Precision 0,9659 | **Citation Accuracy: 0,3259**
    * Hybrid RAG: Recall 0,9659 | Context Precision 0,9660 | **Citation Accuracy: 0,2902**
    * LightRAG: Recall 0,9659 | Context Precision 0,8829 | **Citation Accuracy: 0,1371**
  * *Hiện tượng đáng lưu tâm:* Cả ba hệ thống đều tìm trúng Điều luật liên quan ($Recall > 95\%$). Tuy nhiên, khi đánh giá câu trả lời cuối cùng, Citation Accuracy chỉ đạt $\sim 30\%$, riêng LightRAG chỉ ghi nhận **$13,71\%$**.
  * *Cơ chế kỹ thuật:* Việc cắt khối thô 1.200 token làm đứt gãy quan hệ cha-con. Đoạn trích đưa vào prompt bị mất thông tin chủ thể ở cấp Điều, khiến mô hình suy đoán vị trí pháp lý không chính xác.
  * *Ghi chú phương pháp luận:* Con số ở đây đo trên câu trả lời cuối cùng; sang GĐ2 nhóm đo trên ngữ cảnh truy hồi — đây là hai lớp chẩn đoán bổ sung cho hai mục tiêu khác nhau.
  * *Chốt hạ RQ1:* Các kiến trúc RAG cơ sở chưa đáp ứng được yêu cầu trích dẫn chính xác nếu giữ nguyên phương thức cắt đoạn thô.
* **Thẻ dẫn chứng:** `[Dẫn chứng: Báo cáo toàn văn — Mục 3.2 | Bảng 3.3, Bảng 3.4 | Trang 91–93]`.

---

### SLIDE 8 · GIAI ĐOẠN 2: PARSER V2 & ARTICLE-LEVEL MAXP (LÂM | 06:40 – 08:05)
* **Tiêu đề:** Giai đoạn 2 — Giải pháp phân đoạn cấu trúc vi mô & Gom điểm cực đại Article MaxP
* **Luận điểm cốt lõi:** *Bảo toàn phả hệ bằng tiền tố bất biến và gom điểm cấp Điều để vừa không mất ngữ cảnh cha-con, vừa loại bỏ hiện tượng bão hòa Top-K.*
* **Bố cục hiển thị:** Sơ đồ 2 nửa màn hình:
  * *Nửa trái — Structure-Aware Parser v2:*
    * Bóc tách đệ quy 2.087 Điều luật thành **12.754 phân đoạn vi mô** cấp Khoản và Điểm.
    * Gắn tiền tố phân cấp bất biến: `[Luật Đất đai 2024 > Chương III > Điều 45 > Khoản 1 > Điểm a]`.
    * Khâu Validation tự động bảo toàn 100% phả hệ và nhận diện ký tự tiếng Việt đặc thù.
  * *Nửa phải — Thuật toán gom điểm cực đại Article-level MaxP:*
    * *Vấn đề:* 12.754 đoạn nhỏ gây bão hòa Top-K (Top-5 trả về 5 điểm thuộc cùng 1 điều).
    * *Công thức gom điểm:* $\text{Score}(\text{Article}_i) = \max_{p \in \text{Article}_i} \text{Score}(p)$.
    * *Cơ chế:* 1 Điểm luật trúng khớp sẽ kéo cả Điều luật đại diện lên Top đầu, sau đó trích xuất đúng phân đoạn vi mô chứa bằng chứng để đưa vào prompt.
* **Thẻ dẫn chứng:** `[Tham chiếu: Báo cáo toàn văn — Mục 2.5 | Trang 61–68]`.

---

### SLIDE 9 · GIAI ĐOẠN 2: MA TRẬN ĐỐI SOÁT C1 – C6 & KẾT QUẢ C5 (LÂM | 08:05 – 10:00)
* **Tiêu đề:** Giai đoạn 2 — Kết quả ma trận 6 cấu hình trên Benchmark A (N = 512 câu) & Trả lời RQ2
* **Luận điểm cốt lõi:** *C5 nâng Citation Accuracy trên ngữ cảnh lên 0,9902, giảm 79,9% dung lượng token; xác thực giả thuyết H2.*
* **Bố cục hiển thị:** Bảng ma trận Bảng 3.6 và 3 con số Headline nổi bật:
  * *Bảng số liệu 6 cấu hình (512 câu | 3.072 lượt chấm LLM-Judge):*
    * C1 (Naive BM25): Citation 0,7490 | Điểm 1,0: 72,5% | Token ~2.500
    * C2 (Naive Dense): Citation 0,4000 | Điểm 1,0: 25,4% | Token ~2.898
    * C3 (Naive Hybrid): Citation 0,3986 | Điểm 1,0: 25,6% | Token ~2.898
    * C4 (Parser BM25): Citation 0,9028 | Điểm 1,0: 89,3% | Token ~580
    * **C5 (Parser Dense): Citation 0,9902 | Điểm 1,0: 98,4% (504/512 câu) | Token ~580**
    * C6 (Parser Hybrid $\alpha=0,5$): Citation 0,9786 | Điểm 1,0: 96,3% | Token ~580
  * *Ba kết quả đáng chú ý:*
    * **`0,9902` (Citation Acc C5 trên ngữ cảnh):** Tăng **+59,02 điểm phần trăm** so với C2 (0,4000). Có **504 / 512 câu đạt điểm tuyệt đối 1,0**.
    * **`-79,9%` (Tiết kiệm token):** Dung lượng giảm từ $\sim 2.898$ token xuống còn **$\sim 580$ token**.
    * **`α = 0,8` (Weighted RRF tối ưu):** Đưa Recall lên **0,9297** và MRR lên **0,8220**, khắc phục hiện tượng cào bằng ở C6.
  * *Ghi chú phương pháp luận:* Điểm đo trên ngữ cảnh là điều kiện cần để câu trả lời trích dẫn đúng; đánh giá câu trả lời hoàn chỉnh được thực hiện riêng tại GĐ3.
  * *Chốt hạ RQ2:* Phân đoạn cấu trúc vi mô kết hợp MaxP giải quyết tốt bài toán trích dẫn chính xác trên ngữ cảnh và tối ưu hóa chi phí.
* **Thẻ dẫn chứng:** `[Dẫn chứng: Báo cáo toàn văn — Mục 3.3 | Bảng 3.5, Bảng 3.6, Bảng 3.7 | Trang 96–101]`.

---

### SLIDE 10 · GIAI ĐOẠN 3: TRIẾT LÝ KIẾN TRÚC HYBRID UKG & MODULE 5 (MINH | 10:00 – 11:15)
* **Tiêu đề:** Giai đoạn 3 — Triết lý kiến trúc 2 tầng Hybrid Parser / UKG & Bộ định tuyến Module 5
* **Luận điểm cốt lõi:** *Tách biệt cấu trúc vật lý bất biến và thông tin ngữ nghĩa động để vừa bảo vệ phả hệ văn bản nguồn, vừa khai thác được quan hệ pháp lý phức tạp.*
* **Bố cục hiển thị:** Sơ đồ dòng chảy 2 tầng:
  * *Tầng 1 — Đồ thị Cấu trúc vật lý (Physical Graph):* Khóa cứng 100% phả hệ Chương-Mục-Điều-Khoản-Điểm bằng bộ phân tích tất định, tạo trục xương sống độc lập với LLM.
  * *Tầng 2 — Đồ thị Ngữ nghĩa (Semantic Graph):* Trích xuất các thực thể và quan hệ pháp lý động (quyền, nghĩa vụ, điều kiện, ngoại lệ) gắn lên trục xương sống.
  * *Trọng tâm kỹ thuật Module 5 (Semantic Router):* 
    * Ứng dụng mô hình **Qwen2.5-0.5B** kết hợp toán tử **Max-Fusion** logic OR:  
      $$S_{\text{fusion}} = \max(S_{\text{regex}}, S_{\text{semantic}})$$
    * Khảo sát độc lập tại Phụ lục A cho thấy Causal Attention của Qwen2.5-0.5B khắc phục được "Cạm bẫy trung bình" (Mean-Pooling Trap) của Bi-encoder trên phân đoạn ngắn pháp lý.
    * Tại ngưỡng $\theta = 0,85$, hệ thống đạt **Recall 96,85%**, F1 đạt **0,8146**, loại bỏ an toàn 9,33% phân đoạn thủ tục trước khi chuyển sang trích xuất.
* **Thẻ dẫn chứng:** `[Tham chiếu: Báo cáo toàn văn — Mục 2.6 | Hình 2.2, Bảng 2.4 & Phụ lục A | Bảng A.1, A.2 | Trang 63, 128–130]`.

---

### SLIDE 11 · GIAI ĐOẠN 3: KẾT QUẢ ĐỐI CHUẨN TRÊN BENCHMARK B (MINH | 11:15 – 13:00)
* **Tiêu đề:** Giai đoạn 3 — Kết quả thực nghiệm Benchmark B (N = 50 câu) & Trả lời RQ3, RQ4
* **Luận điểm cốt lõi:** *UKG thể hiện ưu thế rõ rệt ở tầng truy hồi và xử lý ngoại lệ pháp luật; phân tích khách quan trade-off về độ bao phủ điều kiện và ranh giới tái dựng chuỗi.*
* **Bố cục hiển thị:** Bảng số liệu Bảng 3.9, 3.14, 3.15 đối sánh trực diện với LightRAG:
  * *Ghi chú phạm vi mẫu:* $N = 50$ câu hỏi (gồm 47 câu đánh giá truy hồi/chất lượng, 3 câu kiểm tra an toàn/từ chối).
  * *Kết quả giải quyết RQ3:*
    * **Recall@5 cấp Điều:** UKG đạt **0,9184** so với LightRAG **0,7358** (**Vượt +18,26 điểm %**).
    * **MRR@5 cấp Điều:** UKG đạt **0,8848** so với LightRAG **0,5539** (**Vượt +33,09 điểm %**).
    * **Exception Coverage (Độ phủ ngoại lệ):** UKG đạt **0,6786** so với LightRAG **0,3929** (**Vượt +28,57 điểm %** nhờ bóc tách chính xác các mệnh đề "trừ trường hợp...").
    * **Subject-Scope Accuracy:** UKG đạt **0,8889** so với LightRAG **0,7639** (**Vượt +12,50 điểm %**).
    * **Legal Correctness:** UKG đạt **0,8777** so với LightRAG **0,8210** (**Vượt +5,67 điểm %**).
  * *Trade-off về Condition Coverage:* LightRAG đạt 0,8421 và UKG đạt 0,7066. Phản ánh hai triết lý: LightRAG dùng chunk 1.200 token lớn bao phủ rộng; UKG tập trung vào quy phạm lõi nên cần thêm cơ chế lan truyền điều kiện sang các node lân cận.
  * *Kết quả giải quyết RQ4:* Định vị tốt các node đích với Reference-target Recall đạt **58,67%**. Việc tái dựng chuỗi có thứ tự cần thêm cơ chế Constrained Graph Traversal (trên 18 câu hỏi dẫn chiếu, kết quả Chain Exact Match ghi nhận $0,0000$).
* **Thẻ dẫn chứng:** `[Dẫn chứng: Báo cáo toàn văn — Mục 3.4, 3.6, 3.7 | Bảng 3.9, Bảng 3.14, Bảng 3.15 | Trang 103, 108, 110]`.

---

### SLIDE 12 · TỔNG HỢP KẾT QUẢ THEO BỐN CÂU HỎI NGHIÊN CỨU (MINH | 13:00 – 13:55)
* **Tiêu đề:** Tổng hợp kết quả thực nghiệm giải quyết 4 câu hỏi nghiên cứu (RQ1 – RQ4)
* **Luận điểm cốt lõi:** *Đóng gói đanh thép câu trả lời cho cả bốn bài toán khoa học đặt ra ở đầu đề tài.*
* **Bố cục hiển thị:** Bảng ma trận 4 khối đối ứng:
  * **Trả lời RQ1:** Thực nghiệm xác lập khoảng cách giữa truy hồi và trích dẫn: RAG cơ sở đạt Recall trên 95% nhưng Citation Accuracy câu trả lời chỉ khoảng 30% (LightRAG ghi nhận 13,71%) do cắt đoạn thô làm đứt gãy phả hệ pháp lý.
  * **Trả lời RQ2:** Giải pháp Parser v2 và MaxP nâng Citation Accuracy trên ngữ cảnh lên **0,9902** (98,4% tuyệt đối) và tiết kiệm **79,9% token**, xác định điểm cân bằng Weighted RRF tại $\alpha=0,8$.
  * **Trả lời RQ3:** Hybrid UKG vượt trội LightRAG ở truy hồi cấp Điều (Recall +18,26 đpt, MRR +33,09 đpt) và độ phủ ngoại lệ (+28,57 đpt) — hai điểm yếu cố hữu của GraphRAG truyền thống.
  * **Trả lời RQ4:** Định vị tốt các node đích (58,67%); việc tái dựng chuỗi hoàn chỉnh cần thêm cơ chế constrained graph traversal, đây là hướng nghiên cứu trọng tâm tiếp theo.
* **Thẻ dẫn chứng:** `[Tham chiếu: Báo cáo toàn văn — Mục 1, Kết luận | Trang 123–124]`.

---

### SLIDE 13 · BA ĐÓNG GÓP KHOA HỌC CHÍNH (MINH | 13:55 – 14:35)
* **Tiêu đề:** Ba đóng góp khoa học cốt lõi của đề tài & Thông điệp đúc kết
* **Luận điểm cốt lõi:** *Đóng góp đồng thời cả về Phương pháp luận kiểm chuẩn, Giải pháp kỹ thuật phân đoạn và Kiến trúc hệ thống đồ thị.*
* **Bố cục hiển thị:** 3 cột đóng góp mang tính dấu ấn + Hộp thông điệp đúc kết:
  * *Đóng góp 1 — Khung kiểm chuẩn Benchmark:* Xây dựng hai bộ dữ liệu Benchmark A và B cùng hạ tầng Adapter Pattern loại bỏ thiên lệch thực nghiệm.
  * *Đóng góp 2 — Giải pháp phân đoạn cấu trúc vi mô:* Bộ đôi Parser v2 và Article MaxP giải quyết vấn đề sụt giảm trích dẫn và tối ưu hóa tài nguyên tính toán.
  * *Đóng góp 3 — Kiến trúc đồ thị hai tầng Hybrid UKG:* Chứng minh tính hiệu quả của việc kết hợp cây phân cấp vật lý bất biến với đồ thị ngữ nghĩa động trong việc xử lý các quy phạm ngoại lệ phức tạp.
  * *Hộp thông điệp chốt (Takeaway Box):* **"Trong pháp luật, cấu trúc không phải là chi tiết triển khai — nó là điều kiện tiên quyết để AI có thể trích dẫn đúng."**
* **Thẻ dẫn chứng:** `[Tham chiếu: Báo cáo toàn văn — Mục 2, Kết luận | Trang 124–125]`.

---

### SLIDE 14 · HƯỚNG PHÁT TRIỂN & KẾT THÚC (MINH | 14:35 – 15:00)
* **Tiêu đề:** Hướng nghiên cứu tiếp theo & Lời cảm ơn
* **Luận điểm cốt lõi:** *Xác định rõ ràng lộ trình hoàn thiện hệ thống và mở rộng phạm vi pháp lý.*
* **Bố cục hiển thị:**
  * *Hướng phát triển kỹ thuật:* Mở rộng Parser sang Nghị định, Thông tư; tự động hóa cập nhật hiệu lực văn bản; và hoàn thiện cơ chế Constrained Graph Traversal để khép kín chuỗi dẫn chiếu.
  * *Hướng hoàn thiện đánh giá:* Bổ sung thực nghiệm ablation từng thành phần trong gói Parser; mở rộng ngữ liệu; và phối hợp với chuyên gia pháp lý để hiệu chuẩn kết quả LLM Judge độc lập.
  * *Phần cảm ơn trang trọng:* "Trân trọng cảm ơn Quý Thầy Cô trong Hội đồng khoa học đã chú ý lắng nghe! Kính mời Hội đồng đặt câu hỏi (Q&A)."

---
---

# PHẦN 2: KỊCH BẢN LỜI THOẠI STORYTELLING CHUYÊN SÂU 15 PHÚT (FULL SPOKEN SCRIPT)

---

### [00:00 – 01:30] · CHẶNG 1: LƯU THANH LÂM (MỞ MÀN & ĐẶT VẤN ĐỀ)

**[Slide 1 — Bìa báo cáo · 00:00 – 00:20]**
> *"Kính thưa Quý Thầy Cô trong Hội đồng khoa học!  
> Em xin đại diện nhóm nghiên cứu gồm ba thành viên: Lưu Thanh Lâm, Ngô Thế Dương và Nguyễn Bình Minh, dưới sự hướng dẫn khoa học của Thầy Tiến sĩ Nguyễn Mạnh Dũng, trình bày đề tài:  
> **'Đánh giá và tối ưu hóa các kiến trúc RAG trên nền tảng dữ liệu cấu trúc đặc thù'**, tập trung vào bài toán hỏi đáp trên văn bản quy phạm pháp luật Việt Nam."*

**[Slide 2 — Bối cảnh & Thách thức căn cứ pháp lý · 00:20 – 01:30]**
> *"Kính thưa Hội đồng,  
> Trong kỷ nguyên số hóa, nhu cầu tra cứu thông tin pháp luật của người dân và doanh nghiệp đang ngày một tăng cao. Tuy nhiên, lĩnh vực pháp luật có một yêu cầu nghiêm ngặt: Một câu trả lời không chỉ cần đúng về mặt ngữ nghĩa, mà **bắt buộc phải có căn cứ kiểm chứng xác thực đến từng điều khoản cụ thể**.  
> 
> Mặc dù kiến trúc RAG kết hợp mô hình ngôn ngữ lớn với việc truy hồi dữ liệu bên ngoài đã giúp cải thiện đáng kể độ tin cậy, nhưng các nghiên cứu thực nghiệm quốc tế gần đây, tiêu biểu như công bố của Magesh và cộng sự năm 2025 trên tạp chí *Journal of Empirical Legal Studies*, đã chỉ ra rằng các hệ thống AI thương mại hàng đầu vẫn gặp tỷ lệ ảo giác pháp lý từ 17% đến 33%.  
> Trong thực tiễn pháp lý, chỉ cần hệ thống trích dẫn đúng số Điều nhưng dẫn sai một Khoản, hoặc nhầm lẫn một ngoại lệ tại một Điểm, hệ quả pháp lý của hành vi có thể bị đảo lộn hoàn toàn từ hợp pháp sang vi phạm.  
> 
> Nhận diện được rủi ro đó, đề tài của nhóm tập trung giải quyết bài toán cốt lõi: Làm thế nào để vừa tối ưu hiệu quả truy hồi, vừa hỗ trợ mô hình ngôn ngữ lớn xác định chính xác căn cứ pháp lý vi mô mà không làm bùng nổ chi phí tính toán?  
> Để làm rõ đặc thù của văn bản luật Việt Nam và cơ sở nghiên cứu của nhóm, sau đây em xin trân trọng kính mời bạn **Ngô Thế Dương**."*  
*(Lâm chuyển micro cho Dương).*

---

### [01:30 – 05:15] · CHẶNG 2: NGÔ THẾ DƯƠNG (ĐẶC THÙ, LÝ THUYẾT & HẠ TẦNG BENCHMARK)

**[Slide 3 — Đặc thù luật & Khoảng trống · 01:30 – 02:25]**
> *"Em xin cảm ơn bạn Lâm. Kính thưa Quý Thầy Cô,  
> Qua quá trình tìm hiểu, nhóm nhận thấy văn bản quy phạm pháp luật Việt Nam có ba đặc điểm kiến trúc đáng chú ý:  
> Thứ nhất là cấu trúc phân cấp đa tầng nghiêm ngặt: từ Luật xuống Chương, Mục, Điều, Khoản và Điểm. Nội dung quy định tại một Điểm luôn phụ thuộc chặt chẽ vào chủ thể và điều kiện được xác lập ở cấp cha.  
> Thứ hai là mạng lưới dẫn chiếu phức tạp, gồm cả viện dẫn nội bộ giữa các điều luật và dẫn chiếu chéo liên văn bản giữa Luật với các văn bản dưới luật.  
> Thứ ba là sự khác biệt lớn giữa ngôn ngữ trong câu hỏi thông thường của người dân với cách diễn đạt chuẩn tắc của văn bản lập pháp.  
> 
> Từ ba đặc thù đó, nhóm xác định ba khoảng trống nghiên cứu chính:  
> Một là sự thiếu vắng một khung đối chuẩn thực nghiệm công bằng có kiểm soát biến số trên dữ liệu luật Việt Nam;  
> Hai là chưa có đánh giá định lượng về tác động của việc phân đoạn cấu trúc vi mô so với việc cắt khối token thô truyền thống;  
> Và ba là các bộ thước đo RAG tổng quát hiện nay chưa đánh giá được độ chính xác của trích dẫn căn cứ và chuỗi dẫn chiếu.  
> Đây là cơ sở để nhóm xây dựng phương pháp nghiên cứu của đề tài."*

**[Slide 4 — Cơ sở lý thuyết: Ba trường phái RAG · 02:25 – 03:20]**
> *"Để giải quyết các khoảng trống trên, về mặt cơ sở lý thuyết, nhóm lựa chọn khảo sát ba trường phái RAG đại diện hiện nay trên thế giới:  
> Đầu tiên là **Naive Vector RAG**. Hệ thống biểu diễn câu hỏi và tài liệu thành các vector trong không gian đa chiều, sau đó sử dụng độ tương đồng ngữ nghĩa Cosine để tìm những tài liệu liên quan.  
> Thứ hai là **Hybrid RAG**. Phương pháp này kết hợp tìm kiếm từ khóa chính xác BM25 với truy hồi Dense vector. Kết quả từ hai nhánh được dung hợp bằng thuật toán Reciprocal Rank Fusion, sau đó sử dụng Cross-Encoder để tái xếp hạng.  
> Thứ ba là **LightRAG**, một kiến trúc đại diện cho trường phái GraphRAG, khai thác đồ thị thực thể và quan hệ để hỗ trợ suy luận ngữ cảnh rộng và kết nối các tri thức phân tán.  
> 
> Ba kiến trúc đại diện cho những hướng tổ chức và truy hồi dữ liệu khác nhau. Nhóm sử dụng chúng làm các hệ thống cơ sở để đánh giá tại Giai đoạn 1, trước khi khảo sát những phương án tối ưu hóa mở rộng."*

**[Slide 5 — Hệ thống 4 Câu hỏi nghiên cứu RQ1 – RQ4 · 03:20 – 04:05]**
> *"Nhằm định hướng toàn bộ quá trình thực nghiệm, nhóm xây dựng khung nghiên cứu gồm bốn câu hỏi khoa học từ RQ1 đến RQ4:  
> **RQ1** xem xét sự khác biệt về hiệu quả truy hồi và chất lượng trích dẫn giữa ba kiến trúc RAG cơ sở khi áp dụng chiến lược cắt đoạn thô.  
> **RQ2** đánh giá tác động của việc bổ sung Parser v2, bước kiểm tra Validation và cơ chế MaxP khi phân đoạn văn bản theo cấu trúc Điều–Khoản–Điểm.  
> **RQ3** tập trung vào khả năng định vị điều kiện và xử lý ngoại lệ pháp lý của kiến trúc Hybrid Parser/UKG so với GraphRAG truyền thống.  
> Và **RQ4** kiểm tra khả năng tìm kiếm và tái dựng các chuỗi quan hệ dẫn chiếu giữa những quy định có liên quan.  
> Bốn câu hỏi này sẽ được nhóm lần lượt đối chiếu với kết quả thực nghiệm qua ba giai đoạn."*

**[Slide 6 — Thiết kế thực nghiệm & Hạ tầng Benchmark · 04:05 – 05:15]**
> *"Kính thưa Hội đồng,  
> Để kết quả thực nghiệm có giá trị khoa học và khả năng tái lập, nhóm xây dựng hạ tầng kiểm thử **Benchmark Harness** áp dụng Adapter Pattern — chuẩn hóa đầu vào và đầu ra qua một giao diện chung `BaseRAGAdapter`, đồng thời đóng băng toàn bộ biến ngoại lai: cùng ngữ liệu, cùng mô hình nhúng BGE-M3, cùng mô hình ngôn ngữ GPT-4o-mini ở nhiệt độ bằng 0. Mọi chênh lệch số liệu vì vậy phản ánh bản chất thuật toán, không phải nhiễu môi trường.  
> 
> Về mặt dữ liệu, nhóm tự xây dựng hai bộ kiểm chuẩn độc lập:  
> **Benchmark A** gồm 2.087 điều luật tổng hợp từ 7 văn bản luật lớn của Việt Nam, với 512 câu hỏi được biên soạn lại có chọn lọc cho các câu có mức trùng lặp vượt ngưỡng 0,5 nhằm kéo độ trùng lặp từ vựng Jaccard trung bình từ 0,68 xuống 0,31 — mục đích là mô phỏng ngôn ngữ tra cứu đời thường, tránh để phương pháp so khớp từ khóa hưởng lợi không công bằng. Trong Benchmark A, nhóm tách riêng tập đối chuẩn công bằng **Tier 1 gồm 205 câu hỏi** có toàn bộ căn cứ nằm trong 500 điều đã lập chỉ mục cho LightRAG, tạo một sân đấu công bằng tuyệt đối về phạm vi dữ liệu.  
> **Benchmark B** gồm 50 câu hỏi phân tầng tại Chương III Luật Đất đai 2024, gắn nhãn vi mô tới từng Khoản, Điểm, điều kiện, ngoại lệ và chuỗi dẫn chiếu. Quy trình đánh giá kết hợp kiểm toán tất định các chỉ số cấu trúc với thẩm định ngữ nghĩa bằng LLM-as-a-Judge có kiểm tra schema nghiêm ngặt.  
> 
> Sau đây, em xin mời bạn **Lưu Thanh Lâm** trình bày kết quả Benchmark A và phương án cải tiến được nhóm khảo sát."*  
*(Dương chuyển giao micro cho Lâm).*

---

### [05:15 – 10:00] · CHẶNG 3: LƯU THANH LÂM (GIAI ĐOẠN 1 NGHỊCH LÝ & GIAI ĐOẠN 2 ĐỘT PHÁ)

**[Slide 7 — Giai đoạn 1: Nghịch lý sụp đổ trích dẫn · 05:15 – 06:40]**
> *"Em xin cảm ơn bạn Dương. Kính thưa Hội đồng khoa học,  
> Khi đối soát công bằng ba kiến trúc RAG trên tập Tier 1 gồm 205 câu hỏi, nhóm ghi nhận một hiện tượng đáng lưu tâm mà chúng em gọi là **khoảng cách giữa truy hồi và trích dẫn**:  
> 
> Nhìn vào Bảng 3.4, cả ba hệ thống đều thể hiện năng lực tìm kiếm tài liệu rất tốt: Recall@5 đều đạt từ 95,6% đến 96,6%. Độ khớp ngữ cảnh Context Precision của Naive Vector đạt 0,9659 và Hybrid RAG đạt 0,9660; riêng LightRAG đạt 0,8829. Tức là hệ thống hầu như luôn đưa được Điều luật đúng vào trong ngữ cảnh.  
> Nhưng khi đánh giá xem câu trả lời cuối cùng có chỉ ra đúng Khoản nào, đúng Điểm nào làm căn cứ hay không, Citation Accuracy của Naive Vector chỉ đạt **32,59%**, Hybrid RAG đạt **29,02%**, và LightRAG — dù Recall tương đương — chỉ ghi nhận **13,71%**, mức thấp nhất trong ba hệ thống.  
> 
> Khoảng cách gần 83 điểm phần trăm giữa truy hồi và trích dẫn ở LightRAG cho thấy đây là vấn đề mang tính cấu trúc, không phải vấn đề của riêng mô hình nào. Khi kiểm toán dữ liệu, nhóm nhận thấy nguyên nhân nằm ở chiến lược cắt đoạn thô 1.200 token: việc cắt ngang văn bản luật phân cấp đa tầng làm đứt gãy quan hệ cha-con, khiến mô hình mất thông tin chủ thể ở cấp Điều và suy đoán vị trí pháp lý không chính xác.  
> 
> Cần nói rõ một điểm về phương pháp: con số Citation Accuracy ở đây đo trên câu trả lời cuối cùng. Sang Giai đoạn 2, để kiểm soát tốt hơn tác động của phân đoạn, nhóm chuyển sang đo trên ngữ cảnh truy hồi với 3.072 lượt chấm độc lập. Hai phép đo phục vụ hai mục tiêu khác nhau trong lộ trình — chúng em không so sánh trực tiếp, mà xem chúng như hai lớp chẩn đoán bổ sung.  
> Kết quả này trả lời **RQ1**: các kiến trúc RAG cơ sở chưa đáp ứng được yêu cầu trích dẫn chính xác nếu giữ nguyên phương thức cắt đoạn thô."*

**[Slide 8 — Giai đoạn 2: Parser v2 & Article MaxP · 06:40 – 08:05]**
> *"Để khắc phục hiện tượng đứt gãy phả hệ, bước sang Giai đoạn 2, nhóm đề xuất bộ giải pháp cấu trúc gồm hai thành phần cốt lõi:  
> Thứ nhất là bộ phân tích cấu trúc **Structure-Aware Parser v2**. Thay vì cắt đoạn theo số lượng token thô, Parser v2 bóc tách đệ quy văn bản luật theo đúng logic lập pháp, chuyển đổi 2.087 Điều luật thành **12.754 phân đoạn vi mô** cấp Khoản và Điểm. Điểm cải tiến mang tính bản lề là mỗi phân đoạn vi mô đều được gắn kèm một **tiền tố phân cấp bất biến**, ví dụ: `[Luật Đất đai 2024 > Chương III > Điều 45 > Khoản 1 > Điểm a]`. Nhờ đó, dù phân đoạn bị trích xuất độc lập, mô hình ngôn ngữ vẫn nắm bắt trọn vẹn chủ thể cha và ngữ cảnh phân cấp.  
> 
> Tuy nhiên, việc chia nhỏ thành hơn 12 nghìn đoạn vi mô lập tức gây ra hiện tượng 'bội thực cục bộ': Top-5 đoạn trả về có thể cùng thuộc về một Điều luật duy nhất. Do đó, nhóm xây dựng thuật toán gom điểm cực đại **Article-level MaxP**.  
> Nguyên lý toán học là: Điểm số của một Điều luật bằng giá trị lớn nhất trong số điểm của các phân đoạn vi mô thuộc Điều luật đó. Chỉ cần một Điểm luật khớp ngữ nghĩa với câu hỏi, toàn bộ Điều luật đại diện sẽ nhận điểm cực đại và được kéo lên đầu danh sách, sau đó hệ thống trích xuất đúng phân đoạn vi mô chứa bằng chứng để đưa vào prompt."*

**[Slide 9 — Giai đoạn 2: Ma trận C1–C6 & Đột phá C5 · 08:05 – 10:00]**
> *"Trên cùng 512 câu hỏi của Benchmark A, nhóm đối soát sáu cấu hình từ C1 đến C6 với 3.072 lượt thẩm định độc lập bằng LLM-as-a-Judge. Kết quả tại Bảng 3.6 xác thực giả thuyết H2 với ba kết quả đáng chú ý:  
> 
> Thứ nhất, cấu hình **C5 — Parser Dense** — nâng Citation Accuracy trên ngữ cảnh từ 0,4000 ở C2 lên **0,9902**, tức tăng 59,02 điểm phần trăm. Tỷ lệ câu hỏi đạt điểm tuyệt đối 1,0 tăng từ 25,4% lên **98,4%**, tương đương 504 trên tổng số 512 câu.  
> Thứ hai, về mặt tối ưu tài nguyên: dung lượng ngữ cảnh trung bình đưa vào LLM giảm từ gần 2.900 token xuống chỉ còn **khoảng 580 token**, tương đương **tiết kiệm 79,9% chi phí token**. Đây là hiệu quả kép: vừa chính xác hơn, vừa tiết kiệm tài nguyên tính toán hơn.  
> Thứ ba, nhóm quét 11 giá trị trọng số dung hợp Weighted RRF và xác định điểm cân bằng tại **$\alpha = 0,8$**, đưa Recall lên **0,9297** và MRR lên **0,8220**, khắc phục hiện tượng suy giảm khi dung hợp cào bằng ở C6.  
> 
> Cần lưu ý rằng đây là điểm đo trên ngữ cảnh truy hồi — là điều kiện cần để câu trả lời cuối cùng trích dẫn đúng, nhưng chưa phải điều kiện đủ. Đánh giá ở tầng câu trả lời hoàn chỉnh được thực hiện riêng tại Giai đoạn 3. Trong phạm vi ngữ cảnh, kết quả này xác nhận **RQ2**: phân đoạn cấu trúc vi mô kết hợp MaxP giải quyết được bài toán trích dẫn chính xác và tối ưu hóa chi phí.  
> 
> Sau đây, em xin mời bạn **Nguyễn Bình Minh** trình bày kiến trúc đề xuất và kết quả thực nghiệm ở Giai đoạn 3."*  
*(Lâm chuyển micro cho Minh).*

---

### [10:00 – 15:00] · CHẶNG 4: NGUYỄN BÌNH MINH (ĐỒ THỊ UKG, ĐA BƯỚC & KẾT LUẬN)

**[Slide 10 — Giai đoạn 3: Kiến trúc Hybrid UKG & Module 5 · 10:00 – 11:15]**
> *"Em xin cảm ơn bạn Lâm. Kính thưa Quý Thầy Cô,  
> Để xử lý các truy vấn pháp lý đa bước, bước sang Giai đoạn 3, nhóm đề xuất kiến trúc **Hybrid Parser/UKG** với một triết lý thiết kế cốt lõi: tách biệt hai tầng thông tin có bản chất khác nhau.  
> 
> Tầng thứ nhất là **Đồ thị Cấu trúc vật lý (Physical Graph)** — sử dụng bộ phân tích tất định để khóa cứng 100% phả hệ Chương–Mục–Điều–Khoản–Điểm. Đây là trục xương sống không thể sai lệch, được xây dựng độc lập với bất kỳ mô hình ngôn ngữ nào.  
> Tầng thứ hai là **Đồ thị Ngữ nghĩa (Semantic Graph)** — trích xuất các thực thể và quan hệ pháp lý động như quyền, nghĩa vụ, điều kiện, ngoại lệ — và gắn chúng lên trục xương sống đó. Cách tách biệt này giải quyết một mâu thuẫn cố hữu của các hệ GraphRAG hiện nay: nếu để LLM tự do trích xuất, nó sẽ băm nát cấu trúc phân cấp; nhưng nếu chỉ dùng cây cú pháp cứng, hệ thống lại mù tịt trước các quy phạm ngoại lệ.  
> 
> Trọng tâm kỹ thuật nằm ở bộ định tuyến **Module 5 — Semantic Router**. Để lọc văn bản thuần thủ tục mà không làm rơi rụng quy phạm ngầm định, nhóm ứng dụng mô hình **Qwen2.5-0.5B** kết hợp toán tử **Max-Fusion** giữa tín hiệu Regex và tín hiệu nhúng ngữ nghĩa. Khảo sát độc lập tại Phụ lục A cho thấy các mô hình Bi-encoder truyền thống bị 'mean-pooling trap' trên đoạn ngắn pháp lý, trong khi causal attention của Qwen2.5-0.5B bảo toàn được trật tự logic chủ thể $\rightarrow$ điều kiện $\rightarrow$ chế tài. Tại ngưỡng cân bằng $\theta = 0,85$, hệ thống đạt Recall 96,85%, F1 0,8146, loại bỏ an toàn 9,33% phân đoạn thủ tục trước khi chuyển sang Module 6."*

**[Slide 11 — Giai đoạn 3: Thực nghiệm Benchmark B · 11:15 – 13:00]**
> *"Kết quả thực nghiệm trên Benchmark B gồm 50 câu hỏi phân tầng tại Chương III Luật Đất đai 2024, được trình bày tại Bảng 3.9, 3.14 và 3.15, đã làm sáng tỏ **RQ3 và RQ4**:  
> 
> Về **RQ3** — năng lực định vị và xử lý quy phạm phức tạp:  
> Ở tầng truy hồi, Hybrid Parser/UKG đạt Recall@5 **0,9184** so với 0,7358 của LightRAG, tức vượt 18,26 điểm phần trăm. Chỉ số MRR@5 đạt **0,8848** so với 0,5539, vượt 33,09 điểm phần trăm. Điều này cho thấy UKG không chỉ tìm được nhiều căn cứ hơn mà còn xếp hạng chúng ở vị trí ưu tiên cao hơn.  
> Ở tầng nội dung câu trả lời, UKG đạt Legal Correctness **0,8777**, Subject-Scope Accuracy **0,8889** và đặc biệt **Exception Coverage đạt 0,6786 — vượt LightRAG 28,57 điểm phần trăm** (0,3929). Ưu thế ở Exception Coverage có được nhờ đồ thị ngữ nghĩa bóc tách chính xác các mệnh đề ngoại lệ 'trừ trường hợp...', vốn thường bị các GraphRAG truyền thống bỏ qua khi cắt khối văn bản thô.  
> 
> Về Condition Coverage, LightRAG ghi nhận 0,8421 và UKG đạt 0,7066. Sự khác biệt này phản ánh hai triết lý tổ chức ngữ cảnh: LightRAG dùng chunk 1.200 token lớn bao phủ rộng nên vô tình thu thập nhiều điều kiện xung quanh; UKG tập trung vào đơn vị quy phạm lõi nên cần thêm cơ chế lan truyền điều kiện từ node con sang node cha và node lân cận. Đây là trade-off đã được phân tích trong Chương 3, và là ưu tiên số một trong hướng phát triển tiếp theo của nhóm.  
> 
> Về **RQ4** — năng lực tái dựng chuỗi dẫn chiếu: hệ thống định vị tốt các node đích với Reference-target Recall đạt **58,67%**. Việc tái dựng toàn bộ chuỗi theo thứ tự cần thêm cơ chế constrained graph traversal — một bài toán có độ phức tạp tổ hợp cao, nằm ngoài phạm vi thực nghiệm hiện tại. Chúng em xem đây là một đóng góp mang tính chẩn đoán: xác định rõ ranh giới của kiến trúc hiện tại và đề xuất hướng giải quyết cụ thể cho nghiên cứu tiếp theo.  
> Nhìn tổng thể, kết quả Benchmark B cho thấy UKG có ưu thế rõ rệt ở tầng định vị cấu trúc và xử lý ngoại lệ, trong khi vẫn còn dư địa cải thiện ở tầng tổng hợp điều kiện và tái dựng đường dẫn."*

**[Slide 12 — Tổng kết: Đóng gói 4 Câu hỏi nghiên cứu · 13:00 – 13:55]**
> *"Tổng hợp lại từ ba giai đoạn thực nghiệm, bốn câu hỏi nghiên cứu ban đầu đã được giải quyết như sau:  
> Với **RQ1**, thực nghiệm xác lập khoảng cách giữa truy hồi và trích dẫn: các RAG cơ sở đạt Recall trên 95% nhưng Citation Accuracy chỉ khoảng 30% — riêng LightRAG ghi nhận 13,71%. Nguyên nhân là cắt đoạn thô làm đứt gãy phả hệ pháp lý.  
> Với **RQ2**, giải pháp Parser v2 và MaxP nâng Citation Accuracy trên ngữ cảnh lên **0,9902**, đạt **98,4%** câu điểm tuyệt đối, đồng thời tiết kiệm **79,9% token**. Điểm cân bằng Weighted RRF được xác định tại $\alpha = 0,8$.  
> Với **RQ3**, Hybrid UKG vượt LightRAG ở tầng truy hồi cấp Điều (Recall +18,26 đpt, MRR +33,09 đpt) và ở khả năng bao phủ ngoại lệ (+28,57 đpt) — là hai điểm yếu cố hữu của GraphRAG truyền thống.  
> Với **RQ4**, thực nghiệm xác định một ranh giới quan trọng: hệ thống định vị tốt các node đích (58,67%) nhưng việc tái dựng chuỗi hoàn chỉnh cần thêm cơ chế constrained graph traversal. Đây là hướng nghiên cứu trọng tâm tiếp theo của nhóm."*

**[Slide 13 — Ba đóng góp khoa học chính · 13:55 – 14:35]**
> *"Từ những kết quả trên, nhóm xác định ba đóng góp khoa học cốt lõi:  
> Một là **khung kiểm chuẩn Benchmark** với hai bộ dữ liệu và hạ tầng Adapter Pattern loại bỏ thiên lệch thực nghiệm — có thể tái sử dụng cho các nghiên cứu RAG tiếng Việt tiếp theo.  
> Hai là **giải pháp phân đoạn cấu trúc** phối hợp Parser v2 và Article MaxP, giải quyết tận gốc vấn đề sụt giảm trích dẫn và tối ưu hóa tài nguyên tính toán.  
> Ba là **kiến trúc đồ thị hai tầng UKG**, chứng minh tính hiệu quả của việc tách biệt cấu trúc vật lý bất biến và ngữ nghĩa có kiểm soát trong việc xử lý quy phạm ngoại lệ và chủ thể pháp lý phức tạp.  
> 
> Nếu được phép tóm gọn trong một câu: **Trong pháp luật, cấu trúc không phải là chi tiết triển khai — nó là điều kiện tiên quyết để AI có thể trích dẫn đúng.**"*

**[Slide 14 — Hướng phát triển & Kết thúc · 14:35 – 15:00]**
> *"Trong thời gian tới, nhóm hướng đến ba mục tiêu tiếp theo: mở rộng bộ bóc tách cấu trúc sang các văn bản dưới luật như Nghị định, Thông tư; tự động hóa cập nhật hiệu lực khi văn bản sửa đổi; và hoàn thiện cơ chế constrained graph traversal để khép kín chuỗi dẫn chiếu chéo.  
> Về mặt đánh giá, nhóm dự kiến bổ sung ablation từng thành phần trong gói Parser, mở rộng ngữ liệu, và phối hợp với chuyên gia pháp lý để hiệu chuẩn kết quả LLM Judge độc lập.  
> 
> Thay mặt nhóm nghiên cứu, chúng em xin trân trọng cảm ơn Quý Thầy Cô đã chú ý lắng nghe. Nhóm sẵn sàng tiếp nhận ý kiến đóng góp và bước vào phần Hỏi – Đáp."*  
*(Cả ba thành viên Lâm, Dương, Minh cùng đứng nghiêm trang, cúi đầu chào Hội đồng).*

---
---

# PHẦN 3: BẢN PHAO THỰC CHIẾN - Ý NEO TỰ SỰ & CỬ CHỈ SÂN KHẤU (ANCHOR CHEAT SHEET)

> **Mục đích:** Tài liệu cầm tay phục vụ tập dượt thực chiến. Mỗi slide chỉ cần nhớ 2 – 3 từ khóa neo, điểm chỉ tia laser và câu chốt trigger cue để chuyển giao micro mượt mà.

| Slide | Người nói | Thời lượng | Từ khóa neo chuyên sâu | Hành động / Điểm chỉ laser trên Slide | Câu chốt chuyển mic (Trigger Cue) |
| :---: | :---: | :---: | :--- | :--- | :--- |
| **1** | **Lâm** | 20s | • Chào Hội đồng, giới thiệu 3 thành viên, GVHD<br>• Đề tài: RAG trên dữ liệu cấu trúc đặc thù | Đứng giữa bục, mắt bao quát Hội đồng, phong thái tự tin | *(Nói liền mạch sang Slide 2)* |
| **2** | **Lâm** | 70s | • Nhu cầu tra cứu pháp luật kiểm chứng tuyệt đối<br>• RAG ảo giác 17% – 33% (Magesh 2025)<br>• Sai lệch điều khoản làm đổi hệ quả pháp lý | Chỉ laser vào **Hộp cảnh báo 17% – 33%** | *"Sau đây xin mời bạn Ngô Thế Dương trình bày đặc thù dữ liệu và cơ sở nghiên cứu."* |
| **3** | **Dương** | 55s | • 3 đặc thù: Phân cấp đa tầng, Dẫn chiếu, Lệch pha từ vựng<br>• 3 Gap: Khung benchmark, Phân đoạn vi mô, Thước đo trích dẫn | Quét laser lần lượt qua **3 khối đặc thù** và **3 khối Gap** | *(Nói liền mạch sang Slide 4)* |
| **4** | **Dương** | 55s | • 3 trường phái RAG cơ sở: Naive Vector (Cosine), Hybrid (BM25+Dense+RRF), LightRAG (Graph) | Chỉ laser vào **3 cột kiến trúc RAG** | *(Nói liền mạch sang Slide 5)* |
| **5** | **Dương** | 45s | • Bung 4 câu hỏi nghiên cứu định hướng 3 giai đoạn: RQ1 (GĐ1), RQ2 (GĐ2), RQ3 & RQ4 (GĐ3) | Chỉ laser vào **bảng ma trận 4 RQ** | *(Nói liền mạch sang Slide 6)* |
| **6** | **Dương** | 70s | • Benchmark Harness + Adapter Pattern, đóng băng biến số ngoại lai<br>• Benchmark A (512 câu, hạ Jaccard 0,31; Tier 1 205 câu / 500 điều) & Benchmark B (50 câu) | Chỉ laser vào **hộp đóng băng kiểm soát** và **hộp 2 bộ Benchmark** | *"Kết quả GĐ1 và phương án cải tiến ra sao, xin mời bạn Lưu Thanh Lâm tiếp tục trình bày."* |
| **7** | **Lâm** | 85s | • **[Slide đinh] Khoảng cách truy hồi & trích dẫn (RQ1)**<br>• Recall $>95\%$ nhưng Citation chỉ $\sim 30\%$<br>• LightRAG ghi nhận **13,71%** do cắt thô 1.200 token làm đứt gãy phả hệ cha-con | Chỉ laser dứt khoát vào **13,71%** và **32,59%** | *(Nói liền mạch sang Slide 8)* |
| **8** | **Lâm** | 85s | • Parser v2: 12.754 đoạn vi mô kèm tiền tố bất biến [Luật > Chương > Điều > Khoản > Điểm]<br>• Bội thực cục bộ $\rightarrow$ Article MaxP gom điểm cực đại | Chỉ laser vào **tiền tố bất biến ví dụ** và **công thức Article MaxP** | *(Nói liền mạch sang Slide 9)* |
| **9** | **Lâm** | 115s | • **[Slide đinh] Kết quả C5 (RQ2)**<br>• Citation Acc trên ngữ cảnh lên **0,9902** (98,4% đạt 1.0, 504/512 câu)<br>• Tiết kiệm **79,9% token** (~580t)<br>• Weighted RRF tối ưu tại **$\alpha = 0,8$** | Chỉ laser vào 3 con số Headline lớn: **0,9902**, **-79,9%**, **$\alpha=0,8$** | *"Trước câu hỏi đa bước và quan hệ dẫn chiếu, UKG giải quyết ra sao? Xin mời bạn Minh."* |
| **10** | **Minh** | 75s | • Kiến trúc UKG: Tầng vật lý (khóa cứng phả hệ) + Tầng ngữ nghĩa (trích xuất động)<br>• Module 5 Causal Router Qwen2.5-0.5B + Max-Fusion logic OR tại $\theta=0,85$ (Recall 96,85%) | Chỉ laser vào sơ đồ 2 tầng và khối **Module 5** | *(Nói liền mạch sang Slide 11)* |
| **11** | **Minh** | 105s | • **[Slide đinh] Benchmark B (RQ3 & RQ4)**<br>• RQ3: Recall cấp Điều **0,9184** (+18,26 đpt), Exception Coverage **0,6786** (+28,57 đpt)<br>• Trade-off Condition Coverage; RQ4 ranh giới chuỗi dẫn chiếu | Chỉ laser vào số **0,9184**, số **+28,57 đpt**, và phần trade-off | *(Nói liền mạch sang Slide 12)* |
| **12** | **Minh** | 55s | • **[Slide đinh] Bo tròn 4 RQ ở cuối bài**<br>• RQ1: Khoảng cách trích dẫn<br>• RQ2: Parser v2 + MaxP hiệu quả<br>• RQ3: UKG vượt trội ngoại lệ<br>• RQ4: Ranh giới chuỗi dẫn chiếu | Quét laser lần lượt qua **4 hàng tổng kết RQ** | *(Nói liền mạch sang Slide 13)* |
| **13** | **Minh** | 40s | • 3 Đóng góp khoa học cốt lõi: Khung Benchmark chuẩn; Giải pháp phân đoạn cấu trúc; Kiến trúc đồ thị hợp nhất UKG<br>• **Câu chốt "So What"** | Chỉ laser lần lượt vào **3 cột đóng góp** và **Hộp chốt cuối** | *(Nói liền mạch sang Slide 14)* |
| **14** | **Minh** | 25s | • 3 Hướng phát triển: Nghị định, Thông tư; Cập nhật hiệu lực; Constrained Traversal<br>• Lời cảm ơn và mời Q&A | Nhìn thẳng Hội đồng, mỉm cười trang trọng | Cả 3 thành viên cùng đứng nghiêm, cúi đầu chào |

---
---

# PHẦN 4: HỒ SƠ PHÒNG THỦ VẤN ĐÁP (Q&A DEFENSE PLAYBOOK)
## 15 CÂU HỎI PHẢN BIỆN TRỌNG YẾU & MẪU CÂU TRẢ LỜI ĐANH THÉP (20 – 30 GIÂY)

> **Quy tắc vàng khi trả lời phản biện:**
> 1. Luôn cảm ơn Thầy/Cô trước khi trả lời: *"Dạ em xin cảm ơn Thầy/Cô đã đặt một câu hỏi rất sâu sắc về..."*.
> 2. Đi thẳng vào bản chất kỹ thuật trong câu đầu tiên, không vòng vo.
> 3. Trả lời dứt khoát trong 20 – 30 giây, kết thúc bằng một câu khẳng định có chừng mực.

---

### NHÓM 1: CÂU HỎI VỀ PHƯƠNG PHÁP LUẬN & ĐO LƯỜNG (LÂM & DƯƠNG PHỤ TRÁCH)

**Câu 1 (Lâm): "Citation Accuracy ở Giai đoạn 1 và Giai đoạn 2 có định nghĩa giống nhau không? Tại sao lại có sự chênh lệch lớn từ 32% lên 99%?"**
> *"Dạ đây là hai phép đo phục vụ hai mục tiêu khác nhau trong lộ trình nghiên cứu của nhóm.  
> Ở Giai đoạn 1, chỉ số đo trên câu trả lời cuối cùng nhằm chẩn đoán xem RAG cơ sở có trích dẫn đúng căn cứ hay không.  
> Sang Giai đoạn 2, nhóm chuyển sang đo trên ngữ cảnh truy hồi bằng LLM-as-a-Judge nhằm kiểm soát độc lập xem ngữ cảnh có chứa đúng locator hay không.  
> Hai phép đo này là hai lớp chẩn đoán bổ sung, nhóm không so sánh trực tiếp 32% với 99%. Phép so sánh công bằng là giữa C2 (0,4000) và C5 (0,9902) trong cùng Giai đoạn 2 trên cùng một thước đo."*

**Câu 2 (Lâm): "Trong Giai đoạn 2, các em thay đổi nhiều thành phần cùng lúc (micro-chunk, prefix, MaxP). Thành phần nào đóng góp chính?"**
> *"Dạ đây là một điểm nhóm đã ghi nhận tại Mục 3.3.9 của báo cáo. Kết quả vượt trội của C5 là tác động tổng hợp của cả gói giải pháp cấu trúc: phân đoạn vi mô giúp thu hẹp phạm vi, tiền tố bất biến bảo toàn phả hệ cha-con, và MaxP giải quyết bão hòa Top-K.  
> Thiết kế hiện tại chưa cô lập tác động riêng của từng thành phần đơn lẻ, và nhóm xác định việc chạy thêm các cấu hình ablation độc lập là hướng nghiên cứu ưu tiên tiếp theo."*

**Câu 3 (Dương): "Các em dùng GPT-4o-mini vừa sinh câu trả lời vừa làm giám khảo. Kết quả có bị thiên lệch tự thân không?"**
> *"Dạ đây là một rủi ro phương pháp luận mà nhóm đã phân tích tại Mục 3.8.3. Nhóm đã giảm thiểu tối đa thiên lệch bằng cách: thiết kế prompt đánh giá độc lập, kiểm tra nghiêm ngặt JSON schema, và ghi nhận đầy đủ log giao dịch cho từng lượt chấm.  
> Hướng hoàn thiện tiếp theo của nhóm là sử dụng một mô hình ngôn ngữ độc lập từ họ khác để làm giám khảo, đồng thời mời các chuyên gia pháp lý chấm thẩm định trên một tập mẫu ngẫu nhiên để hiệu chuẩn."*

**Câu 4 (Dương): "Việc viết lại 512 câu hỏi ở Benchmark A có làm biến đổi ngữ nghĩa pháp lý gốc không?"**
> *"Dạ quy trình viết lại được nhóm áp dụng có chọn lọc cho các câu hỏi có độ trùng lặp từ vựng Jaccard vượt ngưỡng 0,5, nhằm mục đích duy nhất là đưa câu hỏi về ngôn ngữ đời thường tự nhiên, tránh để phương pháp từ khóa BM25 hưởng lợi do trùng lặp máy móc.  
> Nhóm đã kiểm tra đối soát thủ công trên một phần câu hỏi để bảo đảm ý định pháp lý không bị thay đổi. Việc xây dựng một quy trình kiểm toán ngữ nghĩa tự động cho toàn bộ tập dữ liệu là hướng hoàn thiện tiếp theo."*

**Câu 5 (Dương): "Tại sao ở Giai đoạn 1 nhóm chỉ đánh giá trên 205 câu hỏi Tier 1 mà không dùng toàn bộ 512 câu?"**
> *"Dạ nguyên nhân là do chi phí xây dựng chỉ mục đồ thị của LightRAG rất lớn, nên trong phạm vi thực nghiệm, LightRAG chỉ được lập chỉ mục trên phân vùng 500 điều luật trọng điểm thuộc Bộ luật Hình sự và Lao động.  
> Để bảo đảm nguyên tắc đối chuẩn công bằng (Equal Scope Evaluation), nhóm tách riêng tập Tier 1 gồm 205 câu có toàn bộ căn cứ nằm trong 500 điều này, tránh trường hợp LightRAG bị trượt oan do văn bản chưa được nạp vào hệ thống."*

---

### NHÓM 2: CÂU HỎI VỀ KẾT QUẢ THỰC NGHIỆM & ĐỐI SÁNH (LÂM & MINH PHỤ TRÁCH)

**Câu 6 (Lâm): "Tại sao LightRAG lại đạt Citation Accuracy thấp như vậy ở Giai đoạn 1 (chỉ 13,71%)?"**
> *"Dạ kết quả 13,71% phản ánh hai yếu tố:  
> Thứ nhất, về mặt bản chất mô hình, LightRAG cắt văn bản thành các khối thô 1.200 token làm vỡ nát cấu trúc phân cấp Điều-Khoản-Điểm, khiến mô hình bị mất thông tin chủ thể cha.  
> Thứ hai, LightRAG trả về đoạn văn và thông tin đồ thị chứ không trả về locator chuẩn, adapter của nhóm phải thực hiện ánh xạ để đối soát căn cứ. Kết quả này cho thấy các mô hình GraphRAG phổ thông gặp khó khăn lớn khi áp dụng trực tiếp lên văn bản có phân cấp nghiêm ngặt như luật pháp."*

**Câu 7 (Minh): "Exact Locator Recall@5 của UKG chỉ đạt 0,5560, thấp hơn LightRAG (0,8509). Tại sao lại như vậy?"**
> *"Dạ con số này phản ánh sự khác biệt về độ hạt bằng chứng:  
> LightRAG trả về các khối chunk 1.200 token rất lớn, mỗi chunk vô tình bao hàm trung bình gần 15 locator khác nhau, nên xác suất bao phủ locator theo nghĩa danh nghĩa là rất cao.  
> Ngược lại, UKG trả về đúng phân đoạn vi mô mang duy nhất 1 locator định vị chuẩn xác, nên yêu cầu truy hồi khắt khe hơn nhưng khi trúng thì bằng chứng đưa vào prompt là tập trung và chính xác tuyệt đối. Ngoài ra, UKG còn 8 câu chưa đo được do parser và nhóm ghi nhận N/A chứ không gán bằng 0."*

**Câu 8 (Minh): "Condition Coverage của UKG đạt 0,7066, thấp hơn LightRAG (0,8421). Nhóm giải thích thế nào?"**
> *"Dạ đây là trade-off đã được nhóm phân tích thẳng thắn tại Mục 3.7.3.  
> LightRAG đạt độ phủ điều kiện rộng hơn nhờ các khối chunk lớn chứa sẵn toàn bộ đoạn văn xung quanh. Trong khi đó, UKG bóc tách vi mô tập trung vào đơn vị quy phạm lõi, nên cơ chế mở rộng bằng chứng hiện tại cần được hoàn thiện thêm để lan truyền thông tin điều kiện từ node cha và các node liên kết sang node con. Đây chính là ưu tiên số một trong hướng phát triển tiếp theo của nhóm."*

**Câu 9 (Minh): "Chỉ số Chain Exact Match bằng 0 trên 18 câu hỏi. Vậy đề tài có giải quyết được bài toán dẫn chiếu không?"**
> *"Dạ đối với bài toán dẫn chiếu, hệ thống đã giải quyết tốt bước định vị các quy phạm đích liên quan với Reference-target Recall đạt 58,67%.  
> Tuy nhiên, chỉ số xâu chuỗi hoàn hảo Chain Exact Match ghi nhận 0,0000 vì hệ thống hiện tại mới xuất ra các cạnh đơn lẻ mà chưa tích hợp thuật toán duyệt đồ thị có định hướng (Constrained Graph Traversal).  
> Nhóm xem đây là một đóng góp mang tính chẩn đoán thực nghiệm: xác định rõ ranh giới của kiến trúc hiện tại và thiết lập một mốc kiểm chuẩn ban đầu để các nghiên cứu tiếp theo phát triển."*

**Câu 10 (Lâm): "Việc cắt nhỏ văn bản thành 12.754 phân đoạn vi mô và giảm 79,9% token có làm mất mát thông tin ngữ cảnh không?"**
> *"Dạ rủi ro mất mát ngữ cảnh đã được nhóm triệt tiêu bằng cơ chế tiền tố phân cấp bất biến: mỗi phân đoạn vi mô đều được gắn định danh đầy đủ từ Luật, Chương, Điều đến Khoản, Điểm. Nhờ đó, LLM vẫn nắm trọn chủ thể quy phạm mà không cần phải nạp toàn bộ văn bản thô dài hàng nghìn token.  
> Việc giảm 80% token giúp loại bỏ các đoạn văn nhiễu không liên quan, qua đó vừa nâng cao độ chính xác trích dẫn, vừa tối ưu chi phí vận hành."*

---

### NHÓM 3: CÂU HỎI VỀ KIẾN TRÚC & MÔ HÌNH HÓA (MINH & DƯƠNG PHỤ TRÁCH)

**Câu 11 (Minh): "Kiến trúc UKG gồm 10 module, vậy đóng góp khoa học chính nằm ở đâu?"**
> *"Dạ 10 module là cách tổ chức kiến trúc phần mềm theo nguyên lý phân tách trách nhiệm. Đóng góp khoa học cốt lõi của đề tài nằm ở ba điểm:  
> Một là triết lý tách biệt hai tầng: Đồ thị cấu trúc vật lý bất biến và Đồ thị ngữ nghĩa động;  
> Hai là cơ chế định tuyến ngữ nghĩa Module 5 với toán tử Max-Fusion;  
> Và ba là phương thức dung hợp bằng chứng AUTO_FUSION giúp kết hợp đồng thời cả phả hệ văn bản lẫn quan hệ pháp lý."*

**Câu 12 (Minh): "Tại sao Module 5 lại dùng mô hình nhân quả Qwen2.5-0.5B thay vì dùng các mô hình nhúng embedding chuyên dụng?"**
> *"Dạ thực nghiệm đối chuẩn độc lập trên Golden Set v2 tại Phụ lục A cho thấy: Các mô hình Bi-encoder truyền thống áp dụng phép gộp trung bình (Mean-Pooling) làm phẳng tín hiệu ngữ pháp trên các phân đoạn ngắn pháp luật, dẫn đến hiện tượng trôi ngưỡng nghiêm trọng.  
> Ngược lại, cơ chế Causal Attention của Qwen2.5-0.5B bảo toàn được trật tự logic từ chủ thể, hành vi đến điều kiện và chế tài. Kết hợp cùng toán tử Max-Fusion tại ngưỡng 0,85, mô hình đạt Recall 96,85% và F1 0,8146, loại bỏ an toàn các văn bản thủ tục."*

**Câu 13 (Dương): "Tại sao nhóm lại chọn 7 văn bản luật này trong Benchmark A? Tính đại diện ở đâu?"**
> *"Dạ 7 đạo luật này bao phủ các lĩnh vực có tần suất phát sinh nhu cầu tra cứu thường xuyên nhất trong đời sống dân sự và kinh tế: dân sự, hình sự, lao động, đất đai, doanh nghiệp, hôn nhân và xử lý vi phạm hành chính.  
> Chúng cũng đại diện cho các thể thức văn bản quy phạm khác nhau: từ Bộ luật có tính pháp điển hóa cao đến các Luật chuyên ngành. Đây là phạm vi thiết kế có chủ đích nhằm kiểm chứng tính bền vững của bộ phân tích cấu trúc, và mở rộng sang văn bản dưới luật là bước tiếp theo của đề tài."*

**Câu 14 (Minh): "Toán tử Max-Fusion ở Module 5 có ưu thế gì so với việc lấy điểm trung bình cộng?"**
> *"Dạ thực nghiệm của nhóm chỉ ra Cạm bẫy của hàm trung bình (Average Penalty Trap): Nếu dùng trung bình cộng, khi một điều luật có quy phạm ngầm định không chứa từ khóa cứng, điểm Regex bằng 0 sẽ kéo tụt điểm tổng hợp xuống và làm hệ thống loại nhầm quy phạm đó.  
> Toán tử Max-Fusion mang tính chất logic bảo hiểm (Logic OR): Nếu có từ khóa cứng thì chắc chắn được giữ lại; đồng thời nếu không có từ khóa nhưng vector ngữ nghĩa nhận diện tốt, quy phạm vẫn được bảo toàn."*

**Câu 15 (Lâm): "Nếu hệ thống được đưa vào thực tế phục vụ người dân, nhóm tự tin nhất ở điểm nào và lo ngại nhất ở điểm nào?"**
> *"Dạ điểm nhóm tự tin nhất là tính chính xác và khả năng truy nguyên của căn cứ pháp lý: Nhờ phân đoạn vi mô và tiền tố bất biến, hệ thống hầu như không trích dẫn sai số Điều, Khoản, Điểm trên các câu hỏi đơn văn bản.  
> Điểm nhóm thận trọng nhất là các tình huống pháp lý phức tạp đòi hỏi liên kết chuỗi dẫn chiếu nhiều bước qua nhiều văn bản khác nhau. Đây chính là lý do nhóm xác định bài toán duyệt đồ thị có ràng buộc là trọng tâm phát triển tiếp theo trước khi triển khai rộng rãi."*
