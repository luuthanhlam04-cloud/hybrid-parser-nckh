# KỊCH BẢN THUYẾT TRÌNH BẢO VỆ NCKH (15 PHÚT) — CHUẨN HOÁ TOÀN DIỆN & KHẮC PHỤC TỬ HUYỆT
## ĐỀ TÀI: ĐÁNH GIÁ VÀ TỐI ƯU HÓA CÁC KIẾN TRÚC RAG TRÊN NỀN TẢNG DỮ LIỆU CẤU TRÚC ĐẶC THÙ
**Hội đồng Khoa học & Công nghệ Thông tin (PTIT)**  
**Nhóm tác giả:** Lưu Thanh Lâm · Ngô Thế Dương · Nguyễn Bình Minh  
**Giảng viên hướng dẫn:** TS. Nguyễn Mạnh Dũng  
**Tổng thời lượng:** 15 phút (900 giây) | **Khung lời thoại chuẩn:** ~1.850 từ (~125–130 từ/phút) | **Thời gian dự phòng:** 30 giây

---

## MA TRẬN PHÂN BỔ THỜI GIAN & PHÂN VAI (3 THÀNH VIÊN)

```
[00:00 - 01:30] CHẶNG 1: LƯU THANH LÂM (Slide 1 - 2 | 90s | ~205 từ)
  └── Mở màn, Bối cảnh pháp lý, Tỷ lệ ảo giác 17%-33% (Magesh 2025) & Thách thức căn cứ vi mô.

[01:30 - 05:15] CHẶNG 2: NGÔ THẾ DƯƠNG (Slide 3 - 6 | 225s | ~455 từ)
  └── 3 Đặc thù luật & 3 Gap; 3 Trường phái RAG; Bung 4 RQ; Hạ tầng Benchmark Harness & 2 Bộ dữ liệu A/B.

[05:15 - 10:00] CHẶNG 3: LƯU THANH LÂM (Slide 7 - 9 | 285s | ~545 từ)
  └── Giai đoạn 1: Nghịch lý sụp đổ trích dẫn (RQ1); Giai đoạn 2: Parser v2 & MaxP; Đột phá C5 (RQ2) & Cô lập biến số.

[10:00 - 15:00] CHẶNG 4: NGUYỄN BÌNH MINH (Slide 10 - 14 | 300s | ~685 từ)
  └── Giai đoạn 3: Triết lý UKG 2 tầng & Module 5 Causal; Benchmark B (RQ3, RQ4) & Trade-off; Bo 4 RQ; Đóng góp & Kết luận.
```

---

# PHẦN 1: BẢN THIẾT KẾ KỊCH BẢN CHI TIẾT 14 SLIDE (14 SLIDE BLUEPRINTS & EVIDENCE SIGNPOSTS)

---

### SLIDE 1 · BÌA BÁO CÁO (LÂM | 00:00 – 00:20)
* **Tiêu đề:** Đánh giá và tối ưu hóa các kiến trúc RAG trên nền tảng dữ liệu cấu trúc đặc thù
* **Phụ đề:** Nghiên cứu thực nghiệm trên văn bản quy phạm pháp luật Việt Nam
* **Bố cục hiển thị:**
  * Thông tin cơ sở đào tạo: Học viện Công nghệ Bưu chính Viễn thông (PTIT).
  * Tên đề tài NCKH, GVHD: TS. Nguyễn Mạnh Dũng.
  * Nhóm sinh viên thực hiện: Lưu Thanh Lâm, Ngô Thế Dương, Nguyễn Bình Minh.
  * Hộp thông điệp mở: *"Từ khoảng cách truy hồi - trích dẫn đến kiến trúc đồ thị tri thức pháp lý hai tầng."*
* **Thẻ dẫn chứng:** `[Tham chiếu: Báo cáo toàn văn — Trang bìa | Mã đề tài NCKH 2025-2026]`.

---

### SLIDE 2 · BỐI CẢNH & THÁCH THỨC CĂN CỨ PHÁP LÝ (LÂM | 00:20 – 01:30)
* **Tiêu đề:** Bối cảnh nghiên cứu — Thách thức về tính xác thực của căn cứ pháp lý
* **Luận điểm cốt lõi:** *Hỏi đáp pháp luật đòi hỏi kiểm chứng tuyệt đối; ảo giác trích dẫn làm đảo lộn hệ quả pháp lý của hành vi.*
* **Bố cục hiển thị:**
  * Cột trái — Thực tiễn: Nhu cầu tra cứu pháp luật tự động tăng cao; yêu cầu độ chính xác tuyệt đối ở mức vi mô (Điều, Khoản, Điểm).
  * Cột phải — Bằng chứng khoa học quốc tế: Trích dẫn công bố của Magesh và cộng sự (2025) trên tạp chí *Journal of Empirical Legal Studies* (JELS): Các mô hình LLM thương mại hàng đầu vẫn gặp tỷ lệ ảo giác pháp lý từ **17% đến 33%**.
  * Hộp cảnh báo trung tâm: *"Một câu trả lời đúng ngữ nghĩa nhưng sai căn cứ Điều/Khoản hoặc bỏ sót một ngoại lệ tại một Điểm có thể biến một hành vi từ hợp pháp thành vi phạm pháp luật."*
  * Câu hỏi bài toán đặt ra: Làm sao vừa tối ưu truy hồi, vừa giúp LLM xác định chính xác căn cứ vi mô mà không bùng nổ chi phí tính toán?
* **Thẻ dẫn chứng:** `[Tham chiếu: Báo cáo toàn văn — Mục 1.1, 1.2 | Trang 1–4 | Trích dẫn [3] Magesh et al. (2025)]`.

---

### SLIDE 3 · ĐẶC THÙ VĂN BẢN LUẬT & KHOẢNG TRỐNG NGHIÊN CỨU (DƯƠNG | 01:30 – 02:25)
* **Tiêu đề:** Đặc thù dữ liệu pháp luật Việt Nam & Ba khoảng trống nghiên cứu
* **Luận điểm cốt lõi:** *Văn bản luật có cấu trúc phân cấp nghiêm ngặt, dẫn chiếu chéo phức tạp và lệch pha từ vựng lớn so với ngôn ngữ tự nhiên.*
* **Bố cục hiển thị:** Sơ đồ đối sánh 3 Đặc thù $\longleftrightarrow$ 3 Khoảng trống (Gap):
  * *Đặc thù 1 — Phân cấp đa tầng:* Luật $
ightarrow$ Chương $
ightarrow$ Mục $
ightarrow$ Điều $
ightarrow$ Khoản $
ightarrow$ Điểm. Nội dung ở Điểm phụ thuộc chủ thể ở Điều.  
    $\longrightarrow$ **Khoảng trống 1 (Gap 1):** Thiếu phương pháp phân đoạn bảo toàn phả hệ (Context Preservation).
  * *Đặc thù 2 — Mạng lưới dẫn chiếu chéo:* Điều kiện áp dụng, trường hợp ngoại lệ nằm rải rác ở nhiều điều khoản khác nhau.  
    $\longrightarrow$ **Khoảng trống 2 (Gap 2):** Thiếu cơ chế đồ thị kết nối quy phạm ngoại lệ và liên kết chuỗi.
  * *Đặc thù 3 — Lệch pha từ vựng (Vocabulary Mismatch):* Người dân hỏi bằng ngôn ngữ đời thường, luật quy định bằng thuật ngữ chuyên ngành chuẩn tắc.  
    $\longrightarrow$ **Khoảng trống 3 (Gap 3):** Thiếu bộ kiểm chuẩn độc lập không bị thiên lệch trùng lặp từ khóa.
* **Thẻ dẫn chứng:** `[Tham chiếu: Báo cáo toàn văn — Mục 1.2, 1.3 | Trang 5–12]`.

---

