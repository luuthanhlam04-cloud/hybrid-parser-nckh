# BỘ TÀI LIỆU KỊCH BẢN VÀ THIẾT KẾ THUYẾT TRÌNH BẢO VỆ NCKH (15 PHÚT)
**Đề tài:** Đánh giá và tối ưu hóa các kiến trúc RAG trên nền tảng dữ liệu cấu trúc đặc thù  
**Mã số:** 14-SV-2026-RIPT | **Nhóm thực hiện:** Lưu Thanh Lâm (Nhóm trưởng), Ngô Thế Dương, Nguyễn Bình Minh  
**GVHD:** TS. Nguyễn Mạnh Dũng | **Đơn vị:** Viện Khoa học Kỹ thuật Bưu điện - Học viện Công nghệ Bưu chính Viễn thông

---

# MỤC LỤC BỘ TÀI LIỆU
1. **PHẦN 1: BẢN ĐỀ XUẤT CẤU TRÚC VÀ THIẾT KẾ HIỂN THỊ 20 SLIDE**  
   *(Chi tiết bố cục, nội dung text, số liệu hiển thị, hình ảnh/biểu đồ, điểm nhấn thị giác).*
2. **PHẦN 2: KỊCH BẢN LỜI THOẠI HỌC THUẬT CHUẨN 15 PHÚT (FULL SPOKEN SCRIPT)**  
   *(Thuần văn nói khoa học, điềm đạm, khách quan, phân vai chi tiết Lâm - Dương - Lâm - Minh kèm mốc bấm giờ 00:00 - 15:00).*
3. **PHẦN 3: BẢN PHAO THỰC CHIẾN - TỪ KHÓA NEO VÀ HƯỚNG DẪN TRÌNH BÀY (ANCHOR CHEAT SHEET)**  
   *(Tóm gọn 2-3 từ khóa chính mỗi slide, hành động chỉ tay vào số liệu, câu trigger chuyển mic để không bao giờ bị quên bài).*

---
---

# PHẦN 1: BẢN ĐỀ XUẤT CẤU TRÚC VÀ THIẾT KẾ HIỂN THỊ 20 SLIDE

> **Nguyên tắc thiết kế trực quan:**
> * Màu sắc chủ đạo: Xanh đậm học thuật (Navy/PTIT Blue) + Trắng + Điểm nhấn Cam đất/Xám bạc.
> * Quy tắc số liệu: Số liệu quan trọng font to (Size 28-36pt Bold), có hộp viền nổi bật.
> * Chữ trong slide: Tối đa 4-5 dòng mỗi khối, gạch đầu dòng ngắn, không nhồi nhét văn bản thành đoạn dài.

---

### SLIDE 1 · BÌA BÁO CÁO (LÂM)
* **Bố cục hiển thị:** Bố cục trung tâm trang trọng. Logo Học viện và Viện KHKT Bưu điện ở góc trên.
* **Nội dung hiển thị:**
  * Tiêu đề đề tài (Font to, đậm, căn giữa): **ĐÁNH GIÁ VÀ TỐI ƯU HÓA CÁC KIẾN TRÚC RAG TRÊN NỀN TẢNG DỮ LIỆU CẤU TRÚC ĐẶC THÙ**
  * Mã số đề tài: `14-SV-2026-RIPT` | Nhóm ngành: Công nghệ thông tin
  * Sinh viên thực hiện: **Lưu Thanh Lâm** (Nhóm trưởng) • **Nguyễn Bình Minh** • **Ngô Thế Dương**
  * Giảng viên hướng dẫn: **TS. Nguyễn Mạnh Dũng**
  * Thời gian & Địa điểm: Hà Nội, Năm 2026

---

### SLIDE 2 · MỞ ĐẦU & BỐI CẢNH (DƯƠNG)
* **Tiêu đề:** Nhu cầu tra cứu pháp luật & Rủi ro sai lệch của RAG
* **Bố cục hiển thị:** Chia 3 cột trực quan (Card Layout):
  * *Cột 1 (Thực tiễn):* Nhu cầu tra cứu quyền, nghĩa vụ, chế tài pháp lý tăng cao $\rightarrow$ Đòi hỏi thông tin chính xác tuyệt đối, truy xuất đúng căn cứ.
  * *Cột 2 (Hạn chế RAG):* RAG kết hợp LLM với dữ liệu ngoài nhưng **chưa triệt tiêu được ảo giác**.
  * *Cột 3 (Rủi ro pháp lý - Hộp đỏ cảnh báo):* Nghiên cứu của Magesh (2024) chỉ ra AI thương mại gặp tỷ lệ ảo giác **17% – 33%**. Trích dẫn sai lệch Điều-Khoản có thể làm thay đổi hoàn toàn hệ quả pháp lý.

---

### SLIDE 3 · ĐẶC THÙ VĂN BẢN QUY PHẠM PHÁP LUẬT (DƯƠNG)
* **Tiêu đề:** Ba đặc điểm cấu trúc cốt lõi của văn bản luật Việt Nam
* **Bố cục hiển thị:** 3 khối hộp nằm ngang có mũi tên liên kết phân cấp:
  * *Khối 1 - Cấu trúc phân cấp đa tầng:* Luật > Chương > Mục > Điều > Khoản > Điểm. (Nội dung cấp con phụ thuộc tuyệt đối vào chủ thể cấp cha).
  * *Khối 2 - Mạng lưới dẫn chiếu phức tạp:* Viện dẫn nội bộ ("theo quy định tại khoản 2") hoặc liên văn bản ("theo quy định của Luật Đất đai").
  * *Khối 3 - Lệch pha ngôn ngữ (Vocabulary Mismatch):* Ngôn ngữ truy vấn thông thường của người dân khác biệt xa so với từ vựng chuyên ngành lập pháp.

---

