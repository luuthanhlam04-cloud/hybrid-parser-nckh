# BỘ TÀI LIỆU KỊCH BẢN VÀ THIẾT KẾ THUYẾT TRÌNH BẢO VỆ NCKH (15 PHÚT)
**Đề tài:** Đánh giá và tối ưu hóa các kiến trúc RAG trên nền tảng dữ liệu cấu trúc đặc thù  
**Mã số đề tài:** 14-SV-2026-RIPT | **Lĩnh vực:** Khoa học Máy tính & Công nghệ Thông tin  
**Nhóm sinh viên thực hiện:** Lưu Thanh Lâm (Nhóm trưởng) • Ngô Thế Dương • Nguyễn Bình Minh  
**Giảng viên hướng dẫn:** TS. Nguyễn Mạnh Dũng  
**Đơn vị:** Viện Khoa học Kỹ thuật Bưu điện - Học viện Công nghệ Bưu chính Viễn thông (PTIT)  

---

# MỤC LỤC TÀI LIỆU
1. **PHẦN 1: BẢN ĐỀ XUẤT CẤU TRÚC VÀ THIẾT KẾ HIỂN THỊ 14 SLIDE CHUẨN HÓA**  
   *(Chi tiết bố cục thị giác, nội dung hiển thị, số liệu trọng tâm kích thước lớn, biểu đồ và điểm nhấn học thuật).*
2. **PHẦN 2: KỊCH BẢN LỜI THOẠI HỌC THUẬT CHUYÊN SÂU 15 PHÚT (FULL SPOKEN SCRIPT)**  
   *(Biên soạn chi tiết từng câu từng chữ cho Lâm - Dương - Lâm - Minh từ 00:00 đến 15:00; giải thích thấu đáo cơ chế khoa học, bản chất kỹ thuật đằng sau từng số liệu thực nghiệm, hoàn toàn loại bỏ văn phong sơ sài hoặc đọc số liệu khô khốc).*
3. **PHẦN 3: BẢN PHAO THỰC CHIẾN - TỪ KHÓA NEO & CỬ CHỈ SÂN KHẤU (ANCHOR CHEAT SHEET)**  
   *(Bảng tra cứu cầm tay 14 slide: ý neo chuyên sâu, điểm chỉ laser chính xác, câu chốt chuyển giao micro nhịp nhàng).*

---
---

# PHẦN 1: BẢN ĐỀ XUẤT CẤU TRÚC VÀ THIẾT KẾ HIỂN THỊ 14 SLIDE

> **Quy chuẩn thiết kế thị giác học thuật:**
> * **Hệ màu chủ đạo:** Xanh thẫm học thuật (Navy/PTIT Blue `#003366`) + Trắng nền `#FFFFFF` + Điểm nhấn Cam đất `#D9534F` và Xám kim loại `#4A5568`.
> * **Quy tắc số liệu:** Số liệu đột phá in font to (Size 28 – 36pt Bold), đặt trong hộp viền nổi bật (Callout Box).
> * **Mật độ thông tin:** Trực quan hóa bằng bảng so sánh đối chuẩn và sơ đồ khối luồng dữ liệu; tuyệt đối không đưa cả đoạn văn bản dài lên slide.

---

### SLIDE 1 · BÌA BÁO CÁO (LÂM | 00:00 – 00:40)
* **Bố cục hiển thị:** Bố cục trung tâm trang trọng. Logo Học viện CNBCVT và Viện KHKT Bưu điện ở góc trên bên trái/phải.
* **Nội dung hiển thị:**
  * Tên đề tài (Font to, đậm, căn giữa): **ĐÁNH GIÁ VÀ TỐI ƯU HÓA CÁC KIẾN TRÚC RAG TRÊN NỀN TẢNG DỮ LIỆU CẤU TRÚC ĐẶC THÙ**
  * Mã số đề tài: `14-SV-2026-RIPT`
  * Nhóm sinh viên thực hiện: **Lưu Thanh Lâm** (Nhóm trưởng) • **Ngô Thế Dương** • **Nguyễn Bình Minh**
  * Giảng viên hướng dẫn: **TS. Nguyễn Mạnh Dũng**
  * Cơ sở đào tạo: Học viện Công nghệ Bưu chính Viễn thông — Hà Nội, 2026

---

### SLIDE 2 · BỐI CẢNH & VẤN NẠN ẢO GIÁC PHÁP LÝ (LÂM | 00:40 – 01:40)
* **Tiêu đề:** Nhu cầu tra cứu pháp luật & Rủi ro sai lệch của mô hình ngôn ngữ
* **Bố cục hiển thị:** Chia 3 khối đối sánh (Card Layout):
  * *Khối 1 (Thực tiễn):* Nhu cầu người dân và doanh nghiệp tra cứu quyền, nghĩa vụ, trình tự thủ tục pháp lý tăng mạnh $\rightarrow$ Đòi hỏi thông tin chính xác tuyệt đối, truy xuất đúng căn cứ kiểm chứng.
  * *Khối 2 (Giới hạn RAG):* Kiến trúc Retrieval-Augmented Generation (RAG) kết nối LLM với cơ sở tri thức bên ngoài nhưng **chưa thể triệt tiêu hoàn toàn ảo giác**.
  * *Khối 3 (Hộp cảnh báo đỏ):* Nghiên cứu của Magesh (2024) chỉ ra các mô hình AI thương mại hàng đầu vẫn gặp tỷ lệ ảo giác pháp lý **17% – 33%**. Trích dẫn sai lệch Điều-Khoản có thể làm biến đổi hoàn toàn hệ quả pháp lý của một hành vi.

---

### SLIDE 3 · ĐẶC THÙ VĂN BẢN LUẬT & KHOẢNG TRỐNG NGHIÊN CỨU (DƯƠNG | 01:40 – 02:40)
* **Tiêu đề:** Đặc thù cấu trúc văn bản luật Việt Nam & Ba khoảng trống nghiên cứu
* **Bố cục hiển thị:** Chia đôi màn hình:
  * *Cột trái (3 Đặc thù cấu trúc):*
    * **Phân cấp đa tầng:** Luật $\rightarrow$ Chương $\rightarrow$ Mục $\rightarrow$ Điều $\rightarrow$ Khoản $\rightarrow$ Điểm. Nội dung cấp con phụ thuộc tuyệt đối vào chủ thể cấp cha.
    * **Mạng lưới dẫn chiếu phức tạp:** Viện dẫn nội bộ và dẫn chiếu chéo liên văn bản dày đặc.
    * **Lệch pha từ vựng (Vocabulary Mismatch):** Truy vấn đời thường khác biệt lớn so với thuật ngữ lập pháp chuẩn tắc.
  * *Cột phải (3 Khoảng trống nghiên cứu - Research Gaps):*
    * **Gap 1:** Thiếu một khung đối chuẩn thực nghiệm có kiểm soát biến số trên dữ liệu luật Việt Nam.
    * **Gap 2:** Thiếu khảo sát thực nghiệm về tác động của phân đoạn cấu trúc vi mô so với cắt khối token thô truyền thống.
    * **Gap 3:** Các bộ chỉ số RAG tổng quát hiện nay không đo lường được tính chính xác của trích dẫn căn cứ pháp lý và chuỗi dẫn chiếu.