### SLIDE 4 · CƠ SỞ LÝ THUYẾT: BA TRƯỜNG PHÁI RAG CƠ SỞ (DƯƠNG | 02:25 – 03:20)
* **Tiêu đề:** Cơ sở lý thuyết — Ba trường phái RAG đại diện được khảo sát
* **Luận điểm cốt lõi:** *Mỗi trường phái sở hữu thế mạnh riêng nhưng đều đối mặt ranh giới kỹ thuật rõ rệt trên văn bản cấu trúc đặc thù.*
* **Bố cục hiển thị:** 3 cột kiến trúc đối chuẩn:
  * *Cột 1 — Naive Vector RAG (Dense Only):* Nhúng vector dày đặc (BGE-M3), tìm kiếm bằng độ tương đồng Cosine. Mạnh về ngữ nghĩa khái quát, nhưng dễ nhầm lẫn các điều khoản có mẫu câu tương tự.
  * *Cột 2 — Hybrid RAG (Lexical + Dense):* Kết hợp Okapi BM25 và Dense qua Reciprocal Rank Fusion (RRF) kết hợp Cross-Encoder Reranker. Bắt tốt từ khóa định danh nhưng tốn chi phí tính toán.
  * *Cột 3 — LightRAG (Graph-based RAG):* Trích xuất đồ thị thực thể bằng LLM, kết nối văn bản hai tầng. Khả năng bao quát rộng nhưng chi phí indexing cao và dễ mất liên kết thứ bậc pháp lý.
* **Thẻ dẫn chứng:** `[Tham chiếu: Báo cáo toàn văn — Mục 2.1, 2.2 | Trang 15–35 | Trích dẫn [5], [6], [12], [21]]`.

---

### SLIDE 5 · HỆ THỐNG CÂU HỎI NGHIÊN CỨU (DƯƠNG | 03:20 – 04:05)
* **Tiêu đề:** Bốn câu hỏi nghiên cứu định hướng (RQ1 – RQ4)
* **Luận điểm cốt lõi:** *Thiết kế thực nghiệm 3 giai đoạn được ánh xạ trực tiếp từ 4 câu hỏi khoa học cốt lõi.*
* **Bố cục hiển thị:** Bảng ma trận 4 RQ gắn với 3 Giai đoạn thực nghiệm:
  * **RQ1 (Giai đoạn 1):** *Hiệu quả truy hồi và độ chính xác trích dẫn căn cứ của các kiến trúc RAG cơ sở khác biệt như thế nào khi áp dụng chiến lược cắt đoạn thô?*
  * **RQ2 (Giai đoạn 2):** *Việc bổ sung bộ phân tích cấu trúc vi mô kết hợp giải thuật MaxP tác động như thế nào đến độ chính xác trích dẫn và dung lượng ngữ cảnh?*
  * **RQ3 (Giai đoạn 3):** *Kiến trúc đồ thị tri thức hai tầng Hybrid UKG nâng cao hiệu quả truy hồi và xử lý quy phạm ngoại lệ phức tạp ra sao so với GraphRAG truyền thống?*
  * **RQ4 (Giai đoạn 3):** *Khả năng định vị và tái dựng chuỗi dẫn chiếu chéo nhiều bước của các mô hình đạt mức độ nào?*
* **Thẻ dẫn chứng:** `[Tham chiếu: Báo cáo toàn văn — Mục 1.4 | Trang 12–14]`.

---

### SLIDE 6 · THIẾT KẾ THỰC NGHIỆM & HẠ TẦNG BENCHMARK (DƯƠNG | 04:05 – 05:15)
* **Tiêu đề:** Phương pháp luận — Hạ tầng Benchmark Harness & Hai bộ dữ liệu kiểm chuẩn
* **Luận điểm cốt lõi:** *Thiết kế công bằng (fair-play), cô lập hoàn toàn biến ngoại lai và loại bỏ rò rỉ từ vựng.*
* **Bố cục hiển thị:** 2 khối thông tin kiểm chuẩn:
  * *Khối 1 — Benchmark Harness & Adapter Pattern:*  
    Giao diện chuẩn hóa `BaseRAGAdapter` bao bọc tất cả hệ sinh thái. Cố định toàn bộ tham số nền tảng: Embedding `BAAI/bge-m3`, LLM thẩm định `GPT-4o-mini`, $K=5$, cùng môi trường phần cứng NVIDIA T4 GPU.
  * *Khối 2 — Hai bộ dữ liệu kiểm chuẩn chuyên biệt:*
    * **Benchmark A (N = 512 câu):** Phủ rộng 7 đạo luật trọng điểm. Thực hiện quy trình viết lại chọn lọc cho các câu có độ trùng lặp cao, đưa chỉ số từ vựng Jaccard trung bình từ **0,68 xuống 0,31** để loại bỏ triệt để thiên lệch học vẹt từ khóa.
    * **Benchmark B (N = 50 câu):** Phân tầng tại Chương III Luật Đất đai 2024 (47 câu hỏi truy hồi/chất lượng + 3 câu kiểm tra an toàn/từ chối). Đánh giá chuyên sâu 5 nhóm tình huống: quyền nghĩa vụ trực tiếp, đa điều kiện, ngoại lệ/điều cấm, dẫn chiếu đơn bước và đa bước.
* **Thẻ dẫn chứng:** `[Tham chiếu: Báo cáo toàn văn — Mục 2.3, 2.4, 2.5 | Bảng 2.1, Bảng 2.2, Hình 2.1 | Trang 36–58]`.

---

### SLIDE 7 · GIAI ĐOẠN 1: KẾT QUẢ ĐỐI CHUẨN & TRẢ LỜI RQ1 (LÂM | 05:15 – 06:40)
* **Tiêu đề:** Giai đoạn 1 — Khoảng cách giữa truy hồi và trích dẫn trên tập Tier 1 (N = 205 câu) & Trả lời RQ1
* **Luận điểm cốt lõi:** *Hiệu năng tìm kiếm tài liệu cao chưa đồng nghĩa với việc câu trả lời trích dẫn đúng căn cứ: Cắt đoạn thô làm đứt gãy phả hệ phân cấp.*
* **Bố cục hiển thị:** Bảng số liệu Bảng 3.4 kèm Hộp phân tích cơ chế:
  * *Bảng số liệu đối chuẩn (Tier 1 Fair Subset — N = 205 câu):*
    * Naive Vector RAG: Recall@5: 0,9561 | Context Precision: 0,9659 | **Citation Accuracy (Answer): 0,3259**
    * Hybrid RAG: Recall@5: 0,9659 | Context Precision: 0,9660 | **Citation Accuracy (Answer): 0,2902**
    * LightRAG: Recall@5: 0,9659 | Context Precision: 0,8829 | **Citation Accuracy (Answer): 0,1371**
  * *Hiện tượng đáng lưu tâm:* Cả ba hệ thống đều tìm trúng Điều luật liên quan ($Recall > 95\%$). Tuy nhiên, khi đánh giá câu trả lời cuối cùng, Citation Accuracy chỉ đạt khoảng $30\%$, riêng LightRAG chỉ ghi nhận **$13,71\%$**.
  * *Cơ chế kỹ thuật:* Cắt khối thô 1.200 token làm đứt gãy quan hệ cha-con. Đoạn trích đưa vào prompt bị mất thông tin chủ thể ở cấp Điều, khiến LLM suy đoán vị trí pháp lý không chính xác.
  * *Chốt hạ RQ1:* Các kiến trúc RAG cơ sở chưa đáp ứng được yêu cầu trích dẫn chính xác nếu giữ nguyên phương thức cắt đoạn thô.
* **Thẻ dẫn chứng:** `[Dẫn chứng: Báo cáo toàn văn — Mục 3.2 | Bảng 3.3, Bảng 3.4 | Trang 91–93]`.

---

