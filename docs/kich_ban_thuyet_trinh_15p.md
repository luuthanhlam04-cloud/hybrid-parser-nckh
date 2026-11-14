# BỘ TÀI LIỆU KỊCH BẢN VÀ THIẾT KẾ THUYẾT TRÌNH BẢO VỆ NCKH (15 PHÚT)
## CHUẨN KHOA HỌC QUỐC TẾ (SCIENTIFIC STORYTELLING - Q1 FRAMEWORK)

**Đề tài:** Đánh giá và tối ưu hóa các kiến trúc RAG trên nền tảng dữ liệu cấu trúc đặc thù  
**Mã số đề tài:** 14-SV-2026-RIPT | **Lĩnh vực:** Khoa học Máy tính & Công nghệ Thông tin  
**Nhóm sinh viên thực hiện:** Lưu Thanh Lâm (Nhóm trưởng) • Ngô Thế Dương • Nguyễn Bình Minh  
**Giảng viên hướng dẫn:** TS. Nguyễn Mạnh Dũng  
**Đơn vị:** Viện Khoa học Kỹ thuật Bưu điện - Học viện Công nghệ Bưu chính Viễn thông (PTIT)  

---

# MỤC LỤC BỘ TÀI LIỆU
1. **PHẦN 1: BẢN THIẾT KẾ HIỂN THỊ VÀ BỐ CỤC 14 SLIDE (VISUAL BLUEPRINT)**  
   *(Chi tiết bố cục thị giác, thông điệp đơn nhất mỗi slide, các chỉ dẫn thị giác Signposting dẫn chiếu trực tiếp vào báo cáo toàn văn bancuoi.docx).*
2. **PHẦN 2: KỊCH BẢN LỜI THOẠI STORYTELLING CHUYÊN SÂU 15 PHÚT (FULL SPOKEN SCRIPT)**  
   *(Toàn văn lời nói từng câu từng chữ cho Lâm - Dương - Lâm - Minh từ 00:00 đến 15:00. Triệt tiêu hoàn toàn lối liệt kê kỹ thuật engineering khô khan; vận dụng triệt để khung tự sự khoa học ABT và nguyên lý BLUF; làm sáng tỏ bản chất cơ chế khoa học đằng sau từng số liệu thực nghiệm).*
3. **PHẦN 3: BẢN PHAO THỰC CHIẾN - Ý NEO TỰ SỰ & CỬ CHỈ TRÌNH BÀY (ANCHOR CHEAT SHEET)**  
   *(Bảng tra cứu cầm tay 14 slide: ý neo xung đột - giải pháp, tọa độ chỉ tia laser chính xác, câu chốt chuyển giao micro nhịp nhàng).*

---
---

# PHẦN 1: BẢN THIẾT KẾ HIỂN THỊ VÀ BỐ CỤC 14 SLIDE (VISUAL BLUEPRINT)

> **Triết lý thiết kế thị giác chuẩn Q1 (Signposting & Cognitive Ease):**
> * **Nguyên tắc "1 Slide = 1 Luận điểm khoa học (One Slide, One Insight)":** Không nhồi nhét nhiều thông điệp cạnh tranh nhau trên cùng một slide.
> * **Hệ màu chủ đạo:** Xanh thẫm học thuật (Navy Blue `#0A2540`) + Nền trắng tuyết `#FFFFFF` + Điểm nhấn Cảnh báo/Nghịch lý Cam đất `#E25C3D` + Điểm nhấn Đột phá Xanh lục bảo `#00875A`.
> * **Số liệu trọng tâm:** Font to ngoại cỡ (Size 28 – 36pt Bold), đặt trong hộp Callout viền đậm.
> * **Thẻ định vị dẫn chứng (Evidence Signpost):** Dưới chân mỗi slide chứa số liệu đều có nhãn định vị trang và bảng tương ứng trong báo cáo toàn văn (ví dụ: `[Dẫn chứng: Báo cáo toàn văn — Bảng 3.4 | Trang 92]`), giúp Thầy Cô trong Hội đồng lập tức giở đúng trang kiểm chứng mà không bị lạc giữa 150 trang báo cáo.

---

### SLIDE 1 · BÌA BÁO CÁO (LÂM | 00:00 – 00:20)
* **Bố cục hiển thị:** Bố cục trung tâm trang trọng, cân đối. Logo Học viện CNBCVT và Viện KHKT Bưu điện ở hai góc trên.
* **Nội dung hiển thị:**
  * Tiêu đề đề tài (Font đậm, cỡ lớn, căn giữa): **ĐÁNH GIÁ VÀ TỐI ƯU HÓA CÁC KIẾN TRÚC RAG TRÊN NỀN TẢNG DỮ LIỆU CẤU TRÚC ĐẶC THÙ**
  * Tên phân hệ ứng dụng: *Hệ thống hỏi đáp và định vị quy phạm pháp luật Việt Nam*
  * Mã số đề tài: `14-SV-2026-RIPT`
  * Nhóm sinh viên thực hiện: **Lưu Thanh Lâm** (Nhóm trưởng) • **Ngô Thế Dương** • **Nguyễn Bình Minh**
  * Giảng viên hướng dẫn: **TS. Nguyễn Mạnh Dũng**
  * Đơn vị: Học viện Công nghệ Bưu chính Viễn thông — Hà Nội, 2026

---

### SLIDE 2 · BỐI CẢNH & VẤN NẠN ẢO GIÁC PHÁP LÝ (LÂM | 00:20 – 01:30)
* **Tiêu đề:** Thách thức của RAG trước yêu cầu kiểm chứng tuyệt đối trong pháp luật
* **Luận điểm cốt lõi (Insight):** *Trong pháp luật, một câu trả lời trôi chảy nhưng sai lệch một căn cứ vi mô có thể đảo lộn hoàn toàn quyền và nghĩa vụ pháp lý.*
* **Bố cục hiển thị:** Chia 3 khối đối sánh (Card Layout):
  * *Khối 1 (Thực tiễn):* Nhu cầu người dân tra cứu pháp luật bùng nổ $\rightarrow$ Đòi hỏi câu trả lời bắt buộc phải có căn cứ kiểm chứng xác thực đến cấp quy phạm nhỏ nhất.
  * *Khối 2 (Giới hạn của RAG phổ thông):* RAG kết nối mô hình ngôn ngữ lớn với cơ sở dữ liệu ngoài, nhưng **chưa triệt tiêu được ảo giác**.
  * *Khối 3 (Hộp cảnh báo đỏ):* Nghiên cứu của Magesh (2024) chỉ ra AI thương mại gặp tỷ lệ ảo giác pháp lý từ **17% đến 33%**. Viện dẫn sai Điều-Khoản làm thay đổi hoàn toàn hệ quả pháp lý của hành vi.
* **Dẫn chứng:** `[Tham chiếu: Báo cáo toàn văn — Mục 1, Mở đầu]`.

---

### SLIDE 3 · ĐẶC THÙ CẤU TRÚC LUẬT & BA KHOẢNG TRỐNG NGHIÊN CỨU (DƯƠNG | 01:30 – 02:25)
* **Tiêu đề:** Ba đặc thù văn bản luật Việt Nam & Khoảng trống của các kiến trúc RAG
* **Luận điểm cốt lõi (Insight):** *Văn bản luật sống bằng phả hệ và mạng lưới dẫn chiếu, trong khi các kiến trúc RAG hiện hành lại được thiết kế cho văn bản phẳng phi cấu trúc.*
* **Bố cục hiển thị:** Đối chiếu song song 2 cột:
  * *Cột trái (3 Đặc thù kiến trúc văn bản luật):*
    1. **Cấu trúc phân cấp đa tầng nghiêm ngặt:** Luật $\rightarrow$ Chương $\rightarrow$ Mục $\rightarrow$ Điều $\rightarrow$ Khoản $\rightarrow$ Điểm. Mệnh đề ở cấp con phụ thuộc tuyệt đối vào chủ thể và điều kiện ở cấp cha.
    2. **Mạng lưới dẫn chiếu phức tạp:** Viện dẫn nội bộ và dẫn chiếu liên văn bản dày đặc.
    3. **Lệch pha ngôn ngữ:** Câu hỏi khẩu ngữ tự nhiên của người dân khác xa từ vựng lập pháp quy chuẩn.
  * *Cột phải (3 Khoảng trống nghiên cứu tương ứng):*
    1. **Gap 1:** Thiếu một khung đối chuẩn thực nghiệm có kiểm soát biến số trên dữ liệu luật Việt Nam.
    2. **Gap 2:** Thiếu đánh giá thực nghiệm về tác động của phân đoạn cấu trúc vi mô so với cắt khối token thô truyền thống.
    3. **Gap 3:** Các thước đo RAG tổng quát hiện nay không đo lường được tính chính xác của trích dẫn căn cứ và chuỗi dẫn chiếu.