---

### SLIDE 4 · CƠ SỞ LÝ THUYẾT: BA TRƯỜNG PHÁI RAG CƠ SỞ (DƯƠNG | 02:40 – 03:40)
* **Tiêu đề:** Cơ sở lý thuyết — Ba trường phái RAG đối chuẩn
* **Bố cục hiển thị:** 3 cột kiến trúc trực quan có sơ đồ minh họa luồng dữ liệu:
  * *Cột 1 — Naive Vector RAG (Không gian Dense):* Sử dụng Bi-encoder nhúng câu hỏi và đoạn văn bản thành vector đa chiều, truy hồi Top-K dựa trên độ tương đồng Cosine.
  * *Cột 2 — Hybrid RAG (Dung hợp từ vựng & ngữ nghĩa):* Kết hợp tìm kiếm từ khóa chính xác BM25 và truy hồi Dense vector, dung hợp thứ hạng bằng thuật toán Reciprocal Rank Fusion (RRF), sau đó dùng Cross-Encoder để tái xếp hạng.
  * *Cột 3 — LightRAG (Đại diện GraphRAG):* Trích xuất đồ thị thực thể và quan hệ hai tầng (Low-level & High-level), hỗ trợ truy hồi ngữ cảnh kép Local và Global.
  * *Chốt chân trang:* Ba kiến trúc này được chọn làm đối tượng đối sánh cơ sở tại Giai đoạn 1 của đề tài.

---

### SLIDE 5 · HỆ THỐNG CÂU HỎI NGHIÊN CỨU (DƯƠNG | 03:40 – 04:25)
* **Tiêu đề:** Khung 4 câu hỏi nghiên cứu định hướng đề tài (RQ1 – RQ4)
* **Bố cục hiển thị:** Bảng ma trận lộ trình 4 câu hỏi tương ứng 3 giai đoạn:
  * **RQ1 (GĐ1):** Các kiến trúc RAG cơ sở (Naive, Hybrid, LightRAG) thể hiện năng lực truy hồi và độ chính xác trích dẫn như thế nào trên ngữ liệu luật Việt Nam khi áp dụng chiến lược cắt đoạn thô truyền thống?
  * **RQ2 (GĐ2):** Chiến lược phân đoạn cấu trúc vi mô (Structure-Aware Parser v2) kết hợp tiền tố bất biến và thuật toán gom điểm Article MaxP có giải quyết được nghịch lý trích dẫn và tối ưu hóa dung lượng ngữ cảnh không?
  * **RQ3 (GĐ3):** Kiến trúc đồ thị tri thức hợp nhất (Hybrid UKG 10 module) cải thiện khả năng định vị điều kiện và xử lý mệnh đề ngoại lệ pháp luật so với GraphRAG truyền thống như thế nào?
  * **RQ4 (GĐ3):** Đồ thị tri thức có khả năng giải quyết bài toán truy vết chuỗi quan hệ dẫn chiếu chéo đa bước (Multi-hop cross-reference) trong văn bản quy phạm pháp luật hay không?

---

### SLIDE 6 · THIẾT KẾ THỰC NGHIỆM & HẠ TẦNG BENCHMARK (DƯƠNG | 04:25 – 05:40)
* **Tiêu đề:** Khung kiểm chuẩn Benchmark Harness & Hai bộ dữ liệu đối soát
* **Bố cục hiển thị:** 2 khối lớn:
  * *Khối trên (Hạ tầng Harness & Adapter Pattern):*
    * Mẫu thiết kế `BaseRAGAdapter` bảo đảm chuẩn hóa đầu vào/đầu ra độc lập với từng kiến trúc.
    * Đóng băng nghiêm ngặt biến kiểm soát: GPU NVIDIA Tesla T4 | Embedding BGE-M3 (1024 dim) | Generator & Judge: GPT-4o-mini ($T=0$).
  * *Khối dưới (Hai bộ dữ liệu kiểm chuẩn do nhóm xây dựng):*
    * **Ngữ liệu cốt lõi:** Toàn văn Luật Đất đai 2024 ($2.087$ đơn vị Điều luật trong hệ thống).
    * **Benchmark A (Quy mô rộng):** $512$ câu hỏi đa dạng (kèm tập con chuẩn hóa **Tier 1 gồm 205 câu** có Ground Truth chuyên gia) $\rightarrow$ Khảo sát RQ1 và RQ2 qua $3.072$ lượt thẩm định LLM-Judge.
    * **Benchmark B (Độ sâu ngữ nghĩa):** $50$ câu hỏi phân tầng trên Chương III Luật Đất đai 2024, gán nhãn locator vi mô `LD2024:A{Điều}:K{Khoản}:D{Điểm}`, mệnh đề Điều kiện, Ngoại lệ và Chuỗi dẫn chiếu $\rightarrow$ Khảo sát RQ3 và RQ4.

---

### SLIDE 7 · GIAI ĐOẠN 1: KẾT QUẢ ĐỐI CHUẨN & NGHỊCH LÝ SỤP ĐỔ TRÍCH DẪN (LÂM | 05:40 – 07:10)
* **Tiêu đề:** Kết quả đối chuẩn Giai đoạn 1 trên Tier 1 (N = 205 câu) & Giải quyết RQ1
* **Bố cục hiển thị:** Bảng số liệu Bảng 3.4 kèm 2 ô Callout phân tích cơ chế:
  * *Bảng số liệu đối chuẩn:*
    * Naive Vector RAG: Recall 0,9561 | Context Precision 0,9659 | **Citation Accuracy: 0,3259**
    * Hybrid RAG: Recall 0,9659 | Context Precision 0,9660 | **Citation Accuracy: 0,2902**
    * LightRAG: Recall 0,9659 | Context Precision 0,8829 | **Citation Accuracy: 0,1371**
  * *Hộp đỏ nhấn mạnh:* **Nghịch lý sụp đổ trích dẫn:** Cả 3 hệ thống đều tìm trúng Điều luật ($Recall > 95\%$), nhưng độ chính xác trích dẫn chỉ đạt $\sim 30\%$, riêng LightRAG sụp đổ xuống **$13,71\%$**.
  * *Cơ chế khoa học:* Cắt đoạn thô cơ học (1.200 token) làm chặt đứt liên kết phả hệ cha-con. LLM nhận đoạn trích bị mất chủ thể Điều nên suy đoán bừa bãi.
  * *Chốt RQ1:* Các RAG cơ sở hoàn toàn bất lực trong việc trích dẫn chính xác luật Việt Nam nếu giữ nguyên phương thức cắt đoạn thô truyền thống.