### SLIDE 8 · GIAI ĐOẠN 2: PARSER V2 & ARTICLE-LEVEL MAXP (LÂM | 06:40 – 08:05)
* **Tiêu đề:** Giai đoạn 2 — Giải pháp phân đoạn cấu trúc vi mô & Giải thuật Article MaxP
* **Luận điểm cốt lõi:** *Bảo toàn phả hệ bằng tiền tố bất biến và tối ưu hóa cửa sổ ngữ cảnh bằng Max-Pooling cấp Điều.*
* **Bố cục hiển thị:** Sơ đồ luồng xử lý 2 bước:
  * *Bước 1 — Structure-Aware Parser v2:*  
    Bóc tách đệ quy văn bản thành 12.754 phân đoạn vi mô theo từng cấp Khoản và Điểm.  
    Tự động gắn **tiền tố phả hệ bất biến (Invariant Structural Prefix)**: `[Văn bản: Luật Đất đai 2024 > Chương III > Điều 45 > Khoản 1 > Điểm a]`.
  * *Bước 2 — Giải thuật Article-Level Max-Pooling (MaxP):*  
    *Thách thức:* Phân đoạn nhỏ làm bão hòa cửa sổ Top-K bởi nhiều Khoản trong cùng 1 Điều.  
    *Giải pháp:* Gom cụm các phân đoạn vi mô theo Điều; điểm số đại diện của Điều được tính bằng điểm cực đại:  
    $$S_{	ext{article}} = \max_{c \in 	ext{Article}} S_{	ext{micro}}(c)$$  
    Xếp hạng Top-K ở cấp Điều, sau đó trích xuất chính xác các phân đoạn vi mô đạt điểm cao nhất gửi sang prompt LLM.
* **Thẻ dẫn chứng:** `[Tham chiếu: Báo cáo toàn văn — Mục 2.6 | Bảng 2.3, Hình 2.2 | Trang 60–65]`.

---

### SLIDE 9 · GIAI ĐOẠN 2: MA TRẬN ĐỐI SOÁT C1 – C6 & KẾT QUẢ C5 (LÂM | 08:05 – 10:00)
* **Tiêu đề:** Giai đoạn 2 — Kết quả ma trận 6 cấu hình trên Benchmark A (N = 512 câu) & Trả lời RQ2
* **Luận điểm cốt lõi:** *C5 nâng Citation Accuracy trên ngữ cảnh lên 0,9902, giảm 79,9% dung lượng token; xác thực giả thuyết H2 theo nguyên lý cô lập biến số.*
* **Bố cục hiển thị:** Bảng ma trận Bảng 3.6 và 3 con số Headline nổi bật:
  * *Bảng số liệu 6 cấu hình (512 câu | 3.072 lượt chấm LLM-Judge):*
    * C1 (Naive BM25): Citation 0,7490 | Điểm 1,0: 72,5% | Token ~2.500
    * C2 (Naive Dense): Citation 0,4000 | Điểm 1,0: 25,4% | Token ~2.898
    * C3 (Naive Hybrid): Citation 0,3986 | Điểm 1,0: 25,6% | Token ~2.898
    * C4 (Parser BM25): Citation 0,9028 | Điểm 1,0: 89,3% | Token ~580
    * **C5 (Parser Dense): Citation 0,9902 | Điểm 1,0: 98,4% (504/512 câu) | Token ~580**
    * C6 (Parser Hybrid $alphalpha=0,5$): Citation 0,9786 | Điểm 1,0: 96,3% | Token ~580
  * *Ba kết quả đáng chú ý:*
    * **`0,9902` (Citation Acc C5 trên ngữ cảnh):** Tăng **+59,02 điểm phần trăm** so với C2 (0,4000). Có **504 / 512 câu đạt điểm tuyệt đối 1,0**.
    * **`-79,9%` (Tiết kiệm token):** Dung lượng giảm từ $\sim 2.898$ token xuống còn **$\sim 580$ token**.
    * **`α = 0,8` (Weighted RRF tối ưu tại Bảng 3.7):** Quét 11 giá trị $alphalpha$ từ 0,0 đến 1,0; $alphalpha=0,8$ đạt Recall **0,9297** và MRR **0,8220**, khắc phục hiện tượng cào bằng ở C6.
  * *Ghi chú phương pháp luận (Isolation of Variables):* Con số 32,59% ở GĐ1 đo trên câu trả lời; 0,9902 ở GĐ2 đo độc lập trên ngữ cảnh truy hồi để đánh giá thuần túy hiệu quả Parser mà không bị nhiễu bởi tính ngẫu nhiên của LLM. Đánh giá câu trả lời hoàn chỉnh được dành riêng cho GĐ3.
  * *Chốt hạ RQ2:* Phân đoạn cấu trúc vi mô kết hợp MaxP giải quyết triệt để bài toán trích dẫn ngữ cảnh và tối ưu chi phí tính toán.
* **Thẻ dẫn chứng:** `[Dẫn chứng: Báo cáo toàn văn — Mục 3.3 | Bảng 3.5, Bảng 3.6, Bảng 3.7 | Trang 96–101]`.

---

### SLIDE 10 · GIAI ĐOẠN 3: TRIẾT LÝ KIẾN TRÚC HYBRID UKG & MODULE 5 (MINH | 10:00 – 11:15)
* **Tiêu đề:** Giai đoạn 3 — Triết lý kiến trúc 2 tầng Hybrid Parser / UKG & Bộ định tuyến Module 5
* **Luận điểm cốt lõi:** *Tách biệt cấu trúc vật lý bất biến và ngữ nghĩa động; lập chỉ mục offline một lần, truy vấn online trong mili-giây.*
* **Bố cục hiển thị:** Sơ đồ dòng chảy 2 tầng:
  * *Tầng 1 — Đồ thị Cấu trúc vật lý (Physical Graph):* Khóa cứng 100% phả hệ Chương-Mục-Điều-Khoản-Điểm bằng bộ phân tích tất định, tạo trục xương sống độc lập với LLM.
  * *Tầng 2 — Đồ thị Ngữ nghĩa (Semantic Graph):* Trích xuất các thực thể và quan hệ pháp lý động (quyền, nghĩa vụ, điều kiện, ngoại lệ) gắn lên trục xương sống.
  * *Chi phí vận hành:* Xây dựng đồ thị là tác vụ Offline Indexing (chạy một lần duy nhất). Khi truy vấn trực tuyến, hệ thống chỉ duyệt đồ thị trên cơ sở dữ liệu đã lập trong mili-giây.
  * *Trọng tâm kỹ thuật Module 5 (Semantic Router):* 
    * Ứng dụng mô hình **Qwen2.5-0.5B** kết hợp toán tử **Max-Fusion** logic OR:  
      $$S_{	ext{fusion}} = \max(S_{	ext{regex}}, S_{	ext{semantic}})$$
    * Causal Attention của Qwen2.5-0.5B bảo toàn trật tự logic chủ thể $
ightarrow$ điều kiện $
ightarrow$ chế tài, khắc phục cạm bẫy Mean-Pooling của Bi-encoder trên phân đoạn ngắn.
    * Tại ngưỡng $	heta = 0,85$, hệ thống đạt **Recall 96,85%**, F1 đạt **0,8146**, loại bỏ an toàn 9,33% phân đoạn thủ tục trước khi chuyển sang trích xuất.
* **Thẻ dẫn chứng:** `[Tham chiếu: Báo cáo toàn văn — Mục 2.6 | Hình 2.2, Bảng 2.4 & Phụ lục A | Bảng A.1, A.2 | Trang 63, 128–130]`.

---