---

### SLIDE 4 · CƠ SỞ LÝ THUYẾT: BA TRƯỜNG PHÁI RAG CƠ SỞ (DƯƠNG | 02:25 – 03:20)
* **Tiêu đề:** Cơ sở lý thuyết — Ba trường phái RAG đối chuẩn cơ sở
* **Luận điểm cốt lõi (Insight):** *Khảo sát ba đại diện tiêu biểu cho ba nguyên lý truy xuất thông tin hiện đại trên thế giới để thiết lập đường cơ sở (Baseline).*
* **Bố cục hiển thị:** 3 cột kiến trúc trực quan có sơ đồ luồng dữ liệu:
  * *Cột 1 — Naive Vector RAG (Không gian Dense):* Sử dụng mô hình nhúng Bi-encoder biểu diễn câu hỏi và tài liệu trong không gian vector đa chiều, truy hồi Top-K dựa trên độ tương đồng Cosine.
  * *Cột 2 — Hybrid RAG (Dung hợp từ vựng & ngữ nghĩa):* Kết hợp tìm kiếm từ khóa chính xác BM25 và truy hồi Dense vector, dung hợp thứ hạng bằng thuật toán Reciprocal Rank Fusion (RRF), sau đó dùng Cross-Encoder để tái xếp hạng.
  * *Cột 3 — LightRAG (Đại diện GraphRAG):* Khai thác biểu diễn đồ thị thực thể và quan hệ hai tầng, hỗ trợ truy hồi ngữ cảnh rộng Local và Global.
* **Dẫn chứng:** `[Tham chiếu: Báo cáo toàn văn — Mục 2.4 | Bảng 2.3]`.

---

### SLIDE 5 · HỆ THỐNG CÂU HỎI NGHIÊN CỨU (DƯƠNG | 03:20 – 04:05)
* **Tiêu đề:** Bốn câu hỏi nghiên cứu định hướng toàn bộ đề tài (RQ1 – RQ4)
* **Luận điểm cốt lõi (Insight):** *Lộ trình thực nghiệm ba giai đoạn nhằm từng bước giải mã và tối ưu hóa năng lực trích dẫn pháp lý.*
* **Bố cục hiển thị:** Bảng ma trận 4 câu hỏi nghiên cứu:
  * **RQ1 (Giai đoạn 1):** Ba kiến trúc RAG cơ sở thể hiện năng lực truy hồi và độ chính xác trích dẫn như thế nào trên văn bản luật Việt Nam khi áp dụng chiến lược cắt đoạn thô truyền thống?
  * **RQ2 (Giai đoạn 2):** Chiến lược phân đoạn cấu trúc vi mô (Parser v2) kết hợp tiền tố bất biến và thuật toán gom điểm Article MaxP có giải quyết được nghịch lý trích dẫn và tối ưu hóa dung lượng ngữ cảnh không?
  * **RQ3 (Giai đoạn 3):** Kiến trúc đồ thị tri thức hợp nhất (Hybrid UKG) cải thiện khả năng định vị điều kiện và xử lý mệnh đề ngoại lệ pháp luật so với GraphRAG truyền thống như thế nào?
  * **RQ4 (Giai đoạn 3):** Đồ thị tri thức có khả năng giải quyết bài toán truy vết chuỗi quan hệ dẫn chiếu chéo đa bước trong văn bản quy phạm pháp luật hay không?

---

### SLIDE 6 · THIẾT KẾ THỰC NGHIỆM & HẠ TẦNG BENCHMARK (DƯƠNG | 04:05 – 05:15)
* **Tiêu đề:** Thiết kế thực nghiệm: Khung Benchmark Harness, Hai bộ dữ liệu & Workflow kiểm chuẩn
* **Luận điểm cốt lõi (Insight):** *Thiết lập một sân chơi đối chuẩn công bằng tuyệt đối: Đóng băng biến số ngoại lai, chống thiên lệch từ khóa và chuẩn hóa luồng kiểm toán độc lập.*
* **Bố cục hiển thị:** 3 khối thông tin khoa học then chốt:
  * *Khối 1 — Hạ tầng Harness & Đóng băng biến số:* Mẫu thiết kế `BaseRAGAdapter` chuẩn hóa giao tiếp; cố định phần cứng GPU Tesla T4, mô hình nhúng BGE-M3 (1024 dim), LLM GPT-4o-mini ở nhiệt độ $T=0$.
  * *Khối 2 — Hai bộ Benchmark độc lập do nhóm xây dựng:*
    * **Benchmark A (Quy mô rộng):** Ngữ liệu gồm **2.087 điều luật** thuộc 7 văn bản luật lớn. Tập câu hỏi gồm **512 câu hỏi** đã được biên tập lại để **hạ độ trùng lặp từ vựng Jaccard từ 0,68 xuống 0,31** (chống gian lận từ khóa BM25). Thiết lập tập đối chuẩn công bằng **Tier 1 gồm 205 câu hỏi trên 500 điều** (Bộ luật Hình sự & Lao động) để đối đầu sòng phẳng với LightRAG.
    * **Benchmark B (Độ sâu ngữ nghĩa):** 50 câu hỏi phân tầng tại Chương III Luật Đất đai 2024, gắn nhãn vi mô đến từng Khoản, Điểm, Điều kiện, Ngoại lệ và Chuỗi dẫn chiếu.
  * *Khối 3 — Workflow kiểm toán kép:* Luồng 1 đo đạc tất định (Recall@5, MRR@5, Token, Locator) kết hợp Luồng 2 thẩm định ngữ nghĩa bằng LLM-as-a-Judge (GPT-4o-mini, $T=0$) với cơ chế xác thực JSON schema nghiêm ngặt.
* **Dẫn chứng:** `[Tham chiếu: Báo cáo toàn văn — Mục 2.2, 2.3, 2.7, 2.9 | Bảng 2.1, 2.2]`.

---

### SLIDE 7 · GIAI ĐOẠN 1: NGHỊCH LÝ SỤP ĐỔ TRÍCH DẪN & TRẢ LỜI RQ1 (LÂM | 05:15 – 06:40)
* **Tiêu đề:** Giai đoạn 1 — Nghịch lý sụp đổ trích dẫn trên tập Tier 1 (N = 205 câu) & Trả lời RQ1
* **Luận điểm cốt lõi (Insight):** *Hiệu năng tìm kiếm tài liệu cao hoàn toàn không đồng nghĩa với việc mô hình trích dẫn đúng căn cứ: Cắt đoạn thô cơ học đã chặt đứt phả hệ pháp luật.*
* **Bố cục hiển thị:** Bảng Bảng 3.4 kèm Hộp đỏ nổi bật Nghịch lý kỹ thuật:
  * *Bảng số liệu đối chuẩn (Tier 1 Fair Subset):*
    * Naive Vector RAG: Recall 0,9561 | Context Precision 0,9659 | **Citation Accuracy: 0,3259**
    * Hybrid RAG: Recall 0,9659 | Context Precision 0,9660 | **Citation Accuracy: 0,2902**
    * LightRAG: Recall 0,9659 | Context Precision 0,8829 | **Citation Accuracy: 0,1371**
  * *Cú sốc thực nghiệm:* Cả ba hệ thống đều tìm trúng Điều luật liên quan ($Recall > 95\%$), nhưng độ chính xác trích dẫn chỉ đạt $\sim 30\%$, riêng LightRAG sụp đổ xuống chỉ còn **$13,71\%$**!
  * *Cơ chế khoa học:* Việc cắt khối thô 1.200 token đã làm đứt gãy quan hệ cha-con. LLM nhận đoạn trích bị mất ngữ cảnh chủ thể ở cấp Điều nên bắt đầu suy đoán vô căn cứ.
  * *Chốt hạ RQ1:* Các kiến trúc RAG cơ sở hiện hành không thể đảm bảo độ chính xác trích dẫn nếu giữ nguyên phương thức cắt đoạn thô truyền thống.