---

### SLIDE 8 · GIAI ĐOẠN 2: BỘ GIẢI PHÁP PARSER V2 & THUẬT TOÁN MAXP (LÂM | 07:10 – 08:40)
* **Tiêu đề:** Giải pháp phân đoạn cấu trúc vi mô (Parser v2) & Gom điểm cực đại (Article MaxP)
* **Bố cục hiển thị:** Sơ đồ 2 nửa màn hình minh họa giải pháp:
  * *Nửa trái — Structure-Aware Parser v2:*
    * Bóc tách đệ quy văn bản luật thành **12.754 phân đoạn vi mô** cấp Khoản và Điểm.
    * Cơ chế gán nhãn tiền tố bất biến: Mỗi đoạn vi mô đều được gắn định danh tuyệt đối:  
      `[Luật Đất đai 2024 > Chương III > Điều 45 > Khoản 1 > Điểm a] Điều kiện thực hiện các quyền...`
    * Khâu Validation tự động bảo toàn 100% phả hệ và xử lý ký tự tiếng Việt đặc thù.
  * *Nửa phải — Thuật toán gom điểm cực đại Article-level MaxP:*
    * *Bài toán:* 12.754 đoạn nhỏ gây bão hòa Top-K (trả về 5 điểm thuộc cùng 1 điều).
    * *Công thức gom điểm:* $\text{Score}(\text{Article}_i) = \max_{p \in \text{Article}_i} \text{Score}(p)$.
    * *Nguyên lý vận hành:* Chỉ cần 1 phân đoạn vi mô trúng khớp, toàn bộ Điều luật đại diện được kéo lên Top đầu, sau đó hệ thống trích xuất đúng phân đoạn vi mô chứa bằng chứng để đưa vào prompt.

---

### SLIDE 9 · GIAI ĐOẠN 2: MA TRẬN ĐỐI SOÁT C1 – C6 & ĐỘT PHÁ C5 (LÂM | 08:40 – 10:20)
* **Tiêu đề:** Kết quả ma trận 6 cấu hình trên Benchmark A (N = 512 câu) & Giải quyết RQ2
* **Bố cục hiển thị:** Bảng ma trận Bảng 3.6 và 3 hộp Headline số liệu khổng lồ:
  * *Bảng số liệu 6 cấu hình (N = 512 câu | 3.072 lượt chấm):*
    * C1 (Naive BM25): Citation 0,7490 | 1.0: 72,5% | Token ~2.500
    * C2 (Naive Dense): Citation 0,4000 | 1.0: 25,4% | Token ~2.898
    * C3 (Naive Hybrid): Citation 0,3986 | 1.0: 25,6% | Token ~2.898
    * C4 (Parser BM25): Citation 0,9028 | 1.0: 89,3% | Token ~580
    * **C5 (Parser Dense): Citation 0,9902 | 1.0: 98,4% (504/512 câu) | Token ~580**
    * C6 (Parser Hybrid $\alpha=0,5$): Citation 0,9786 | 1.0: 96,3% | Token ~580
  * *Ba con số đột phá:*
    * **`0,9902` (Citation Acc C5):** Tăng $+59,02$ điểm % so với C2, $98,4\%$ câu đạt trích dẫn tuyệt đối.
    * **`-79,9%` (Tiết kiệm token):** Dung lượng giảm từ $\sim 2.898$ token xuống còn **$\sim 580$ token**.
    * **`α = 0,8` (Weighted RRF tối ưu):** Đạt Recall **0,9297** và MRR **0,8220**, khắc phục hiện tượng suy giảm hiệu quả khi cào bằng $\alpha=0,5$.
  * *Chốt RQ2:* Phân đoạn cấu trúc vi mô kết hợp MaxP xác thực hoàn toàn giả thuyết H2, giải quyết triệt để bài toán trích dẫn và tối ưu chi phí.

---

### SLIDE 10 · GIAI ĐOẠN 3: KIẾN TRÚC HYBRID UKG & MODULE 5 CAUSAL ROUTER (MINH | 10:20 – 11:30)
* **Tiêu đề:** Kiến trúc 10 Module Hybrid Parser / UKG & Bộ định tuyến ngữ nghĩa Module 5
* **Bố cục hiển thị:** Sơ đồ dòng chảy 10 Module chia 2 tầng:
  * *Tầng 1 — Đồ thị Cấu trúc vật lý (Physical Graph - M1 đến M4):* Parser v2, Validation, lưu trữ phân cấp cha-con bất biến.
  * *Tầng 2 — Đồ thị Ngữ nghĩa (Semantic Graph - M5 đến M9):*
    * **Module 5 (Semantic Router):** Ứng dụng Causal LLM **Qwen2.5-0.5B** kết hợp toán tử **Max-Fusion** logic OR:  
      $$S_{\text{fusion}} = \max(S_{\text{regex}}, S_{\text{semantic}})$$
    * Tại điểm cân bằng tối ưu $\theta = 0,85$, hệ thống đạt **Recall 96,85%**, F1 đạt đỉnh **0,8146**, loại bỏ an toàn $9,33\%$ phân đoạn rác thủ tục mà không gây đứt gãy tri thức pháp lý.
    * Khắc phục hoàn toàn "Cạm bẫy trung bình" (Mean-Pooling Trap) của các mô hình Bi-encoder thông thường (chứng minh tại Phụ lục A).
  * *Tầng 3 — AUTO_FUSION (M10):* Dung hợp đồ thị vật lý và đồ thị ngữ nghĩa khi truy vấn.

---

### SLIDE 11 · GIAI ĐOẠN 3: ĐÁNH GIÁ CHUYÊN SÂU TRÊN BENCHMARK B (MINH | 11:30 – 13:00)
* **Tiêu đề:** Kết quả thực nghiệm Benchmark B (N = 50 câu) & Giải quyết RQ3, RQ4
* **Bố cục hiển thị:** Bảng Bảng 3.18 và Bảng 3.24 đối sánh trực diện với LightRAG:
  * *Ưu thế vượt trội ở RQ3 (Bảng 18 & Bảng 24):*
    * **Article-level Recall@5:** UKG đạt **0,9184** vs LightRAG **0,7358** (**Vượt +18,26 điểm %**).
    * **MRR@5:** UKG đạt **0,8848** vs LightRAG **0,5539** (**Vượt +33,09 điểm %**).
    * **Exception Coverage (Độ phủ ngoại lệ):** UKG đạt **0,6786** vs LightRAG **0,3929** (**Vượt +28,57 điểm %**).
    * **Subject-Scope Accuracy:** UKG đạt **0,8889** vs LightRAG **0,7639** (**Vượt +12,50 điểm %**).
    * **Legal Correctness:** UKG đạt **0,8777** vs LightRAG **0,8210** (**Vượt +5,67 điểm %**).
  * *Phân tích khách quan hiện tượng Condition Coverage:* UKG đạt 0,7066 so với LightRAG 0,8421 (-13,55 đpt) do UKG định vị tập trung vào quy phạm lõi thay vì bao phủ loãng của chunk 1.200 token.
  * *Đánh giá trung thực hạn chế ở RQ4 (Bảng 23):* Reference-target Recall đạt **0,5867**; nhưng **Chain Exact Match đạt 0,0000 (0/18 câu)** do không gian đồ thị bùng nổ tổ hợp khi duyệt đa bước tự do.