### SLIDE 11 · GIAI ĐOẠN 3: KẾT QUẢ ĐỐI CHUẨN TRÊN BENCHMARK B (MINH | 11:15 – 13:00)
* **Tiêu đề:** Giai đoạn 3 — Kết quả thực nghiệm Benchmark B (N = 50 câu) & Trả lời RQ3, RQ4
* **Luận điểm cốt lõi:** *UKG thể hiện ưu thế vượt trội ở tầng truy hồi và xử lý ngoại lệ pháp luật; minh bạch phân tích các trade-off kỹ thuật và ranh giới chuỗi dẫn chiếu.*
* **Bố cục hiển thị:** Bảng đối sánh trực diện đa chiều giữa LightRAG và Hybrid UKG (Bảng 3.9, 3.11, 3.15, 3.16):
  * *Bảng đối chuẩn tổng hợp (N = 50 câu: 47 câu truy hồi/chất lượng + 3 câu từ chối an toàn):*
    * **Recall@5 cấp Điều (Bảng 3.9):** UKG đạt **0,9184** vs LightRAG **0,7358** (**Vượt +18,26 điểm %**).
    * **MRR@5 cấp Điều (Bảng 3.9):** UKG đạt **0,8848** vs LightRAG **0,5539** (**Vượt +33,09 điểm %**).
    * **Citation Precision cấp Điều (Bảng 3.16):** UKG đạt **0,8369** vs LightRAG **0,3333** (**Gấp 2,5 lần**).
    * **Citation Recall cấp Điều (Bảng 3.16):** UKG đạt **0,9078** vs LightRAG **0,2961** (**Gấp hơn 3 lần**).
    * **Citation Precision cấp Khoản (Bảng 3.16):** UKG đạt **0,7757** vs LightRAG **0,0435** (**Gấp gần 18 lần**).
    * **Exception Coverage (Bảng 3.15):** UKG đạt **0,6786** vs LightRAG **0,3929** (**Vượt +28,57 điểm %** nhờ bóc tách chính xác mệnh đề "trừ trường hợp...").
    * **Subject-Scope Accuracy:** UKG đạt **0,8889** vs LightRAG **0,7639** (**Vượt +12,50 điểm %**).
    * **Legal Correctness:** UKG đạt **0,8777** vs LightRAG **0,8210** (**Vượt +5,67 điểm %**).
  * *Minh bạch hai Trade-off kỹ thuật:*
    * **Condition Coverage (Bảng 3.15):** LightRAG đạt **0,8421** vs UKG đạt **0,7066** ($-13,55$ đpt). Lý do: LightRAG dùng chunk 1.200 token lớn bao phủ rộng; UKG tập trung quy phạm lõi nên cần thêm cơ chế lan truyền điều kiện.
    * **Exact Locator Recall@5 (*) (Bảng 3.11):** LightRAG đạt **0,8509** vs UKG đạt **0,5560**.
  * *Footnote hiển thị dưới chân slide:*  
    `(*) Exact Locator đo mức trùng khớp chuỗi ký tự cục bộ; UKG ưu tiên tính toàn vẹn của thực thể quy phạm cấp Điều (Citation Precision cấp Điều đạt 0,8369 so với 0,3333 của LightRAG).`  
    `(**) Quy mô mẫu phân tầng theo Bảng 3.16: Cấp Điều có N = 47; Cấp Khoản có N = 46 (1 câu không có nhãn Khoản); Cấp Điểm có N = 37 (10 câu căn cứ dừng ở cấp Khoản, không có Điểm). Không gán điểm 0 cho trường hợp không áp dụng.`
  * *Kết quả giải quyết RQ4 (Bảng 3.14):* Định vị tốt các node đích với Reference-target Recall đạt **58,67%**. Việc tái dựng chuỗi có thứ tự cần thêm cơ chế Constrained Graph Traversal (trên 18 câu dẫn chiếu, Chain Exact Match ghi nhận $0,0000$).
* **Thẻ dẫn chứng:** `[Dẫn chứng: Báo cáo toàn văn — Mục 3.4, 3.6, 3.7 | Bảng 3.9, Bảng 3.11, Bảng 3.14, Bảng 3.15, Bảng 3.16 | Trang 103–112]`.

---

### SLIDE 12 · TỔNG HỢP KẾT QUẢ THEO BỐN CÂU HỎI NGHIÊN CỨU (MINH | 13:00 – 13:55)
* **Tiêu đề:** Tổng hợp kết quả thực nghiệm giải quyết 4 câu hỏi nghiên cứu (RQ1 – RQ4)
* **Luận điểm cốt lõi:** *Đóng gói đanh thép câu trả lời cho cả bốn bài toán khoa học đặt ra ở đầu đề tài.*
* **Bố cục hiển thị:** Bảng ma trận 4 khối đối ứng:
  * **Trả lời RQ1:** Xác lập khoảng cách giữa truy hồi và trích dẫn: RAG cơ sở đạt Recall trên 95% nhưng Citation Accuracy câu trả lời chỉ khoảng 30% (LightRAG ghi nhận 13,71%) do cắt đoạn thô làm đứt gãy phả hệ pháp lý.
  * **Trả lời RQ2:** Parser v2 và MaxP nâng Citation Accuracy trên ngữ cảnh lên **0,9902** (98,4% tuyệt đối) và tiết kiệm **79,9% token**, xác định điểm cân bằng Weighted RRF tại $alphalpha=0,8$.
  * **Trả lời RQ3:** Hybrid UKG vượt trội LightRAG ở truy hồi cấp Điều (Recall +18,26 đpt, MRR +33,09 đpt), độ chính xác trích dẫn cấp Điều gấp 2,5 lần (0,8369 vs 0,3333) và độ phủ ngoại lệ (+28,57 đpt).
  * **Trả lời RQ4:** Định vị tốt các node đích (58,67%); việc tái dựng chuỗi hoàn chỉnh cần thêm cơ chế constrained graph traversal, xác lập ranh giới cho giai đoạn nghiên cứu tiếp theo.
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

> **Nguyên tắc vàng:**  
> - Tổng số từ nói thực tế: **~1.850 từ** (Tốc độ chuẩn: 125–130 từ/phút).  
> - Thời gian trình bày: **14 phút 30 giây** (Dư 30 giây đệm an toàn).  
> - Giữ phong thái **Precise Confidence**: Tự tin, đĩnh đạc, dựa trên số liệu thực chứng, không cường điệu hoá.

---

### [00:00 – 01:30] · CHẶNG 1: LƯU THANH LÂM (MỞ MÀN & ĐẶT VẤN ĐỀ)

**[Slide 1 — Bìa báo cáo · 00:00 – 00:20 | 59 từ]**
> *"Kính thưa Hội đồng khoa học!  
> Em xin đại diện nhóm tác giả gồm: Lưu Thanh Lâm, Ngô Thế Dương và Nguyễn Bình Minh, dưới sự hướng dẫn của TS. Nguyễn Mạnh Dũng, trình bày đề tài:  
> **'Đánh giá và tối ưu hóa các kiến trúc RAG trên nền tảng dữ liệu cấu trúc đặc thù'**, tập trung vào văn bản pháp luật Việt Nam."*

**[Slide 2 — Bối cảnh & Thách thức căn cứ pháp lý · 00:20 – 01:30 | 148 từ]**
> *"Kính thưa Hội đồng, tra cứu pháp luật đòi hỏi kiểm chứng tuyệt đối: câu trả lời bắt buộc phải có căn cứ chính xác đến từng điều khoản cụ thể.  
> Tuy nhiên, công bố của Magesh và cộng sự (2025) trên tạp chí JELS chỉ ra rằng các hệ thống AI thương mại hàng đầu vẫn gặp tỷ lệ ảo giác pháp lý từ 17% đến 33%.  
> Trong thực tế, chỉ cần trích dẫn đúng số Điều nhưng sai một Khoản hay bỏ sót một ngoại lệ tại một Điểm, hệ quả pháp lý có thể đảo lộn hoàn toàn từ hợp pháp sang vi phạm.  
> Nhóm đặt ra bài toán cốt lõi: Làm sao vừa tối ưu truy hồi, vừa giúp LLM xác định chính xác căn cứ vi mô mà không bùng nổ chi phí tính toán?  
> Sau đây, xin mời bạn Ngô Thế Dương trình bày đặc thù dữ liệu."*  
*(Lâm chuyển micro cho Dương).*

---

### [01:30 – 05:15] · CHẶNG 2: NGÔ THẾ DƯƠNG (ĐẶC THÙ, LÝ THUYẾT & HẠ TẦNG BENCHMARK)

**[Slide 3 — Đặc thù luật & Khoảng trống · 01:30 – 02:25 | 114 từ]**
> *"Em xin cảm ơn bạn Lâm. Kính thưa Quý Thầy Cô,  
> Văn bản luật Việt Nam có ba đặc thù kiến trúc: Một là cấu trúc phân cấp đa tầng từ Luật, Chương đến Điều, Khoản, Điểm; nội dung ở Điểm luôn phụ thuộc chặt chẽ vào chủ thể ở cấp trên. Hai là mạng lưới dẫn chiếu chéo phức tạp quy định điều kiện và ngoại lệ. Ba là sự lệch pha từ vựng lớn giữa câu hỏi của người dân và thuật ngữ chuẩn tắc.  
> Từ đó xuất hiện ba khoảng trống nghiên cứu: Thiếu chuẩn benchmark không rò rỉ từ vựng; thiếu giải pháp phân đoạn bảo toàn phả hệ; và thiếu thước đo trích dẫn phân tầng vi mô."*