### SLIDE 4 · KHOẢNG TRỐNG NGHIÊN CỨU (DƯƠNG)
* **Tiêu đề:** Ba khoảng trống nghiên cứu chính (Research Gaps)
* **Bố cục hiển thị:** 3 khối hộp đối sánh có icon "Gap":
  * *Gap 1:* **Thiếu khung đối chuẩn thống nhất:** Các nghiên cứu trước dùng mô hình nhúng và chiến lược chunking khác nhau, gây nhiễu khi so sánh kiến trúc.
  * *Gap 2:* **Thiếu khảo sát phân đoạn cấu trúc vi mô:** Chưa có đánh giá thực nghiệm toàn diện về việc phân đoạn theo Điều-Khoản-Điểm so với cắt token thô truyền thống.
  * *Gap 3:* **Thiếu thước đo căn cứ pháp lý & chuỗi dẫn chiếu:** Các metric tổng quát (RAGAS) không đo được độ chính xác trích dẫn cấp Khoản/Điểm và khả năng tái dựng đường dẫn dẫn chiếu.

---

### SLIDE 5 · MỤC TIÊU & NHIỆM VỤ NGHIÊN CỨU (DƯƠNG) - [SLIDE LƯỚT]
* **Tiêu đề:** Mục tiêu tổng quát & 5 Nhiệm vụ nghiên cứu
* **Bố cục hiển thị:** 
  * *Hộp trên:* Mục tiêu tổng quát (Nghiên cứu, đánh giá và tối ưu hóa ảnh hưởng của phân đoạn và biểu diễn cấu trúc đối với RAG pháp luật).
  * *Dưới:* Sơ đồ 5 nhiệm vụ tuần tự (Hạ tầng Harness $\rightarrow$ Đối chuẩn Baseline GĐ1 $\rightarrow$ Đột phá Parser GĐ2 $\rightarrow$ Thiết kế UKG 10 module $\rightarrow$ Kiểm thử chuyên sâu GĐ3).

---

### SLIDE 6 · HỆ THỐNG CÂU HỎI & GIẢ THUYẾT NGHIÊN CỨU (DƯƠNG) - [SLIDE LƯỚT]
* **Tiêu đề:** Khung 4 câu hỏi nghiên cứu (RQ1 – RQ4)
* **Bố cục hiển thị:** Bảng ma trận gọn 4 dòng:
  * **RQ1 (GĐ1):** Sự khác biệt giữa Naive Vector, Hybrid RAG và LightRAG trên dữ liệu luật Việt Nam?
  * **RQ2 (GĐ2):** Tác động của Regex Parser v2 và thuật toán MaxP đối với dung lượng ngữ cảnh và độ chính xác trích dẫn?
  * **RQ3 (GĐ3):** Đồ thị UKG cải thiện khả năng định vị điều kiện, ngoại lệ so với LightRAG như thế nào?
  * **RQ4 (GĐ3):** Năng lực tái dựng chuỗi quan hệ dẫn chiếu chéo của đồ thị tri thức?

---

### SLIDE 7 · CƠ SỞ LÝ THUYẾT (DƯƠNG)
* **Tiêu đề:** Nguyên lý RAG & Phân cấp 6 mức trừu tượng hệ thống
* **Bố cục hiển thị:** 2 phần:
  * *Bên trái:* Công thức nguyên lý RAG: $D_q = \text{Retrieve}(q, K) \rightarrow C_q = \text{ConstructContext}(D_q) \rightarrow \hat{a} = \text{Generate}(q, C_q)$.
  * *Bên phải:* Sơ đồ hình tháp 6 mức trừu tượng (Từ mức 1: Token Chunks $\rightarrow$ Mức 2: Phân đoạn cấu trúc $\rightarrow$ Mức 3: Nút phân cấp $\rightarrow$ Mức 4: Thực thể $\rightarrow$ Mức 5: Đồ thị tri thức $\rightarrow$ Mức 6: Quan hệ suy luận).

---

### SLIDE 8 · HẠ TẦNG THỰC NGHIỆM (DƯƠNG) - [SLIDE LƯỚT]
* **Tiêu đề:** Khung kiểm thử Benchmark Harness & Adapter Pattern
* **Bố cục hiển thị:** Sơ đồ kiến trúc Adapter Pattern:
  * Lớp điều phối trung tâm (Benchmark Runner) kết nối với các hệ thống qua giao diện chuẩn `BaseRAGAdapter`.
  * Hộp thông số kiểm soát cố định: Phần cứng GPU NVIDIA Tesla T4 | Mô hình nhúng BGE-M3 (1024 dim) | Mô hình tạo sinh/Judge: GPT-4o-mini qua API cố định nhiệt độ $T=0$.

---

### SLIDE 9 · ĐẶC TẢ BA KIẾN TRÚC RAG CƠ SỞ (DƯƠNG)
* **Tiêu đề:** Ba kiến trúc RAG khảo sát tại Giai đoạn 1
* **Bố cục hiển thị:** 3 cột đối sánh đặc tả:
  * *Pipeline 1 (Naive Vector RAG):* Cắt đoạn thô theo Điều (trung bình 2.898 token), truy hồi Top-5 Cosine.
  * *Pipeline 2 (Hybrid RAG):* Kết hợp Dense (BGE-M3) + BM25 (PyVi) qua Reciprocal Rank Fusion ($k=60$) + Reranker Cross-Encoder.
  * *Pipeline 3 (Graph-based LightRAG):* Cắt khối thô 1.200 token, trích xuất đồ thị thực thể/quan hệ, truy hồi kép Local + Global.

---