* **Dẫn chứng:** `[Tham chiếu: Báo cáo toàn văn — Mục 3.2 | Bảng 3.3, Bảng 3.4 | Trang 91–93]`.

---

### SLIDE 8 · GIAI ĐOẠN 2: PARSER V2 & ARTICLE-LEVEL MAXP (LÂM | 06:40 – 08:05)
* **Tiêu đề:** Giai đoạn 2 — Giải pháp phân đoạn cấu trúc vi mô & Gom điểm cực đại Article MaxP
* **Luận điểm cốt lõi (Insight):** *Gắn "căn cước phả hệ" bất biến cho từng phân đoạn vi mô và gom điểm cấp Điều để vừa không mất ngữ cảnh cha-con, vừa loại bỏ hiện tượng bão hòa Top-K.*
* **Bố cục hiển thị:** Sơ đồ 2 nửa màn hình:
  * *Nửa trái — Structure-Aware Parser v2:*
    * Bóc tách đệ quy 2.087 Điều luật thành **12.754 phân đoạn vi mô** cấp Khoản và Điểm.
    * Gắn tiền tố bất biến: `[Luật Đất đai 2024 > Chương III > Điều 45 > Khoản 1 > Điểm a]`.
    * Khâu Validation tự động bảo toàn 100% phả hệ và nhận diện ký tự tiếng Việt đặc thù.
  * *Nửa phải — Thuật toán gom điểm cực đại Article-level MaxP:*
    * *Vấn đề:* 12.754 đoạn nhỏ gây bão hòa Top-K (Top-5 trả về 5 điểm thuộc cùng 1 điều).
    * *Công thức:* $\text{Score}(\text{Article}_i) = \max_{p \in \text{Article}_i} \text{Score}(p)$.
    * *Cơ chế:* 1 Điểm luật trúng khớp sẽ kéo cả Điều luật đại diện lên Top đầu, sau đó trích xuất đúng phân đoạn vi mô chứa bằng chứng để đưa vào prompt.
* **Dẫn chứng:** `[Tham chiếu: Báo cáo toàn văn — Mục 2.5 | Trang 61–68]`.

---

### SLIDE 9 · GIAI ĐOẠN 2: MA TRẬN ĐỐI SOÁT C1 – C6 & ĐỘT PHÁ C5 (LÂM | 08:05 – 10:00)
* **Tiêu đề:** Giai đoạn 2 — Kết quả ma trận 6 cấu hình trên Benchmark A (N = 512 câu) & Trả lời RQ2
* **Luận điểm cốt lõi (Insight):** *C5 đưa độ chính xác trích dẫn lên mức gần như hoàn hảo (0,9902), tiết kiệm gần 80% token; xác thực hoàn toàn giả thuyết H2.*
* **Bố cục hiển thị:** Bảng ma trận Bảng 3.6 và 3 con số Headline khổng lồ:
  * *Bảng số liệu 6 cấu hình (512 câu | 3.072 lượt chấm LLM-Judge):*
    * C1 (Naive BM25): Citation 0,7490 | Điểm 1,0: 72,5% | Token ~2.500
    * C2 (Naive Dense): Citation 0,4000 | Điểm 1,0: 25,4% | Token ~2.898
    * C3 (Naive Hybrid): Citation 0,3986 | Điểm 1,0: 25,6% | Token ~2.898
    * C4 (Parser BM25): Citation 0,9028 | Điểm 1,0: 89,3% | Token ~580
    * **C5 (Parser Dense): Citation 0,9902 | Điểm 1,0: 98,4% (504/512 câu) | Token ~580**
    * C6 (Parser Hybrid $\alpha=0,5$): Citation 0,9786 | Điểm 1,0: 96,3% | Token ~580
  * *Ba con số đột phá:*
    * **`0,9902` (Citation Acc C5):** Tăng **+59,02 điểm phần trăm** so với C2 (0,4000). Có **504 / 512 câu đạt điểm tuyệt đối 1,0**.
    * **`-79,9%` (Tiết kiệm token):** Dung lượng giảm từ $\sim 2.898$ token xuống còn **$\sim 580$ token**.
    * **`α = 0,8` (Weighted RRF tối ưu):** Đưa Recall lên **0,9297** và MRR lên **0,8220**, khắc phục hiện tượng cào bằng ở C6.
  * *Chốt hạ RQ2:* Phân đoạn cấu trúc vi mô kết hợp MaxP giải quyết triệt để bài toán trích dẫn chính xác và tối ưu hóa chi phí.
* **Dẫn chứng:** `[Tham chiếu: Báo cáo toàn văn — Mục 3.3 | Bảng 3.5, Bảng 3.6, Bảng 3.7 | Trang 96–101]`.

---

### SLIDE 10 · GIAI ĐOẠN 3: KIẾN TRÚC HYBRID UKG & MODULE 5 CAUSAL ROUTER (MINH | 10:00 – 11:15)
* **Tiêu đề:** Giai đoạn 3 — Triết lý kiến trúc 2 tầng Hybrid Parser / UKG & Bộ định tuyến Module 5
* **Luận điểm cốt lõi (Insight):** *Giải quyết xung đột giữa tính bất biến của cấu trúc văn bản và tính linh hoạt của ngữ nghĩa bằng kiến trúc đồ thị hai tầng và bộ định tuyến nhân quả siêu nhẹ.*
* **Bố cục hiển thị:** Sơ đồ dòng chảy 2 tầng rõ rệt:
  * *Tầng 1 — Đồ thị Cấu trúc vật lý (Physical Graph):* Khóa cứng 100% phả hệ văn bản nguồn, bảo đảm tính bất biến tuyệt đối.
  * *Tầng 2 — Đồ thị Ngữ nghĩa (Semantic Graph):* 
    * **Module 5 (Semantic Router):** Ứng dụng mô hình Causal LLM **Qwen2.5-0.5B** kết hợp toán tử **Max-Fusion** logic OR:  
      $$S_{\text{fusion}} = \max(S_{\text{regex}}, S_{\text{semantic}})$$
    * Khắc phục hoàn toàn "Cạm bẫy trung bình" (Mean-Pooling Trap) của các mô hình Dense Bi-encoder thông thường (chứng minh tại Phụ lục A).
    * Tại điểm cân bằng tối ưu $\theta = 0,85$, hệ thống đạt **Recall 96,85%**, F1 đạt **0,8146**, loại bỏ an toàn 9,33% lượng phân đoạn rác thủ tục chuyển sang Module 6 mà không gây đứt gãy tri thức pháp lý.
* **Dẫn chứng:** `[Tham chiếu: Báo cáo toàn văn — Mục 2.6 | Hình 2.2, Bảng 2.4 & Phụ lục A | Bảng A.1, A.2]`.

---