---

### SLIDE 12 · TỔNG KẾT: ĐÓNG GÓI CÂU TRẢ LỜI CHO 4 CÂU HỎI NGHIÊN CỨU (MINH | 13:00 – 14:00)
* **Tiêu đề:** Tổng hợp kết quả thực nghiệm giải quyết 4 câu hỏi nghiên cứu (RQ1 – RQ4)
* **Bố cục hiển thị:** Bảng ma trận tổng hợp 4 khối đóng gói:
  * **RQ1 (Giới hạn RAG cơ sở):** Chứng minh thực nghiệm Nghịch lý trích dẫn: Recall cao ($>95\%$) nhưng Citation sụp đổ ($\sim 30\%$, LightRAG còn $13,71\%$) do cắt thô làm gãy cấu trúc phả hệ.
  * **RQ2 (Hiệu năng Parser & MaxP):** Xác thực trọn vẹn giải pháp: C5 nâng Citation lên **$0,9902$** ($98,4\%$ tuyệt đối), giảm **$79,9\%$ token**; xác định tỷ lệ dung hợp tối ưu $\alpha=0,8$.
  * **RQ3 (Năng lực đồ thị UKG):** Đồ thị tri thức hợp nhất vượt trội GraphRAG truyền thống: Recall cấp Điều đạt **$0,9184$** ($+18,26$ đpt), độ phủ ngoại lệ đạt **$0,6786$** ($+28,57$ đpt).
  * **RQ4 (Chuỗi dẫn chiếu đa bước):** Định vị tốt các nút đích liên quan ($58,67\%$), nhưng xác định rõ giới hạn tổ hợp của chuỗi hoàn chỉnh (*Exact Match = 0*), đặt nền tảng cho thuật toán duyệt đồ thị có ràng buộc.

---

### SLIDE 13 · BA ĐÓNG GÓP KHOA HỌC CHÍNH (MINH | 14:00 – 14:35)
* **Tiêu đề:** Ba đóng góp khoa học cốt lõi của đề tài
* **Bố cục hiển thị:** 3 cột đóng góp mang tính dấu ấn:
  * *Đóng góp 1 — Khung kiểm chuẩn Benchmark chuẩn mực:* Xây dựng thành công Benchmark A ($2.087$ điều, $512$ câu) và Benchmark B ($50$ câu chuyên sâu) kèm Adapter Pattern loại bỏ thiên lệch thực nghiệm.
  * *Đóng góp 2 — Giải pháp phân đoạn cấu trúc vi mô:* Bộ đôi Parser v2 và Article MaxP giải quyết triệt để sự sụp đổ trích dẫn, đạt Citation Acc $0,9902$ và tiết kiệm gần $80\%$ chi phí token.
  * *Đóng góp 3 — Kiến trúc đồ thị hợp nhất Hybrid UKG:* Hiện thực hóa mô hình 10 module kết hợp cây phân cấp vật lý và đồ thị ngữ nghĩa, chứng minh ưu thế vượt trội khi xử lý ngoại lệ và phạm vi chủ thể pháp luật.

---

### SLIDE 14 · HƯỚNG PHÁT TRIỂN & KẾT LUẬN (MINH | 14:35 – 15:00)
* **Tiêu đề:** Hướng nghiên cứu tiếp theo & Lời cảm ơn
* **Bố cục hiển thị:**
  * *3 Hướng phát triển:* (1) Mở rộng Parser sang Nghị định, Thông tư; (2) Tự động hóa cập nhật tri thức khi luật sửa đổi; (3) Hoàn thiện thuật toán duyệt đồ thị có định hướng (Constrained Graph Traversal) để khép kín chuỗi dẫn chiếu đa bước.
  * *Phần cảm ơn trang trọng:* "Trân trọng cảm ơn Quý Thầy Cô trong Hội đồng khoa học đã chú ý lắng nghe! Kính mời Hội đồng đặt câu hỏi (Q&A)."

---
---

# PHẦN 2: KỊCH BẢN LỜI THOẠI HỌC THUẬT CHUYÊN SÂU 15 PHÚT (FULL SPOKEN SCRIPT)

---

### [00:00 – 01:40] · CHẶNG 1: LƯU THANH LÂM (MỞ MÀN & ĐẶT VẤN ĐỀ)

**[Slide 1 — Bìa báo cáo · 00:00]**
> *"Kính thưa Quý Thầy Cô trong Hội đồng khoa học!  
> Em tên là **Lưu Thanh Lâm**, đại diện nhóm nghiên cứu gồm ba thành viên: em, bạn **Ngô Thế Dương** và bạn **Nguyễn Bình Minh**. Dưới sự hướng dẫn khoa học tận tình của **Tiến sĩ Nguyễn Mạnh Dũng**, hôm nay nhóm chúng em xin phép được báo cáo kết quả đề tài nghiên cứu khoa học:  
> **'Đánh giá và tối ưu hóa các kiến trúc RAG trên nền tảng dữ liệu cấu trúc đặc thù'**.*
>
> *Đề tài tập trung giải quyết bài toán cốt lõi: Làm thế nào để các hệ thống truy hồi và tạo sinh văn bản hiện đại có thể trích dẫn chính xác tuyệt đối các căn cứ pháp luật Việt Nam theo từng Điều, Khoản, Điểm mà không làm bùng nổ chi phí tính toán."*

**[Slide 2 — Bối cảnh & Ảo giác pháp lý · 00:40]**
> *"Kính thưa Hội đồng, trong kỷ nguyên số hóa, nhu cầu tra cứu quyền, nghĩa vụ và quy trình thủ tục pháp lý của người dân cũng như doanh nghiệp đang ngày một gia tăng. Lĩnh vực pháp luật có một đặc thù bất biến: Mọi câu trả lời bắt buộc phải có căn cứ kiểm chứng xác thực và chính xác tuyệt đối.  
> 
> Mặc dù kiến trúc RAG kết hợp mô hình ngôn ngữ lớn với cơ sở dữ liệu bên ngoài đã giúp giảm thiểu đáng kể sự bịa đặt thông tin, nhưng các nghiên cứu thực nghiệm quốc tế gần đây, tiêu biểu như công bố của Magesh năm 2024, đã chỉ ra rằng các hệ thống AI thương mại hàng đầu vẫn gặp tỷ lệ ảo giác pháp lý từ 17% đến 33%.  
> Trong đời sống pháp lý, việc một mô hình trích dẫn nhầm một Điều, bỏ sót một Khoản hoặc nhầm lẫn một ngoại lệ tại một Điểm có thể làm thay đổi hoàn toàn quyền lợi và nghĩa vụ của các chủ thể.  
> 
> Vậy nguyên nhân gốc rễ nào khiến các mô hình RAG hiện nay gặp khó khăn trước văn bản luật Việt Nam? Để làm rõ đặc thù dữ liệu và hạ tầng nghiên cứu, sau đây em xin trân trọng nhường lời cho bạn **Ngô Thế Dương**."*  
*(Lâm chuyển micro và clicker cho Dương, bước lùi sang bên cạnh).*