### SLIDE 10 · GIAI ĐOẠN 1: KẾT QUẢ & NGHỊCH LÝ SỤP ĐỔ TRÍCH DẪN (LÂM) - [SLIDE ĐINH]
* **Tiêu đề:** Kết quả Giai đoạn 1 & Nghịch lý sụp đổ trích dẫn trên tập Tier 1 (N = 205 câu)
* **Bố cục hiển thị:** Bảng số liệu Bảng 3.4 kèm 2 ô số liệu Callout cực to:
  * Bảng số liệu:
    * Naive Vector RAG: Recall 0,9561 | Context Precision 0,9659 | **Citation Acc: 0,3259**
    * Hybrid RAG: Recall 0,9659 | Context Precision 0,9660 | **Citation Acc: 0,2902**
    * LightRAG: Recall 0,9659 | Context Precision 0,8829 | **Citation Acc: 0,1371**
  * *Ô nhấn mạnh 1:* **Nghịch lý Giai đoạn 1:** Recall đạt rất cao (95,6% – 96,6%), Context Precision ~0,966 nhưng **Citation Accuracy chỉ đạt ~30%**.
  * *Ô nhấn mạnh 2:* **Sự sụp đổ của LightRAG (13,71%):** Dù truy hồi trúng 96,59% tài liệu, việc băm văn bản thành các khối thô 1.200 token làm vỡ nát cấu trúc phân cấp, khiến mô hình trích dẫn nhầm lẫn nghiêm trọng.

---

### SLIDE 11 · GIAI ĐOẠN 2: PHÂN TÍCH CẤU TRÚC (LÂM)
* **Tiêu đề:** Structure-Aware Parser v2 & Cơ chế bảo toàn tiền tố phân cấp
* **Bố cục hiển thị:** Sơ đồ luồng bóc tách đệ quy:
  * Văn bản luật (2.087 Điều) $\rightarrow$ Regex Parser v2 bóc tách đệ quy thành **12.754 phân đoạn vi mô** cấp Khoản và Điểm.
  * Hộp ví dụ tiền tố định vị bất biến:  
    `[Luật Đất đai 2024 > Chương III > Điều 45 > Khoản 1 > Điểm a] Điều kiện thực hiện các quyền...`
  * Khối Validation: Kiểm tra 100% tính liên kết cha-con và bảo tồn ký tự tiếng Việt đặc thù (Điểm đ).

---

### SLIDE 12 · GIAI ĐOẠN 2: THUẬT TOÁN MAXP AGGREGATION (LÂM)
* **Tiêu đề:** Thuật toán gom điểm cực đại Article-level MaxP
* **Bố cục hiển thị:** Sơ đồ bài toán & giải pháp:
  * *Bài toán:* Phân đoạn nhỏ (12.754 đoạn) dẫn đến nguy cơ "bội thực cục bộ" (Top-5 trả về 5 điểm thuộc cùng 1 điều luật).
  * *Giải pháp MaxP:*  
    $$\text{Score}(\text{Article}_i) = \max_{p \in \text{Article}_i} \text{Score}(p)$$
    Chỉ cần 1 phân đoạn vi mô trúng khớp, toàn bộ Điều luật đại diện được kéo lên Top đầu, sau đó trả về đúng phân đoạn vi mô chứa bằng chứng.

---

### SLIDE 13 · MA TRẬN ĐỐI SOÁT C1 – C6 (LÂM) - [SLIDE LƯỚT]
* **Tiêu đề:** Ma trận đối soát thực nghiệm 6 cấu hình trên Benchmark A (N = 512 câu)
* **Bố cục hiển thị:** Bảng 3.5 & Bảng 3.6 tinh giản (7 cột chuẩn):
  * C1 (Naive BM25): Citation 0,7490 | Token ~2.500
  * C2 (Naive Dense): Citation 0,4000 | Tỷ lệ tuyệt đối: 25,4% | Token ~2.898
  * C3 (Naive Hybrid): Citation 0,3986 | Tỷ lệ tuyệt đối: 25,6% | Token ~2.898
  * C4 (Parser BM25): Citation 0,9028 | Tỷ lệ tuyệt đối: 89,3% | Token ~580
  * **C5 (Parser Dense): Citation 0,9902 | Tỷ lệ tuyệt đối: 98,4% | Token ~580**
  * C6 (Parser Hybrid): Citation 0,9786 | Tỷ lệ tuyệt đối: 96,3% | Token ~580

---

### SLIDE 14 · ĐỘT PHÁ GIAI ĐOẠN 2 & XÁC THỰC GIẢ THUYẾT H2 (LÂM) - [SLIDE ĐINH]
* **Tiêu đề:** Đột phá trích dẫn và Tối ưu hóa dung lượng ngữ cảnh
* **Bố cục hiển thị:** 3 con số Headline khổng lồ ở giữa:
  * **`0,9902`** (Citation Accuracy C5): Tăng **+59,02 điểm phần trăm** so với C2 (0,4000). Có **504 / 512 câu đạt điểm tuyệt đối 1,0**.
  * **`-79,9%`** (Tiết kiệm token): Giảm từ ~2.898 token xuống chỉ còn **~580 token** mỗi truy vấn.
  * **`α = 0,8`** (Weighted RRF tối ưu): Khắc phục hiện tượng suy giảm hiệu quả khi dung hợp cào bằng ($\alpha = 0,5$), đưa Recall lên **0,9297**.

---

### SLIDE 15 · GIAI ĐOẠN 3: KIẾN TRÚC HYBRID PARSER / UKG (MINH)
* **Tiêu đề:** Kiến trúc 10 Module toàn diện của Hybrid Parser / UKG
* **Bố cục hiển thị:** Sơ đồ dòng chảy 10 Module chia làm 2 tầng rõ rệt:
  * *Tầng Đồ thị Cấu trúc vật lý (Physical Graph - M1 đến M4):* Parser v2, Validation, cây phân cấp văn bản.
  * *Tầng Đồ thị Ngữ nghĩa (Semantic Graph - M5 đến M9):* 
    * **Module 5 (Semantic Router):** Ứng dụng mô hình nhân quả siêu nhẹ **Qwen2.5-0.5B** kết hợp toán tử **Max-Fusion** tại điểm gãy tối ưu $\theta = 0,85$ (đạt Recall 96,85%, lọc 8,9% rác, bảo vệ cấu trúc bất biến).
    * **Module 6:** Trích xuất thực thể, quan hệ pháp lý.
  * *Tầng Truy hồi hợp nhất (M10 - AUTO_FUSION):* Kết hợp đồ thị vật lý và đồ thị tri thức để sinh câu trả lời.