**[Slide 4 — Cơ sở lý thuyết: Ba trường phái RAG · 02:25 – 03:20 | 108 từ]**
> *"Để giải quyết các khoảng trống đó, nhóm khảo sát ba trường phái RAG đại diện:  
> Thứ nhất, Naive Vector RAG dùng embedding BGE-M3 và Cosine similarity, mạnh về ngữ nghĩa khái quát nhưng dễ nhầm các điều khoản tương tự.  
> Thứ hai, Hybrid RAG dung hợp BM25 và Dense qua thuật toán RRF kết hợp Cross-Encoder Reranker, cải thiện khả năng bắt từ khóa định danh.  
> Thứ ba, LightRAG đại diện cho GraphRAG, trích xuất đồ thị thực thể bằng LLM để kết nối tri thức hai tầng.  
> Cả ba trường phái đều chưa được kiểm chứng hệ thống trên văn bản luật Việt Nam với yêu cầu trích dẫn khắt khe."*

**[Slide 5 — Hệ thống 4 Câu hỏi nghiên cứu RQ1 – RQ4 · 03:20 – 04:05 | 96 từ]**
> *"Từ đó, nhóm xây dựng bốn câu hỏi nghiên cứu định hướng:  
> RQ1: Hiệu năng truy hồi và trích dẫn của các RAG cơ sở khác biệt thế nào khi cắt đoạn thô?  
> RQ2: Bộ phân tích cấu trúc Parser v2 và giải thuật MaxP cải thiện độ chính xác trích dẫn và chi phí ra sao?  
> RQ3: Kiến trúc đồ thị hai tầng Hybrid UKG nâng cao hiệu quả truy hồi và xử lý ngoại lệ phức tạp thế nào so với GraphRAG?  
> RQ4: Khả năng định vị và tái dựng chuỗi dẫn chiếu chéo nhiều bước đạt mức độ nào?"*

**[Slide 6 — Thiết kế thực nghiệm & Hạ tầng Benchmark · 04:05 – 05:15 | 140 từ]**
> *"Để trả lời bốn RQ, nhóm xây dựng Benchmark Harness chuẩn hóa giao diện Adapter Pattern, đóng băng toàn bộ biến ngoại lai: cùng ngữ liệu, cùng embedding BGE-M3 và LLM thế hệ GPT-4o-mini.  
> Nhóm biên soạn hai bộ kiểm chuẩn độc lập:  
> Benchmark A gồm 512 câu hỏi phủ 7 đạo luật trọng điểm, viết lại chọn lọc đưa Jaccard trung bình từ 0,68 xuống 0,31 để loại bỏ triệt để thiên lệch học vẹt từ khóa.  
> Benchmark B gồm 50 câu hỏi phân tầng tại Chương III Luật Đất đai 2024 để kiểm tra chuyên sâu đa điều kiện, ngoại lệ và dẫn chiếu.  
> Sau đây, xin mời bạn Lâm trình bày kết quả."*  
*(Dương chuyển micro cho Lâm).*

---

### [05:15 – 10:00] · CHẶNG 3: LƯU THANH LÂM (GIAI ĐOẠN 1 NGHỊCH LÝ & GIAI ĐOẠN 2 ĐỘT PHÁ)

**[Slide 7 — Giai đoạn 1: Nghịch lý sụp đổ trích dẫn · 05:15 – 06:40 | 162 từ]**
> *"Em xin cảm ơn bạn Dương. Kính thưa Hội đồng,  
> Đối soát công bằng ba kiến trúc RAG trên tập Tier 1 gồm 205 câu hỏi, nhóm phát hiện khoảng cách giữa truy hồi và trích dẫn:  
> Tại Bảng 3.4, cả ba hệ thống đều tìm kiếm rất tốt: Recall@5 vượt 95%, Context Precision Naive và Hybrid trên 0,96, LightRAG đạt 0,8829.  
> Tuy nhiên, Citation Accuracy sụt giảm nghiêm trọng: Naive Vector chỉ đạt 32,59%, Hybrid đạt 29,02%, và LightRAG chỉ 13,71%.  
> Nguyên nhân: cắt khối thô 1.200 token làm đứt gãy phả hệ; Điểm trích dẫn bị tách rời tên Điều và Chương, khiến LLM mất căn cứ xác lập vị trí pháp lý.  
> Kết quả này trả lời cho RQ1: RAG cơ sở thất bại ở trích dẫn nếu giữ nguyên cắt đoạn thô."*

**[Slide 8 — Giai đoạn 2: Parser v2 & Article MaxP · 06:40 – 08:05 | 155 từ]**
> *"Để khắc phục đứt gãy phả hệ, bước sang Giai đoạn 2, nhóm đề xuất giải pháp cấu trúc gồm hai thành phần:  
> Thứ nhất là Structure-Aware Parser v2. Parser bóc tách đệ quy văn bản luật thành 12.754 phân đoạn vi mô theo từng cấp Khoản, Điểm, đồng thời gán tiền tố bất biến chứa đầy đủ phả hệ từ tên Luật, Chương đến Điều vào từng phân đoạn.  
> Thứ hai, để xử lý việc phân đoạn nhỏ làm bão hòa cửa sổ Top-K bởi nhiều Khoản trong cùng một Điều, nhóm đề xuất giải thuật Article-Level Max-Pooling (MaxP). Hệ thống gom cụm các phân đoạn theo Điều và lấy điểm cực đại của phân đoạn đại diện để xếp hạng Top-K cấp Điều; sau đó tái cấu trúc ngữ cảnh cục bộ gồm đúng các phân đoạn liên quan nhất gửi sang LLM.  
> Giải pháp này vừa thu hẹp ngữ cảnh, vừa bảo toàn tính toàn vẹn pháp lý."*

**[Slide 9 — Giai đoạn 2: Ma trận C1–C6 & Đột phá C5 · 08:05 – 10:00 | 225 từ]**
> *"Trên 512 câu hỏi Benchmark A với 3.072 lượt thẩm định bằng LLM-Judge, kết quả tại Bảng 3.6 làm sáng tỏ RQ2 với ba điểm cốt lõi:  
> Thứ nhất, cấu hình C5 (Parser kết hợp Dense) nâng Citation Accuracy trên ngữ cảnh từ 0,4000 ở C2 lên 0,9902 (+59,02 đpt), với 98,4% số câu đạt điểm tuyệt đối 1,0.  
> Thứ hai, nhờ phân đoạn vi mô và MaxP, dung lượng token ngữ cảnh giảm mạnh 79,9%, từ gần 2.900 token xuống chỉ còn 580 token, giảm mạnh chi phí API và độ trễ.  
> Thứ ba, tại Bảng 3.7 qua quét 11 giá trị alpha, nhóm xác định điểm cân bằng Weighted RRF tại alpha = 0,8 đạt Recall 0,9297 và MRR 0,8220, khắc phục hiện tượng cào bằng ở C6.  
> Nhóm nhấn mạnh nguyên tắc Cô lập biến số (Isolation of Variables): Con số 32,59% ở GĐ1 đo trên câu trả lời, còn 0,9902 ở GĐ2 đo trên ngữ cảnh truy hồi để kiểm chứng thuần túy hiệu năng của Parser mà không bị nhiễu bởi tính ngẫu nhiên của LLM.  
> Sau đây, xin mời bạn Nguyễn Bình Minh trình bày Giai đoạn 3."*  
*(Lâm chuyển micro cho Minh).*

---

### [10:00 – 15:00] · CHẶNG 4: NGUYỄN BÌNH MINH (ĐỒ THỊ UKG, ĐA BƯỚC & KẾT LUẬN)

