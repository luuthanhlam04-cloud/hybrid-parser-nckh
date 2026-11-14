# -*- coding: utf-8 -*-
"""
Generator for the finalized, unified 15-minute thesis defense script.
Synthesizes all consensus points from Antigravity, GPT, and DeepSeek.
Strictly verified against bancuoi.docx.
"""
import os
import re

content = r"""# KỊCH BẢN THUYẾT TRÌNH BÁO CÁO VÀ HỒ SƠ BẢO VỆ NCKH (15 PHÚT)
## ĐỀ TÀI: ĐÁNH GIÁ VÀ TỐI ƯU HÓA CÁC KIẾN TRÚC RAG TRÊN NỀN TẢNG DỮ LIỆU CẤU TRÚC ĐẶC THÙ
**Hội đồng Khoa học & Công nghệ Thông tin (PTIT)**  
**Nhóm tác giả:** Lưu Thanh Lâm · Ngô Thế Dương · Nguyễn Bình Minh  
**Giảng viên hướng dẫn:** TS. Nguyễn Mạnh Dũng  
**Tổng thời lượng:** 15 phút (900 giây) | **Khung lời thoại chuẩn:** ~1.850 từ (~125–130 từ/phút) | **Thời gian dự phòng:** 30 giây

---

## MA TRẬN PHÂN BỔ THỜI GIAN & PHÂN VAI (3 THÀNH VIÊN)

```
[00:00 - 01:30] CHẶNG 1: LƯU THANH LÂM (Slide 1 - 2 | 90s | ~200 từ)
  └── Mở màn, Bối cảnh pháp lý, Tỷ lệ ảo giác 17%-33% (Magesh 2025) & Thách thức căn cứ vi mô.

[01:30 - 05:15] CHẶNG 2: NGÔ THẾ DƯƠNG (Slide 3 - 6 | 225s | ~455 từ)
  └── 3 Đặc thù luật & 3 Vấn đề kiểm chứng; 3 Trường phái RAG đối chứng; 4 RQ; Hạ tầng Benchmark Harness & 2 Bộ dữ liệu A/B.

[05:15 - 10:00] CHẶNG 3: LƯU THANH LÂM (Slide 7 - 9 | 285s | ~540 từ)
  └── Giai đoạn 1: Khoảng cách truy hồi - trích dẫn (RQ1); Giai đoạn 2: Parser v2 & MaxP; Đột phá C5 (RQ2) & Tách tầng đánh giá.

[10:00 - 15:00] CHẶNG 4: NGUYỄN BÌNH MINH (Slide 10 - 14 | 300s | ~655 từ)
  └── Giai đoạn 3: Triết lý UKG 2 tầng & Module 5; Benchmark B (RQ3, RQ4) & Trade-off; Tổng hợp 4 RQ; Đóng góp & Kết luận.
```

---

# PHẦN 1: BẢN THIẾT KẾ KỊCH BẢN CHI TIẾT 14 SLIDE (14 SLIDE BLUEPRINTS & EVIDENCE SIGNPOSTS)

---

### SLIDE 1 · BÌA BÁO CÁO (LÂM | 00:00 – 00:20)
* **Tiêu đề:** Đánh giá và tối ưu hóa các kiến trúc RAG trên nền tảng dữ liệu cấu trúc đặc thù
* **Phụ đề:** Nghiên cứu thực nghiệm trên văn bản quy phạm pháp luật Việt Nam
* **Bố cục hiển thị:**
  * Cơ sở đào tạo: Học viện Công nghệ Bưu chính Viễn thông (PTIT).
  * Tên đề tài NCKH, Giảng viên hướng dẫn: TS. Nguyễn Mạnh Dũng.
  * Nhóm sinh viên thực hiện: Lưu Thanh Lâm, Ngô Thế Dương, Nguyễn Bình Minh.
  * Thông điệp mở đầu: *"Khảo sát khoảng cách truy hồi – trích dẫn và giải pháp kiến trúc đồ thị tri thức pháp lý hai tầng."*
* **Thẻ dẫn chứng:** `[Tham chiếu: Báo cáo toàn văn — Trang bìa | Đề tài NCKH 2025–2026]`.

---

### SLIDE 2 · BỐI CẢNH & THÁCH THỨC CĂN CỨ PHÁP LÝ (LÂM | 00:20 – 01:30)
* **Tiêu đề:** Bối cảnh nghiên cứu — Thách thức về tính xác thực của căn cứ pháp lý
* **Luận điểm cốt lõi:** *Hỏi đáp pháp luật đòi hỏi kiểm chứng tuyệt đối; ảo giác trích dẫn làm đảo lộn hệ quả pháp lý của hành vi.*
* **Bố cục hiển thị:**
  * Cột trái — Thực tiễn: Nhu cầu tra cứu pháp luật tự động tăng cao; yêu cầu độ chính xác tuyệt đối ở mức vi mô (Điều, Khoản, Điểm).
  * Cột phải — Bằng chứng khoa học quốc tế: Công bố của Magesh và cộng sự (2025) trên tạp chí *Journal of Empirical Legal Studies* (JELS): Các mô hình ngôn ngữ lớn thương mại hàng đầu vẫn gặp tỷ lệ ảo giác pháp lý từ **17% đến 33%**.
  * Hộp cảnh báo trung tâm: *"Một câu trả lời đúng ngữ nghĩa nhưng sai căn cứ Điều, Khoản hoặc bỏ sót một ngoại lệ tại một Điểm có thể làm thay đổi hoàn toàn hệ quả pháp lý của hành vi."*
  * Bài toán cốt lõi: Làm sao vừa tối ưu hiệu quả tìm kiếm, vừa hỗ trợ mô hình xác định chính xác căn cứ pháp lý vi mô mà không làm bùng nổ dung lượng ngữ cảnh?
* **Thẻ dẫn chứng:** `[Tham chiếu: Báo cáo toàn văn — Mục 1.1, 1.2 | Trang 1–4 | Trích dẫn [3] Magesh et al. (2025)]`.

---

### SLIDE 3 · ĐẶC THÙ VĂN BẢN LUẬT & BA VẤN ĐỀ KIỂM CHỨNG (DƯƠNG | 01:30 – 02:25)
* **Tiêu đề:** Đặc thù văn bản luật Việt Nam & Ba vấn đề nghiên cứu cần kiểm chứng
* **Luận điểm cốt lõi:** *Đặc thù phân cấp đa tầng, dẫn chiếu chéo và lệch pha từ vựng định hình ba bài toán kiểm chứng thực nghiệm.*
* **Bố cục hiển thị:** Sơ đồ đối sánh 3 Đặc thù $\longleftrightarrow$ 3 Vấn đề kiểm chứng (Mục 1.7.2):
  * *Đặc thù 1 — Phân cấp đa tầng:* Luật $\rightarrow$ Chương $\rightarrow$ Mục $\rightarrow$ Điều $\rightarrow$ Khoản $\rightarrow$ Điểm. Nội dung ở Điểm phụ thuộc chủ thể ở Điều.  
    $\longrightarrow$ **Vấn đề 1:** Khảo sát có kiểm soát ảnh hưởng của phân đoạn cấu trúc đến hiệu quả truy hồi và khả năng bảo toàn phả hệ.
  * *Đặc thù 2 — Mạng lưới dẫn chiếu chéo:* Điều kiện áp dụng và trường hợp ngoại lệ nằm rải rác ở nhiều điều luật.  
    $\longrightarrow$ **Vấn đề 2:** Đánh giá mức độ bao phủ các thành phần quy phạm (điều kiện, ngoại lệ, chủ thể) trong câu trả lời.
  * *Đặc thù 3 — Lệch pha từ vựng:* Ngôn ngữ đời thường của người dân khác biệt lớn so với thuật ngữ pháp lý chuẩn tắc.  
    $\longrightarrow$ **Vấn đề 3:** Đánh giá khả năng tìm đích dẫn chiếu và tái dựng đường dẫn có thứ tự trên bộ kiểm chuẩn hạn chế lợi thế trùng lặp từ khóa.
* **Thẻ dẫn chứng:** `[Tham chiếu: Báo cáo toàn văn — Mục 1.2, 1.3, 1.7.2 | Trang 5–14]`.

---

### SLIDE 4 · CƠ SỞ LÝ THUYẾT: BA TRƯỜNG PHÁI RAG ĐỐI CHỨNG (DƯƠNG | 02:25 – 03:20)
* **Tiêu đề:** Cơ sở lý thuyết — Ba trường phái RAG đại diện được chọn làm đối chứng
* **Luận điểm cốt lõi:** *Ba kiến trúc đại diện cho ba cách tổ chức và truy hồi thông tin khác nhau, được sử dụng làm hệ thống đối chứng trên dữ liệu luật Việt Nam.*
* **Bố cục hiển thị:** 3 cột kiến trúc đối chuẩn:
  * *Cột 1 — Naive Vector RAG (Dense Only):* Nhúng vector dày đặc (BGE-M3), tìm kiếm bằng độ tương đồng Cosine; thế mạnh là nắm bắt ngữ nghĩa khái quát.
  * *Cột 2 — Hybrid RAG (Lexical + Dense):* Dung hợp từ khóa Okapi BM25 và Dense qua Reciprocal Rank Fusion (RRF) kết hợp Cross-Encoder Reranker; hỗ trợ bắt các từ khóa định danh.
  * *Cột 3 — LightRAG (Graph-based RAG):* Trích xuất đồ thị thực thể – quan hệ bằng mô hình ngôn ngữ để kết nối văn bản hai tầng; hỗ trợ bao quát tri thức liên kết.
* **Thẻ dẫn chứng:** `[Tham chiếu: Báo cáo toàn văn — Mục 2.1, 2.2 | Trang 15–35 | Trích dẫn [5], [6], [12], [21]]`.

---

### SLIDE 5 · HỆ THỐNG CÂU HỎI NGHIÊN CỨU (DƯƠNG | 03:20 – 04:05)
* **Tiêu đề:** Bốn câu hỏi nghiên cứu định hướng (RQ1 – RQ4)
* **Luận điểm cốt lõi:** *Thiết kế thực nghiệm 3 giai đoạn được ánh xạ trực tiếp từ 4 câu hỏi khoa học cốt lõi.*
* **Bố cục hiển thị:** Bảng ma trận 4 RQ gắn với 3 Giai đoạn thực nghiệm:
  * **RQ1 (Giai đoạn 1):** *Hiệu quả truy hồi và độ chính xác trích dẫn căn cứ của các kiến trúc RAG cơ sở khác biệt như thế nào khi áp dụng chiến lược cắt đoạn thô?*
  * **RQ2 (Giai đoạn 2):** *Việc bổ sung bộ phân tích cấu trúc vi mô kết hợp giải thuật MaxP tác động như thế nào đến độ chính xác trích dẫn ngữ cảnh và dung lượng tài liệu?*
  * **RQ3 (Giai đoạn 3):** *Kiến trúc đồ thị tri thức hai tầng Hybrid UKG nâng cao hiệu quả truy hồi và xử lý quy phạm ngoại lệ ra sao khi đối sánh trực diện với LightRAG?*
  * **RQ4 (Giai đoạn 3):** *Khả năng định vị đích dẫn chiếu và tái dựng chuỗi quan hệ có thứ tự của các mô hình đạt mức độ nào?*
* **Thẻ dẫn chứng:** `[Tham chiếu: Báo cáo toàn văn — Mục 1.4 | Trang 12–14]`.

---

### SLIDE 6 · THIẾT KẾ THỰC NGHIỆM & HẠ TẦNG BENCHMARK (DƯƠNG | 04:05 – 05:15)
* **Tiêu đề:** Phương pháp luận — Hạ tầng Benchmark Harness & Hai bộ dữ liệu kiểm chuẩn
* **Luận điểm cốt lõi:** *Thiết lập khung đánh giá thống nhất và kiểm soát các biến thực nghiệm có thể chuẩn hóa.*
* **Bố cục hiển thị:** 2 khối thông tin kiểm chuẩn:
  * *Khối 1 — Benchmark Harness & Adapter Pattern:*  
    Giao diện chuẩn hóa `BaseRAGAdapter` bao bọc tất cả hệ sinh thái. Cố định các biến có thể chuẩn hóa: cùng văn bản nguồn, cùng mô hình nhúng `BAAI/bge-m3`, LLM thẩm định `GPT-4o-mini`, $K=5$, cùng môi trường phần cứng NVIDIA T4 GPU.
  * *Khối 2 — Hai bộ dữ liệu kiểm chuẩn chuyên biệt:*
    * **Benchmark A (N = 512 câu):** Phủ rộng 7 đạo luật trọng điểm. Thực hiện diễn đạt lại có chọn lọc trên các câu có độ trùng lặp cao, đưa chỉ số từ vựng Jaccard trung bình từ **0,68 xuống 0,31** nhằm hạn chế lợi thế không mong muốn của truy hồi từ khóa.
    * **Benchmark B (N = 50 câu):** Phân tầng tại Chương III Luật Đất đai 2024 (47 câu hỏi truy hồi/chất lượng + 3 câu kiểm tra an toàn/từ chối). Đánh giá chuyên sâu quyền nghĩa vụ, đa điều kiện, ngoại lệ và dẫn chiếu.
    * *Ghi chú điều kiện Tier 1 (N = 205 câu):* Tập con được lựa chọn sao cho toàn bộ căn cứ cần thiết nằm trong 500 điều mà LightRAG đã lập chỉ mục, đảm bảo bao phủ căn cứ tương đương khi đối chuẩn ở Giai đoạn 1.
* **Thẻ dẫn chứng:** `[Tham chiếu: Báo cáo toàn văn — Mục 2.3, 2.4, 2.5, 2.10 | Bảng 2.1, 2.2, Hình 2.1 | Trang 36–58]`.

---

### SLIDE 7 · GIAI ĐOẠN 1: KẾT QUẢ ĐỐI CHUẨN & TRẢ LỜI RQ1 (LÂM | 05:15 – 06:40)
* **Tiêu đề:** Giai đoạn 1 — Khoảng cách giữa truy hồi và trích dẫn trên tập Tier 1 (N = 205 câu) & Trả lời RQ1
* **Luận điểm cốt lõi:** *Hiệu năng tìm kiếm tài liệu cao chưa đồng nghĩa với việc câu trả lời trích dẫn đúng: Cắt đoạn thô thiếu thông tin phân cấp làm suy giảm khả năng định vị.*
* **Bố cục hiển thị:** Bảng số liệu Bảng 3.4 kèm Hộp phân tích cơ chế:
  * *Bảng số liệu đối chuẩn (Tier 1 Fair Subset — N = 205 câu):*
    * Naive Vector RAG: Recall@5: 0,9561 | Context Precision: 0,9659 | **Citation Accuracy (Answer): 0,3259**
    * Hybrid RAG: Recall@5: 0,9659 | Context Precision: 0,9660 | **Citation Accuracy (Answer): 0,2902**
    * LightRAG: Recall@5: 0,9659 | Context Precision: 0,8829 | **Citation Accuracy (Answer): 0,1371**
  * *Hiện tượng quan sát được:* Cả ba hệ thống đều tìm được Điều luật liên quan ($Recall > 95\%$). Tuy nhiên, khi đánh giá câu trả lời cuối cùng, Citation Accuracy chỉ đạt khoảng $30\%$, riêng LightRAG ghi nhận **$13,71\%$**.
  * *Cơ chế kỹ thuật:* Cả ba hệ thống đều sử dụng khối văn bản thô thiếu cấu trúc phân cấp tường minh (Naive và Hybrid dùng Điều thô, riêng LightRAG chia chunk 1.200 token), khiến mô hình ngôn ngữ khó xác định mối liên hệ giữa nội dung truy hồi và vị trí pháp lý cần viện dẫn.
  * *Chốt hạ RQ1:* Các kiến trúc RAG cơ sở bộc lộ khoảng cách lớn giữa khả năng tìm tài liệu và khả năng xác định chính xác căn cứ trích dẫn.
* **Thẻ dẫn chứng:** `[Dẫn chứng: Báo cáo toàn văn — Mục 3.2 | Bảng 3.3, Bảng 3.4 | Trang 91–93]`.

---

### SLIDE 8 · GIAI ĐOẠN 2: PARSER V2 & ARTICLE-LEVEL MAXP (LÂM | 06:40 – 08:05)
* **Tiêu đề:** Giai đoạn 2 — Giải pháp phân đoạn cấu trúc vi mô & Giải thuật Article MaxP
* **Luận điểm cốt lõi:** *Bảo toàn phả hệ bằng tiền tố cấu trúc và tối ưu hóa cửa sổ ngữ cảnh bằng Max-Pooling cấp Điều.*
* **Bố cục hiển thị:** Sơ đồ luồng xử lý 2 bước:
  * *Bước 1 — Structure-Aware Parser v2:*  
    Bóc tách đệ quy văn bản thành 12.754 phân đoạn vi mô theo từng cấp Khoản và Điểm.  
    Tự động gắn **tiền tố cấu trúc bất biến**: `[Văn bản: Luật Đất đai 2024 > Chương III > Điều 45 > Khoản 1 > Điểm a]`, giúp duy trì thông tin định vị và quan hệ phân cấp cha-con.
  * *Bước 2 — Giải thuật Article-Level Max-Pooling (MaxP):*  
    *Vấn đề xử lý:* Phân đoạn nhỏ dễ làm bão hòa cửa sổ Top-K bởi nhiều Khoản trong cùng 1 Điều.  
    *Cơ chế:* Gom cụm các phân đoạn vi mô theo Điều; điểm số đại diện của Điều được tính bằng điểm cực đại của phân đoạn thành phần:  
    $$S_{\text{article}} = \max_{c \in \text{Article}} S_{\text{micro}}(c)$$  
    Xếp hạng Top-K ở cấp Điều, sau đó lựa chọn các phân đoạn vi mô liên quan nhất để xây dựng ngữ cảnh đưa vào mô hình ngôn ngữ.
* **Thẻ dẫn chứng:** `[Tham chiếu: Báo cáo toàn văn — Mục 2.6 | Bảng 2.3, Hình 2.2 | Trang 60–65]`.

---

### SLIDE 9 · GIAI ĐOẠN 2: MA TRẬN ĐỐI SOÁT C1 – C6 & KẾT QUẢ C5 (LÂM | 08:05 – 10:00)
* **Tiêu đề:** Giai đoạn 2 — Kết quả đối soát 6 cấu hình trên Benchmark A (N = 512 câu) & Trả lời RQ2
* **Luận điểm cốt lõi:** *C5 nâng Citation Accuracy trên ngữ cảnh lên 0,9902, giảm 79,9% dung lượng ngữ cảnh; phân tách rõ tầng đánh giá ngữ cảnh và tầng sinh.*
* **Bố cục hiển thị:** Bảng ma trận Bảng 3.6 và 3 con số kết quả nổi bật:
  * *Bảng số liệu 6 cấu hình (512 câu | 3.072 lượt chấm LLM-Judge):*
    * C1 (Naive BM25): Citation 0,7490 | Điểm 1,0: 72,5% | Token ~2.500
    * C2 (Naive Dense): Citation 0,4000 | Điểm 1,0: 25,4% | Token ~2.898
    * C3 (Naive Hybrid): Citation 0,3986 | Điểm 1,0: 25,6% | Token ~2.898
    * C4 (Parser BM25): Citation 0,9028 | Điểm 1,0: 89,3% | Token ~580
    * **C5 (Parser Dense): Citation 0,9902 | Điểm 1,0: 98,4% (504/512 câu) | Token ~580**
    * C6 (Parser Hybrid $\alpha=0,5$): Citation 0,9786 | Điểm 1,0: 96,3% | Token ~580
  * *Ba kết quả đáng chú ý:*
    * **`0,9902` (Citation Acc C5 trên ngữ cảnh):** Tăng **+59,02 điểm phần trăm** so với C2 (0,4000). Có **504 / 512 câu đạt điểm tuyệt đối 1,0**.
    * **`-79,9%` (Giảm dung lượng ngữ cảnh):** Dung lượng giảm từ $\sim 2.898$ token xuống còn **$\sim 580$ token**.
    * **Khảo sát $\alpha$ tại Bảng 3.7:** Quét 11 giá trị $\alpha$ từ 0,0 đến 1,0; cấu hình cân bằng $\alpha=0,8$ đạt Recall **0,9297** và MRR **0,8220**, cải thiện so với cấu hình cào bằng trọng số ở C6.
  * *Ghi chú phương pháp luận:* Ở GĐ2, nhóm đánh giá riêng chất lượng căn cứ xuất hiện trong ngữ cảnh truy hồi bằng LLM-Judge, không đồng nhất với độ chính xác câu trả lời pháp lý cuối cùng; C2 và C5 khác nhau ở cả gói giải pháp (phân đoạn vi mô, tiền tố, MaxP). Đánh giá sinh câu trả lời hoàn chỉnh được thực hiện tại Giai đoạn 3.
  * *Chốt hạ RQ2:* Gói xử lý cấu trúc vi mô kết hợp MaxP cải thiện đáng kể chất lượng căn cứ trong ngữ cảnh và tối ưu hóa dung lượng đầu vào.
* **Thẻ dẫn chứng:** `[Dẫn chứng: Báo cáo toàn văn — Mục 3.3, 3.9.2 | Bảng 3.5, Bảng 3.6, Bảng 3.7 | Trang 96–101]`.

---

### SLIDE 10 · GIAI ĐOẠN 3: TRIẾT LÝ KIẾN TRÚC HYBRID UKG & MODULE 5 (MINH | 10:00 – 11:15)
* **Tiêu đề:** Giai đoạn 3 — Triết lý kiến trúc 2 tầng Hybrid Parser / UKG & Bộ định tuyến Module 5
* **Luận điểm cốt lõi:** *Tách biệt cấu trúc phân cấp vật lý và lớp ngữ nghĩa pháp lý; các bước xử lý tri thức thực hiện trong quá trình lập chỉ mục.*
* **Bố cục hiển thị:** Sơ đồ dòng chảy 2 tầng:
  * *Tầng 1 — Đồ thị Cấu trúc vật lý (Physical Graph):* Sử dụng các quy tắc xác định trước để xây dựng cấu trúc phân cấp Chương-Mục-Điều-Khoản-Điểm, Module 3 Validation cách ly các node lỗi nghiêm trọng.
  * *Tầng 2 — Đồ thị Ngữ nghĩa (Semantic Graph):* Trích xuất các thực thể và quan hệ pháp lý động (quyền, nghĩa vụ, điều kiện, ngoại lệ) gắn lên trục phân cấp.
  * *Quá trình vận hành:* Các bước phân tích, trích xuất và hợp nhất tri thức chạy trong quá trình lập chỉ mục; khi truy vấn trực tuyến, hệ thống duyệt đồ thị và truy hồi vector đã dựng.
  * *Trọng tâm kỹ thuật Module 5 (Semantic Router):* 
    * Mô hình ngôn ngữ nhân quả **Qwen2.5-0.5B** tạo biểu diễn vector kết hợp tín hiệu Regex bằng toán tử **Max-Fusion**:  
      $$S_{\text{fusion}} = \max(S_{\text{regex}}, S_{\text{semantic}})$$
    * Cơ chế Causal Attention giúp bảo toàn trật tự logic quy phạm, hạn chế làm phẳng tín hiệu ngữ pháp trên phân đoạn ngắn.
    * *Kết quả kiểm chuẩn Golden Set (193 node) tại ngưỡng $\theta = 0,85$:* Đạt **Recall 96,85%**, Precision **70,29%**, F1 **0,8146**; loại bỏ 9,33% phân đoạn thủ tục, chấp nhận ranh giới đánh đổi 4 node quy phạm bị bỏ sót (FN = 4).
* **Thẻ dẫn chứng:** `[Tham chiếu: Báo cáo toàn văn — Mục 2.6 | Hình 2.2, Bảng 2.4 & Phụ lục A | Bảng A.1, A.2 | Trang 63, 128–130]`.

---

### SLIDE 11 · GIAI ĐOẠN 3: KẾT QUẢ ĐỐI CHUẨN TRÊN BENCHMARK B (MINH | 11:15 – 13:00)
* **Tiêu đề:** Giai đoạn 3 — Kết quả thực nghiệm Benchmark B (N = 50 câu) & Trả lời RQ3, RQ4
* **Luận điểm cốt lõi:** *UKG thể hiện ưu thế ở truy hồi cấp Điều và nhận diện ngoại lệ; minh bạch các ranh giới về điều kiện và chuỗi dẫn chiếu.*
* **Bố cục hiển thị:** Bảng đối sánh trực diện 3 khối thông tin (Bảng 3.9, 3.11, 3.15, 3.16):
  * *Khối 1 — Khả năng truy hồi cấp Điều (Bảng 3.9, N = 47 câu):*
    * **Recall@5 cấp Điều:** UKG đạt **0,9184** vs LightRAG **0,7358** (**Vượt +18,26 điểm %**).
    * **MRR@5 cấp Điều:** UKG đạt **0,8848** vs LightRAG **0,5539** (**Vượt +33,09 điểm %**).
  * *Khối 2 — Chất lượng câu trả lời & Độ chính xác trích dẫn:*
    * **Citation Precision cấp Điều (Bảng 3.16, N = 47):** UKG đạt **0,8369** vs LightRAG **0,3333** (**Gấp 2,5 lần**).
    * **Citation Precision cấp Khoản (Bảng 3.16, N = 46):** UKG đạt **0,7757** vs LightRAG **0,0435** (**Gấp gần 18 lần**).
    * **Exception Coverage (Bảng 3.15, N = 14):** UKG đạt **0,6786** vs LightRAG **0,3929** (**Vượt +28,57 điểm %** nhờ bóc tách mệnh đề ngoại lệ).
    * **Legal Correctness (Bảng 3.15, N = 50):** UKG đạt **0,8777** vs LightRAG **0,8210** (**Vượt +5,67 điểm %**).
  * *Khối 3 — Hai ranh giới kỹ thuật cần tiếp tục hoàn thiện:*
    * **Condition Coverage (Bảng 3.15, N = 19):** UKG đạt **0,7066** vs LightRAG **0,8421** ($-13,55$ đpt) do phân đoạn vi mô tập trung quy phạm lõi, cần thêm cơ chế lan truyền điều kiện diện rộng.
    * **Tái dựng chuỗi dẫn chiếu (RQ4, Bảng 3.14):** UKG định vị được **58,67%** node đích (Reference-target Recall), nhưng Chain Exact Match = 0 trên 18 câu hỏi dẫn chiếu (46/47 đường dẫn dừng ở 1 bước), xác lập hướng đi cần giải thuật Constrained Graph Traversal.
  * *Hàng đối soát Exact Locator Recall@5 (Bảng 3.11):* LightRAG đạt **0,8509** vs UKG đạt **0,5560**.
  * *Footnote kép hiển thị chân slide:*  
    `(*) Exact Locator đo mức trùng khớp chuỗi ký tự cục bộ trên 39/47 câu đo được của UKG so với 47/47 câu của LightRAG (8 câu N/A không gán 0). Do chunk LightRAG bao phủ trung bình ~15 locator/chunk trong khi evidence UKG là phân đoạn vi mô (1 locator/đoạn), chỉ số này phản ánh khác biệt về độ hạt bằng chứng hơn là năng lực định vị; khả năng trích dẫn thực tế ở tầng câu trả lời được phản ánh qua Citation Precision/Recall ở Bảng 3.16.`  
    `(**) Mẫu số phân tầng Bảng 3.16: Điều N=47, Khoản N=46 (1 câu nhãn vàng dừng ở Điều), Điểm N=37 (10 câu nhãn vàng dừng ở Khoản, không có Điểm). Không gán điểm 0 cho trường hợp không áp dụng.`
* **Thẻ dẫn chứng:** `[Dẫn chứng: Báo cáo toàn văn — Mục 3.4, 3.5, 3.6, 3.7 | Bảng 3.9, Bảng 3.11, Bảng 3.14, Bảng 3.15, Bảng 3.16 | Trang 103–112]`.

---

### SLIDE 12 · TỔNG HỢP KẾT QUẢ THEO BỐN CÂU HỎI NGHIÊN CỨU (MINH | 13:00 – 13:55)
* **Tiêu đề:** Tổng hợp kết quả thực nghiệm giải quyết 4 câu hỏi nghiên cứu (RQ1 – RQ4)
* **Luận điểm cốt lõi:** *Đóng gói khách quan câu trả lời cho cả bốn bài toán khoa học đặt ra ở đầu đề tài.*
* **Bố cục hiển thị:** Bảng ma trận 4 khối đối ứng:
  * **Trả lời RQ1:** Xác lập khoảng cách giữa truy hồi và trích dẫn: RAG cơ sở đạt Recall trên 95% nhưng Citation Accuracy câu trả lời chỉ khoảng 30% (LightRAG ghi nhận 13,71%) do sử dụng văn bản thô thiếu cấu trúc phân cấp tường minh.
  * **Trả lời RQ2:** Parser v2 và MaxP nâng Citation Accuracy trên ngữ cảnh lên **0,9902** (98,4% tuyệt đối) và giảm **79,9% dung lượng ngữ cảnh**, xác nhận hiệu quả của gói xử lý cấu trúc.
  * **Trả lời RQ3:** Hybrid UKG vượt trội LightRAG ở truy hồi cấp Điều (Recall +18,26 đpt, MRR +33,09 đpt), độ chính xác trích dẫn cấp Điều gấp 2,5 lần (0,8369 vs 0,3333) và độ bao phủ ngoại lệ (+28,57 đpt); tuy nhiên hiệu quả chưa đồng đều ở thành phần điều kiện.
  * **Trả lời RQ4:** Định vị được một phần căn cứ đích (58,67%); việc tái dựng chuỗi có thứ tự hoàn chỉnh cần thêm cơ chế constrained graph traversal, xác lập ranh giới cho giai đoạn nghiên cứu tiếp theo.
* **Thẻ dẫn chứng:** `[Tham chiếu: Báo cáo toàn văn — Mục 1, Kết luận | Trang 123–124]`.

---

### SLIDE 13 · BA ĐÓNG GÓP KHOA HỌC CHÍNH (MINH | 13:55 – 14:35)
* **Tiêu đề:** Ba đóng góp khoa học cốt lõi của đề tài & Thông điệp đúc kết
* **Luận điểm cốt lõi:** *Đóng góp đồng thời về Khung đánh giá kiểm chuẩn, Giải pháp phân đoạn cấu trúc và Kiến trúc hệ thống đồ thị.*
* **Bố cục hiển thị:** 3 cột đóng góp mang tính dấu ấn + Hộp thông điệp đúc kết:
  * *Đóng góp 1 — Dữ liệu và phương pháp đánh giá:* Xây dựng bộ kiểm chuẩn Benchmark A, Benchmark B và khung kiểm thử Adapter Pattern phục vụ đối sánh các kiến trúc RAG trên dữ liệu luật Việt Nam.
  * *Đóng góp 2 — Phương pháp tổ chức và truy hồi cấu trúc:* Khảo sát thực nghiệm phân đoạn cấu trúc vi mô kết hợp Article-level MaxP, ghi nhận cải thiện về chất lượng căn cứ ngữ cảnh và tối ưu dung lượng đầu vào.
  * *Đóng góp 3 — Kiến trúc hệ thống đồ thị hai tầng:* Thiết kế và triển khai Hybrid Parser/UKG, kết hợp đồ thị cấu trúc vật lý với lớp ngữ nghĩa pháp lý, đánh giá khả năng truy hồi và xử lý các thành phần quy phạm chuyên biệt.
  * *Thông điệp đúc kết:* **"Trong dữ liệu pháp luật, cấu trúc không chỉ là hình thức tổ chức văn bản mà còn ảnh hưởng trực tiếp đến khả năng định vị và sử dụng căn cứ của hệ thống RAG."**
* **Thẻ dẫn chứng:** `[Tham chiếu: Báo cáo toàn văn — Mục 2, Kết luận | Trang 124–125]`.

---

### SLIDE 14 · HƯỚNG PHÁT TRIỂN & KẾT THÚC (MINH | 14:35 – 15:00)
* **Tiêu đề:** Hướng nghiên cứu tiếp theo & Lời cảm ơn
* **Luận điểm cốt lõi:** *Xác định rõ ràng lộ trình hoàn thiện hệ thống và mở rộng phạm vi pháp lý.*
* **Bố cục hiển thị:**
  * *Mở rộng phạm vi văn bản:* Bổ sung bộ bóc tách cấu trúc sang các văn bản dưới luật như Nghị định, Thông tư và tự động hóa cập nhật hiệu lực văn bản.
  * *Hoàn thiện thuật toán:* Phát triển cơ chế lan truyền điều kiện diện rộng và giải thuật Constrained Graph Traversal để khép kín chuỗi dẫn chiếu chéo.
  * *Nâng cao thẩm định:* Bổ sung thực nghiệm ablation từng thành phần và phối hợp chuyên gia pháp lý để hiệu chuẩn kết quả độc lập.
  * *Lời cảm ơn trang trọng:* "Trân trọng cảm ơn Quý Thầy Cô trong Hội đồng khoa học đã chú ý lắng nghe! Kính mời Hội đồng đặt câu hỏi (Q&A)."

---
---

# PHẦN 2: KỊCH BẢN LỜI THOẠI STORYTELLING CHUYÊN SÂU 15 PHÚT (FULL SPOKEN SCRIPT)

> **Nguyên tắc vàng:**  
> - Tổng số từ nói thực tế: **~1.850 từ** (Tốc độ chuẩn: 125–130 từ/phút).  
> - Thời gian trình bày: **14 phút 30 giây** (Dư 30 giây đệm an toàn).  
> - Giữ phong thái: **Điềm tĩnh – Tự chủ – Tự hào có căn cứ – Trung thực trước giới hạn**.

---

### [00:00 – 01:30] · CHẶNG 1: LƯU THANH LÂM (MỞ MÀN & ĐẶT VẤN ĐỀ)

**[Slide 1 — Bìa báo cáo · 00:00 – 00:20 | 65 từ]**
> *"Kính thưa Hội đồng khoa học!  
> Em xin đại diện nhóm tác giả gồm ba thành viên: Lưu Thanh Lâm, Ngô Thế Dương và Nguyễn Bình Minh, dưới sự hướng dẫn của TS. Nguyễn Mạnh Dũng, trình bày đề tài:  
> **'Đánh giá và tối ưu hóa các kiến trúc RAG trên nền tảng dữ liệu cấu trúc đặc thù'**, tập trung vào bài toán hỏi đáp trên văn bản quy phạm pháp luật Việt Nam."*

**[Slide 2 — Bối cảnh & Thách thức căn cứ pháp lý · 00:20 – 01:30 | 154 từ]**
> *"Kính thưa Hội đồng, tra cứu pháp luật đòi hỏi kiểm chứng tuyệt đối: câu trả lời bắt buộc phải có căn cứ chính xác đến từng điều khoản cụ thể.  
> Tuy nhiên, công bố của Magesh và cộng sự (2025) trên tạp chí JELS chỉ ra rằng các hệ thống AI thương mại hàng đầu vẫn gặp tỷ lệ ảo giác pháp lý từ 17% đến 33%.  
> Trong thực tiễn pháp lý, chỉ cần hệ thống trích dẫn đúng số Điều nhưng dẫn sai một Khoản, hoặc nhầm lẫn một ngoại lệ tại một Điểm, hệ quả pháp lý của hành vi có thể bị đảo lộn hoàn toàn từ hợp pháp sang vi phạm.  
> Nhóm đặt ra bài toán cốt lõi: Làm sao vừa tối ưu hiệu quả tìm kiếm, vừa giúp mô hình ngôn ngữ lớn xác định chính xác căn cứ vi mô mà không làm bùng nổ dung lượng ngữ cảnh?  
> Sau đây, xin mời bạn Ngô Thế Dương trình bày đặc thù dữ liệu và cơ sở nghiên cứu."*  
*(Lâm chuyển micro cho Dương).*

---

### [01:30 – 05:15] · CHẶNG 2: NGÔ THẾ DƯƠNG (ĐẶC THÙ, LÝ THUYẾT & HẠ TẦNG BENCHMARK)

**[Slide 3 — Đặc thù luật & Ba vấn đề kiểm chứng · 01:30 – 02:25 | 123 từ]**
> *"Em xin cảm ơn bạn Lâm. Kính thưa Quý Thầy Cô,  
> Văn bản luật Việt Nam có ba đặc thù kiến trúc nổi bật: cấu trúc phân cấp đa tầng từ Luật xuống Điều, Khoản, Điểm; mạng lưới dẫn chiếu chéo phức tạp quy định điều kiện và ngoại lệ; cùng sự lệch pha từ vựng lớn giữa câu hỏi của người dân và thuật ngữ chuẩn tắc.  
> Từ những đặc thù này, nhóm tập trung vào ba vấn đề cần kiểm chứng thực nghiệm: Một là tác động của phân đoạn cấu trúc đến hiệu quả truy hồi; Hai là mức độ bảo đảm đầy đủ các thành phần quy phạm trong câu trả lời; và Ba là khả năng truy vết các quan hệ dẫn chiếu giữa những điều luật liên quan."*

**[Slide 4 — Cơ sở lý thuyết: Ba trường phái RAG đối chứng · 02:25 – 03:20 | 113 từ]**
> *"Để kiểm chứng các vấn đề trên, nhóm lựa chọn khảo sát ba trường phái RAG đại diện hiện nay làm hệ thống đối chứng:  
> Trước hết là **Naive Vector RAG** dựa trên biểu diễn vector dày đặc và độ tương đồng Cosine, rất mạnh về ngữ nghĩa khái quát.  
> Thứ hai là **Hybrid RAG** dung hợp từ khóa BM25 và Dense qua thuật toán RRF kết hợp Cross-Encoder Reranker, cải thiện khả năng bắt từ khóa định danh.  
> Thứ ba là **LightRAG** đại diện cho trào lưu GraphRAG, trích xuất đồ thị thực thể bằng mô hình ngôn ngữ lớn để kết nối tri thức hai tầng.  
> Nhóm sử dụng ba kiến trúc này làm đối chứng để khảo sát hiệu quả trên dữ liệu pháp luật Việt Nam."*

**[Slide 5 — Hệ thống 4 Câu hỏi nghiên cứu RQ1 – RQ4 · 03:20 – 04:05 | 102 từ]**
> *"Từ đó, nhóm xây dựng bốn câu hỏi nghiên cứu định hướng toàn bộ thực nghiệm:  
> RQ1: Hiệu năng truy hồi và độ chính xác trích dẫn của các RAG cơ sở khác biệt thế nào khi cắt đoạn thô?  
> RQ2: Bộ phân tích cấu trúc Parser v2 và giải thuật MaxP cải thiện độ chính xác trích dẫn ngữ cảnh và dung lượng tài liệu ra sao?  
> RQ3: Kiến trúc đồ thị hai tầng Hybrid UKG nâng cao hiệu quả truy hồi và xử lý ngoại lệ phức tạp thế nào khi đối sánh trực diện với LightRAG?  
> RQ4: Khả năng định vị đích dẫn chiếu và tái dựng chuỗi quan hệ có thứ tự đạt mức độ nào?"*

**[Slide 6 — Thiết kế thực nghiệm & Hạ tầng Benchmark · 04:05 – 05:15 | 116 từ]**
> *"Để trả lời bốn RQ, nhóm xây dựng Benchmark Harness chuẩn hóa giao diện Adapter Pattern, kiểm soát các biến thực nghiệm có thể chuẩn hóa: cùng văn bản nguồn, cùng embedding BGE-M3 và LLM thế hệ GPT-4o-mini.  
> Nhóm biên soạn hai bộ kiểm chuẩn độc lập:  
> Benchmark A gồm 512 câu hỏi phủ 7 đạo luật trọng điểm, được diễn đạt lại có chọn lọc để đưa Jaccard trung bình từ 0,68 xuống 0,31 nhằm hạn chế lợi thế không mong muốn của truy hồi từ khóa.  
> Benchmark B gồm 50 câu hỏi phân tầng tại Chương III Luật Đất đai 2024 để kiểm tra chuyên sâu đa điều kiện, ngoại lệ và dẫn chiếu.  
> Sau đây, xin mời bạn Lâm trình bày kết quả Giai đoạn 1 và 2."*  
*(Dương chuyển micro cho Lâm).*

---

### [05:15 – 10:00] · CHẶNG 3: LƯU THANH LÂM (GIAI ĐOẠN 1 NGHỊCH LÝ & GIAI ĐOẠN 2 ĐỘT PHÁ)

**[Slide 7 — Giai đoạn 1: Khoảng cách truy hồi – trích dẫn · 05:15 – 06:40 | 136 từ]**
> *"Em xin cảm ơn bạn Dương. Kính thưa Hội đồng,  
> Khi đối soát công bằng ba kiến trúc RAG trên tập Tier 1 gồm 205 câu hỏi, nhóm phát hiện khoảng cách đáng chú ý giữa khả năng tìm kiếm và khả năng trích dẫn:  
> Tại Bảng 3.4, cả ba hệ thống đều tìm kiếm tài liệu rất tốt: Recall@5 đều vượt 95%, Context Precision Naive và Hybrid trên 0,96, LightRAG đạt 0,8829.  
> Tuy nhiên, Citation Accuracy trên câu trả lời sụt giảm nghiêm trọng: Naive Vector chỉ đạt 32,59%, Hybrid đạt 29,02%, và LightRAG ghi nhận 13,71%.  
> Nguyên nhân kỹ thuật là việc sử dụng các khối văn bản thô thiếu cấu trúc phân cấp tường minh khiến mô hình khó xác định mối liên hệ giữa nội dung truy hồi và vị trí pháp lý cần viện dẫn.  
> Kết quả này trả lời cho RQ1: RAG cơ sở bộc lộ khoảng cách lớn ở bài toán trích dẫn nếu giữ nguyên phương thức cắt đoạn thô."*

**[Slide 8 — Giai đoạn 2: Parser v2 & Article MaxP · 06:40 – 08:05 | 161 từ]**
> *"Để khắc phục hiện tượng trên, bước sang Giai đoạn 2, nhóm đề xuất giải pháp cấu trúc gồm hai thành phần cốt lõi:  
> Trước hết là bộ phân tích cấu trúc Structure-Aware Parser v2. Parser bóc tách đệ quy văn bản luật thành 12.754 phân đoạn vi mô theo từng cấp Khoản, Điểm, đồng thời gắn tiền tố cấu trúc bất biến chứa đầy đủ phả hệ từ tên Luật, Chương đến Điều vào từng phân đoạn, giúp duy trì thông tin định vị và quan hệ phân cấp.  
> Tiếp đó, để xử lý việc phân đoạn nhỏ làm bão hòa cửa sổ Top-K bởi nhiều Khoản trong cùng một Điều, nhóm đề xuất giải thuật Article-Level Max-Pooling (MaxP). Hệ thống gom cụm các phân đoạn theo Điều và lấy điểm cực đại của phân đoạn đại diện để xếp hạng Top-K cấp Điều; sau đó lựa chọn các phân đoạn vi mô liên quan để xây dựng ngữ cảnh đưa vào mô hình ngôn ngữ.  
> Giải pháp này vừa thu hẹp dung lượng ngữ cảnh, vừa bảo toàn thông tin phân cấp."*

**[Slide 9 — Giai đoạn 2: Ma trận C1–C6 & Kết quả C5 · 08:05 – 10:00 | 194 từ]**
> *"Trên 512 câu hỏi Benchmark A với 3.072 lượt thẩm định bằng LLM-Judge, kết quả tại Bảng 3.6 làm sáng tỏ RQ2 với ba điểm đáng chú ý:  
> Điểm nổi bật nhất, cấu hình C5 (Parser kết hợp Dense) nâng Citation Accuracy trên ngữ cảnh từ 0,4000 ở C2 lên 0,9902, tăng 59,02 điểm phần trăm, với 98,4% số câu đạt điểm tuyệt đối 1,0.  
> Đồng thời, nhờ phân đoạn vi mô và MaxP, dung lượng ngữ cảnh giảm mạnh 79,9%, từ gần 2.900 token xuống chỉ còn 580 token.  
> Qua khảo sát 11 giá trị trọng số tại Bảng 3.7, nhóm xác định cấu hình cân bằng tại alpha = 0,8 đạt Recall 0,9297 và MRR 0,8220, cải thiện rõ rệt so với cấu hình cào bằng ở C6.  
> Ở đây, nhóm lưu ý về phương pháp luận: Giai đoạn 2 đánh giá riêng chất lượng căn cứ xuất hiện trong ngữ cảnh truy hồi bằng LLM-Judge, thay vì chấm câu trả lời hoàn chỉnh. Kết quả C2 và C5 phản ánh tác động tích cực của gói xử lý cấu trúc trong điều kiện Dense Retrieval, tạo tiền đề để đánh giá câu trả lời toàn trình ở Giai đoạn 3.  
> Sau đây, xin mời bạn Nguyễn Bình Minh trình bày Giai đoạn 3."*  
*(Lâm chuyển micro cho Minh).*

---

### [10:00 – 15:00] · CHẶNG 4: NGUYỄN BÌNH MINH (ĐỒ THỊ UKG, ĐA BƯỚC & KẾT LUẬN)

**[Slide 10 — Giai đoạn 3: Kiến trúc Hybrid UKG & Module 5 · 10:00 – 11:15 | 163 từ]**
> *"Em xin cảm ơn bạn Lâm. Kính thưa Quý Thầy Cô,  
> Để xử lý truy vấn đa bước và quy phạm ngoại lệ, nhóm xây dựng kiến trúc Hybrid Parser/UKG với triết lý tách biệt hai tầng:  
> Tầng 1 là Đồ thị vật lý (Physical Graph) — sử dụng các quy tắc xác định trước để xây dựng cấu trúc phân cấp Chương-Mục-Điều-Khoản-Điểm, Module 3 Validation cách ly các node lỗi nghiêm trọng.  
> Tầng 2 là Đồ thị ngữ nghĩa (Semantic Graph) — trích xuất động các quan hệ dẫn chiếu, điều kiện và ngoại lệ.  
> Các bước xử lý tri thức được thực hiện trong quá trình lập chỉ mục; khi truy vấn trực tuyến, hệ thống khai thác cấu trúc và quan hệ đã dựng để thu thập bằng chứng.  
> Trọng tâm là Module 5 Semantic Router: Ứng dụng mô hình ngôn ngữ nhân quả Qwen2.5-0.5B kết hợp toán tử Max-Fusion logic OR giữa Regex và Vector. Cơ chế Causal Attention bảo toàn trật tự logic chủ thể - điều kiện - chế tài. Tại ngưỡng theta = 0,85 trên Golden Set 193 node, hệ thống đạt Recall 96,85%, F1 0,8146, loại an toàn 9,33% phân đoạn thủ tục, chấp nhận ranh giới đánh đổi 4 node quy phạm bị bỏ sót."*

**[Slide 11 — Giai đoạn 3: Thực nghiệm Benchmark B · 11:15 – 13:00 | 216 từ]**
> *"Kính thưa Hội đồng, kết quả thực nghiệm trên Benchmark B gồm 50 câu hỏi tại Chương III Luật Đất đai 2024 làm sáng tỏ RQ3 và RQ4 qua ba khối thông tin:  
> Về năng lực truy hồi cấp Điều (Bảng 3.9), Hybrid UKG đạt Recall@5 0,9184 vs 0,7358 của LightRAG (vượt +18,26 đpt) và MRR@5 đạt 0,8848 vs 0,5539 (vượt +33,09 đpt).  
> Về chất lượng trích dẫn và nội dung câu trả lời, UKG thể hiện ưu thế vượt trội: Citation Precision cấp Điều đạt 0,8369 vs 0,3333 của LightRAG (gấp 2,5 lần); cấp Khoản đạt 0,7757 vs 0,0435 (gấp gần 18 lần). Ở tầng nội dung, Legal Correctness đạt 0,8777 và đặc biệt Exception Coverage đạt 0,6786 — vượt LightRAG 28,57 điểm phần trăm nhờ bóc tách chính xác các mệnh đề ngoại lệ.  
> Về hai ranh giới kỹ thuật cần hoàn thiện: Condition Coverage của UKG đạt 0,7066 vs 0,8421 của LightRAG do phân đoạn vi mô tập trung vào quy phạm lõi, cần thêm cơ chế lan truyền điều kiện diện rộng. Về RQ4, UKG định vị được 58,67% node đích, nhưng việc tái dựng chuỗi có thứ tự cần thêm giải thuật duyệt đồ thị có ràng buộc khi Chain Exact Match ghi nhận 0,0000 trên 18 câu.  
> Riêng chỉ số Exact Locator Recall@5 đạt 0,5560 vs 0,8509 do khác biệt lớn về độ hạt: chunk LightRAG chứa trung bình khoảng 15 locator trong khi phân đoạn UKG chỉ mang 1 locator."*

**[Slide 12 — Tổng kết: Đóng gói 4 Câu hỏi nghiên cứu · 13:00 – 13:55 | 132 từ]**
> *"Tổng hợp lại từ ba giai đoạn, nhóm đã đóng gói lời giải cho bốn bài toán nghiên cứu ban đầu:  
> Với RQ1: Xác lập thực nghiệm khoảng cách giữa truy hồi và trích dẫn, chỉ ra hạn chế của việc sử dụng văn bản thô thiếu cấu trúc phân cấp.  
> Với RQ2: Cung cấp bằng chứng thực nghiệm cho thấy Parser v2 và MaxP nâng Citation Accuracy ngữ cảnh lên 0,9902 và giảm 79,9% dung lượng ngữ cảnh.  
> Với RQ3: Hybrid UKG đạt kết quả cao hơn LightRAG ở truy hồi cấp Điều (Recall +18,26 đpt, MRR +33,09 đpt), độ chính xác trích dẫn cấp Điều gấp 2,5 lần, và độ bao phủ ngoại lệ (+28,57 đpt); tuy nhiên hiệu quả chưa đồng đều ở thành phần điều kiện.  
> Với RQ4: Hệ thống xác định được một phần căn cứ đích (58,67%), làm rõ ranh giới cần giải thuật duyệt đồ thị có ràng buộc để khép kín chuỗi dẫn chiếu."*

**[Slide 13 — Ba đóng góp khoa học chính · 13:55 – 14:35 | 122 từ]**
> *"Từ các kết quả trên, đề tài xác định ba đóng góp khoa học cốt lõi:  
> Một là Khung dữ liệu và phương pháp kiểm chuẩn gồm Benchmark A, Benchmark B và hạ tầng Adapter Pattern phục vụ đối sánh các kiến trúc RAG trên dữ liệu luật Việt Nam.  
> Hai là Phương pháp tổ chức và truy hồi cấu trúc vi mô kết hợp Article-level MaxP, cải thiện đáng kể chất lượng đánh giá căn cứ và tối ưu hóa dung lượng đầu vào.  
> Ba là Kiến trúc hệ thống đồ thị hai tầng Hybrid UKG, kết hợp đồ thị cấu trúc vật lý với lớp ngữ nghĩa pháp lý để nâng cao khả năng truy hồi và xử lý quy phạm ngoại lệ.  
> Thông điệp đúc kết của nhóm là: Trong dữ liệu pháp luật, cấu trúc không chỉ là hình thức tổ chức văn bản mà còn ảnh hưởng trực tiếp đến khả năng định vị và sử dụng căn cứ của hệ thống RAG."*

**[Slide 14 — Hướng phát triển & Kết thúc · 14:35 – 15:00 | 55 từ]**
> *"Trong thời gian tới, nhóm hướng đến mở rộng bộ bóc tách cấu trúc sang Nghị định, Thông tư; tự động hóa cập nhật hiệu lực văn bản; và hoàn thiện giải thuật constrained graph traversal để khép kín chuỗi dẫn chiếu.  
> Thay mặt nhóm nghiên cứu, chúng em xin trân trọng cảm ơn Quý Thầy Cô trong Hội đồng đã chú ý lắng nghe. Nhóm kính mời Hội đồng đặt câu hỏi."*  
*(Cả ba thành viên Lâm, Dương, Minh cùng đứng nghiêm trang, cúi đầu chào Hội đồng).*

---
---

# PHẦN 3: GHI CHÚ TẬP DƯỢT VÀ NEO NỘI DUNG (ANCHOR NOTES)

> **Mục đích:** Tài liệu cầm tay phục vụ tập dượt thực chiến. Mỗi slide chỉ cần nhớ 2 – 3 từ khóa neo, điểm chỉ tia laser và câu chốt trigger cue để chuyển giao micro mượt mà.

| Slide | Người nói | Thời lượng | Từ khóa neo chuyên sâu | Hành động / Điểm chỉ laser trên Slide | Câu chốt chuyển mic (Trigger Cue) |
| :---: | :---: | :---: | :--- | :--- | :--- |
| **1** | **Lâm** | 20s | • Chào Hội đồng, giới thiệu 3 thành viên, GVHD<br>• Đề tài: RAG trên dữ liệu cấu trúc đặc thù | Đứng giữa bục, mắt bao quát Hội đồng, phong thái tự tin | *(Nói liền mạch sang Slide 2)* |
| **2** | **Lâm** | 70s | • Nhu cầu tra cứu pháp luật kiểm chứng tuyệt đối<br>• RAG ảo giác 17% – 33% (Magesh 2025)<br>• Sai lệch điều khoản làm đổi hệ quả pháp lý | Chỉ laser vào **Hộp cảnh báo 17% – 33%** | *"Sau đây xin mời bạn Ngô Thế Dương trình bày đặc thù dữ liệu và cơ sở nghiên cứu."* |
| **3** | **Dương** | 55s | • 3 đặc thù: Phân cấp đa tầng, Dẫn chiếu, Lệch pha từ vựng<br>• 3 Vấn đề: Phân đoạn cấu trúc, Thành phần quy phạm, Chuỗi dẫn chiếu | Quét laser lần lượt qua **3 khối đặc thù** và **3 vấn đề kiểm chứng** | *(Nói liền mạch sang Slide 4)* |
| **4** | **Dương** | 55s | • 3 trường phái RAG đối chứng: Naive Vector (Cosine), Hybrid (BM25+Dense+RRF), LightRAG (Graph) | Chỉ laser vào **3 cột kiến trúc RAG** | *(Nói liền mạch sang Slide 5)* |
| **5** | **Dương** | 45s | • 4 câu hỏi nghiên cứu định hướng 3 giai đoạn: RQ1 (GĐ1), RQ2 (GĐ2), RQ3 & RQ4 (GĐ3) | Chỉ laser vào **bảng ma trận 4 RQ** | *(Nói liền mạch sang Slide 6)* |
| **6** | **Dương** | 70s | • Benchmark Harness kiểm soát biến có thể chuẩn hóa<br>• BM-A 512 câu (Jaccard 0,68 $\to$ 0,31); BM-B 50 câu; Tier 1 205 câu | Chỉ laser vào **chỉ số Jaccard 0,31** và **cấu trúc 50 câu Benchmark B** | *"Sau đây xin mời bạn Lâm trình bày kết quả Giai đoạn 1 và 2."* |
| **7** | **Lâm** | 85s | • Khoảng cách truy hồi – trích dẫn: Recall > 95% nhưng Citation chỉ ~30% (LightRAG 13,71%)<br>• Văn bản thô thiếu cấu trúc phân cấp tường minh; chốt RQ1 | Chỉ laser vào **Bảng 3.4**, nhấn vào hàng Citation Accuracy | *(Nói liền mạch sang Slide 8)* |
| **8** | **Lâm** | 85s | • Parser v2 bóc tách 12.754 phân đoạn vi mô + tiền tố bất biến<br>• Giải thuật Article MaxP gom cụm cấp Điều chống bão hòa Top-K | Quét laser theo luồng: **Phân đoạn vi mô $\rightarrow$ Tiền tố $\rightarrow$ Article MaxP** | *(Nói liền mạch sang Slide 9)* |
| **9** | **Lâm** | 115s | • **[Slide trọng tâm] Ma trận C1–C6: C5 đạt 0,9902** (+59,02 đpt)<br>• Giảm **79,9% dung lượng ngữ cảnh**; Weighted RRF $\alpha=0,8$ cân bằng<br>• Phân tách tầng đánh giá ngữ cảnh và câu trả lời | Chỉ laser vào số **0,9902**, số **-79,9%**, và điểm **$\alpha = 0,8$** | *"Sau đây xin mời bạn Nguyễn Bình Minh trình bày kiến trúc UKG và kết quả Giai đoạn 3."* |
| **10** | **Minh** | 75s | • Kiến trúc UKG: Tầng vật lý (quy tắc tất định) + Tầng ngữ nghĩa (trích xuất động)<br>• Lập chỉ mục offline; Module 5 Router tại $\theta=0,85$ (Recall 96,85%, 4 FN) | Chỉ laser vào sơ đồ 2 tầng và khối **Module 5** | *(Nói liền mạch sang Slide 11)* |
| **11** | **Minh** | 105s | • **[Slide trọng tâm] Benchmark B (RQ3 & RQ4)**<br>• RQ3: Recall 0,9184 (+18,26 đpt), Citation Precision Điều 0,8369 vs 0,3333, Exception 0,6786 (+28,57 đpt)<br>• Ranh giới Condition Coverage & Exact Locator; RQ4 ranh giới chuỗi<br>• [Phao N]: Điều N=47, Khoản N=46, Điểm N=37 | Chỉ laser vào số **0,9184**, số **0,8369**, số **+28,57 đpt**, và footnote độ hạt | *(Nói liền mạch sang Slide 12)* |
| **12** | **Minh** | 55s | • Tổng hợp 4 RQ: RQ1 (khoảng cách trích dẫn), RQ2 (Parser v2 + MaxP 0,9902), RQ3 (UKG vượt trội ngoại lệ), RQ4 (ranh giới chuỗi) | Quét laser lần lượt qua **4 khối RQ** đã được giải quyết | *(Nói liền mạch sang Slide 13)* |
| **13** | **Minh** | 40s | • 3 Đóng góp: Khung Benchmark, Phân đoạn vi mô, Kiến trúc UKG 2 tầng<br>• Đúc kết: Cấu trúc ảnh hưởng trực tiếp đến định vị và sử dụng căn cứ | Chỉ laser vào **Hộp thông điệp cốt lõi** | *(Nói liền mạch sang Slide 14)* |
| **14** | **Minh** | 25s | • Hướng phát triển: Nghị định, Thông tư, Constrained Graph Traversal<br>• Lời cảm ơn trang trọng | Mắt hướng về Thầy Chủ tịch Hội đồng, chuyển sang thế sẵn sàng Q&A | Cả nhóm cúi đầu chào Hội đồng |

---
---

# PHẦN 4: BỘ CÂU HỎI VÀ ĐỊNH HƯỚNG TRẢ LỜI PHẢN BIỆN (Q&A PLAYBOOK)
## 18 CÂU HỎI PHẢN BIỆN TRỌNG YẾU & ĐỊNH HƯỚNG TRẢ LỜI ĐĨNH ĐẠC (20 – 30 GIÂY)

> **Quy tắc vàng khi trả lời phản biện:**
> 1. Luôn cảm ơn Thầy/Cô: *"Dạ em xin cảm ơn Thầy/Cô đã đặt một câu hỏi rất sâu sắc về..."*.
> 2. Đi thẳng vào bản chất kỹ thuật trong câu đầu tiên, không vòng vo.
> 3. Trả lời dứt khoát trong 20 – 30 giây, trung thực 100% theo đúng báo cáo, biến hạn chế thành hướng nghiên cứu tiếp theo.

---

### NHÓM 1: CÂU HỎI VỀ PHƯƠNG PHÁP LUẬN & ĐO LƯỜNG (LÂM & DƯƠNG PHỤ TRÁCH)

**Câu 1 (Lâm): "Citation Accuracy ở Giai đoạn 1 và Giai đoạn 2 có định nghĩa giống nhau không? Tại sao lại có sự chênh lệch lớn từ 32% lên 99%?"**
> *"Dạ thưa Thầy/Cô, hai giai đoạn sử dụng cùng tên trường đánh giá nhưng khác nhau về đối tượng. Ở Giai đoạn 1, chỉ số đo lường sự xuất hiện của căn cứ trích dẫn trong câu trả lời hoàn chỉnh do mô hình sinh ra. Sang Giai đoạn 2, nhóm đánh giá riêng mức độ phù hợp của căn cứ trong ngữ cảnh truy hồi bằng LLM-as-a-Judge.  
> Vì vậy, hai giá trị này phục vụ hai mục tiêu khác nhau và nhóm không so sánh trực tiếp 32% với 99%. Trong Giai đoạn 2, phép đối chiếu công bằng là giữa C2 (0,4000) và C5 (0,9902) trên cùng một thước đo ngữ cảnh, phản ánh hiệu quả của gói xử lý cấu trúc kết hợp MaxP trong điều kiện Dense Retrieval."*

**Câu 2 (Lâm): "Trong Giai đoạn 2, các em thay đổi nhiều thành phần cùng lúc (micro-chunk, prefix, MaxP). Thành phần nào đóng góp chính?"**
> *"Dạ đây là một giới hạn đã được nhóm ghi nhận tại Mục 3.3.9 của báo cáo. Kết quả của C5 là tác động tổng hợp của cả gói giải pháp cấu trúc: phân đoạn vi mô giúp thu hẹp phạm vi, tiền tố cấu trúc bảo toàn phả hệ cha-con, và MaxP giải quyết bão hòa Top-K.  
> Thiết kế hiện tại chưa cô lập ảnh hưởng riêng của từng thành phần đơn lẻ, và nhóm xác định việc thực hiện các cấu hình ablation độc lập là hướng nghiên cứu ưu tiên tiếp theo."*

**Câu 3 (Dương): "Các em dùng GPT-4o-mini vừa sinh câu trả lời vừa làm giám khảo. Kết quả có bị thiên lệch tự thân không?"**
> *"Dạ thưa Thầy/Cô, đây là một giới hạn nhóm đã nhận diện tại Mục 3.8.3. Việc sử dụng GPT-4o-mini cho cả sinh và thẩm định ở Giai đoạn 1 và 2 có thể tạo ra thiên lệch tương đồng về cách diễn giải. Nhóm đã tách riêng prompt thẩm định, bắt buộc kiểm tra JSON schema và thiết lập cơ chế thử lại tối đa 3 lần.  
> Tuy nhiên, những biện pháp này chưa thay thế được một phép thẩm định độc lập tuyệt đối. Sang Giai đoạn 3, các chỉ số Citation Precision/Recall tại Bảng 3.16 đã chuyển hoàn toàn sang tính toán tất định dựa trên quy tắc (Rule-based Locator Matching), không còn phụ thuộc LLM chấm. Hướng hoàn thiện là sử dụng thêm mô hình đánh giá khác và đối chiếu chuyên gia pháp lý."*

**Câu 4 (Dương): "Việc viết lại 512 câu hỏi ở Benchmark A có làm biến đổi ngữ nghĩa pháp lý gốc không?"**
> *"Dạ mục tiêu của quy trình tại Mục 2.3.5 là giảm sự trùng lặp từ vựng nhưng duy trì căn cứ pháp lý của truy vấn. Nhóm lựa chọn các câu có overlap lớn hơn 0,5 để diễn đạt lại, giúp giảm Jaccard trung bình từ 0,68 xuống 0,31.  
> Tuy nhiên, báo cáo cũng ghi nhận chưa có nhật ký đầy đủ xác nhận toàn bộ 512 câu đều được viết lại thành công. Vì vậy, nhóm xem đây là bước kiểm soát trùng lặp từ vựng, chưa phải một phép chứng minh độc lập về tính tương đương ngữ nghĩa của mọi truy vấn, và việc kiểm tra ngữ nghĩa tự động toàn bộ tập là hướng hoàn thiện tiếp theo."*

**Câu 5 (Dương): "Tại sao ở Giai đoạn 1 nhóm chỉ đánh giá trên 205 câu hỏi Tier 1 mà không dùng toàn bộ 512 câu?"**
> *"Dạ thưa Thầy/Cô, tại Giai đoạn 1, LightRAG mới được lập chỉ mục trên 500 điều thuộc Bộ luật Hình sự và Bộ luật Lao động do giới hạn nguồn lực trích xuất đồ thị.  
> Nhóm lựa chọn 205 câu hỏi Tier 1 sao cho toàn bộ căn cứ cần thiết của từng câu đều nằm trọn vẹn trong phạm vi 500 điều đó. Mục tiêu là đảm bảo điều kiện bao phủ căn cứ tương đương, tránh trường hợp LightRAG bị đánh giá thấp chỉ vì thiếu hụt tài liệu tham chiếu nguồn."*

---

### NHÓM 2: CÂU HỎI VỀ KẾT QUẢ THỰC NGHIỆM & ĐỐI SÁNH (LÂM & MINH PHỤ TRÁCH)

**Câu 6 (Lâm): "Tại sao LightRAG lại đạt Citation Accuracy thấp như vậy ở Giai đoạn 1 (chỉ 13,71%)?"**
> *"Dạ kết quả cho thấy đây là vấn đề chung của cả ba hệ thống cơ sở chứ không riêng LightRAG, khi Citation Accuracy của Naive Vector và Hybrid RAG cũng chỉ đạt khoảng 30%.  
> Một nguyên nhân kỹ thuật là việc sử dụng các khối văn bản thô thiếu cấu trúc phân cấp tường minh khiến mô hình khó xác định vị trí pháp lý chính xác. Với LightRAG, cấu hình chunk 1.200 token còn tạo ra sự khác biệt giữa phạm vi văn bản được truy hồi và vị trí pháp lý cụ thể cần viện dẫn. Đây là cơ sở để nhóm nghiên cứu sâu hơn về phân đoạn cấu trúc ở các giai đoạn sau."*

**Câu 7 (Minh): "Exact Locator Recall@5 của UKG chỉ đạt 0,5560, thấp hơn LightRAG (0,8509). Tại sao lại như vậy?"**
> *"Dạ đây là chỉ số đánh giá khả năng tìm thấy chuỗi ký tự locator trong Top-5 bằng chứng truy hồi. Hai hệ thống có đơn vị truy hồi khác nhau: chunk của LightRAG dài 1.200 token chứa trung bình khoảng 15 locator nên xác suất trúng chuỗi ký tự cao hơn; trong khi evidence của UKG là các phân đoạn vi mô chỉ mang 1 locator duy nhất.  
> Ngoài ra, chỉ số của UKG hiện mới đo được trên 39/47 câu hỏi (8 câu N/A không gán 0). Do khác biệt về độ hạt bằng chứng, nhóm không dùng riêng chỉ số này để kết luận bên nào định vị chính xác hơn mà đối chiếu thêm với Citation Precision và Recall ở tầng câu trả lời tại Bảng 3.16."*

**Câu 8 (Minh): "Condition Coverage của UKG đạt 0,7066, thấp hơn LightRAG (0,8421). Nhóm giải thích thế nào?"**
> *"Dạ đây là sự khác biệt được quan sát khách quan trong thực nghiệm. LightRAG đạt Condition Coverage 0,8421, cao hơn 0,7066 của Hybrid UKG; ngược lại, UKG đạt kết quả cao hơn rõ rệt về Exception Coverage (0,6786 so với 0,3929).  
> Điều này cho thấy hiệu quả hai hệ thống chưa đồng đều giữa các loại thành phần quy phạm. Nhóm nhận định phân đoạn vi mô tập trung vào quy phạm lõi nên cần tiếp tục cải thiện cơ chế tổng hợp và lan truyền điều kiện từ nhiều node liên quan thay vì chỉ định vị cục bộ."*

**Câu 9 (Minh): "Chỉ số Chain Exact Match bằng 0 trên 18 câu hỏi. Vậy đề tài có giải quyết được bài toán dẫn chiếu không?"**
> *"Dạ hệ thống hiện tại đã xác định được một phần các node đích với Reference-target Recall đạt 58,67%, nhưng chưa tái dựng được chuỗi dẫn chiếu hoàn chỉnh theo tiêu chí đánh giá có thứ tự. Phân tích đầu ra cho thấy phần lớn đường dẫn dự đoán mới dừng ở một bước.  
> Vì vậy, nhóm xác định cần bổ sung cơ chế duyệt đồ thị có ràng buộc (Constrained Graph Traversal) để bảo toàn thứ tự và loại quan hệ giữa các node. Với LightRAG, phép đo Chain Exact Match hiện chưa thực hiện được theo giao thức chung nên nhóm không đưa ra so sánh trực tiếp."*

**Câu 10 (Lâm): "Việc cắt nhỏ văn bản thành 12.754 phân đoạn vi mô và giảm 79,9% token có làm mất mát thông tin ngữ cảnh không?"**
> *"Dạ mục tiêu của nhóm không phải bảo đảm mọi phân đoạn đều giữ nguyên toàn bộ nội dung xung quanh, mà là duy trì thông tin định vị và quan hệ phân cấp cần thiết thông qua tiền tố cấu trúc.  
> Giải thuật Article-level MaxP giúp lựa chọn các phân đoạn phù hợp theo cấp Điều để gửi vào mô hình. Tuy nhiên, việc giảm dung lượng ngữ cảnh vẫn cần được cân bằng với khả năng thu thập đầy đủ điều kiện và ngoại lệ diện rộng, và đây là nội dung nhóm tiếp tục hoàn thiện."*

---

### NHÓM 3: CÂU HỎI VỀ KIẾN TRÚC & MÔ HÌNH HÓA (MINH & DƯƠNG PHỤ TRÁCH)

**Câu 11 (Minh): "Kiến trúc UKG gồm 10 module, vậy đóng góp khoa học chính nằm ở đâu?"**
> *"Dạ 10 module là cách tổ chức kiến trúc phần mềm theo nguyên lý phân tách trách nhiệm. Đóng góp khoa học cốt lõi của đề tài nằm ở ba điểm:  
> Một là xây dựng khung kiểm chuẩn Benchmark A, B phục vụ đánh giá RAG pháp luật Việt Nam;  
> Hai là khảo sát giải pháp phân đoạn cấu trúc vi mô kết hợp Article MaxP giúp cải thiện chất lượng căn cứ ngữ cảnh;  
> Và ba là thiết kế kiến trúc Hybrid UKG kết hợp đồ thị cấu trúc vật lý với lớp ngữ nghĩa để đánh giá chuyên biệt các thành phần quy phạm."*

**Câu 12 (Minh): "Tại sao Module 5 lại dùng mô hình ngôn ngữ nhân quả Qwen2.5-0.5B thay vì dùng các mô hình nhúng embedding chuyên dụng?"**
> *"Dạ nhóm đã khảo sát nhiều mô hình biểu diễn và lựa chọn Qwen2.5-0.5B dựa trên kết quả kiểm chuẩn Golden Set v2. Mô hình được khai thác để tạo vector ngữ nghĩa, kết hợp với tín hiệu Regex bằng toán tử Max-Fusion.  
> Cơ sở lựa chọn ở đây là kết quả thực nghiệm của bộ định tuyến trên dữ liệu kiểm chuẩn: cơ chế Causal Attention bảo toàn trật tự logic quy phạm tốt hơn trên phân đoạn ngắn so với phép gộp trung bình của Bi-encoder; không phải giả định rằng mọi mô hình nhân quả đều vượt trội mô hình nhúng chuyên dụng."*

**Câu 13 (Dương): "Tại sao nhóm lại chọn 7 văn bản luật này trong Benchmark A? Tính đại diện ở đâu?"**
> *"Dạ nhóm lựa chọn 7 văn bản thuộc các lĩnh vực hình sự, dân sự, lao động, đất đai, doanh nghiệp, hôn nhân gia đình và xử lý vi phạm hành chính.  
> Mục tiêu là xây dựng một phạm vi dữ liệu đa dạng về thể thức văn bản để khảo sát bộ phân tích cấu trúc và các phương thức truy hồi. Tuy nhiên, nhóm không xem tập dữ liệu này là mẫu đại diện thống kê cho toàn bộ hệ thống văn bản quy phạm pháp luật Việt Nam."*

**Câu 14 (Minh): "Toán tử Max-Fusion ở Module 5 có ưu thế gì so với việc lấy điểm trung bình cộng?"**
> *"Dạ thực nghiệm chỉ ra rằng nếu dùng trung bình cộng giữa điểm Regex và điểm ngữ nghĩa, khi một điều luật có quy phạm ngầm định không chứa từ khóa cứng, điểm Regex bằng 0 sẽ kéo tụt điểm tổng hợp xuống và loại nhầm quy phạm đó.  
> Toán tử Max-Fusion giúp không làm mất tín hiệu mạnh chỉ vì tín hiệu còn lại thấp. Tuy nhiên, Max-Fusion không bảo đảm loại bỏ hoàn toàn cảnh báo giả, vì vậy hệ thống vẫn cần ngưỡng quyết định theta = 0,85 và kiểm chuẩn thực nghiệm."*

**Câu 15 (Lâm): "Nếu hệ thống được đưa vào thực tế phục vụ người dân, nhóm tự tin nhất ở điểm nào và lo ngại nhất ở điểm nào?"**
> *"Dạ điểm mạnh của hệ thống là khả năng duy trì thông tin định vị cấu trúc và thu thập căn cứ pháp lý chi tiết trong phạm vi dữ liệu kiểm thử, giúp hạn chế việc trích dẫn sai số Điều, Khoản.  
> Tuy nhiên, nhóm chưa xem hệ thống là một công cụ tự động đưa ra kết luận pháp lý mà không cần chuyên gia kiểm chứng. Những tình huống nhiều điều kiện và dẫn chiếu liên văn bản vẫn cần tiếp tục hoàn thiện trước khi triển khai thực tế."*

---

### NHÓM 4: CÂU HỎI KỸ THUẬT CNTT & TRIỂN KHAI HỆ THỐNG (MINH & DƯƠNG PHỤ TRÁCH)

**Câu 16 (Minh): "Chi phí xây dựng UKG bằng LLM tốn kém thế nào? Hệ thống có scale phục vụ 1.000 người dùng đồng thời được không?"**
> *"Dạ nhóm đã tách biệt quá trình lập chỉ mục và truy vấn trực tuyến để hạn chế việc phải thực hiện lại toàn bộ quá trình trích xuất tri thức khi người dùng đặt câu hỏi.  
> Trong môi trường thử nghiệm, nhóm đã đo đạc một số thành phần xử lý nội bộ như thời gian nhân ma trận vector trên GPU và BM25 trên CPU, nhưng chưa thực hiện kiểm thử tải đồng thời ở quy mô 1.000 người dùng. Vì vậy, hiện tại nhóm chưa đủ dữ liệu thực nghiệm để khẳng định khả năng chịu tải đó. Đây là bước đánh giá cần thiết trước khi triển khai thực tế."*

**Câu 17 (Dương): "Nếu văn bản luật scan bị lỗi OCR (mất dấu, sai định dạng), Parser có bị vỡ trận không?"**
> *"Dạ đây là thách thức điển hình của các phương pháp phân tích dựa trên luật. Trong kiến trúc tại Mục 2.6.3, Module 3 Validation được thiết kế để kiểm tra tính toàn vẹn theo schema, thứ bậc và tính duy nhất. Khi Regex không nhận diện được do lỗi định dạng nghiêm trọng, hệ thống cách ly node lỗi và ghi log cảnh báo, không tự ý sửa nội dung thiếu căn cứ.  
> Hiện tại Parser xử lý dữ liệu đầu vào đã chuẩn hóa; việc tích hợp tiền xử lý sửa lỗi OCR và phân đoạn mềm là hướng nghiên cứu tiếp theo."*

**Câu 18 (Dương): "Hệ số kết hợp BM25 và Vector $\alpha = 0,5$ có phải là đoán mò không? Căn cứ vào đâu?"**
> *"Dạ alpha = 0,5 là cấu hình dung hợp trọng số bằng nhau, được sử dụng làm baseline cho Weighted RRF tại cấu hình C6.  
> Tại Bảng 3.7, nhóm đã khảo sát 11 giá trị trọng số từ 0,0 đến 1,0 để đánh giá mức ảnh hưởng của hai nhánh Dense và BM25. Kết quả tại alpha = 0,8 cải thiện so với cấu hình 0,5 (đạt Recall 0,9297, MRR 0,8220), tuy nhiên vẫn chưa vượt truy hồi vector thuần trên Benchmark A. Vì vậy, nhóm xem đây là cấu hình cân bằng để tiếp tục khảo sát, không kết luận đây là điểm tối ưu toàn cục."*
"""

with open('c:/Users/luuth/NCKH/Benchmark/docs/kich_ban_thuyet_trinh_15p.md', 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated c:/Users/luuth/NCKH/Benchmark/docs/kich_ban_thuyet_trinh_15p.md successfully.')