---

### SLIDE 16 · BỘ DỮ LIỆU BENCHMARK B (MINH) - [SLIDE LƯỚT]
* **Tiêu đề:** Thiết kế bộ kiểm chuẩn chuyên sâu Benchmark B
* **Bố cục hiển thị:** 3 khối thông tin:
  * *Phạm vi dữ liệu:* Chương III Luật Đất đai 2024 (Điều 26 – Điều 48: Quyền và nghĩa vụ người sử dụng đất).
  * *Quy mô kiểm thử:* 50 câu hỏi phân tầng (47 câu hỏi phức tạp trong phạm vi + 3 câu hỏi kiểm thử an toàn ngoài phạm vi).
  * *Chuẩn hóa Locator độc lập:* Gán nhãn căn cứ theo chuẩn bất biến `LD2024:A{Điều}:K{Khoản}:D{Điểm}`, hoàn toàn độc lập với ID chỉ mục của từng hệ thống.

---

### SLIDE 17 · KẾT QUẢ BENCHMARK B: TRUY HỒI & ĐỊNH VỊ CĂN CỨ (MINH) - [SLIDE ĐINH]
* **Tiêu đề:** Hiệu năng truy hồi & Định vị căn cứ pháp lý trên Benchmark B
* **Bố cục hiển thị:** Bảng so sánh trực diện giữa Hybrid Parser/UKG và LightRAG:
  * **Article-level Recall@5:** UKG đạt **0,9362** vs LightRAG **0,7536** (**Vượt +18,26 điểm phần trăm**).
  * **Khoản/Điểm Locator Coverage:** UKG đạt độ tập trung cao, mỗi phân đoạn mang đúng 1 locator duy nhất; loại bỏ hiện tượng bao phủ loãng của chunk 1.200 token.
  * **Condition Coverage:** UKG đạt **0,8085** so với 0,7234 của LightRAG.

---

### SLIDE 18 · ĐÁNH GIÁ CHUYÊN SÂU NỘI DUNG & HẠN CHẾ DẪN CHIẾU (MINH)
* **Tiêu đề:** Chất lượng câu trả lời (RQ3) & Đánh giá chuỗi dẫn chiếu (RQ4)
* **Bố cục hiển thị:** 2 phần:
  * *Bên trái (Ưu thế ngữ nghĩa RQ3):*
    * **Legal Correctness:** UKG đạt **0,8777** (so với 0,8210 của LightRAG).
    * **Exception Coverage:** UKG đạt **0,6786** (**Vượt +28,57 điểm phần trăm** nhờ nắm bắt các mệnh đề ngoại lệ).
  * *Bên phải (Ghi nhận trung thực hạn chế RQ4):*
    * Reference-target Recall: Đạt 0,5867 (tìm được các nút đích).
    * **Chain Exact Match:** Đạt **0,0000 (0/18 câu)** do hệ thống mới truy xuất được các cạnh đơn lẻ, chưa ghép nối thành công toàn bộ chuỗi đa bước phức tạp.

---

### SLIDE 19 · BA ĐÓNG GÓP KHOA HỌC CHÍNH (MINH)
* **Tiêu đề:** Ba đóng góp khoa học cốt lõi của đề tài
* **Bố cục hiển thị:** 3 cột đóng góp mang tính dấu ấn:
  * *Đóng góp 1 - Phương pháp luận Benchmark:* Xây dựng Benchmark A (2.087 điều, 512 câu) và Benchmark B (50 câu chuyên sâu) kèm Adapter Pattern chống thiên lệch thực nghiệm.
  * *Đóng góp 2 - Giải pháp phân đoạn cấu trúc:* Bộ giải pháp Parser v2 + Article-level MaxP giải quyết triệt để sự sụt giảm trích dẫn, đưa Citation Accuracy lên 0,9902 và giảm 79,9% token.
  * *Đóng góp 3 - Kiến trúc Hybrid 10 module:* Hiện thực hóa thành công sự kết hợp giữa cây phân cấp vật lý và đồ thị ngữ nghĩa UKG, chứng minh ưu thế vượt trội về bao phủ ngoại lệ pháp luật.

---

### SLIDE 20 · KẾT LUẬN & HƯỚNG PHÁT TRIỂN (MINH) - [SLIDE LƯỚT]
* **Tiêu đề:** Kết luận đề tài & Hướng nghiên cứu tiếp theo
* **Bố cục hiển thị:**
  * *3 Hướng phát triển:* (1) Mở rộng parser sang Nghị định, Thông tư; (2) Tự động hóa cập nhật hiệu lực pháp lý; (3) Hoàn thiện thuật toán Graph Traversal để nâng cao Chain Exact Match.
  * *Phần cảm ơn trang trọng:* "Trân trọng cảm ơn Quý Thầy Cô trong Hội đồng đã chú ý lắng nghe! Kính mời Hội đồng đặt câu hỏi (Q&A)."

---
---

# PHẦN 2: KỊCH BẢN LỜI THOẠI HỌC THUẬT CHUẨN 15 PHÚT (FULL SPOKEN SCRIPT)

> **Hướng dẫn phong thái:**
> * Giọng điệu điềm đạm, tốc độ vừa phải (~130 từ/phút), dứt khoát, âm lượng rõ ràng.
> * Xưng hô: "Kính thưa Quý Thầy Cô trong Hội đồng, em là..., nhóm chúng em...".
> * Tuyệt đối không đọc từng chữ trên slide; mắt nhìn thẳng vào Hội đồng, slide là điểm tựa thị giác.