**[Slide 10 — Giai đoạn 3: Kiến trúc Hybrid UKG & Module 5 · 10:00 – 11:15 | 155 từ]**
> *"Em xin cảm ơn bạn Lâm. Kính thưa Quý Thầy Cô,  
> Để xử lý truy vấn đa bước và quy phạm ngoại lệ, nhóm xây dựng Hybrid UKG với triết lý tách biệt hai tầng:  
> Tầng 1 là Đồ thị vật lý (Physical Graph) — khóa cứng bất biến 100% phả hệ văn bản luật bằng bộ phân tích tất định.  
> Tầng 2 là Đồ thị ngữ nghĩa (Semantic Graph) — trích xuất động các quan hệ dẫn chiếu, điều kiện và ngoại lệ.  
> Đồ thị được lập chỉ mục offline một lần; khi truy vấn online, hệ thống duyệt đồ thị trong mili-giây.  
> Trọng tâm là Module 5 Semantic Router: Ứng dụng Qwen2.5-0.5B kết hợp Max-Fusion logic OR giữa Regex và Vector. Causal Attention bảo toàn logic chủ thể - điều kiện - chế tài, khắc phục cạm bẫy Mean-Pooling của Bi-encoder. Tại ngưỡng theta = 0,85, hệ thống đạt Recall 96,85%, F1 0,8146, loại an toàn 9,33% phân đoạn thủ tục."*

**[Slide 11 — Giai đoạn 3: Thực nghiệm Benchmark B · 11:15 – 13:00 | 235 từ]**
> *"Kính thưa Hội đồng, thực nghiệm Benchmark B gồm 50 câu hỏi tại Chương III Luật Đất đai 2024 làm sáng tỏ RQ3 và RQ4:  
> Về RQ3 — năng lực định vị và xử lý quy phạm:  
> Ở tầng truy hồi cấp Điều (Bảng 3.9), Hybrid UKG đạt Recall@5 0,9184 vs 0,7358 của LightRAG (vượt +18,26 đpt) và MRR@5 đạt 0,8848 vs 0,5539 (vượt +33,09 đpt).  
> Ở tầng trích dẫn câu trả lời (Bảng 3.16), Citation Precision cấp Điều đạt 0,8369 vs 0,3333 của LightRAG (gấp 2,5 lần); cấp Khoản đạt 0,7757 vs 0,0435 (gấp 18 lần).  
> Ở tầng nội dung (Bảng 3.15), Legal Correctness đạt 0,8777 và đặc biệt Exception Coverage đạt 0,6786 — vượt LightRAG 28,57 điểm phần trăm nhờ bóc tách chính xác mệnh đề ngoại lệ.  
> Về mặt trade-off: Condition Coverage của UKG đạt 0,7066 vs 0,8421 của LightRAG do chunk lớn vô tình gom nhiều điều kiện; và Exact Locator Recall@5 tại Bảng 3.11 LightRAG cao hơn (0,8509 vs 0,5560) do đo khớp chuỗi ký tự cục bộ, trong khi UKG ưu tiên toàn vẹn thực thể cấp Điều.  
> Về RQ4: UKG định vị tốt node đích với Reference-target Recall 58,67%. Tái dựng chuỗi thứ tự cần thêm giải thuật Constrained Graph Traversal (Chain Exact Match đạt 0,0000 trên 18 câu)."*

**[Slide 12 — Tổng kết: Đóng gói 4 Câu hỏi nghiên cứu · 13:00 – 13:55 | 125 từ]**
> *"Tổng hợp lại từ ba giai đoạn, nhóm đã đóng gói lời giải cho bốn bài toán nghiên cứu:  
> RQ1: Xác lập khoảng cách giữa truy hồi và trích dẫn, chỉ ra nguyên nhân đứt gãy phả hệ của việc cắt đoạn thô.  
> RQ2: Chứng minh Parser v2 và MaxP nâng Citation Accuracy ngữ cảnh lên 0,9902, giảm 79,9% token, xác lập alpha = 0,8 tối ưu.  
> RQ3: Hybrid UKG vượt trội LightRAG ở truy hồi cấp Điều (Recall +18,26 đpt, MRR +33,09 đpt), độ chính xác trích dẫn cấp Điều gấp 2,5 lần (0,8369 vs 0,3333) và độ bao phủ ngoại lệ (+28,57 đpt).  
> RQ4: Định vị tốt căn cứ đích (58,67%), chỉ rõ ranh giới cần giải thuật duyệt đồ thị có ràng buộc để khép kín chuỗi dẫn chiếu."*

**[Slide 13 — Ba đóng góp khoa học chính · 13:55 – 14:35 | 110 từ]**
> *"Từ các kết quả trên, đề tài đóng góp ba giá trị cốt lõi:  
> Một là Khung kiểm chuẩn Benchmark A và B cùng Adapter Pattern loại bỏ thiên lệch thực nghiệm.  
> Hai là Giải pháp phân đoạn vi mô phối hợp Parser v2 và MaxP, giải quyết triệt để sụt giảm trích dẫn và tối ưu chi phí.  
> Ba là Kiến trúc đồ thị hai tầng Hybrid UKG, chứng minh hiệu quả phân tách cấu trúc vật lý và ngữ nghĩa động trong xử lý quy phạm ngoại lệ.  
> Thông điệp cốt lõi của đề tài là: Trong pháp luật, cấu trúc không phải là chi tiết triển khai — nó là điều kiện tiên quyết để AI trích dẫn đúng."*

**[Slide 14 — Hướng phát triển & Kết thúc · 14:35 – 15:00 | 58 từ]**
> *"Trong thời gian tới, nhóm hướng đến mở rộng sang Nghị định, Thông tư; tự động hóa cập nhật hiệu lực; và hoàn thiện giải thuật constrained graph traversal.  
> Thay mặt nhóm, chúng em xin trân trọng cảm ơn Quý Thầy Cô đã chú ý lắng nghe. Nhóm kính mời Hội đồng đặt câu hỏi."*  
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
| **6** | **Dương** | 70s | • Benchmark Harness + Adapter Pattern cố định biến ngoại lai<br>• BM-A 512 câu (Jaccard 0,68 $	o$ 0,31); BM-B 50 câu phân tầng | Chỉ laser vào **chỉ số Jaccard 0,31** và **cấu trúc 50 câu Benchmark B** | *"Sau đây xin mời bạn Lâm trình bày kết quả Giai đoạn 1 và 2."* |
| **7** | **Lâm** | 85s | • Nghịch lý GĐ1: Recall > 95% nhưng Citation chỉ ~30% (LightRAG 13,71%)<br>• Cắt đoạn thô 1.200 token làm đứt gãy phả hệ; chốt RQ1 | Chỉ laser vào **Bảng 3.4**, nhấn vào hàng Citation Accuracy | *(Nói liền mạch sang Slide 8)* |
| **8** | **Lâm** | 85s | • Parser v2 bóc tách 12.754 phân đoạn vi mô + tiền tố bất biến<br>• Giải thuật Article MaxP chống bão hòa Top-K | Quét laser theo luồng: **Phân đoạn vi mô $
ightarrow$ Tiền tố $
ightarrow$ Article MaxP** | *(Nói liền mạch sang Slide 9)* |
| **9** | **Lâm** | 115s | • **[Slide đinh] Ma trận C1–C6: C5 đạt 0,9902** (+59,02 đpt)<br>• Tiết kiệm **79,9% token**; Weighted RRF $alphalpha=0,8$ tối ưu<br>• Cô lập biến số (Isolation of Variables) | Chỉ laser vào số **0,9902**, số **-79,9%**, và điểm **$alphalpha = 0,8$** | *"Sau đây xin mời bạn Nguyễn Bình Minh trình bày kiến trúc UKG và kết quả Giai đoạn 3."* |
| **10** | **Minh** | 75s | • Kiến trúc UKG: Tầng vật lý (khóa cứng phả hệ) + Tầng ngữ nghĩa (trích xuất động)<br>• Indexing offline 1 lần; Module 5 Causal Router tại $	heta=0,85$ (Recall 96,85%) | Chỉ laser vào sơ đồ 2 tầng và khối **Module 5** | *(Nói liền mạch sang Slide 11)* |
| **11** | **Minh** | 105s | • **[Slide đinh] Benchmark B (RQ3 & RQ4)**<br>• RQ3: Recall 0,9184 (+18,26 đpt), Citation Precision Điều 0,8369 vs 0,3333, Exception Coverage 0,6786 (+28,57 đpt)<br>• Trade-off Condition Coverage & Exact Locator; RQ4 ranh giới chuỗi<br>• [Phao N]: Cấp Điều N=47, Khoản N=46, Điểm N=37 (nhãn dừng ở cấp trên) | Chỉ laser vào số **0,9184**, số **0,8369**, số **+28,57 đpt**, và footnote trade-off | *(Nói liền mạch sang Slide 12)* |
| **12** | **Minh** | 55s | • Bo 4 RQ: RQ1 (sụt giảm trích dẫn), RQ2 (Parser v2 + MaxP 0,9902), RQ3 (UKG vượt trội ngoại lệ), RQ4 (ranh giới chuỗi) | Quét laser lần lượt qua **4 khối RQ** đã được giải quyết | *(Nói liền mạch sang Slide 13)* |
| **13** | **Minh** | 40s | • 3 Đóng góp: Khung Benchmark, Phân đoạn vi mô, Kiến trúc UKG 2 tầng<br>• Takeaway: Cấu trúc là điều kiện tiên quyết để trích dẫn đúng | Chỉ laser vào **Hộp thông điệp cốt lõi** | *(Nói liền mạch sang Slide 14)* |
| **14** | **Minh** | 25s | • Hướng phát triển: Nghị định, Thông tư, Constrained Graph Traversal<br>• Lời cảm ơn trang trọng | Mắt hướng về Thầy Chủ tịch Hội đồng, chuyển sang thế sẵn sàng Q&A | Cả nhóm cúi đầu chào Hội đồng |