### SLIDE 11 · GIAI ĐOẠN 3: KẾT QUẢ THỰC NGHIỆM TRÊN BENCHMARK B (MINH | 11:15 – 13:00)
* **Tiêu đề:** Giai đoạn 3 — Kết quả đối chuẩn trên Benchmark B (N = 50 câu) & Trả lời RQ3, RQ4
* **Luận điểm cốt lõi (Insight):** *UKG vượt trội LightRAG ở khả năng bao phủ ngoại lệ pháp luật (+28,57 đpt), định vị quy phạm tập trung; thẳng thắn xác định ranh giới tổ hợp của chuỗi dẫn chiếu đa bước.*
* **Bố cục hiển thị:** Bảng Bảng 3.18 và Bảng 3.24 đối sánh trực diện với LightRAG:
  * *Ưu thế vượt trội ở RQ3 (Bảng 18 & Bảng 24):*
    * **Recall@5 cấp Điều:** UKG đạt **0,9184** vs LightRAG **0,7358** (**Vượt +18,26 điểm %**).
    * **MRR@5 cấp Điều:** UKG đạt **0,8848** vs LightRAG **0,5539** (**Vượt +33,09 điểm %**).
    * **Exception Coverage (Độ phủ ngoại lệ):** UKG đạt **0,6786** vs LightRAG **0,3929** (**Vượt +28,57 điểm %** nhờ bóc tách chuẩn xác các mệnh đề loại trừ "trừ trường hợp...").
    * **Subject-Scope Accuracy:** UKG đạt **0,8889** vs LightRAG **0,7639** (**Vượt +12,50 điểm %**).
    * **Legal Correctness:** UKG đạt **0,8777** vs LightRAG **0,8210** (**Vượt +5,67 điểm %**).
  * *Hiện tượng khách quan về Condition Coverage:* UKG đạt 0,7066 so với LightRAG 0,8421 (-13,55 đpt) do UKG định vị tập trung vào quy phạm lõi, trong khi LightRAG dùng chunk 1.200 token thô bao phủ loãng các câu chung quanh.
  * *Đánh giá trung thực ở RQ4 (Bảng 23):* Reference-target Recall đạt **0,5867**; nhưng **Chain Exact Match đạt 0,0000 (0/18 câu)** do không gian tìm kiếm trên đồ thị tri thức dày đặc gặp hiện tượng bùng nổ tổ hợp.
* **Dẫn chứng:** `[Tham chiếu: Báo cáo toàn văn — Mục 3.4, 3.6, 3.7 | Bảng 3.9, Bảng 3.14, Bảng 3.15 | Trang 103, 108, 110]`.

---

### SLIDE 12 · TỔNG HỢP KẾT QUẢ THEO BỐN CÂU HỎI NGHIÊN CỨU (MINH | 13:00 – 13:55)
* **Tiêu đề:** Tổng hợp kết quả thực nghiệm giải quyết trọn vẹn 4 câu hỏi nghiên cứu
* **Luận điểm cốt lõi (Insight):** *Đóng gói đanh thép câu trả lời cho cả bốn bài toán đặt ra ở đầu đề tài.*
* **Bố cục hiển thị:** Bảng ma trận 4 khối đối ứng:
  * **Trả lời RQ1:** Chứng minh thực nghiệm Nghịch lý trích dẫn: Recall cao ($>95\%$) nhưng Citation sụp đổ ($\sim 30\%$, LightRAG còn $13,71\%$) do cắt thô làm đứt gãy phả hệ.
  * **Trả lời RQ2:** Xác thực giải pháp Parser v2 và MaxP: Nâng Citation lên **$0,9902$** ($98,4\%$ tuyệt đối) và tiết kiệm **$79,9\%$ token**, xác định ngưỡng dung hợp tối ưu $\alpha=0,8$.
  * **Trả lời RQ3:** Kiến trúc Hybrid UKG vượt trội LightRAG: Recall cấp Điều đạt **$0,9184$** ($+18,26$ đpt), độ phủ ngoại lệ đạt **$0,6786$** ($+28,57$ đpt).
  * **Trả lời RQ4:** Định vị tốt các nút đích liên quan ($58,67\%$), xác định rõ ranh giới tổ hợp của chuỗi xích hoàn chỉnh (*Exact Match = 0*), đặt nền tảng cho duyệt đồ thị có ràng buộc.
* **Dẫn chứng:** `[Tham chiếu: Báo cáo toàn văn — Mục 1, Kết luận | Trang 123–124]`.

---

### SLIDE 13 · BA ĐÓNG GÓP KHOA HỌC CHÍNH (MINH | 13:55 – 14:35)
* **Tiêu đề:** Ba đóng góp khoa học cốt lõi của đề tài
* **Luận điểm cốt lõi (Insight):** *Đóng góp đồng thời cả về Phương pháp luận kiểm chuẩn, Giải pháp kỹ thuật phân đoạn và Kiến trúc hệ thống đồ thị.*
* **Bố cục hiển thị:** 3 cột đóng góp mang tính dấu ấn:
  * *Đóng góp 1 — Khung kiểm chuẩn Benchmark chuẩn mực:* Xây dựng thành công Benchmark A ($2.087$ điều, $512$ câu hỏi giảm trùng lặp từ vựng) và Benchmark B ($50$ câu hỏi chuyên sâu) kèm Adapter Pattern loại bỏ hoàn toàn thiên lệch thực nghiệm.
  * *Đóng góp 2 — Giải pháp phân đoạn cấu trúc vi mô:* Bộ đôi Parser v2 và Article MaxP giải quyết triệt để sự sụp đổ trích dẫn, đạt Citation Acc $0,9902$ và tiết kiệm gần $80\%$ chi phí token.
  * *Đóng góp 3 — Kiến trúc đồ thị hợp nhất Hybrid UKG:* Hiện thực hóa thành công mô hình kết hợp cây phân cấp vật lý và đồ thị ngữ nghĩa, chứng minh ưu thế vượt trội trong việc xử lý các quy phạm ngoại lệ và chủ thể pháp luật.
* **Dẫn chứng:** `[Tham chiếu: Báo cáo toàn văn — Mục 2, Kết luận | Trang 124–125]`.

---

### SLIDE 14 · HƯỚNG PHÁT TRIỂN & KẾT THÚC (MINH | 14:35 – 15:00)
* **Tiêu đề:** Hướng nghiên cứu tiếp theo & Lời cảm ơn
* **Luận điểm cốt lõi (Insight):** *Xác định rõ ràng lộ trình mở rộng quy mô pháp lý và thuật toán suy luận đồ thị.*
* **Bố cục hiển thị:**
  * *3 Hướng phát triển:* (1) Mở rộng Parser sang Nghị định, Thông tư; (2) Tự động hóa cập nhật hiệu lực khi văn bản sửa đổi; (3) Hoàn thiện thuật toán duyệt đồ thị có ràng buộc (Constrained Graph Traversal) để khép kín chuỗi dẫn chiếu chéo.
  * *Phần cảm ơn trang trọng:* "Trân trọng cảm ơn Quý Thầy Cô trong Hội đồng khoa học đã chú ý lắng nghe! Kính mời Hội đồng đặt câu hỏi (Q&A)."

---
---

# PHẦN 2: KỊCH BẢN LỜI THOẠI STORYTELLING CHUYÊN SÂU 15 PHÚT (FULL SPOKEN SCRIPT)

---

### [00:00 – 01:30] · CHẶNG 1: LƯU THANH LÂM (MỞ MÀN & ĐẶT VẤN ĐỀ)

**[Slide 1 — Bìa báo cáo · 00:00 – 00:20]**
> *"Kính thưa Quý Thầy Cô trong Hội đồng khoa học!  
> Em tên là **Lưu Thanh Lâm**, đại diện nhóm nghiên cứu gồm ba thành viên: em, bạn **Ngô Thế Dương** và bạn **Nguyễn Bình Minh**. Dưới sự hướng dẫn khoa học của **Thầy Tiến sĩ Nguyễn Mạnh Dũng**, hôm nay nhóm chúng em xin phép được báo cáo kết quả đề tài nghiên cứu khoa học:  
> **'Đánh giá và tối ưu hóa các kiến trúc RAG trên nền tảng dữ liệu cấu trúc đặc thù'**, tập trung vào bài toán hỏi đáp trên văn bản quy phạm pháp luật Việt Nam."*