---

### [00:00 – 01:00] · CHẶNG 1: LÂM (MỞ MÀN & ĐẶT VẤN ĐỀ)

**[Slide 1 — 00:00]**
> *"Kính thưa Quý Thầy Cô trong Hội đồng khoa học! Em tên là **Lưu Thanh Lâm**, đại diện nhóm nghiên cứu gồm em, bạn **Nguyễn Bình Minh** và bạn **Ngô Thế Dương**. Dưới sự hướng dẫn tận tình của **Thầy Tiến sĩ Nguyễn Mạnh Dũng**, hôm nay nhóm chúng em xin phép được báo cáo kết quả đề tài nghiên cứu khoa học: **'Đánh giá và tối ưu hóa các kiến trúc RAG trên nền tảng dữ liệu cấu trúc đặc thù'**.*
>
> *Đề tài tập trung giải quyết bài toán cốt lõi: Làm thế nào để hệ thống truy hồi và tạo sinh văn bản có thể trích dẫn chính xác tuyệt đối các căn cứ pháp luật Việt Nam theo từng Điều, Khoản, Điểm. Sau đây, để trình bày về bối cảnh thực tiễn và hạ tầng kiến trúc hệ thống, em xin phép nhường lời cho bạn **Ngô Thế Dương**."*  
*(Lâm chuyển mic cho Dương, bước lùi lại 1 bước).*

---

### [01:00 – 05:30] · CHẶNG 2: DƯƠNG (BỐI CẢNH & HẠ TẦNG KỸ THUẬT)

**[Slide 2 — 01:00]**
> *"Em xin cảm ơn bạn Lâm. Kính thưa Thầy Cô, nhu cầu tra cứu pháp luật đòi hỏi thông tin trả về không chỉ đúng về mặt nội dung mà bắt buộc phải có căn cứ kiểm chứng xác thực. Mặc dù các kiến trúc RAG truyền thống đã giúp mô hình ngôn ngữ lớn giảm bớt sự bịa đặt, nhưng trong thực tế, các nghiên cứu gần đây của Magesh năm 2024 chỉ ra rằng các hệ thống AI thương mại vẫn gặp tỷ lệ ảo giác pháp lý từ 17% đến 33%. Trong lĩnh vực luật, việc trích dẫn sai lệch một điều khoản có thể làm thay đổi hoàn toàn quyền và nghĩa vụ của các chủ thể."*

**[Slide 3 — 01:40]**
> *"Nguyên nhân gốc rễ bắt nguồn từ ba đặc thù kiến trúc của văn bản quy phạm pháp luật Việt Nam: Thứ nhất là cấu trúc phân cấp đa tầng từ Luật xuống Chương, Mục, Điều, Khoản, Điểm — nội dung của một Điểm luôn phụ thuộc chặt chẽ vào chủ thể ở cấp cha. Thứ hai là mạng lưới dẫn chiếu phức tạp, đòi hỏi phải liên kết nhiều điều luật nằm rải rác. Và thứ ba là sự lệch pha ngôn ngữ giữa cách hỏi thông thường của người dân với văn phong lập pháp chuyên ngành."*

**[Slide 4 — 02:20]**
> *"Từ những đặc thù đó, nhóm nhận diện ba khoảng trống nghiên cứu chính: Thứ nhất là sự thiếu hụt một khung đối soát thực nghiệm có kiểm soát biến số; thứ hai là thiếu các thực nghiệm đo lường tác động của việc phân đoạn cấu trúc vi mô so với cắt khối token thô; và thứ ba là các bộ chỉ số đo lường RAG tổng quát hiện nay chưa đánh giá được khả năng định vị chính xác vị trí pháp lý."*

**[Slide 5 & 6 — 03:00] · [Lướt nhanh 40 giây]**
> *"Để giải quyết các khoảng trống trên, mục tiêu của đề tài là xây dựng khung kiểm chuẩn thực nghiệm và đề xuất giải pháp tối ưu hóa phân đoạn cũng như biểu diễn tri thức đồ thị. Nhóm cụ thể hóa mục tiêu thành 4 câu hỏi nghiên cứu từ RQ1 đến RQ4, tương ứng với lộ trình thực nghiệm qua 3 giai đoạn chặt chẽ được thể hiện trên slide."*

**[Slide 7 — 03:40]**
> *"Về mặt cơ sở lý thuyết, nhóm mô hình hóa hệ thống dựa trên nguyên lý truy xuất tăng cường và phân cấp 6 mức trừu tượng của dữ liệu: từ các khối token thô ở mức 1, nâng dần lên phân đoạn vi mô, cây phân cấp văn bản, và cao nhất là đồ thị tri thức pháp lý ở mức 5 và mức 6."*

**[Slide 8 — 04:20] · [Lướt nhanh 35 giây]**
> *"Để đảm bảo tính khách quan khoa học, nhóm thiết kế khung kiểm thử Benchmark Harness áp dụng mẫu kiến trúc Adapter Pattern. Toàn bộ các biến kiểm soát thực nghiệm được đóng băng cố định: cùng chạy trên GPU Tesla T4, cùng sử dụng mô hình nhúng BGE-M3 và mô hình sinh GPT-4o-mini ở nhiệt độ 0, bảo đảm mọi chênh lệch ghi nhận được đều bắt nguồn từ bản chất kiến trúc."*

**[Slide 9 — 04:55]**
> *"Tại Giai đoạn 1, nhóm thiết lập ba pipeline đối chuẩn cơ sở gồm: Naive Vector RAG cắt theo Điều thô; Hybrid RAG kết hợp từ khóa BM25 và Vector qua dung hợp thứ hạng RRF; và mô hình đồ thị cục bộ LightRAG.  
> Vậy kết quả khảo sát Giai đoạn 1 đã bộc lộ nghịch lý gì và giải pháp Giai đoạn 2 ra sao? Sau đây em xin mời bạn **Lưu Thanh Lâm** tiếp tục trình bày."*  
*(Dương chuyển mic lại cho Lâm).*