---

### [01:40 – 05:40] · CHẶNG 2: NGÔ THẾ DƯƠNG (ĐẶC THÙ, LÝ THUYẾT & HẠ TẦNG BENCHMARK)

**[Slide 3 — Đặc thù luật & Khoảng trống · 01:40]**
> *"Em xin cảm ơn bạn Lâm. Kính thưa Quý Thầy Cô, qua quá trình khảo sát văn bản quy phạm pháp luật Việt Nam, nhóm nhận diện ba đặc thù cấu trúc mang tính chi phối:  
> Thứ nhất là cấu trúc phân cấp đa tầng nghiêm ngặt: từ Luật xuống Chương, Mục, Điều, Khoản và Điểm. Nội dung quy định tại một Điểm luôn phụ thuộc hoàn toàn vào chủ thể và điều kiện được xác lập ở cấp cha.  
> Thứ hai là mạng lưới dẫn chiếu phức tạp, gồm cả viện dẫn nội bộ giữa các điều luật và dẫn chiếu chéo liên văn bản giữa Luật với các Nghị định, Thông tư.  
> Và thứ ba là sự lệch pha ngôn ngữ rất lớn giữa câu hỏi tự nhiên bằng khẩu ngữ của người dân với từ vựng lập pháp quy chuẩn.  
> 
> Từ ba đặc thù trên, nhóm xác định ba khoảng trống nghiên cứu chính:  
> Một là sự thiếu vắng một khung đối chuẩn thực nghiệm công bằng có kiểm soát biến số;  
> Hai là chưa có công trình nào đánh giá định lượng tác động của việc phân đoạn cấu trúc vi mô so với việc cắt khối token thô truyền thống;  
> Và ba là các bộ thước đo RAG tổng quát hiện nay không đánh giá được khả năng định vị chính xác vị trí pháp lý và chuỗi dẫn chiếu."*

**[Slide 4 — Cơ sở lý thuyết: Ba trường phái RAG · 02:40]**
> *"Để giải quyết các khoảng trống đó, về mặt cơ sở lý thuyết, nghiên cứu của nhóm tập trung khảo sát ba trường phái RAG đại diện hiện nay trên thế giới:  
> Thứ nhất, **Naive Vector RAG** sử dụng mô hình nhúng Bi-encoder để biểu diễn câu hỏi và tài liệu trong không gian vector đa chiều, sau đó truy hồi Top-K dựa trên độ tương đồng Cosine.  
> Thứ hai, **Hybrid RAG** kết hợp năng lực tìm kiếm từ khóa chính xác của BM25 với khả năng nắm bắt ngữ nghĩa của Dense vector, sử dụng thuật toán Reciprocal Rank Fusion (RRF) để dung hợp kết quả và mô hình Cross-Encoder để tái xếp hạng.  
> Thứ ba, **LightRAG** đại diện cho trường phái GraphRAG, khai thác biểu diễn đồ thị thực thể và quan hệ nhằm hỗ trợ suy luận ngữ cảnh rộng và kết nối các tri thức rải rác.  
> 
> Ba kiến trúc này được nhóm lựa chọn làm đối tượng đối sánh cơ sở ở Giai đoạn 1, trước khi nhóm tiến hành các đề xuất tối ưu hóa chuyên sâu."*

**[Slide 5 — Hệ thống 4 Câu hỏi nghiên cứu RQ1 – RQ4 · 03:40]**
> *"Nhằm định hướng toàn bộ quá trình thực nghiệm, nhóm xây dựng khung nghiên cứu gồm bốn câu hỏi khoa học từ RQ1 đến RQ4:  
> **RQ1** khảo sát hiệu năng thực tế và giới hạn trích dẫn của ba kiến trúc RAG cơ sở trên dữ liệu luật Việt Nam khi cắt đoạn thô.  
> **RQ2** đánh giá tác động của giải pháp phân đoạn cấu trúc vi mô Parser v2 kết hợp thuật toán gom điểm Article MaxP đối với độ chính xác trích dẫn và dung lượng ngữ cảnh.  
> **RQ3** kiểm chứng năng lực định vị điều kiện và xử lý ngoại lệ pháp luật của đồ thị tri thức hợp nhất UKG so với GraphRAG truyền thống.  
> Và **RQ4** đo lường khả năng tái dựng chuỗi quan hệ dẫn chiếu chéo đa bước của hệ thống đồ thị.  
> Bốn câu hỏi này sẽ được nhóm lần lượt trả lời qua ba giai đoạn thực nghiệm."*

**[Slide 6 — Thiết kế thực nghiệm & Hạ tầng Benchmark · 04:25]**
> *"Kính thưa Hội đồng, để đảm bảo tính khách quan khoa học cao nhất, nhóm thiết kế khung kiểm chuẩn **Benchmark Harness** áp dụng mẫu kiến trúc Adapter Pattern. Tất cả các kiến trúc đều được đóng gói độc lập và kết nối qua giao diện chuẩn `BaseRAGAdapter`. Toàn bộ các biến ngoại lai được đóng băng cố định: cùng chạy trên một GPU NVIDIA Tesla T4, cùng sử dụng mô hình nhúng BGE-M3 1024 chiều, và mô hình ngôn ngữ GPT-4o-mini qua API với nhiệt độ bằng 0. Quá trình đánh giá được thực hiện tự động bằng phương pháp LLM-as-a-Judge.  
> 
> Về mặt ngữ liệu, nhóm sử dụng toàn văn Luật Đất đai 2024 gồm 2.087 đơn vị điều luật trong toàn hệ thống. Nhóm đã tự thiết kế hai bộ kiểm chuẩn độc lập:  
> **Benchmark A** gồm 512 câu hỏi thực tế đa dạng, trong đó nhóm xây dựng tập con đối chuẩn công bằng **Tier 1 gồm 205 câu hỏi** có Ground Truth chuyên gia chuẩn hóa tuyệt đối để đo lường RQ1 và RQ2 qua 3.072 lượt chấm điểm độc lập.  
> **Benchmark B** gồm 50 câu hỏi phân tầng chuyên sâu tại Chương III Luật Đất đai, được gán nhãn định vị vi mô đến từng Khoản, Điểm, Điều kiện, Ngoại lệ và Chuỗi dẫn chiếu để đo lường RQ3 và RQ4.  
> 
> Sau đây, kết quả thực nghiệm Giai đoạn 1 đã bộc lộ nghịch lý gì và giải pháp Giai đoạn 2 ra sao, em xin trân trọng kính mời bạn **Lưu Thanh Lâm** tiếp tục trình bày."*  
*(Dương chuyển giao micro cho Lâm).*