---
---

# PHẦN 4: HỒ SƠ PHÒNG THỦ VẤN ĐÁP (Q&A DEFENSE PLAYBOOK)
## 18 CÂU HỎI PHẢN BIỆN TRỌNG YẾU & MẪU CÂU TRẢ LỜI ĐANH THÉP (20 – 30 GIÂY)

> **Quy tắc vàng khi trả lời phản biện:**
> 1. Luôn cảm ơn Thầy/Cô: *"Dạ em xin cảm ơn Thầy/Cô đã đặt một câu hỏi rất sâu sắc về..."*.
> 2. Đi thẳng vào bản chất kỹ thuật trong câu đầu tiên, không vòng vo.
> 3. Trả lời dứt khoát trong 20 – 30 giây, trung thực 100% theo đúng báo cáo, kết thúc bằng một khẳng định có chừng mực.

---

### NHÓM 1: CÂU HỎI VỀ PHƯƠNG PHÁP LUẬN & ĐO LƯỜNG (LÂM & DƯƠNG PHỤ TRÁCH)

**Câu 1 (Lâm): "Citation Accuracy ở Giai đoạn 1 và Giai đoạn 2 có định nghĩa giống nhau không? Tại sao lại có sự chênh lệch lớn từ 32% lên 99%?"**
> *"Dạ đây là hai phép đo độc lập phục vụ hai mục tiêu khác nhau theo nguyên lý Cô lập biến số (Isolation of Variables).  
> Ở Giai đoạn 1, chỉ số đo trên câu trả lời sinh ra của LLM nhằm chẩn đoán xem RAG cơ sở có trích dẫn đúng căn cứ hay không.  
> Sang Giai đoạn 2, nhóm chủ động cô lập tầng sinh của LLM để đánh giá thuần túy hiệu năng của Parser trên ngữ cảnh truy hồi bằng LLM-as-a-Judge.  
> Nhóm không so sánh trực tiếp 32% với 99%. Phép so sánh công bằng và có cơ sở khoa học là giữa C2 (0,4000) và C5 (0,9902) trong cùng Giai đoạn 2 trên cùng một thước đo ngữ cảnh. Đánh giá sinh toàn trình được dành trọn vẹn cho Giai đoạn 3."*

**Câu 2 (Lâm): "Trong Giai đoạn 2, các em thay đổi nhiều thành phần cùng lúc (micro-chunk, prefix, MaxP). Thành phần nào đóng góp chính?"**
> *"Dạ đây là một điểm nhóm đã ghi nhận tại Mục 3.3.9 của báo cáo. Kết quả vượt trội của C5 là tác động tổng hợp của cả gói giải pháp cấu trúc: phân đoạn vi mô giúp thu hẹp phạm vi, tiền tố bất biến bảo toàn phả hệ cha-con, và MaxP giải quyết bão hòa Top-K.  
> Thiết kế hiện tại chưa cô lập tác động riêng của từng thành phần đơn lẻ, và nhóm xác định việc chạy thêm các cấu hình ablation độc lập là hướng nghiên cứu ưu tiên tiếp theo."*

**Câu 3 (Dương): "Các em dùng GPT-4o-mini vừa sinh câu trả lời vừa làm giám khảo. Kết quả có bị thiên lệch tự thân không?"**
> *"Dạ thưa Thầy/Cô, đây là một hạn chế phương pháp luận đã được nhóm ghi nhận trung thực tại Mục 3.8.3. Ở Giai đoạn 1 và 2, Citation Accuracy được chấm bằng LLM-as-a-Judge (GPT-4o-mini) — cùng họ mô hình với mô hình sinh, nên chưa đạt tính độc lập tuyệt đối về mô hình. Nhóm đã giảm thiểu bằng cách tách biệt hoàn toàn prompt thẩm định, bắt buộc kiểm tra JSON schema, ghi log kiểm toán và thiết lập cơ chế thử lại tối đa 3 lần khi định dạng không hợp lệ.  
> Đặc biệt sang Giai đoạn 3, các chỉ số Citation Precision và Recall tại Bảng 3.16 đã được chuyển đổi hoàn toàn sang phương pháp tính toán tất định dựa trên quy tắc (Rule-based Locator Matching), không còn phụ thuộc vào LLM chấm. Hướng hoàn thiện tiếp theo là sử dụng mô hình thẩm định độc lập từ nhà phát triển khác hoặc mời chuyên gia pháp lý chấm mẫu để hiệu chuẩn."*

**Câu 4 (Dương): "Việc viết lại 512 câu hỏi ở Benchmark A có làm biến đổi ngữ nghĩa pháp lý gốc không?"**
> *"Dạ quy trình viết lại tại Mục 2.3.5 được thiết kế với nguyên tắc bất biến ngữ nghĩa: chỉ thay đổi từ ngữ diễn đạt của người dân, giữ nguyên căn cứ pháp lý đích. Nhóm thực hiện viết lại có chọn lọc trên các câu có độ trùng lặp từ vựng Jaccard vượt ngưỡng 0,5, đưa chỉ số trùng lặp trung bình từ 0,68 xuống 0,31 để loại bỏ hiện tượng học vẹt từ khóa.  
> Báo cáo cũng ghi nhận hạn chế là chưa có nhật ký xác nhận toàn bộ 512 câu đều viết lại thành công, và việc xây dựng pipeline kiểm tra ngữ nghĩa tự động cho toàn bộ tập dữ liệu là hướng nghiên cứu hoàn thiện tiếp theo."*

**Câu 5 (Dương): "Tại sao ở Giai đoạn 1 nhóm chỉ đánh giá trên 205 câu hỏi Tier 1 mà không dùng toàn bộ 512 câu?"**
> *"Dạ đây là thiết kế fair-play có chủ đích được giải thích tại Mục 3.2.1.  
> LightRAG cần đồ thị tri thức trích xuất hoàn chỉnh, và tại Giai đoạn 1 chỉ mục đồ thị bao phủ trọn vẹn tập văn bản của 205 câu hỏi Tier 1.  
> Để so sánh công bằng và khoa học nhất giữa ba kiến trúc cơ sở, nhóm bắt buộc phải đưa cả ba hệ thống về cùng một sân chơi với đầy đủ dữ liệu nguồn, tránh việc đánh giá thấp LightRAG do thiếu hụt chỉ mục cục bộ."*

---

### NHÓM 2: CÂU HỎI VỀ KẾT QUẢ THỰC NGHIỆM & ĐỐI SÁNH (LÂM & MINH PHỤ TRÁCH)