---

### [05:30 – 10:15] · CHẶNG 3: LÂM (NGHỊCH LÝ GIAI ĐOẠN 1 & ĐỘT PHÁ GIAI ĐOẠN 2)

**[Slide 10 — 05:30] · [SLIDE ĐINH]**
> *"Em xin cảm ơn bạn Dương. Kính thưa Hội đồng, khi tiến hành đối soát công bằng trên tập kiểm thử Tier 1 gồm 205 câu hỏi, nhóm chúng em đã phát hiện một nghịch lý kỹ thuật mang tính bước ngoặt:  
> **Hiệu năng tìm kiếm tài liệu cao hoàn toàn không đồng nghĩa với việc mô hình trích dẫn đúng căn cứ pháp lý!**  
> Cụ thể, cả ba hệ thống đều đạt khả năng truy hồi tài liệu rất tốt, đạt Recall từ 95,6% đến 96,6%, độ khớp ngữ cảnh Context Precision đạt trên 0,96. Thế nhưng, độ chính xác trích dẫn Citation Accuracy của Naive Vector RAG chỉ đạt 32,59% và Hybrid RAG chỉ đạt 29,02%.  
> Đáng chú ý nhất, mô hình đồ thị LightRAG dù đạt Recall tới 96,59% nhưng độ chính xác trích dẫn lại sụp đổ xuống chỉ còn **13,71%**. Kết quả kiểm toán cho thấy: Việc chia cắt tài liệu thành các khối thô 1.200 token đã làm vỡ nát cấu trúc phân cấp, khiến mô hình bị mất phương hướng định vị điều khoản."*

**[Slide 11 — 06:30]**
> *"Để giải quyết triệt để nghịch lý này, bước sang Giai đoạn 2, nhóm đề xuất bộ phân tích cấu trúc **Regex Parser v2**. Thay vì cắt khối thô cơ học, hệ thống bóc tách văn bản đệ quy theo đúng thứ tự logic lập pháp, chuyển đổi 2.087 Điều luật thành **12.754 phân đoạn vi mô** cấp Khoản và Điểm. Điểm mấu chốt là mỗi phân đoạn vi mô đều được gắn kèm một tiền tố phân cấp bất biến từ Luật, Chương, Điều đến Khoản, Điểm, kết hợp cùng bộ kiểm thực Validation bảo đảm không xảy ra đứt gãy phả hệ."*

**[Slide 12 — 07:25]**
> *"Tuy nhiên, khi phân chia thành hơn 12 nghìn đoạn nhỏ, hệ thống lập tức đối mặt với nguy cơ 'bội thực cục bộ': Top-5 đoạn trả về có thể cùng thuộc về một Điều luật. Do đó, nhóm xây dựng thuật toán gom điểm cực đại **Article-level MaxP**. Nguyên lý là: Chỉ cần một phân đoạn vi mô khớp ngữ nghĩa với câu hỏi, toàn bộ Điều luật đại diện sẽ nhận điểm tối đa và được kéo lên đầu danh sách, sau đó hệ thống trích xuất đúng phân đoạn vi mô chứa bằng chứng để đưa vào prompt."*

**[Slide 13 — 08:15] · [Lướt nhanh 30 giây]**
> *"Nhóm thiết lập ma trận đối soát toàn diện gồm sáu cấu hình từ C1 đến C6 trên 512 câu hỏi của Benchmark A, thực hiện tổng cộng 3.072 lượt đánh giá độc lập bằng phương pháp LLM-as-a-Judge như được thể hiện tại Bảng 3.6 trên slide."*

**[Slide 14 — 08:45] · [SLIDE ĐINH]**
> *"Kết quả thực nghiệm đã xác thực hoàn toàn giả thuyết nghiên cứu H2 với những bước nhảy vọt về chất lượng:  
> Thứ nhất, cấu hình **C5 (Parser Dense)** đã nâng điểm Citation Accuracy từ 0,4000 lên mức **0,9902**, tăng tới 59,02 điểm phần trăm so với Naive Dense. Tỷ lệ câu hỏi đạt trích dẫn chuẩn xác tuyệt đối tăng từ 25,4% lên tới **98,4%** (tức 504 trên tổng số 512 câu).  
> Thứ hai, dung lượng ngữ cảnh trung bình giảm từ gần 2.900 token xuống chỉ còn **khoảng 580 token**, tương đương **tiết kiệm 79,9% chi phí token** đưa vào mô hình.  
> Đồng thời, qua khảo sát tỷ lệ dung hợp Weighted RRF, nhóm xác định được ngưỡng tối ưu tại $\alpha = 0,8$, khắc phục hiện tượng suy giảm hiệu năng khi dung hợp cào bằng.  
> 
> Giai đoạn 2 đã giải quyết xuất sắc bài toán đơn văn bản. Tuy nhiên, trước các câu hỏi đa bước và có quan hệ dẫn chiếu phức tạp, hệ thống mở rộng lên đồ thị tri thức ra sao? Sau đây xin mời bạn **Nguyễn Bình Minh** trình bày Giai đoạn 3."*  
*(Lâm chuyển mic cho Minh).*

---

### [10:15 – 15:00] · CHẶNG 4: MINH (ĐỒ THỊ UKG, ĐA BƯỚC & KẾT LUẬN)