---

### [05:40 – 10:20] · CHẶNG 3: LƯU THANH LÂM (GIAI ĐOẠN 1 NGHỊCH LÝ & GIAI ĐOẠN 2 ĐỘT PHÁ)

**[Slide 7 — Giai đoạn 1: Nghịch lý sụp đổ trích dẫn · 05:40]**
> *"Em xin cảm ơn bạn Dương. Kính thưa Hội đồng khoa học, khi tiến hành đối soát công bằng ba kiến trúc RAG cơ sở trên tập Tier 1 gồm 205 câu hỏi, nhóm chúng em đã phát hiện một hiện tượng thực nghiệm rất đáng chú ý — chúng em định danh là **Nghịch lý sụp đổ trích dẫn (The Citation Collapse Paradox)**:  
> 
> Nhìn vào Bảng 3.4 trên màn hình, cả ba hệ thống đều thể hiện năng lực tìm kiếm tài liệu rất xuất sắc: Recall@5 đều đạt từ 95,6% đến 96,6%, độ khớp ngữ cảnh Context Precision đạt trên 0,96. Tức là hệ thống hầu như luôn đưa được Điều luật đúng vào trong ngữ cảnh!  
> Thế nhưng, khi chấm điểm độ chính xác trích dẫn căn cứ pháp lý Citation Accuracy, Naive Vector RAG chỉ đạt **32,59%** và Hybrid RAG chỉ đạt **29,02%**.  
> Đặc biệt nghiêm trọng, mô hình đồ thị LightRAG dù đạt Recall tới 96,59% nhưng độ chính xác trích dẫn lại sụp đổ xuống chỉ còn **13,71%**.  
> 
> **Cơ sở khoa học giải mã nghịch lý này là gì?**  
> Khi kiểm toán dữ liệu ngữ cảnh, nhóm nhận thấy các kiến trúc truyền thống áp dụng chiến lược cắt đoạn thô cơ học 1.200 token. Việc cắt ngang một văn bản luật phân cấp đa tầng đã làm chặt đứt mối liên kết phả hệ cha-con. Khi các phân đoạn bị chia cắt đưa vào prompt, mô hình ngôn ngữ lớn bị mất hoàn toàn thông tin chủ thể ở cấp Điều, dẫn đến hiện tượng trích dẫn nhầm lẫn điều khoản hoặc suy đoán vô căn cứ.  
> Kết quả này trả lời dứt khoát cho **Câu hỏi nghiên cứu RQ1**: Các kiến trúc RAG cơ sở hiện nay hoàn toàn bất lực trong việc đảm bảo trích dẫn chính xác luật Việt Nam nếu giữ nguyên phương pháp cắt đoạn thô truyền thống."*

**[Slide 8 — Giai đoạn 2: Parser v2 & Article MaxP · 07:10]**
> *"Để khắc phục triệt để hiện tượng đứt gãy phả hệ, bước sang Giai đoạn 2, nhóm đề xuất bộ giải pháp cấu trúc gồm hai thành phần cốt lõi:  
> Thứ nhất là bộ phân tích cú pháp **Structure-Aware Parser v2**. Thay vì cắt đoạn theo số lượng token thô, Parser v2 bóc tách đệ quy văn bản luật theo đúng cấu trúc logic lập pháp, chuyển đổi 2.087 Điều luật thành **12.754 phân đoạn vi mô** cấp Khoản và Điểm. Điểm cải tiến mang tính bản lề là mỗi phân đoạn vi mô đều được gắn kèm một **tiền tố phân cấp bất biến**, ví dụ: `[Luật Đất đai 2024 > Chương III > Điều 45 > Khoản 1 > Điểm a]`. Nhờ đó, dù phân đoạn bị trích xuất độc lập, LLM vẫn nắm bắt trọn vẹn chủ thể cha và ngữ cảnh phân cấp.  
> 
> Tuy nhiên, việc chia nhỏ thành hơn 12 nghìn đoạn vi mô lập tức gây ra hiện tượng 'bội thực cục bộ' (Local Saturation): Top-5 đoạn trả về có thể cùng thuộc về một Điều luật duy nhất. Do đó, nhóm xây dựng thuật toán gom điểm cực đại **Article-level MaxP**.  
> Nguyên lý toán học là: Điểm số của một Điều luật bằng giá trị lớn nhất trong số điểm của các phân đoạn vi mô thuộc Điều luật đó. Chỉ cần một Điểm luật khớp ngữ nghĩa với câu hỏi, toàn bộ Điều luật đại diện sẽ nhận điểm cực đại và được kéo lên đầu danh sách, sau đó hệ thống trích xuất đúng phân đoạn vi mô chứa bằng chứng để đưa vào prompt."*

**[Slide 9 — Giai đoạn 2: Ma trận C1–C6 & Đột phá C5 · 08:40]**
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

### [10:20 – 15:00] · CHẶNG 4: NGUYỄN BÌNH MINH (ĐỒ THỊ UKG, ĐA BƯỚC & KẾT LUẬN)

**[Slide 10 — Giai đoạn 3: Kiến trúc Hybrid UKG & Module 5 · 10:20]**
> *"Em xin cảm ơn bạn Lâm. Kính thưa Quý Thầy Cô trong Hội đồng, để xử lý các truy vấn pháp lý đa bước, bước sang Giai đoạn 3, nhóm đề xuất kiến trúc toàn diện **Hybrid Parser / UKG gồm 10 Module** phân tách thành hai tầng rõ rệt:  
> Tầng 1 là Đồ thị Cấu trúc vật lý từ Module 1 đến Module 4, lưu trữ toàn vẹn cây phân cấp văn bản.  
> Tầng 2 là Đồ thị Ngữ nghĩa từ Module 5 đến Module 9, trích xuất các quan hệ quyền, nghĩa vụ và chế tài.  
> 
> Trọng tâm đột phá nằm ở **Module 5 (Semantic Router)**. Để lọc các văn bản thủ tục mà không làm đứt gãy tri thức pháp lý, nhóm ứng dụng mô hình ngôn ngữ nhân quả siêu nhẹ **Qwen2.5-0.5B** kết hợp toán tử **Max-Fusion** logic OR giữa tín hiệu Regex và tín hiệu nhúng ngữ nghĩa.  
> Khảo sát thực nghiệm độc lập tại Phụ lục A chỉ ra rằng các mô hình Bi-encoder truyền thống bị mắc kẹt trong 'Cạm bẫy trung bình' (Mean-Pooling Trap), làm triệt tiêu tín hiệu phân đoạn ngắn. Ngược lại, cơ chế Causal Attention của Qwen2.5-0.5B bảo toàn trọn vẹn ngữ nghĩa mệnh đề.  
> Tại điểm cân bằng tối ưu $\theta = 0,85$, hệ thống đạt độ bao phủ **Recall 96,85%**, F1 đạt đỉnh **0,8146**, loại bỏ an toàn 9,33% lượng phân đoạn rác thủ tục chuyển sang Module 6 mà vẫn bảo vệ tuyệt đối tính bất biến của đồ thị."*