**[Slide 2 — Bối cảnh & Ảo giác pháp lý · 00:20 – 01:30]**
> *"Kính thưa Hội đồng, trong kỷ nguyên số hóa, nhu cầu tra cứu thông tin pháp luật của người dân và doanh nghiệp đang ngày một tăng cao. Tuy nhiên, lĩnh vực pháp luật có một yêu cầu nghiêm ngặt: Một câu trả lời không chỉ cần đúng về mặt ngữ nghĩa, mà **bắt buộc phải có căn cứ kiểm chứng xác thực đến từng điều khoản cụ thể**.  
> 
> Mặc dù kiến trúc RAG kết hợp mô hình ngôn ngữ lớn với việc truy hồi dữ liệu bên ngoài đã giúp cải thiện đáng kể độ tin cậy, nhưng các nghiên cứu thực nghiệm quốc tế gần đây, tiêu biểu như công bố của Magesh năm 2024, đã chỉ ra rằng các hệ thống AI thương mại hàng đầu vẫn gặp tỷ lệ ảo giác pháp lý từ 17% đến 33%.  
> Trong thực tiễn pháp lý, chỉ cần hệ thống trích dẫn đúng số Điều nhưng dẫn sai một Khoản, hoặc nhầm lẫn một ngoại lệ tại một Điểm, hệ quả pháp lý của hành vi có thể bị đảo lộn hoàn toàn từ hợp pháp sang vi phạm.  
> 
> Nhận diện được rủi ro đó, đề tài của nhóm tập trung giải quyết bài toán cốt lõi: Làm thế nào để vừa tối ưu hiệu quả truy hồi, vừa hỗ trợ mô hình ngôn ngữ lớn xác định chính xác căn cứ pháp lý vi mô mà không làm bùng nổ chi phí tính toán?  
> Để làm rõ đặc thù của văn bản luật Việt Nam và cơ sở nghiên cứu của nhóm, sau đây em xin trân trọng kính mời bạn **Ngô Thế Dương**."*  
*(Lâm chuyển micro và clicker cho Dương, bước lùi sang bên).*

---

### [01:30 – 05:15] · CHẶNG 2: NGÔ THẾ DƯƠNG (ĐẶC THÙ, LÝ THUYẾT & HẠ TẦNG BENCHMARK)

**[Slide 3 — Đặc thù luật & Khoảng trống · 01:30 – 02:25]**
> *"Em xin cảm ơn bạn Lâm. Kính thưa Quý Thầy Cô, qua quá trình khảo sát cấu trúc văn bản quy phạm pháp luật Việt Nam, nhóm nhận diện ba đặc thù mang tính chi phối:  
> Thứ nhất là cấu trúc phân cấp đa tầng nghiêm ngặt: từ Luật xuống Chương, Mục, Điều, Khoản và Điểm. Một Điểm quy định không bao giờ đứng độc lập, mà ý nghĩa pháp lý của nó phụ thuộc hoàn toàn vào chủ thể và điều kiện được xác lập ở cấp cha.  
> Thứ hai là mạng lưới dẫn chiếu phức tạp, gồm cả viện dẫn nội bộ giữa các điều luật và dẫn chiếu chéo liên văn bản giữa Luật với Nghị định, Thông tư.  
> Và thứ ba là sự lệch pha từ vựng rất lớn giữa câu hỏi tự nhiên bằng khẩu ngữ của người dân với văn phong lập pháp quy chuẩn.  
> 
> Từ ba đặc thù đó, nhóm xác định ba khoảng trống nghiên cứu chính:  
> Một là sự thiếu vắng một khung đối chuẩn thực nghiệm công bằng có kiểm soát biến số trên dữ liệu luật Việt Nam;  
> Hai là chưa có nghiên cứu nào đánh giá định lượng tác động của việc phân đoạn cấu trúc vi mô so với việc cắt khối token thô truyền thống;  
> Và ba là các bộ chỉ số RAG tổng quát hiện nay không đánh giá được độ chính xác của trích dẫn căn cứ và chuỗi dẫn chiếu.  
> Đây chính là cơ sở thôi thúc nhóm thiết kế phương pháp nghiên cứu của đề tài."*

**[Slide 4 — Cơ sở lý thuyết: Ba trường phái RAG · 02:25 – 03:20]**
> *"Để giải quyết các khoảng trống trên, về mặt cơ sở lý thuyết, nghiên cứu của nhóm tập trung khảo sát ba trường phái RAG đại diện hiện nay trên thế giới:  
> Thứ nhất, **Naive Vector RAG** biểu diễn câu hỏi và tài liệu trong không gian vector đa chiều, sau đó truy hồi Top-K dựa trên độ tương đồng Cosine.  
> Thứ hai, **Hybrid RAG** kết hợp năng lực tìm kiếm từ khóa chính xác của BM25 với khả năng nắm bắt ngữ nghĩa của Dense vector, sử dụng thuật toán Reciprocal Rank Fusion để dung hợp kết quả và mô hình Cross-Encoder để tái xếp hạng.  
> Thứ ba, **LightRAG** đại diện cho trường phái GraphRAG, khai thác biểu diễn đồ thị thực thể và quan hệ hai tầng nhằm hỗ trợ suy luận ngữ cảnh rộng và kết nối các tri thức phân tán.  
> 
> Ba kiến trúc đại diện cho ba nguyên lý tổ chức và truy xuất thông tin khác nhau. Nhóm sử dụng chúng làm các hệ thống cơ sở để đánh giá tại Giai đoạn 1, trước khi khảo sát những phương án tối ưu hóa mở rộng."*

**[Slide 5 — Hệ thống 4 Câu hỏi nghiên cứu RQ1 – RQ4 · 03:20 – 04:05]**
> *"Nhằm định hướng toàn bộ quá trình thực nghiệm, nhóm xây dựng khung nghiên cứu gồm bốn câu hỏi khoa học từ RQ1 đến RQ4:  
> **RQ1** khảo sát hiệu năng thực tế và giới hạn trích dẫn của ba kiến trúc RAG cơ sở trên dữ liệu luật Việt Nam khi cắt đoạn thô.  
> **RQ2** đánh giá tác động của giải pháp phân đoạn cấu trúc vi mô Parser v2 kết hợp thuật toán gom điểm Article MaxP đối với độ chính xác trích dẫn và dung lượng ngữ cảnh.  
> **RQ3** kiểm chứng năng lực định vị điều kiện và xử lý ngoại lệ pháp luật của đồ thị tri thức hợp nhất UKG so với GraphRAG truyền thống.  
> Và **RQ4** đo lường khả năng tái dựng chuỗi quan hệ dẫn chiếu chéo đa bước của hệ thống đồ thị.  
> Bốn câu hỏi này sẽ được nhóm lần lượt giải quyết và đối chiếu kết quả qua ba giai đoạn thực nghiệm."*

**[Slide 6 — Thiết kế thực nghiệm & Hạ tầng Benchmark · 04:05 – 05:15]**
> *"Kính thưa Hội đồng, để kết quả thực nghiệm có giá trị khoa học và khả năng tái lập cao, nhóm đã đầu tư xây dựng hạ tầng kiểm chuẩn độc lập **Benchmark Harness** áp dụng mẫu thiết kế Adapter Pattern. Tất cả các hệ thống đều được chuẩn hóa đầu vào và đầu ra qua giao diện chung `BaseRAGAdapter`. Toàn bộ các biến ngoại lai được đóng băng nghiêm ngặt: cùng chạy trên một GPU NVIDIA Tesla T4, cùng sử dụng mô hình nhúng BGE-M3 1024 chiều, và mô hình ngôn ngữ GPT-4o-mini ở nhiệt độ bằng 0.  
> 
> Về mặt dữ liệu, nhóm tự xây dựng hai bộ kiểm chuẩn độc lập:  
> **Benchmark A** được xây dựng trên kho ngữ liệu gồm **2.087 điều luật** tổng hợp từ 7 đạo luật lớn của Việt Nam. Nhóm biên soạn **512 câu hỏi** và đặc biệt đã thực hiện quy trình viết lại nhằm **giảm độ trùng lặp từ vựng Jaccard từ 0,68 xuống 0,31**, nhằm mô phỏng đúng ngôn ngữ đời thường và ngăn chặn hiện tượng phương pháp từ khóa thắng oan. Trong Benchmark A, nhóm tách riêng một tập đối chuẩn công bằng **Tier 1 gồm 205 câu hỏi trên 500 điều** thuộc Bộ luật Hình sự và Lao động để đối đầu sòng phẳng với LightRAG trong cùng phạm vi chỉ mục.  
> **Benchmark B** gồm 50 câu hỏi phân tầng chuyên sâu tại Chương III Luật Đất đai 2024, được gắn nhãn vàng vi mô đến từng Khoản, Điểm, Điều kiện, Ngoại lệ và Chuỗi dẫn chiếu.  
> Quy trình đánh giá kết hợp kiểm toán tất định các chỉ số cấu trúc với phương pháp LLM-as-a-Judge được kiểm tra schema nghiêm ngặt.  
> 
> Sau đây, kết quả Giai đoạn 1 đã phát hiện ra nghịch lý gì và giải pháp Giai đoạn 2 ra sao, em xin kính mời bạn **Lưu Thanh Lâm** tiếp tục trình bày."*  
*(Dương chuyển giao micro cho Lâm).*