**[Slide 15 — 10:15]**
> *"Em xin cảm ơn bạn Lâm. Kính thưa Quý Thầy Cô, để xử lý các truy vấn pháp lý đa bước, bước sang Giai đoạn 3, nhóm đề xuất kiến trúc toàn diện **Hybrid Parser / UKG gồm 10 Module** phân tách thành hai tầng rõ rệt:  
> Tầng đồ thị vật lý từ Module 1 đến Module 4 lưu trữ toàn vẹn cây phân cấp văn bản.  
> Tầng đồ thị ngữ nghĩa từ Module 5 đến Module 9 trích xuất các quan hệ quyền, nghĩa vụ và chế tài. Trong đó, tại Module 5, nhóm ứng dụng mô hình nhân quả siêu nhẹ **Qwen2.5-0.5B** kết hợp cơ chế **Max-Fusion** tại ngưỡng tối ưu 0,85, bảo toàn 96,85% các quy phạm cần bóc tách mà vẫn duy trì tính bất biến của đồ thị vật lý. Cuối cùng, Module 10 thực hiện truy hồi kết hợp giữa hai lớp đồ thị để tổng hợp câu trả lời."*

**[Slide 16 — 11:10] · [Lướt nhanh 35 giây]**
> *"Để kiểm chứng kiến trúc này, nhóm xây dựng bộ kiểm chuẩn chuyên sâu **Benchmark B** tập trung vào Chương III Luật Đất đai 2024, gồm 50 câu hỏi phân tầng được gắn nhãn định vị pháp lý độc lập, nhằm khảo sát năng lực xử lý ngoại lệ và chuỗi dẫn chiếu."*

**[Slide 17 — 11:45] · [SLIDE ĐINH]**
> *"Kết quả thực nghiệm trên Benchmark B cho thấy ưu thế vượt trội của kiến trúc đề xuất so với LightRAG:  
> Về truy hồi cấp Điều, Hybrid Parser/UKG đạt Recall 93,62%, **vượt LightRAG 18,26 điểm phần trăm**.  
> Quan trọng hơn, nhờ mỗi phân đoạn vi mô mang duy nhất một định vị pháp lý chuẩn xác, hệ thống loại bỏ hoàn toàn hiện tượng 'trúng giả' do độ bao phủ loãng của các khối văn bản lớn."*

**[Slide 18 — 12:35]**
> *"Khi đánh giá sâu về mặt nội dung tại Slide 18, kiến trúc UKG đạt điểm tính chính xác pháp lý Legal Correctness 0,8777 (so với 0,8210 của LightRAG), và độ bao phủ ngoại lệ đạt 67,86%, **vượt LightRAG tới 28,57 điểm phần trăm**.  
> Tuy nhiên, với tinh thần trung thực khoa học, nhóm cũng ghi nhận một hạn chế quan trọng: Đối với các câu hỏi dẫn chiếu nhiều bước phức tạp, chỉ số Chain Exact Match của hệ thống mới đạt 0,0000. Nguyên nhân là do hệ thống hiện mới truy xuất được các cặp cạnh đơn lẻ mà chưa nối được toàn vẹn toàn bộ chuỗi suy luận đa bước."*

**[Slide 19 — 13:25]**
> *"Tổng kết lại, đề tài mang lại ba nhóm đóng góp khoa học chính:  
> Một là xây dựng thành công hai bộ Benchmark A và Benchmark B chuẩn mực kèm khung Adapter Pattern chống thiên lệch thực nghiệm.  
> Hai là đề xuất giải pháp phối hợp giữa Parser v2 và thuật toán MaxP, giải quyết triệt để sự sụt giảm trích dẫn, đưa Citation Accuracy lên 0,9902 và tiết kiệm gần 80% token.  
> Ba là chứng minh thực nghiệm rằng việc kết hợp cây cấu trúc vật lý với đồ thị ngữ nghĩa UKG giúp nâng cao đáng kể độ chính xác pháp lý và khả năng bao phủ các trường hợp ngoại lệ."*

**[Slide 20 — 14:15]**
> *"Trong thời gian tới, nhóm hướng đến việc mở rộng bộ phân tích cấu trúc sang các văn bản dưới luật như Nghị định, Thông tư, đồng thời nghiên cứu thuật toán duyệt đồ thị nhiều bước để hoàn thiện chuỗi dẫn chiếu chéo.  
> 
> Thay mặt nhóm nghiên cứu, chúng em xin trân trọng cảm ơn Quý Thầy Cô trong Hội đồng khoa học đã chú ý lắng nghe. Nhóm chúng em rất mong nhận được những nhận xét và góp ý quý báu của Thầy Cô. Chúng em xin sẵn sàng bước vào phần Hỏi và Đáp!"*  
*(Cả 3 thành viên Lâm, Dương, Minh cùng đứng nghiêm trang, cúi đầu chào Hội đồng).*

---
---

# PHẦN 3: BẢN PHAO THỰC CHIẾN - TỪ KHÓA NEO & CỬ CHỈ TRÌNH BÀY (ANCHOR CHEAT SHEET)

> **Mục đích:** Đây là tài liệu cầm tay để tập dượt. Các bạn không cần học thuộc từng câu chữ ở Phần 2, chỉ cần nhìn vào bảng dưới đây để nhớ đúng các "Ý neo", "Chỉ tay vào đâu" và "Câu chốt chuyển mic".