**[Slide 11 — Giai đoạn 3: Thực nghiệm Benchmark B · 11:30]**
> *"Nhóm kiểm chứng kiến trúc đề xuất trên **Benchmark B** gồm 50 câu hỏi phân tầng tại Chương III Luật Đất đai 2024 trong thế đối đầu trực tiếp với LightRAG.  
> Kết quả thực nghiệm tại Bảng 3.18 và Bảng 3.24 đã làm sáng tỏ **Câu hỏi nghiên cứu RQ3 và RQ4**:  
> 
> Về mặt tích cực giải quyết **RQ3**:  
> Thứ nhất, về truy hồi cấp Điều, Hybrid Parser/UKG đạt Recall@5 **0,9184**, **vượt LightRAG 18,26 điểm phần trăm** (0,7358); chỉ số MRR@5 đạt **0,8848**, **vượt trội 33,09 điểm phần trăm**.  
> Thứ hai, về chất lượng nội dung, UKG đạt điểm tính chính xác pháp lý Legal Correctness **0,8777** (so với 0,8210 của LightRAG), và độ chính xác phạm vi chủ thể đạt **0,8889** (so với 0,7639).  
> Đặc biệt, ở chỉ số **Độ phủ Ngoại lệ (Exception Coverage)**, UKG đạt **0,6786**, **vượt xa LightRAG tới 28,57 điểm phần trăm** (0,3929). Ưu thế này có được nhờ đồ thị ngữ nghĩa đã bóc tách chính xác các nút ngoại lệ 'trừ trường hợp...', vốn thường bị các mô hình GraphRAG truyền thống bỏ qua.  
> 
> Nhóm cũng ghi nhận một hiện tượng khách quan: LightRAG đạt Condition Coverage cao hơn UKG (0,8421 so với 0,7066) vì LightRAG gom các khối văn bản thô 1.200 token lớn nên vô tình bao hàm cả các câu điều kiện chung, nhưng việc này lại dẫn đến độ bao phủ loãng và làm tăng ảo giác.  
> 
> Về mặt hạn chế giải quyết **RQ4**: Đối với bài toán truy vết dẫn chiếu chéo, hệ thống đạt độ thu hồi nút đích Reference-target Recall **58,67%**. Tuy nhiên, chỉ số khôi phục chuỗi hoàn chỉnh **Chain Exact Match đạt 0,0000 (0/18 câu)**.  
> Với tinh thần trung thực khoa học, nhóm xác định nguyên nhân là do không gian tìm kiếm trên đồ thị tri thức pháp lý dày đặc gặp hiện tượng bùng nổ tổ hợp, hệ thống mới chỉ tìm được các cạnh đơn lẻ mà chưa xâu chuỗi được toàn vẹn toàn bộ hành trình đa bước."*

**[Slide 12 — Tổng kết: Đóng gói 4 Câu hỏi nghiên cứu · 13:00]**
> *"Kính thưa Hội đồng khoa học, để tổng hợp lại toàn bộ công trình, bốn câu hỏi nghiên cứu ban đầu đã được nhóm giải quyết trọn vẹn bằng thực nghiệm:  
> Với **RQ1**, nhóm chứng minh thực nghiệm Nghịch lý trích dẫn: Các RAG cơ sở đạt Recall cao trên 95% nhưng sụp đổ trích dẫn xuống ~30% (LightRAG còn 13,71%) do cắt thô làm gãy cấu trúc phả hệ.  
> Với **RQ2**, nhóm xác thực giải pháp Parser v2 và MaxP giải quyết triệt để nghịch lý trên, nâng Citation Accuracy lên **0,9902** (98,4% tuyệt đối) và tiết kiệm **79,9% token**, xác định ngưỡng dung hợp tối ưu $\alpha=0,8$.  
> Với **RQ3**, kiến trúc Hybrid UKG chứng minh ưu thế vượt trội khi nâng Recall cấp Điều thêm 18,26 điểm phần trăm và nâng độ phủ ngoại lệ thêm **28,57 điểm phần trăm**.  
> Và với **RQ4**, nhóm xác định rõ ranh giới thực nghiệm của bài toán dẫn chiếu đa bước, chỉ ra giới hạn tổ hợp của chuỗi xích hoàn chỉnh làm tiền đề phát triển tiếp theo."*

**[Slide 13 — Ba đóng góp khoa học chính · 14:00]**
> *"Từ những kết quả trên, đề tài mang lại ba đóng góp khoa học cốt lõi:  
> Một là xây dựng thành công hai bộ Benchmark A và Benchmark B chuẩn mực kèm khung Adapter Pattern loại bỏ hoàn toàn thiên lệch thực nghiệm.  
> Hai là đề xuất giải pháp phối hợp giữa Parser v2 và thuật toán MaxP, giải quyết tận gốc sự sụt giảm trích dẫn pháp lý và tối ưu hóa tài nguyên tính toán.  
> Ba là hiện thực hóa thành công kiến trúc 10 module kết hợp cây phân cấp vật lý và đồ thị ngữ nghĩa UKG, chứng minh ưu thế vượt trội trong việc xử lý các quy phạm ngoại lệ và chủ thể pháp lý phức tạp."*

**[Slide 14 — Hướng phát triển & Kết luận · 14:35]**
> *"Trong thời gian tới, nhóm hướng đến ba mục tiêu tiếp theo: mở rộng bộ bóc tách cấu trúc sang các văn bản dưới luật như Nghị định, Thông tư; tự động hóa việc cập nhật hiệu lực khi văn bản sửa đổi; và hoàn thiện thuật toán duyệt đồ thị có ràng buộc (Constrained Graph Traversal) để khép kín chuỗi dẫn chiếu chéo.  
> 
> Thay mặt nhóm nghiên cứu, chúng em xin trân trọng cảm ơn Thầy Cô trong Hội đồng khoa học đã chú ý lắng nghe. Nhóm chúng em rất mong nhận được những ý kiến đóng góp quý báu từ Quý Thầy Cô và xin sẵn sàng bước vào phần Hỏi và Đáp!"*  
*(Cả ba thành viên Lâm, Dương, Minh cùng đứng nghiêm trang, cúi đầu chào Hội đồng).*

---
---