---

### [05:15 – 10:00] · CHẶNG 3: LƯU THANH LÂM (GIAI ĐOẠN 1 NGHỊCH LÝ & GIAI ĐOẠN 2 ĐỘT PHÁ)

**[Slide 7 — Giai đoạn 1: Nghịch lý sụp đổ trích dẫn · 05:15 – 06:40]**
> *"Em xin cảm ơn bạn Dương. Kính thưa Hội đồng khoa học, khi tiến hành đối soát công bằng ba kiến trúc RAG cơ sở trên tập Tier 1 gồm 205 câu hỏi, nhóm chúng em đã phát hiện một hiện tượng thực nghiệm chấn động — chúng em định danh là **Nghịch lý sụp đổ trích dẫn (The Citation Collapse Paradox)**:  
> 
> Nhìn vào Bảng 3.4 trên màn hình, cả ba hệ thống đều thể hiện năng lực tìm kiếm tài liệu rất xuất sắc: Recall@5 đều đạt từ 95,6% đến 96,6%, độ khớp ngữ cảnh Context Precision đạt trên 0,96. Tức là hệ thống hầu như luôn đưa được Điều luật đúng vào trong ngữ cảnh!  
> Thế nhưng, khi đánh giá xem câu trả lời có chỉ ra đúng Khoản nào, Điểm nào làm căn cứ pháp lý hay không, thì độ chính xác trích dẫn Citation Accuracy của Naive Vector chỉ đạt **32,59%** và Hybrid RAG chỉ đạt **29,02%**.  
> Đặc biệt nghiêm trọng, mô hình đồ thị LightRAG dù đạt Recall tới 96,59% nhưng độ chính xác trích dẫn lại sụp đổ xuống chỉ còn **13,71%**!  
> 
> **Cơ sở khoa học giải mã nghịch lý này là gì?**  
> Khi kiểm toán dữ liệu, nhóm nhận thấy các kiến trúc truyền thống áp dụng chiến lược cắt đoạn thô cơ học 1.200 token. Việc cắt ngang một văn bản luật phân cấp đa tầng đã làm chặt đứt mối liên kết phả hệ cha-con. Khi các phân đoạn bị chia cắt đưa vào prompt, mô hình ngôn ngữ lớn bị mất hoàn toàn thông tin chủ thể ở cấp Điều, dẫn đến hiện tượng trích dẫn nhầm lẫn điều khoản hoặc suy đoán vô căn cứ.  
> Kết quả này trả lời dứt khoát cho **Câu hỏi nghiên cứu RQ1**: Các kiến trúc RAG cơ sở hiện nay hoàn toàn bất lực trong việc đảm bảo trích dẫn chính xác luật Việt Nam nếu giữ nguyên phương thức cắt đoạn thô truyền thống."*

**[Slide 8 — Giai đoạn 2: Parser v2 & Article MaxP · 06:40 – 08:05]**
> *"Để khắc phục triệt để hiện tượng đứt gãy phả hệ, bước sang Giai đoạn 2, nhóm đề xuất bộ giải pháp cấu trúc gồm hai thành phần cốt lõi:  
> Thứ nhất là bộ phân tích cú pháp **Structure-Aware Parser v2**. Thay vì cắt đoạn theo số lượng token thô, Parser v2 bóc tách đệ quy văn bản luật theo đúng cấu trúc logic lập pháp, chuyển đổi 2.087 Điều luật thành **12.754 phân đoạn vi mô** cấp Khoản và Điểm. Điểm cải tiến mang tính bản lề là mỗi phân đoạn vi mô đều được gắn kèm một **tiền tố phân cấp bất biến**, ví dụ: `[Luật Đất đai 2024 > Chương III > Điều 45 > Khoản 1 > Điểm a]`. Nhờ đó, dù phân đoạn bị trích xuất độc lập, LLM vẫn nắm bắt trọn vẹn chủ thể cha và ngữ cảnh phân cấp.  
> 
> Tuy nhiên, việc chia nhỏ thành hơn 12 nghìn đoạn vi mô lập tức gây ra hiện tượng 'bội thực cục bộ': Top-5 đoạn trả về có thể cùng thuộc về một Điều luật duy nhất. Do đó, nhóm xây dựng thuật toán gom điểm cực đại **Article-level MaxP**.  
> Nguyên lý toán học là: Điểm số của một Điều luật bằng giá trị lớn nhất trong số điểm của các phân đoạn vi mô thuộc Điều luật đó. Chỉ cần một Điểm luật khớp ngữ nghĩa với câu hỏi, toàn bộ Điều luật đại diện sẽ nhận điểm cực đại và được kéo lên đầu danh sách, sau đó hệ thống trích xuất đúng phân đoạn vi mô chứa bằng chứng để đưa vào prompt."*

**[Slide 9 — Giai đoạn 2: Ma trận C1–C6 & Đột phá C5 · 08:05 – 10:00]**
> *"Nhóm tiến hành đối soát toàn diện ma trận sáu cấu hình từ C1 đến C6 trên toàn bộ 512 câu hỏi của Benchmark A thông qua 3.072 lượt thẩm định bằng LLM-as-a-Judge.  
> Kết quả tại Bảng 3.6 đã xác thực hoàn toàn **Câu hỏi nghiên cứu RQ2** và giả thuyết H2 với ba bước nhảy vọt:  
> 
> Thứ nhất, cấu hình **C5 (Parser Dense)** đã nâng điểm Citation Accuracy từ 0,4000 ở Naive Dense lên mức kỷ lục **0,9902**, tăng tới 59,02 điểm phần trăm. Tỷ lệ câu hỏi đạt trích dẫn chuẩn xác tuyệt đối tăng từ 25,4% lên tới **98,4%** (tức 504 trên tổng số 512 câu hỏi đạt điểm 1,0 tối đa).  
> Thứ hai, về mặt tối ưu tài nguyên, dung lượng ngữ cảnh trung bình đưa vào LLM giảm từ gần 2.900 token xuống chỉ còn **khoảng 580 token**, tương đương **tiết kiệm 79,9% chi phí token**.  
> Thứ ba, nhóm đã thực hiện quét 11 giá trị trọng số dung hợp Weighted RRF và xác định điểm tối ưu tại $\alpha = 0,8$, đưa Recall lên **0,9297** và MRR lên **0,8220**, khắc phục hiện tượng suy giảm hiệu năng khi cào bằng trọng số ở cấu hình C6 thông thường.  
> 
> Nhóm rút ra kết luận thực tiễn: Nếu hệ thống ưu tiên tuyệt đối tính chuẩn xác trích dẫn và tiết kiệm chi phí, C5 là lựa chọn tối ưu; còn nếu bài toán đòi hỏi bao phủ vét tài liệu tối đa, cấu hình Weighted RRF với $\alpha=0,8$ sẽ mang lại hiệu quả cân bằng nhất.  
> 
> Giai đoạn 2 đã giải quyết xuất sắc bài toán trích dẫn đơn văn bản. Tuy nhiên, trước các câu hỏi đa bước và có quan hệ dẫn chiếu phức tạp, hệ thống mở rộng lên đồ thị tri thức ra sao? Sau đây xin mời bạn **Nguyễn Bình Minh** trình bày Giai đoạn 3."*  
*(Lâm chuyển micro cho Minh).*