**Câu 6 (Lâm): "Tại sao LightRAG lại đạt Citation Accuracy thấp như vậy ở Giai đoạn 1 (chỉ 13,71%)?"**
> *"Dạ nguyên nhân kỹ thuật nằm ở việc LightRAG tổ chức tri thức dạng đồ thị thực thể tự do mà không gắn chặt vào phả hệ văn bản luật.  
> Khi trích xuất các node thực thể, mô hình gom thông tin từ nhiều câu khác nhau nhưng làm mất đi tiền tố cấu trúc Điều và Khoản.  
> Khi sinh câu trả lời, mô hình nắm được khái niệm pháp lý nhưng không còn đủ căn cứ định danh để trích dẫn chính xác, dẫn đến điểm Citation Accuracy sụt giảm dù Recall vẫn đạt trên 95%."*

**Câu 7 (Minh): "Exact Locator Recall@5 của UKG chỉ đạt 0,5560, thấp hơn LightRAG (0,8509). Tại sao lại như vậy?"**
> *"Dạ đây là một trade-off kiến trúc có chủ đích đã được phân tích tại Mục 3.5.3.  
> Chỉ số Exact Locator tại Bảng 3.11 đo lường sự trùng khớp chuỗi ký tự cục bộ. LightRAG sử dụng các chunk cắt theo token nên dễ gom trúng chuỗi ký tự, nhưng làm mất tính toàn vẹn pháp lý.  
> Ngược lại, UKG ưu tiên tính toàn vẹn của thực thể quy phạm cấp Điều. Nhờ sự đánh đổi này, khi đánh giá câu trả lời thực tế tại Bảng 3.16, Citation Precision cấp Điều của UKG đạt 0,8369 — vượt trội gấp 2,5 lần so với 0,3333 của LightRAG, và cấp Khoản đạt 0,7757 so với 0,0435 của LightRAG."*

**Câu 8 (Minh): "Condition Coverage của UKG đạt 0,7066, thấp hơn LightRAG (0,8421). Nhóm giải thích thế nào?"**
> *"Dạ kết quả này phản ánh hai triết lý tổ chức ngữ cảnh đối nghịch nhau.  
> LightRAG sử dụng các đoạn cắt lớn 1.200 token nên vô tình bao hàm nhiều điều kiện lân cận trong văn bản; nhưng nhược điểm là làm loãng ngữ cảnh và bỏ sót ngoại lệ — Exception Coverage của LightRAG chỉ đạt 0,3929.  
> UKG tập trung vào đơn vị quy phạm lõi nên đạt Exception Coverage vượt trội 0,6786 (+28,57 điểm phần trăm). Để nâng cao Condition Coverage, hướng hoàn thiện tiếp theo của nhóm là bổ sung cơ chế lan truyền điều kiện giữa các node con và node lân cận trong đồ thị."*

**Câu 9 (Minh): "Chỉ số Chain Exact Match bằng 0 trên 18 câu hỏi. Vậy đề tài có giải quyết được bài toán dẫn chiếu không?"**
> *"Dạ nhóm nhìn nhận con số 0% này là một đóng góp chẩn đoán quan trọng của đề tài.  
> Kết quả cho thấy: Hệ thống định vị rất tốt căn cứ đích với Reference-target Recall đạt 58,67%. Tuy nhiên, việc tự động xâu chuỗi toàn bộ các mắt xích theo đúng thứ tự logic mà không bị chệch hướng đòi hỏi thuật toán duyệt đồ thị có ràng buộc (Constrained Graph Traversal).  
> Kết quả thực nghiệm xác lập rõ ràng rằng LLM không thể tự suy diễn bắc cầu nếu thiếu giải thuật định hướng đồ thị, và nhóm đã xác định đây là trọng tâm nghiên cứu tiếp theo."*

**Câu 10 (Lâm): "Việc cắt nhỏ văn bản thành 12.754 phân đoạn vi mô và giảm 79,9% token có làm mất mát thông tin ngữ cảnh không?"**
> *"Dạ hoàn toàn không mất mát thông tin ạ.  
> Nhóm áp dụng kỹ thuật Tiền tố bất biến: Mỗi phân đoạn vi mô dù chỉ là một Điểm nhưng luôn mang theo đầy đủ thông tin về Luật, Chương và Điều cha.  
> Đồng thời, giải thuật Article MaxP cho phép tái cấu trúc ngữ cảnh cục bộ gồm đúng các phân đoạn có liên quan nhất thuộc Điều đó trước khi gửi vào prompt. Vì vậy, hệ thống vừa loại bỏ được các đoạn văn thủ tục dư thừa, vừa bảo toàn trọn vẹn ngữ cảnh quy phạm cốt lõi."*

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

---

### NHÓM 4: CÂU HỎI KỸ THUẬT CNTT & TRIỂN KHAI HỆ THỐNG (PTIT DEFENSE PACK)

**Câu 16 (Minh): "Chi phí xây dựng UKG bằng LLM tốn kém thế nào? Hệ thống có scale phục vụ 1.000 người dùng đồng thời được không?"**
> *"Dạ thưa Thầy/Cô, việc trích xuất và xây dựng UKG là **quá trình lập chỉ mục ngoại tuyến (Offline Indexing)**, chỉ chạy một lần duy nhất khi nạp văn bản luật mới vào hệ thống, hoàn toàn không chạy lại trong thời gian thực.  
> Khi phục vụ người dùng tra cứu trực tuyến (Online Inference), hệ thống chỉ thực hiện duyệt đồ thị trên cơ sở dữ liệu đã dựng và truy hồi vector trong mili-giây, chi phí LLM lúc này chỉ nằm ở bước sinh câu trả lời.  
> Về bài toán chịu tải đồng thời 1.000 người dùng, do tầng truy hồi đồ thị đã được phân tách độc lập, hệ thống hoàn toàn có thể scale theo kiến trúc microservices thông thường; tuy nhiên nhóm xin ghi nhận và sẽ triển khai benchmark đo tải đồng thời trong hướng phát triển tiếp theo."*

**Câu 17 (Dương): "Nếu văn bản luật scan bị lỗi OCR (mất dấu, sai định dạng), Parser có bị vỡ trận không?"**
> *"Dạ thưa Thầy/Cô, đây chính là thách thức điển hình của các phương pháp phân tích dựa trên luật (Rule-based).  
> Trong kiến trúc của nhóm tại Mục 2.6.3, **Mô-đun 3 (Validation)** được thiết kế để kiểm tra tính toàn vẹn theo schema, thứ bậc và tính duy nhất. Khi Regex không nhận diện được do lỗi định dạng nghiêm trọng, **hệ thống thực hiện cơ chế cách ly node lỗi và ghi log cảnh báo, kiên quyết không tự ý sửa nội dung thiếu căn cứ**.  
> Trong phiên bản hiện tại, node bị lỗi có thể không xuất hiện trong đồ thị ngữ nghĩa; việc tích hợp mô hình sửa lỗi chính tả tiền xử lý OCR và phân đoạn mềm (semantic boundary) là hướng nghiên cứu nhóm đang tiếp tục hoàn thiện."*

**Câu 18 (Dương): "Hệ số kết hợp BM25 và Vector $alphalpha = 0,5$ có phải là đoán mò không? Căn cứ vào đâu?"**
> *"Dạ thưa Thầy/Cô, hoàn toàn không phải đoán mò ạ. Tại Bảng 3.7 trong báo cáo, nhóm đã thực nghiệm **quét toàn diện 11 giá trị $alphalpha$ từ 0,0 đến 1,0 với bước nhảy 0,1**.  
> Kết quả chỉ ra rằng cấu hình $alphalpha = 0,5$ ở C6 chỉ là baseline trọng số bằng nhau và thực tế cho hiệu năng chưa tối ưu. Trên tập dữ liệu thực nghiệm, nhóm xác định **$alphalpha = 0,8$ là điểm cân bằng tối ưu** (đạt Recall 0,9297 và MRR 0,8220), vừa tận dụng tối đa sức mạnh của Dense Embedding vừa duy trì tín hiệu từ khóa chính xác của BM25 cho các truy vấn pháp lý chứa thuật ngữ định danh."*