# PHẦN 3: BẢN PHAO THỰC CHIẾN - TỪ KHÓA NEO & CỬ CHỈ SÂN KHẤU (ANCHOR CHEAT SHEET)

> **Mục đích:** Tài liệu cầm tay phục vụ tập dượt thực chiến. Mỗi slide chỉ cần nhớ 2 – 3 từ khóa neo, điểm chỉ tay laser và câu chốt trigger cue để chuyển giao micro mượt mà.

| Slide | Người nói | Thời lượng | Từ khóa neo chuyên sâu | Hành động / Điểm chỉ laser trên Slide | Câu chốt chuyển mic (Trigger Cue) |
| :---: | :---: | :---: | :--- | :--- | :--- |
| **1** | **Lâm** | 40s | • Chào Hội đồng, giới thiệu 3 thành viên, GVHD<br>• Đề tài: RAG trên dữ liệu cấu trúc đặc thù | Đứng giữa bục, mắt bao quát Hội đồng, phong thái tự tin | *(Nói liền mạch sang Slide 2)* |
| **2** | **Lâm** | 60s | • Nhu cầu tra cứu pháp luật chính xác tuyệt đối<br>• RAG ảo giác 17% – 33% (Magesh 2024)<br>• Sai lệch điều khoản làm đổi hệ quả pháp lý | Chỉ laser vào **Hộp đỏ cảnh báo 17% – 33%** | *"Sau đây xin mời bạn Ngô Thế Dương trình bày đặc thù dữ liệu và hạ tầng nghiên cứu."* |
| **3** | **Dương** | 60s | • 3 đặc thù: Phân cấp đa tầng, Dẫn chiếu, Lệch pha từ vựng<br>• 3 Gap: Khung benchmark, Phân đoạn vi mô, Thước đo trích dẫn | Quét laser lần lượt qua **3 khối đặc thù** và **3 khối Gap** | *(Nói liền mạch sang Slide 4)* |
| **4** | **Dương** | 60s | • 3 trường phái RAG cơ sở: Naive Vector (Cosine), Hybrid (BM25+Dense+RRF), LightRAG (Graph) | Chỉ laser vào **3 cột kiến trúc RAG** | *(Nói liền mạch sang Slide 5)* |
| **5** | **Dương** | 45s | • Bung 4 câu hỏi nghiên cứu định hướng 3 giai đoạn: RQ1 (GĐ1), RQ2 (GĐ2), RQ3 & RQ4 (GĐ3) | Chỉ laser vào **bảng ma trận 4 RQ** | *(Nói liền mạch sang Slide 6)* |
| **6** | **Dương** | 75s | • Benchmark Harness + Adapter Pattern, đóng băng GPU T4, BGE-M3, GPT-4o-mini T=0<br>• Ngữ liệu 2.087 điều<br>• Benchmark A (512 câu, Tier 1 205 câu) & Benchmark B (50 câu) | Chỉ laser vào **hộp đóng băng kiểm soát** và **hộp 2 bộ Benchmark** | *"Kết quả GĐ1 và đột phá GĐ2 ra sao, xin mời bạn Lưu Thanh Lâm tiếp tục trình bày."* |
| **7** | **Lâm** | 90s | • **[Slide đinh] Nghịch lý Giai đoạn 1 (RQ1)**<br>• Recall $>95\%$ nhưng Citation chỉ $\sim 30\%$<br>• LightRAG sụp đổ còn **13,71%** do cắt thô 1.200 token làm đứt gãy phả hệ cha-con | Chỉ laser dứt khoát vào **13,71% màu đỏ** và **32,59%** | *(Nói liền mạch sang Slide 8)* |
| **8** | **Lâm** | 90s | • Parser v2: 12.754 đoạn vi mô kèm tiền tố bất biến [Luật > Chương > Điều > Khoản > Điểm]<br>• Bội thực cục bộ $\rightarrow$ Article MaxP gom điểm cực đại | Chỉ laser vào **tiền tố bất biến ví dụ** và **công thức Article MaxP** | *(Nói liền mạch sang Slide 9)* |
| **9** | **Lâm** | 100s | • **[Slide đinh] Đột phá C5 (RQ2)**<br>• Citation Acc vọt lên **0,9902** (98,4% đạt 1.0, 504/512 câu)<br>• Tiết kiệm **79,9% token** (~580t)<br>• Weighted RRF quét tối ưu tại **$\alpha = 0,8$** | Chỉ laser vào 3 con số Headline lớn: **0,9902**, **-79,9%**, **$\alpha=0,8$** | *"Trước câu hỏi đa bước và quan hệ dẫn chiếu, UKG giải quyết ra sao? Xin mời bạn Minh."* |
| **10** | **Minh** | 70s | • Kiến trúc UKG 10 module: Tầng vật lý (M1-M4) + Tầng ngữ nghĩa (M5-M9)<br>• Module 5 Causal Router Qwen2.5-0.5B + Max-Fusion logic OR tại $\theta=0,85$ (Recall 96,85%) | Chỉ laser vào sơ đồ 2 tầng và khối **Module 5** | *(Nói liền mạch sang Slide 11)* |
| **11** | **Minh** | 90s | • **[Slide đinh] Benchmark B (RQ3 & RQ4)**<br>• RQ3: Recall cấp Điều **0,9184** (+18,26 đpt), Exception Coverage **0,6786** (+28,57 đpt)<br>• RQ4: Thừa nhận trung thực Chain Exact Match = 0,0000 do bùng nổ tổ hợp đồ thị dày | Chỉ laser vào số **0,9184**, số **+28,57 đpt**, sau đó chỉ sang **0,0000** | *(Nói liền mạch sang Slide 12)* |
| **12** | **Minh** | 60s | • **[Slide đinh] Bo tròn 4 RQ ở cuối bài**<br>• RQ1: Sụp đổ trích dẫn<br>• RQ2: Parser v2 + MaxP thành công<br>• RQ3: Đồ thị UKG vượt trội ngoại lệ<br>• RQ4: Giới hạn chuỗi dẫn chiếu | Quét laser lần lượt qua **4 hàng tổng kết RQ** | *(Nói liền mạch sang Slide 13)* |
| **13** | **Minh** | 35s | • 3 Đóng góp khoa học cốt lõi: Khung Benchmark chuẩn; Giải pháp phân đoạn cấu trúc; Kiến trúc đồ thị hợp nhất UKG | Chỉ laser lần lượt vào **3 cột đóng góp** | *(Nói liền mạch sang Slide 14)* |
| **14** | **Minh** | 25s | • 3 Hướng phát triển: Nghị định, Thông tư; Cập nhật hiệu lực; Duyệt đồ thị có ràng buộc<br>• Lời cảm ơn và mời Q&A | Nhìn thẳng Hội đồng, mỉm cười trang trọng | Cả 3 thành viên cùng đứng nghiêm, cúi đầu chào |