---

### [10:00 – 15:00] · CHẶNG 4: NGUYỄN BÌNH MINH (ĐỒ THỊ UKG, ĐA BƯỚC & KẾT LUẬN)

**[Slide 10 — Giai đoạn 3: Kiến trúc Hybrid UKG & Module 5 · 10:00 – 11:15]**
> *"Em xin cảm ơn bạn Lâm. Kính thưa Quý Thầy Cô trong Hội đồng, để xử lý các truy vấn pháp lý đa bước, bước sang Giai đoạn 3, nhóm đề xuất kiến trúc toàn diện **Hybrid Parser / UKG gồm 10 Module**.  
> Thay vì để mô hình ngôn ngữ tự do trích xuất đồ thị một cách mất kiểm soát như các kiến trúc GraphRAG truyền thống, triết lý cốt lõi của Hybrid UKG là **tách biệt rành mạch thành hai tầng đồ thị**:  
> Tầng 1 là **Đồ thị Cấu trúc vật lý (Physical Graph)**: Sử dụng bộ phân tích tất định khóa cứng 100% phả hệ Chương-Mục-Điều-Khoản-Điểm, đóng vai trò là 'trục xương sống bất biến không thể sai lệch'.  
> Tầng 2 là **Đồ thị Ngữ nghĩa (Semantic Graph)**: Trích xuất các thực thể và quan hệ pháp lý động như quyền, nghĩa vụ và ngoại lệ để gắn lên trục xương sống đó.  
> 
> Trọng tâm đột phá nằm ở **Module 5 (Semantic Router)**. Để lọc các văn bản thuần thủ tục hành chính mà không làm rơi rụng các quy phạm ngầm định, nhóm ứng dụng mô hình Causal LLM siêu nhẹ **Qwen2.5-0.5B** kết hợp toán tử **Max-Fusion** logic OR giữa tín hiệu Regex và tín hiệu nhúng ngữ nghĩa.  
> Khảo sát thực nghiệm độc lập tại Phụ lục A chỉ ra rằng các mô hình Bi-encoder truyền thống bị mắc kẹt trong 'Cạm bẫy trung bình' (Mean-Pooling Trap), làm triệt tiêu tín hiệu phân đoạn ngắn. Ngược lại, cơ chế Causal Attention của Qwen2.5-0.5B bảo toàn trọn vẹn ngữ nghĩa mệnh đề.  
> Tại điểm cân bằng tối ưu $\theta = 0,85$, hệ thống đạt độ bao phủ **Recall 96,85%**, F1 đạt đỉnh **0,8146**, loại bỏ an toàn 9,33% lượng phân đoạn rác thủ tục chuyển sang Module 6 mà không gây đứt gãy tri thức pháp lý."*

**[Slide 11 — Giai đoạn 3: Thực nghiệm Benchmark B · 11:15 – 13:00]**
> *"Nhóm kiểm chứng kiến trúc đề xuất trên **Benchmark B** gồm 50 câu hỏi phân tầng tại Chương III Luật Đất đai 2024 trong thế đối đầu trực tiếp với LightRAG.  
> Kết quả thực nghiệm tại Bảng 3.18 và Bảng 3.24 đã làm sáng tỏ **Câu hỏi nghiên cứu RQ3 và RQ4**:  
> 
> Về mặt tích cực giải quyết **RQ3**:  
> Thứ nhất, về truy hồi cấp Điều, Hybrid Parser/UKG đạt Recall@5 **0,9184**, **vượt LightRAG 18,26 điểm phần trăm** (0,7358); chỉ số MRR@5 đạt **0,8848**, **vượt trội 33,09 điểm phần trăm** (0,5539).  
> Thứ hai, về chất lượng nội dung, UKG đạt điểm tính chính xác pháp lý Legal Correctness **0,8777** (so với 0,8210 của LightRAG), và độ chính xác phạm vi chủ thể đạt **0,8889** (so với 0,7639).  
> Đặc biệt, ở chỉ số **Độ phủ Ngoại lệ (Exception Coverage)**, UKG đạt **0,6786**, **vượt xa LightRAG tới 28,57 điểm phần trăm** (0,3929). Ưu thế này có được nhờ đồ thị ngữ nghĩa đã bóc tách chính xác các nút ngoại lệ 'trừ trường hợp...', vốn thường bị các mô hình GraphRAG truyền thống bỏ qua.  
> 
> Nhóm cũng ghi nhận một hiện tượng khách quan: LightRAG đạt Condition Coverage cao hơn UKG (0,8421 so với 0,7066) vì LightRAG gom các khối văn bản thô 1.200 token lớn nên vô tình bao hàm cả các câu điều kiện chung, nhưng việc này lại dẫn đến độ bao phủ loãng và làm tăng ảo giác.  
> 
> Về mặt hạn chế giải quyết **RQ4**: Đối với bài toán truy vết dẫn chiếu chéo, hệ thống đạt độ thu hồi nút đích Reference-target Recall **58,67%**. Tuy nhiên, chỉ số khôi phục chuỗi hoàn chỉnh **Chain Exact Match đạt 0,0000 (0/18 câu)**.  
> Với tinh thần trung thực khoa học, nhóm xác định nguyên nhân là do không gian tìm kiếm trên đồ thị tri thức pháp lý dày đặc gặp hiện tượng bùng nổ tổ hợp, hệ thống mới chỉ tìm được các cạnh đơn lẻ mà chưa xâu chuỗi được toàn vẹn toàn bộ hành trình đa bước."*

**[Slide 12 — Tổng kết: Đóng gói 4 Câu hỏi nghiên cứu · 13:00 – 13:55]**
> *"Kính thưa Hội đồng khoa học, để tổng hợp lại toàn bộ công trình, bốn câu hỏi nghiên cứu ban đầu đã được nhóm giải quyết trọn vẹn bằng thực nghiệm:  
> Với **RQ1**, nhóm chứng minh thực nghiệm Nghịch lý trích dẫn: Các RAG cơ sở đạt Recall cao trên 95% nhưng sụp đổ trích dẫn xuống ~30% (LightRAG còn 13,71%) do cắt thô làm gãy cấu trúc phả hệ.  
> Với **RQ2**, nhóm xác thực giải pháp Parser v2 và MaxP giải quyết triệt để nghịch lý trên, nâng Citation Accuracy lên **0,9902** (98,4% tuyệt đối) và tiết kiệm **79,9% token**, xác định ngưỡng dung hợp tối ưu $\alpha=0,8$.  
> Với **RQ3**, kiến trúc Hybrid UKG chứng minh ưu thế vượt trội khi nâng Recall cấp Điều thêm 18,26 điểm phần trăm và nâng độ phủ ngoại lệ thêm **28,57 điểm phần trăm**.  
> Và với **RQ4**, nhóm xác định rõ ranh giới thực nghiệm của bài toán dẫn chiếu đa bước, chỉ ra giới hạn tổ hợp của chuỗi xích hoàn chỉnh làm tiền đề phát triển tiếp theo."*

**[Slide 13 — Ba đóng góp khoa học chính · 13:55 – 14:35]**
> *"Từ những kết quả trên, đề tài mang lại ba đóng góp khoa học cốt lõi:  
> Một là xây dựng thành công hai bộ Benchmark A và Benchmark B chuẩn mực kèm khung Adapter Pattern loại bỏ hoàn toàn thiên lệch thực nghiệm.  
> Hai là đề xuất giải pháp phối hợp giữa Parser v2 và thuật toán MaxP, giải quyết tận gốc sự sụt giảm trích dẫn pháp lý và tối ưu hóa tài nguyên tính toán.  
> Ba là hiện thực hóa thành công kiến trúc kết hợp cây phân cấp vật lý và đồ thị ngữ nghĩa UKG, chứng minh ưu thế vượt trội trong việc xử lý các quy phạm ngoại lệ và chủ thể pháp lý phức tạp."*