| Slide | Người nói | Thời lượng | 2 - 3 Từ khóa / Ý neo chính | Hành động / Điểm chỉ tay trên Slide | Câu chốt chuyển mic (Trigger Cue) |
| :---: | :---: | :---: | :--- | :--- | :--- |
| **1** | **Lâm** | 30s | • Chào Hội đồng, giới thiệu nhóm 3 người<br>• Đề tài: RAG trên dữ liệu cấu trúc đặc thù | Đứng giữa, phong thái tự tin, nhìn bao quát Hội đồng | *"Sau đây xin mời bạn Ngô Thế Dương trình bày bối cảnh và kiến trúc kỹ thuật."* |
| **2** | **Dương** | 40s | • Nhu cầu tra cứu pháp luật tăng cao<br>• RAG ảo giác pháp lý 17% – 33% (Magesh) | Chỉ tay vào **Hộp đỏ 17% - 33%** | *(Nói liền mạch sang Slide 3)* |
| **3** | **Dương** | 40s | • 3 đặc thù luật: Phân cấp đa tầng, Dẫn chiếu mạng lưới, Lệch pha ngôn ngữ | Chỉ tay lần lượt vào **3 khối hộp ngang** | *(Nói liền mạch sang Slide 4)* |
| **4** | **Dương** | 35s | • 3 khoảng trống: Khung đối soát, Phân đoạn vi mô, Thước đo trích dẫn | Chỉ vào **3 icon Gap** | *(Nói liền mạch sang Slide 5)* |
| **5** | **Dương** | 20s | • **[Slide lướt]** Mục tiêu: Đánh giá & tối ưu RAG; 5 nhiệm vụ cụ thể | Lướt mắt nhìn Hội đồng, tay chỉ nhẹ sơ đồ | *(Nói liền mạch sang Slide 6)* |
| **6** | **Dương** | 25s | • **[Slide lướt]** Khung 4 câu hỏi RQ1 đến RQ4 tương ứng 3 giai đoạn | Chỉ vào **bảng 4 RQ** | *(Nói liền mạch sang Slide 7)* |
| **7** | **Dương** | 40s | • Nguyên lý RAG: Retrieve $\rightarrow$ Context $\rightarrow$ Generate<br>• 6 mức trừu tượng: từ Token thô đến Đồ thị | Chỉ vào **hình tháp 6 mức trừu tượng** | *(Nói liền mạch sang Slide 8)* |
| **8** | **Dương** | 35s | • **[Slide lướt]** Benchmark Harness + Adapter Pattern<br>• Đóng băng GPU T4, BGE-M3, GPT-4o-mini | Chỉ vào **hộp thông số đóng băng kiểm soát** | *(Nói liền mạch sang Slide 9)* |
| **9** | **Dương** | 40s | • 3 pipeline GĐ1: Naive (Điều thô), Hybrid (BM25+Dense), LightRAG (Khối 1.200t) | Chỉ vào **3 cột Pipeline** | *"Kết quả GĐ1 và đột phá GĐ2 ra sao, xin mời bạn Lâm tiếp tục trình bày."* |
| **10** | **Lâm** | 60s | • **[Slide đinh] Nghịch lý Giai đoạn 1**<br>• Recall 96% nhưng Citation chỉ ~30%<br>• LightRAG sụp đổ còn 13,71% do cắt thô | Chỉ tay dứt khoát vào số **13,71% màu đỏ** và **32,59%** | *(Nói liền mạch sang Slide 11)* |
| **11** | **Lâm** | 50s | • Đột phá Regex Parser v2 $\rightarrow$ 12.754 phân đoạn vi mô<br>• Tiền tố bất biến [Luật > Chương > Điều > Khoản > Điểm] | Chỉ vào **hộp ví dụ tiền tố định vị** | *(Nói liền mạch sang Slide 12)* |
| **12** | **Lâm** | 50s | • Bội thực cục bộ $\rightarrow$ Thuật toán MaxP<br>• 1 đoạn trúng kéo cả Điều lên, trả về đúng bằng chứng | Chỉ vào **công thức MaxP** và sơ đồ minh họa | *(Nói liền mạch sang Slide 13)* |
| **13** | **Lâm** | 25s | • **[Slide lướt]** Ma trận C1 – C6 trên 512 câu hỏi Benchmark A (3.072 lượt chấm) | Quét tay qua bảng ma trận 6 cấu hình | *(Bấm ngay sang Slide 14)* |
| **14** | **Lâm** | 60s | • **[Slide đinh] Đột phá kết quả C5:**<br>• Citation Acc vọt lên **0,9902** (98,4% đạt 1.0)<br>• Tiết kiệm **79,9% token** (~580t)<br>• Quét $\alpha = 0,8$ | Chỉ thẳng vào 3 số lớn: **0,9902**, **-79,9%**, **$\alpha=0,8$** | *"Trước câu hỏi đa bước và dẫn chiếu, UKG giải quyết ra sao? Xin mời bạn Minh."* |
| **15** | **Minh** | 55s | • Kiến trúc UKG 10 Module: Physical Graph (M1-M4) + Semantic Graph (M5-M9)<br>• M5 Causal Router Max-Fusion | Chỉ tay vào 2 tầng đồ thị và khối **Module 5** | *(Nói liền mạch sang Slide 16)* |
| **16** | **Minh** | 35s | • **[Slide lướt]** Benchmark B: Chương III Luật Đất đai 2024, 50 câu hỏi phân tầng | Chỉ vào **hộp cấu trúc 50 câu hỏi** | *(Nói liền mạch sang Slide 17)* |
| **17** | **Minh** | 50s | • **[Slide đinh]** UKG vượt LightRAG cấp Điều **+18,26 đpt** (93,62% vs 75,36%)<br>• Định vị vi mô không bị loãng | Chỉ vào số **0,9362** và cột chênh lệch | *(Nói liền mạch sang Slide 18)* |
| **18** | **Minh** | 50s | • Legal Correctness 0,8777; Exception Coverage **+28,57 đpt**<br>• Thừa nhận Chain Exact Match = 0 (tính trung thực) | Chỉ vào số **+28,57 đpt**, sau đó chỉ sang **0,0000** | *(Nói liền mạch sang Slide 19)* |
| **19** | **Minh** | 40s | • 3 Đóng góp khoa học: Khung Benchmark chuẩn; Giải pháp Parser+MaxP; Kiến trúc UKG | Chỉ lần lượt vào **3 cột đóng góp** | *(Nói liền mạch sang Slide 20)* |
| **20** | **Minh** | 30s | • Hướng phát triển: Nghị định, Thông tư, duyệt đồ thị đa bước<br>• Lời cảm ơn và mời Q&A | Nhìn thẳng Hội đồng, mỉm cười trang trọng | Cả 3 bạn cùng đứng nghiêm, cúi đầu chào |