**[Slide 14 — Hướng phát triển & Kết luận · 14:35 – 15:00]**
> *"Trong thời gian tới, nhóm hướng đến ba mục tiêu tiếp theo: mở rộng bộ bóc tách cấu trúc sang các văn bản dưới luật như Nghị định, Thông tư; tự động hóa việc cập nhật hiệu lực khi văn bản sửa đổi; và hoàn thiện thuật toán duyệt đồ thị có ràng buộc (Constrained Graph Traversal) để khép kín chuỗi dẫn chiếu chéo.  
> 
> Thay mặt nhóm nghiên cứu, chúng em xin trân trọng cảm ơn Thầy Cô trong Hội đồng khoa học đã chú ý lắng nghe. Nhóm chúng em rất mong nhận được những ý kiến đóng góp quý báu từ Quý Thầy Cô và xin sẵn sàng bước vào phần Hỏi và Đáp!"*  
*(Cả ba thành viên Lâm, Dương, Minh cùng đứng nghiêm trang, cúi đầu chào Hội đồng).*

---
---

# PHẦN 3: BẢN PHAO THỰC CHIẾN - TỪ KHÓA NEO & CỬ CHỈ SÂN KHẤU (ANCHOR CHEAT SHEET)

> **Mục đích:** Tài liệu cầm tay phục vụ tập dượt thực chiến. Mỗi slide chỉ cần nhớ 2 – 3 từ khóa neo, điểm chỉ tia laser và câu chốt trigger cue để chuyển giao micro mượt mà.

| Slide | Người nói | Thời lượng | Từ khóa neo chuyên sâu | Hành động / Điểm chỉ laser trên Slide | Câu chốt chuyển mic (Trigger Cue) |
| :---: | :---: | :---: | :--- | :--- | :--- |
| **1** | **Lâm** | 20s | • Chào Hội đồng, giới thiệu 3 thành viên, GVHD<br>• Đề tài: RAG trên dữ liệu cấu trúc đặc thù | Đứng giữa bục, mắt bao quát Hội đồng, phong thái tự tin | *(Nói liền mạch sang Slide 2)* |
| **2** | **Lâm** | 70s | • Nhu cầu tra cứu pháp luật kiểm chứng tuyệt đối<br>• RAG ảo giác 17% – 33% (Magesh 2024)<br>• Sai lệch điều khoản làm đổi hệ quả pháp lý | Chỉ laser vào **Hộp đỏ cảnh báo 17% – 33%** | *"Sau đây xin mời bạn Ngô Thế Dương trình bày đặc thù dữ liệu và cơ sở nghiên cứu."* |
| **3** | **Dương** | 55s | • 3 đặc thù: Phân cấp đa tầng, Dẫn chiếu, Lệch pha từ vựng<br>• 3 Gap: Khung benchmark, Phân đoạn vi mô, Thước đo trích dẫn | Quét laser lần lượt qua **3 khối đặc thù** và **3 khối Gap** | *(Nói liền mạch sang Slide 4)* |
| **4** | **Dương** | 55s | • 3 trường phái RAG cơ sở: Naive Vector (Cosine), Hybrid (BM25+Dense+RRF), LightRAG (Graph) | Chỉ laser vào **3 cột kiến trúc RAG** | *(Nói liền mạch sang Slide 5)* |
| **5** | **Dương** | 45s | • Bung 4 câu hỏi nghiên cứu định hướng 3 giai đoạn: RQ1 (GĐ1), RQ2 (GĐ2), RQ3 & RQ4 (GĐ3) | Chỉ laser vào **bảng ma trận 4 RQ** | *(Nói liền mạch sang Slide 6)* |
| **6** | **Dương** | 70s | • Benchmark Harness + Adapter Pattern, đóng băng T4, BGE-M3, GPT-4o-mini T=0<br>• Benchmark A (512 câu, hạ Jaccard 0,31; Tier 1 205 câu / 500 điều) & Benchmark B (50 câu) | Chỉ laser vào **hộp đóng băng kiểm soát** và **hộp 2 bộ Benchmark** | *"Kết quả GĐ1 và phương án cải thiện ra sao, xin mời bạn Lưu Thanh Lâm tiếp tục trình bày."* |
| **7** | **Lâm** | 85s | • **[Slide đinh] Nghịch lý Giai đoạn 1 (RQ1)**<br>• Recall $>95\%$ nhưng Citation chỉ $\sim 30\%$<br>• LightRAG sụp đổ còn **13,71%** do cắt thô 1.200 token làm đứt gãy phả hệ cha-con | Chỉ laser dứt khoát vào **13,71% màu đỏ** và **32,59%** | *(Nói liền mạch sang Slide 8)* |
| **8** | **Lâm** | 85s | • Parser v2: 12.754 đoạn vi mô kèm tiền tố bất biến [Luật > Chương > Điều > Khoản > Điểm]<br>• Bội thực cục bộ $\rightarrow$ Article MaxP gom điểm cực đại | Chỉ laser vào **tiền tố bất biến ví dụ** và **công thức Article MaxP** | *(Nói liền mạch sang Slide 9)* |
| **9** | **Lâm** | 115s | • **[Slide đinh] Đột phá C5 (RQ2)**<br>• Citation Acc vọt lên **0,9902** (98,4% đạt 1.0, 504/512 câu)<br>• Tiết kiệm **79,9% token** (~580t)<br>• Weighted RRF quét tối ưu tại **$\alpha = 0,8$** | Chỉ laser vào 3 con số Headline lớn: **0,9902**, **-79,9%**, **$\alpha=0,8$** | *"Trước câu hỏi đa bước và quan hệ dẫn chiếu, UKG giải quyết ra sao? Xin mời bạn Minh."* |
| **10** | **Minh** | 75s | • Kiến trúc UKG: Tầng vật lý (khóa cứng phả hệ) + Tầng ngữ nghĩa (trích xuất động)<br>• Module 5 Causal Router Qwen2.5-0.5B + Max-Fusion logic OR tại $\theta=0,85$ (Recall 96,85%) | Chỉ laser vào sơ đồ 2 tầng và khối **Module 5** | *(Nói liền mạch sang Slide 11)* |
| **11** | **Minh** | 105s | • **[Slide đinh] Benchmark B (RQ3 & RQ4)**<br>• RQ3: Recall cấp Điều **0,9184** (+18,26 đpt), Exception Coverage **0,6786** (+28,57 đpt)<br>• RQ4: Thừa nhận trung thực Chain Exact Match = 0,0000 do bùng nổ tổ hợp đồ thị dày | Chỉ laser vào số **0,9184**, số **+28,57 đpt**, sau đó chỉ sang **0,0000** | *(Nói liền mạch sang Slide 12)* |
| **12** | **Minh** | 55s | • **[Slide đinh] Bo tròn 4 RQ ở cuối bài**<br>• RQ1: Sụp đổ trích dẫn<br>• RQ2: Parser v2 + MaxP thành công<br>• RQ3: Đồ thị UKG vượt trội ngoại lệ<br>• RQ4: Giới hạn chuỗi dẫn chiếu | Quét laser lần lượt qua **4 hàng tổng kết RQ** | *(Nói liền mạch sang Slide 13)* |
| **13** | **Minh** | 40s | • 3 Đóng góp khoa học cốt lõi: Khung Benchmark chuẩn; Giải pháp phân đoạn cấu trúc; Kiến trúc đồ thị hợp nhất UKG | Chỉ laser lần lượt vào **3 cột đóng góp** | *(Nói liền mạch sang Slide 14)* |
| **14** | **Minh** | 25s | • 3 Hướng phát triển: Nghị định, Thông tư; Cập nhật hiệu lực; Duyệt đồ thị có ràng buộc<br>• Lời cảm ơn và mời Q&A | Nhìn thẳng Hội đồng, mỉm cười trang trọng | Cả 3 thành viên cùng đứng nghiêm, cúi đầu chào |
