# KỊCH BẢN THUYẾT TRÌNH BÁO CÁO VÀ HỒ SƠ BẢO VỆ NCKH (15 PHÚT)
**ĐỀ TÀI:** ĐÁNH GIÁ VÀ TỐI ƯU HÓA CÁC KIẾN TRÚC RAG TRÊN NỀN TẢNG DỮ LIỆU CẤU TRÚC ĐẶC THÙ  
**HỘI ĐỒNG:** BẢO VỆ ĐỀ TÀI NGHIÊN CỨU KHOA HỌC SINH VIÊN  
**NHÓM TÁC GIẢ:** LƯU THANH LÂM – NGÔ THẾ DƯƠNG – NGUYỄN BÌNH MINH  
**GIẢNG VIÊN HƯỚNG DẪN:** TS. NGUYỄN MẠNH DŨNG  

---

# PHẦN 1: TỔNG QUAN PHÂN VAI & ĐIỀU PHỐI THỜI GIAN

* **Tổng thời lượng bảo vệ:** Đúng 15 phút (900 giây).
* **Thời gian thuyết trình phát biểu:** ~13 phút 55 giây (Tổng số từ thoại: 1.814 từ, tốc độ nói trung bình ~130 từ/phút).
* **Khoảng đệm an toàn:** 1 phút 05 giây (Dành cho việc chuyển slide, ngắt nhịp và ổn định trước phần Q&A).
* **Chiến lược học thuật:** Minh bạch theo trọng tâm (Relevance-based Transparency), Đĩnh đạc, Thận trọng và Tự tin dựa trên bằng chứng thực nghiệm (Precise Confidence).

### Bảng phân bổ điều phối 3 thành viên

| Chặng | Diễn giả | Slide | Nội dung trọng tâm | Thời lượng phát biểu | Quỹ thời gian tối đa |
|---|---|:---:|---|:---:|:---:|
| **Chặng 1** | **Lưu Thanh Lâm** | Slide 1 – 2 | Bìa đề tài, Đặt vấn đề & Bài toán ảo giác pháp lý | 1 phút 35 giây | 00:00 – 01:45 |
| **Chặng 2** | **Ngô Thế Dương** | Slide 3 – 6 | Đặc thù văn bản luật, Khảo sát 3 trường phái RAG, 4 RQ & Phương pháp kiểm chuẩn | 3 phút 25 giây | 01:45 – 05:15 |
| **Chặng 3** | **Lưu Thanh Lâm** | Slide 7 – 9 | Giai đoạn 1 (Khoảng cách tìm kiếm – trích dẫn) & Giai đoạn 2 (Parser v2, MaxP, Đột phá C5) | 3 phút 10 giây | 05:15 – 08:25 |
| **Chặng 4** | **Nguyễn Bình Minh** | Slide 10 – 14 | Giai đoạn 3 (Kiến trúc Hybrid UKG, Thực nghiệm Benchmark B, Đóng gói 4 RQ, 3 Đóng góp) | 5 phút 30 giây | 08:25 – 13:55 |
| **Dự phòng** | **Cả nhóm** | — | Khoảng đệm an toàn, chuyển giao micro và kính mời Hội đồng đặt câu hỏi | — | **13:55 – 15:00 (1:05)** |

---

# PHẦN 2: KỊCH BẢN CHI TIẾT 14 SLIDE (BLUEPRINT & LỜI THOẠI)

---

### **[Slide 1] Trang bìa & Giới thiệu đề tài**
* **Người trình bày:** Lưu Thanh Lâm
* **Thời lượng mục tiêu:** 30 giây (Dự kiến: 65 từ)
* **Blueprint Slide:**
  * Tiêu đề đề tài: *Đánh giá và tối ưu hóa các kiến trúc RAG trên nền tảng dữ liệu cấu trúc đặc thù*
  * Nhóm tác giả: Lưu Thanh Lâm (Trưởng nhóm), Ngô Thế Dương, Nguyễn Bình Minh
  * Giảng viên hướng dẫn: TS. Nguyễn Mạnh Dũng
  * Đơn vị công tác: Khoa Công nghệ Thông tin
* **Lời thoại trình bày:**
> *"Kính thưa Hội đồng khoa học!  
> Em xin đại diện nhóm tác giả gồm: Lưu Thanh Lâm, Ngô Thế Dương và Nguyễn Bình Minh, dưới sự hướng dẫn của TS. Nguyễn Mạnh Dũng, trình bày đề tài:  
> **'Đánh giá và tối ưu hóa các kiến trúc RAG trên nền tảng dữ liệu cấu trúc đặc thù'**, tập trung vào văn bản pháp luật Việt Nam."*
* **Ghi chú hành vi:** Đứng thẳng ở trung tâm, giọng mở đầu rõ ràng, ấm, chào trang trọng.

---

### **[Slide 2] Vấn đề nghiên cứu & Bài toán ảo giác pháp lý**
* **Người trình bày:** Lưu Thanh Lâm
* **Thời lượng mục tiêu:** 1 phút 05 giây (Dự kiến: ~140 từ)
* **Blueprint Slide:**
  * **Yêu cầu lĩnh vực:** Tra cứu pháp luật đòi hỏi căn cứ có thể truy vết và kiểm chứng chính xác đến từng Điều, Khoản, Điểm.
  * **Khoảng cách thực tiễn:** Khảo sát của Magesh và cộng sự (2025, *JELS*) ghi nhận tỷ lệ thông tin sai lệch từ 17% đến 33% ở các công cụ AI hỗ trợ nghiên cứu pháp lý thương mại trong điều kiện đánh giá của công trình.
  * **Hệ quả thực tế:** Trích dẫn sai Khoản hoặc bỏ sót Điểm ngoại lệ có thể làm đảo lộn hoàn toàn quyền và nghĩa vụ pháp lý.
  * **Bài toán cốt lõi:** Cân bằng giữa hiệu quả tìm kiếm và năng lực định vị căn cứ vi mô mà không làm bùng nổ dung lượng ngữ cảnh.
* **Lời thoại trình bày:**
> *"Kính thưa Hội đồng, tra cứu pháp luật đòi hỏi căn cứ có thể truy vết và kiểm chứng chính xác đến từng Điều, Khoản, Điểm cụ thể.  
> Tuy nhiên, công bố của Magesh và cộng sự (2025) trên tạp chí JELS ghi nhận tỷ lệ thông tin sai lệch từ 17% đến 33% ở các công cụ AI hỗ trợ nghiên cứu pháp lý được khảo sát, trong điều kiện đánh giá của công trình.  
> Trong thực tế, chỉ cần trích dẫn đúng Điều nhưng sai một Khoản hay bỏ sót một ngoại lệ tại một Điểm, hệ quả pháp lý có thể đảo lộn hoàn toàn từ hợp pháp sang vi phạm.  
> Nhóm đặt bài toán cốt lõi: Làm sao vừa tối ưu tìm kiếm, vừa giúp mô hình định vị chính xác căn cứ vi mô mà không làm bùng nổ dung lượng ngữ cảnh?  
> Sau đây, xin mời bạn Ngô Thế Dương trình bày đặc thù dữ liệu."*
* **Ghi chú hành vi:** Lâm nhấn giọng có kiểm soát ở cụm *"đảo lộn hoàn toàn từ hợp pháp sang vi phạm"*, sau đó lịch thiệp chuyển micro sang Dương.

---

### **[Slide 3] Đặc thù văn bản luật & Ba vấn đề kiểm chứng thực nghiệm**
* **Người trình bày:** Ngô Thế Dương
* **Thời lượng mục tiêu:** 50 giây (Dự kiến: ~110 từ)
* **Blueprint Slide:**
  * **3 Đặc thù dữ liệu (Mục 1.7.1):**
    1. Cấu trúc phân cấp đa tầng: Luật $\rightarrow$ Chương $\rightarrow$ Mục $\rightarrow$ Điều $\rightarrow$ Khoản $\rightarrow$ Điểm.
    2. Mạng lưới dẫn chiếu chéo phức tạp: Quan hệ điều kiện, viện dẫn thi hành và quy phạm ngoại lệ.
    3. Lệch pha từ vựng: Khoảng cách lớn giữa ngôn ngữ đời thường của người dân và thuật ngữ pháp lý quy chuẩn.
  * **3 Vấn đề kiểm chứng thực nghiệm (Mục 1.7.2):**
    1. Tác động của phân đoạn cấu trúc đến hiệu quả truy hồi.
    2. Mức độ bảo đảm đầy đủ các thành phần quy phạm trong câu trả lời.
    3. Khả năng truy vết quan hệ dẫn chiếu giữa những điều luật liên quan.
* **Lời thoại trình bày:**
> *"Em xin cảm ơn bạn Lâm. Kính thưa Quý Thầy Cô,  
> Văn bản luật Việt Nam có ba đặc thù: phân cấp đa tầng từ Luật xuống Điều, Khoản, Điểm; mạng lưới dẫn chiếu chéo quy định điều kiện, ngoại lệ; và sự lệch pha từ vựng giữa câu hỏi người dân với thuật ngữ chuẩn tắc.  
> Từ đó, nhóm tập trung vào ba vấn đề kiểm chứng thực nghiệm: tác động của phân đoạn cấu trúc đến hiệu quả truy hồi; mức độ bảo đảm đầy đủ các thành phần quy phạm trong câu trả lời; và khả năng truy vết quan hệ dẫn chiếu giữa những điều luật liên quan."*
* **Ghi chú hành vi:** Dương nói đĩnh đạc, rõ ràng từng đầu mục.

---

### **[Slide 4] Khảo sát đối chứng ba trường phái RAG đại diện**
* **Người trình bày:** Ngô Thế Dương
* **Thời lượng mục tiêu:** 50 giây (Dự kiến: ~110 từ)
* **Blueprint Slide:**
  * **3 Trường phái đối chứng (Mục 1.4 – 1.6):**
    * **Naive Vector RAG:** Nhúng vector dày đặc (Dense Embedding) + Cosine Similarity. Ưu thế: Khái quát ngữ nghĩa tổng thể; Hạn chế: Dễ mất từ khóa định danh cụ thể.
    * **Hybrid RAG:** Dung hợp BM25 + Dense qua thuật toán RRF kết hợp Cross-Encoder Reranker. Ưu thế: Cân bằng từ khóa và ngữ nghĩa; Hạn chế: Chưa nắm bắt quan hệ phân cấp.
    * **LightRAG (GraphRAG đại diện):** Khai thác LLM trích xuất đồ thị thực thể – quan hệ hai tầng (Low-level & High-level). Ưu thế: Liên kết tri thức mở; Hạn chế: Đòi hỏi tài nguyên lớn, phân đoạn chunk cố định 1.200 token.
* **Lời thoại trình bày:**
> *"Để kiểm chứng các vấn đề trên, nhóm lựa chọn khảo sát ba trường phái RAG đại diện làm hệ thống đối chứng:  
> Naive Vector RAG dựa trên nhúng vector dày đặc và độ tương đồng Cosine, mạnh về ngữ nghĩa khái quát.  
> Hybrid RAG dung hợp từ khóa BM25 và Dense qua giải thuật RRF kết hợp Cross-Encoder Reranker, cải thiện khả năng bắt từ khóa định danh.  
> LightRAG đại diện cho GraphRAG, trích xuất đồ thị thực thể – quan hệ để kết nối tri thức hai tầng.  
> Ba kiến trúc này đại diện cho ba cách tổ chức dữ liệu khác nhau để đối chuẩn trên văn bản luật Việt Nam."*
* **Ghi chú hành vi:** Thể hiện thái độ khách quan khoa học, không chê bai phiến diện hệ thống đối chứng.

---

### **[Slide 5] Bốn câu hỏi nghiên cứu (RQ1 – RQ4)**
* **Người trình bày:** Ngô Thế Dương
* **Thời lượng mục tiêu:** 50 giây (Dự kiến: ~105 từ)
* **Blueprint Slide:**
  * **RQ1 (Baseline Performance):** Hiệu năng truy hồi và độ chính xác trích dẫn của các RAG cơ sở khác biệt thế nào khi cắt đoạn thô?
  * **RQ2 (Structural Optimization):** Bộ phân tích cấu trúc Parser v2 và giải thuật MaxP cải thiện trích dẫn ngữ cảnh và dung lượng ra sao?
  * **RQ3 (Graph-based Reasoning):** Kiến trúc đồ thị hai tầng Hybrid UKG nâng cao hiệu quả truy hồi và xử lý ngoại lệ thế nào khi đối sánh với LightRAG?
  * **RQ4 (Multi-step Reference):** Khả năng định vị đích dẫn chiếu và tái dựng chuỗi quan hệ có thứ tự đạt mức độ nào?
* **Lời thoại trình bày:**
> *"Từ đó, nhóm xây dựng bốn câu hỏi nghiên cứu định hướng:  
> RQ1: Hiệu năng truy hồi và độ chính xác trích dẫn của các RAG cơ sở khác biệt thế nào khi cắt đoạn thô?  
> RQ2: Bộ phân tích cấu trúc Parser v2 và giải thuật MaxP cải thiện trích dẫn ngữ cảnh và dung lượng ra sao?  
> RQ3: Kiến trúc đồ thị hai tầng Hybrid UKG nâng cao hiệu quả truy hồi và xử lý ngoại lệ thế nào khi đối sánh với LightRAG?  
> RQ4: Khả năng định vị đích dẫn chiếu và tái dựng chuỗi quan hệ có thứ tự đạt mức độ nào?"*
* **Ghi chú hành vi:** Đọc dứt khoát 4 RQ, tạo khung sườn logic vững chắc cho toàn bộ bài thuyết trình.

---

### **[Slide 6] Phương pháp kiểm chuẩn & Hai bộ dữ liệu Benchmark A, B**
* **Người trình bày:** Ngô Thế Dương
* **Thời lượng mục tiêu:** 1 phút (Dự kiến: ~135 từ)
* **Blueprint Slide:**
  * **Kiểm soát biến thực nghiệm:** Benchmark Harness chuẩn hóa giao diện qua Adapter Pattern: cùng tập câu hỏi, cùng embedding BGE-M3 và LLM thế hệ GPT-4o-mini.
  * **Quy chuẩn đối chứng GĐ1:** Do LightRAG lập chỉ mục trên 500 điều luật, nhóm xây dựng tập Tier 1 gồm 205 câu hỏi có toàn bộ căn cứ nằm trong 500 điều này để bảo đảm độ bao phủ dữ liệu công bằng.
  * **2 Bộ kiểm chuẩn độc lập (Mục 3.1 & 3.2):**
    * **Benchmark A (N=512):** Phủ 7 đạo luật trọng điểm; được diễn đạt lại có chọn lọc giúp hạ Jaccard trung bình từ 0,68 xuống 0,31 nhằm hạn chế lợi thế của truy hồi từ khóa.
    * **Benchmark B (N=50):** Phân tầng sâu tại Chương III Luật Đất đai 2024 (47 câu phân tích chuyên sâu + 3 câu thẩm định đa tầng) đánh giá đa điều kiện, ngoại lệ và dẫn chiếu.
* **Lời thoại trình bày:**
> *"Để trả lời bốn câu hỏi nghiên cứu, nhóm xây dựng Benchmark Harness chuẩn hóa giao diện thông qua Adapter Pattern, kiểm soát các biến thực nghiệm có thể chuẩn hóa: cùng tập câu hỏi, cùng embedding BGE-M3 và mô hình GPT-4o-mini.  
> Riêng ở Giai đoạn 1, do LightRAG được lập chỉ mục trên 500 điều luật, nhóm lựa chọn 205 câu Tier 1 sao cho toàn bộ căn cứ cần thiết đều nằm trong phạm vi này nhằm đối chuẩn công bằng về độ bao phủ dữ liệu.  
> Nhóm biên soạn hai bộ kiểm chuẩn độc lập: Benchmark A gồm 512 câu hỏi phủ 7 đạo luật, được diễn đạt lại có chọn lọc để giảm Jaccard trung bình từ 0,68 xuống 0,31 nhằm hạn chế lợi thế của truy hồi từ khóa; Benchmark B gồm 50 câu hỏi phân tầng tại Chương III Luật Đất đai 2024.  
> Sau đây, xin mời bạn Lâm trình bày kết quả."*
* **Ghi chú hành vi:** Dương chuyển giao nhịp nhàng lại cho Lâm.

---

### **[Slide 7] Kết quả Giai đoạn 1: Khoảng cách giữa tìm kiếm và trích dẫn (RQ1)**
* **Người trình bày:** Lưu Thanh Lâm
* **Thời lượng mục tiêu:** 1 phút (Dự kiến: ~140 từ)
* **Blueprint Slide:**
  * **Bảng 3.3 & 3.4 — Đối chuẩn Tier 1 (N=205 câu, 500 điều luật):**
    | Kiến trúc | Recall@5 (Bảng 3.3) | Context Precision (Bảng 3.4) | Citation Accuracy (Bảng 3.4) |
    |---|:---:|:---:|:---:|
    | **Naive Vector RAG** | 0,9561 | 0,9659 | **0,3259** |
    | **Hybrid RAG** | **0,9659** | **0,9660** | **0,2902** |
    | **LightRAG** | **0,9659** | 0,8829 | **0,1371** |
  * **Phát hiện khoa học cốt lõi:** Nghịch lý truy hồi tốt nhưng trích dẫn kém (Citation Accuracy chỉ đạt 13% – 33%).
  * **Cơ chế giải thích:** Văn bản thô cấp Điều (Naive/Hybrid) và chunk 1.200 token (LightRAG) thiếu thông tin phân cấp tường minh, tạo khoảng cách giữa phạm vi truy hồi và vị trí căn cứ cần viện dẫn.
* **Lời thoại trình bày:**
> *"Em xin cảm ơn bạn Dương. Kính thưa Hội đồng,  
> Đối chuẩn ba kiến trúc RAG trên tập Tier 1 gồm 205 câu hỏi, nhóm ghi nhận khoảng cách rõ rệt giữa tìm kiếm và trích dẫn:  
> Tại Bảng 3.4, cả ba hệ thống đều tìm kiếm tốt: Recall@5 vượt 95%, Context Precision Naive và Hybrid trên 0,96, LightRAG đạt 0,8829.  
> Tuy nhiên, Citation Accuracy trên câu trả lời sụt giảm sâu: Naive Vector đạt 32,59%, Hybrid đạt 29,02%, và LightRAG chỉ 13,71%.  
> Kết quả gợi ý cơ chế giải thích: việc sử dụng văn bản thô thiếu cấu trúc phân cấp tường minh khiến mô hình khó xác định vị trí pháp lý cần viện dẫn. Riêng LightRAG chia chunk 1.200 token tạo thêm khoảng cách giữa phạm vi truy hồi và căn cứ cần trích dẫn.  
> Kết quả này trả lời cho RQ1: RAG cơ sở bộc lộ khoảng cách lớn ở bài toán trích dẫn nếu giữ nguyên cắt đoạn thô."*
* **Ghi chú hành vi:** Lâm nhấn mạnh nghịch lý bằng giọng điềm tĩnh, chỉ tay vào sự sụt giảm ở cột Citation Accuracy.

---

### **[Slide 8] Giai đoạn 2: Giải pháp cấu trúc Parser v2 & Article MaxP**
* **Người trình bày:** Lưu Thanh Lâm
* **Thời lượng mục tiêu:** 55 giây (Dự kiến: ~120 từ)
* **Blueprint Slide:**
  * **Structure-Aware Parser v2 (Mục 2.2):** Phân đoạn đệ quy theo cấu trúc pháp lý thành 12.754 đơn vị vi mô (cấp Khoản, Điểm); tự động gắn tiền tố phả hệ bất biến `[Luật > Chương > Điều > Khoản]` vào từng đơn vị để duy trì định vị.
  * **Article-Level Max-Pooling (MaxP) (Mục 2.3):**
    * Gom cụm các phân đoạn theo Điều: $S(d_i, q) = \max_{c \in d_i} s(c, q)$.
    * Tránh bão hòa Top-K bởi nhiều Khoản cùng Điều, chọn lọc phân đoạn vi mô đại diện để đưa vào ngữ cảnh.
* **Lời thoại trình bày:**
> *"Để giải quyết khoảng cách trên, ở Giai đoạn 2, nhóm đề xuất giải pháp cấu trúc:  
> Bộ phân tích Structure-Aware Parser v2 bóc tách đệ quy văn bản thành 12.754 phân đoạn vi mô cấp Khoản, Điểm; gắn tiền tố phả hệ bất biến từ Luật, Chương đến Điều, bảo toàn thông tin định vị phân cấp.  
> Nhằm tránh bão hòa Top-K bởi nhiều Khoản cùng Điều, nhóm đề xuất giải thuật Article-Level Max-Pooling: gom cụm phân đoạn theo Điều, lấy điểm cực đại để xếp hạng cấp Điều; sau đó chọn lọc phân đoạn vi mô liên quan đưa vào mô hình.  
> Giải pháp này vừa thu hẹp dung lượng ngữ cảnh, vừa bảo toàn thông tin phân cấp."*
* **Ghi chú hành vi:** Trình bày gãy gọn hai trụ cột kỹ thuật: Parser v2 định danh, MaxP gom cụm.

---

### **[Slide 9] Kết quả Giai đoạn 2: Đột phá cấu hình C5 & Khảo sát tham số (RQ2)**
* **Người trình bày:** Lưu Thanh Lâm
* **Thời lượng mục tiêu:** 1 phút (Dự kiến: ~125 từ)
* **Blueprint Slide:**
  * **Bảng 3.6 — Đánh giá trên Benchmark A (N=512, 3.072 lượt LLM-Judge):**
    * Cấu hình C2 (Raw Chunk + Dense): Citation Accuracy ngữ cảnh = **0,4000** | Token = 2.891
    * Cấu hình C5 (Parser v2 + Article MaxP + Dense): Citation Accuracy ngữ cảnh = **0,9902** (+59,02 đpt, 98,4% đạt điểm 1,0) | Token = **580** (Giảm 79,9%)
  * **Bảng 3.7 — Khảo sát trọng số RRF (α):** α = 0,8 đạt Recall 0,9297, MRR 0,8220 (Cấu hình cân bằng giữa Dense và BM25).
  * **Lưu ý phương pháp luận:** GĐ2 đánh giá riêng chất lượng căn cứ trong ngữ cảnh truy hồi bằng LLM-Judge độc lập với việc sinh câu trả lời hoàn chỉnh.
* **Lời thoại trình bày:**
> *"Trên 512 câu hỏi Benchmark A với 3.072 lượt đánh giá LLM-Judge, Bảng 3.6 làm sáng tỏ RQ2:  
> Điểm nổi bật nhất, LLM-Judge Citation Accuracy trên ngữ cảnh truy hồi ở cấu hình C5 đạt 0,9902, tăng 59,02 điểm phần trăm so với C2, với 98,4% số câu đạt điểm tuyệt đối 1,0.  
> Đồng thời, dung lượng ngữ cảnh giảm mạnh 79,9%, từ gần 2.900 token xuống còn 580 token. Khảo sát tại Bảng 3.7 ghi nhận cấu hình cân bằng alpha = 0,8 duy trì tốt cả truy hồi Dense và từ khóa.  
> Nhóm lưu ý: Giai đoạn 2 đánh giá riêng chất lượng căn cứ trong ngữ cảnh bằng LLM-Judge, độc lập với việc sinh câu trả lời, tạo tiền đề để đánh giá toàn trình ở Giai đoạn 3.  
> Sau đây, xin mời bạn Nguyễn Bình Minh trình bày tiếp."*
* **Ghi chú hành vi:** Lâm nêu bật 2 con số ấn tượng nhất (0,9902 và -79,9% token), làm rõ phương pháp luận rồi chuyển micro cho Minh.

---

### **[Slide 10] Giai đoạn 3: Kiến trúc Hybrid UKG & Semantic Router Module 5**
* **Người trình bày:** Nguyễn Bình Minh
* **Thời lượng mục tiêu:** 1 phút 10 giây (Dự kiến: ~150 từ)
* **Blueprint Slide:**
  * **Kiến trúc đồ thị hai tầng Hybrid UKG (Mục 2.6):**
    * **Physical Graph (Đồ thị vật lý):** Dựng khung phân cấp Chương-Mục-Điều-Khoản bằng quy tắc tất định; Module 3 Validation cách ly các node lỗi cấu trúc.
    * **Semantic Graph (Đồ thị ngữ nghĩa):** Trích xuất động quan hệ dẫn chiếu, điều kiện và ngoại lệ; thực hiện hoàn toàn trong pha lập chỉ mục.
  * **Module 5 Semantic Router (Mục 2.6.4):**
    * Mô hình ngôn ngữ tự hồi quy Qwen2.5-0.5B kết hợp toán tử Max-Fusion giữa Regex và điểm Vector.
    * Đánh giá Golden Set v2 ($N=193$): Tại θ = 0,85, Recall đạt 96,85%, F1 đạt 0,8146.
    * Giảm 9,33% khối lượng xử lý chuyển tiếp (18 node), trong đó loại 14 node thủ tục và chấp nhận đánh đổi 4 node quy phạm bị bỏ sót.
* **Lời thoại trình bày:**
> *"Em xin cảm ơn bạn Lâm. Kính thưa Quý Thầy Cô,  
> Để xử lý truy vấn đa bước và ngoại lệ, nhóm xây dựng kiến trúc Hybrid Parser/UKG hai tầng:  
> Tầng 1 là Đồ thị vật lý — dùng quy tắc tất định dựng phân cấp, Module 3 Validation cách ly các node lỗi cấu trúc.  
> Tầng 2 là Đồ thị ngữ nghĩa — trích xuất động quan hệ dẫn chiếu, điều kiện và ngoại lệ.  
> Quá trình xử lý tri thức thực hiện lúc lập chỉ mục; khi truy vấn, hệ thống duyệt đồ thị để thu thập bằng chứng.  
> Trọng tâm là Module 5 Semantic Router: kết hợp mô hình Qwen2.5-0.5B và toán tử Max-Fusion giữa Regex và Vector. Trên Golden Set 193 node, tại ngưỡng theta = 0,85, hệ thống đạt Recall 96,85% và F1 0,8146. So với ngưỡng 0,80, cơ chế này giúp giảm 9,33% khối lượng xử lý chuyển tiếp, trong đó loại 14 node thủ tục nhưng chấp nhận đánh đổi 4 node quy phạm bị bỏ sót."*
* **Ghi chú hành vi:** Minh mở đầu dõng dạc, giải thích rành mạch kiến trúc và trade-off kỹ thuật.

---

### **[Slide 11] Kết quả Giai đoạn 3: Đối đầu trực diện LightRAG (RQ3 & RQ4)**
* **Người trình bày:** Nguyễn Bình Minh
* **Thời lượng mục tiêu:** 1 phút 20 giây (Dự kiến: ~170 từ)
* **Blueprint Slide:**
  * **Bảng đối soát Benchmark B (N=50, Chương III Luật Đất đai 2024):**
    | Nhóm chỉ số | Chỉ số thực nghiệm | LightRAG | Hybrid UKG | Chênh lệch / Ý nghĩa |
    |---|---|:---:|:---:|---|
    | **Truy hồi cấp Điều** | Recall@5 | 0,7358 | **0,9184** | **+18,26 đpt** (Bảng 3.9) |
    | | MRR@5 | 0,5539 | **0,8848** | **+33,09 đpt** (Bảng 3.9) |
    | **Độ chính xác trích dẫn** | Citation Precision (Điều) | 0,3333 | **0,8369** | **+50,36 đpt** (Bảng 3.16) |
    | | Citation Precision (Khoản) | 0,0435 | **0,7757** | **+73,22 đpt** (Bảng 3.16) |
    | **Chất lượng nội dung** | Legal Correctness | 0,8210 | **0,8777** | **+5,67 đpt** (Bảng 3.15) |
    | | Exception Coverage | 0,3929 | **0,6786** | **+28,57 đpt** (Bảng 3.15) |
    | **Ranh giới kỹ thuật** | Condition Coverage | **0,8421** | 0,7066 | UKG thấp hơn -13,55 đpt (Bảng 3.15) |
    | | Exact Locator Recall@5 | **0,8509** | 0,5560* | Footnote kép (*39/47 câu đo được; Độ hạt)* |
    | | Chain Exact Match (N=18) | N/A | **0,0000** | Ranh giới cần Constrained Traversal (Bảng 3.10) |
  * *\*Footnote kỹ thuật:* UKG đo trên 39/47 câu (8 câu not_measured); LightRAG đo trên 47/47 câu. Chunk 1.200 token của LightRAG chứa trung bình ~15 locator, trong khi phân đoạn UKG chỉ chứa 1 locator. LightRAG chưa hỗ trợ trích xuất đường dẫn theo giao thức này nên Chain Exact Match là N/A.
* **Lời thoại trình bày:**
> *"Kính thưa Hội đồng, thực nghiệm Benchmark B gồm 50 câu hỏi tại Chương III Luật Đất đai 2024 làm sáng tỏ RQ3 và RQ4 qua ba khối thông tin:  
> Về truy hồi cấp Điều (Bảng 3.9), Hybrid UKG đạt Recall@5 0,9184 so với 0,7358 của LightRAG (vượt 18,26 điểm phần trăm) và MRR@5 đạt 0,8848 so với 0,5539 (vượt 33,09 điểm phần trăm).  
> Về chất lượng trích dẫn, Citation Precision cấp Điều đạt 0,8369 so với 0,3333; cấp Khoản đạt 0,7757 so với 0,0435 của LightRAG. Ở tầng nội dung, Legal Correctness đạt 0,8777 và Exception Coverage đạt 0,6786 — cao hơn LightRAG 28,57 điểm phần trăm trong xử lý các tình huống có ngoại lệ.  
> Về ranh giới kỹ thuật: Condition Coverage đạt 0,7066 so với 0,8421, cho thấy hệ thống còn hạn chế khi tổng hợp điều kiện phân tán. Với Exact Locator Recall@5, LightRAG đạt 0,8509 trên 47 câu, còn UKG đạt 0,5560 trên 39 câu đo được do khác biệt về độ hạt phân đoạn. Về Chain Exact Match, hệ thống đạt 0,0000 trên 18 câu đa bước, còn LightRAG ở trạng thái chưa hỗ trợ trích xuất đường dẫn theo giao thức này."*
* **Ghi chú hành vi:** Minh bình tĩnh, chỉ trực tiếp vào các chỉ số trade-off, phong thái tự tin và minh bạch.

---

### **[Slide 12] Tổng hợp đóng gói câu trả lời cho bốn RQ**
* **Người trình bày:** Nguyễn Bình Minh
* **Thời lượng mục tiêu:** 1 phút (Dự kiến: ~135 từ)
* **Blueprint Slide:**
  * **RQ1 (Baseline Performance):** Xác lập thực nghiệm khoảng cách giữa tìm kiếm và trích dẫn, chỉ ra hạn chế của việc cắt đoạn thô thiếu cấu trúc phân cấp.
  * **RQ2 (Structural Optimization):** Bằng chứng thực nghiệm khẳng định Parser v2 và MaxP nâng Citation Accuracy ngữ cảnh lên 0,9902 và giảm 79,9% dung lượng đầu vào.
  * **RQ3 (Graph-based Reasoning):** Hybrid UKG vượt trội LightRAG ở truy hồi cấp Điều, trích dẫn cấp Khoản và độ bao phủ ngoại lệ; làm rõ ranh giới ở điều kiện pháp lý phân tán.
  * **RQ4 (Multi-step Reference):** Hệ thống định vị được 58,67% căn cứ đích đơn lẻ; chỉ ra sự cần thiết của giải thuật duyệt đồ thị có ràng buộc để khép kín chuỗi quan hệ có thứ tự.
* **Lời thoại trình bày:**
> *"Từ ba giai đoạn thực nghiệm, nhóm đối chiếu lại bốn câu hỏi nghiên cứu ban đầu:  
> RQ1: Xác lập thực nghiệm khoảng cách giữa truy hồi và trích dẫn, chỉ ra hạn chế của việc sử dụng văn bản thô thiếu cấu trúc phân cấp.  
> RQ2: Cung cấp bằng chứng cho thấy Parser v2 và MaxP nâng Citation Accuracy ngữ cảnh lên 0,9902 và giảm 79,9% dung lượng ngữ cảnh.  
> RQ3: Hybrid UKG đạt kết quả cao hơn LightRAG ở truy hồi cấp Điều, độ chính xác trích dẫn cấp Điều, Khoản và độ bao phủ ngoại lệ; tuy nhiên còn hạn chế ở thành phần điều kiện phân tán.  
> RQ4: Hệ thống định vị được 58,67% căn cứ đích đơn lẻ, làm rõ ranh giới cần giải thuật duyệt đồ thị có ràng buộc để khép kín chuỗi dẫn chiếu có thứ tự."*
* **Ghi chú hành vi:** Minh đúc kết mạch lạc, trả lời trọn vẹn 4 RQ đặt ra từ đầu bài.

---

### **[Slide 13] Ba đóng góp khoa học cốt lõi & Thông điệp kết luận**
* **Người trình bày:** Nguyễn Bình Minh
* **Thời lượng mục tiêu:** 40 giây (Dự kiến: ~85 từ)
* **Blueprint Slide:**
  * **3 Đóng góp khoa học cốt lõi:**
    1. *Khung kiểm chuẩn & Phương pháp đánh giá:* Bộ Benchmark A (512 câu), Benchmark B (50 câu) cùng hạ tầng Adapter Pattern chuẩn hóa.
    2. *Phương pháp tổ chức dữ liệu cấu trúc:* Bộ bóc tách Parser v2 và giải thuật Article MaxP giúp tối ưu hóa dung lượng và định vị căn cứ.
    3. *Kiến trúc đồ thị hai tầng:* Mô hình Hybrid UKG kết hợp đồ thị vật lý và ngữ nghĩa để xử lý quy phạm ngoại lệ.
  * **Thông điệp đúc kết:** *"Trong dữ liệu pháp luật, cấu trúc không chỉ là hình thức tổ chức văn bản mà còn ảnh hưởng trực tiếp đến khả năng định vị và sử dụng căn cứ của hệ thống RAG."*
* **Lời thoại trình bày:**
> *"Từ kết quả ba giai đoạn, đề tài xác định ba đóng góp: khung kiểm chuẩn Benchmark A, B cùng Adapter Pattern; phương pháp phân đoạn cấu trúc vi mô kết hợp MaxP; và kiến trúc đồ thị hai tầng Hybrid UKG.  
> Thông điệp đúc kết của nhóm là: Trong dữ liệu pháp luật, cấu trúc không chỉ là hình thức tổ chức văn bản mà còn ảnh hưởng trực tiếp đến khả năng định vị và sử dụng căn cứ của hệ thống RAG."*
* **Ghi chú hành vi:** Minh nói chậm rãi, nhấn từng từ ở câu thông điệp kết luận, phong thái trang trọng.

---

### **[Slide 14] Lộ trình phát triển & Lời cảm ơn**
* **Người trình bày:** Nguyễn Bình Minh
* **Thời lượng mục tiêu:** 30 giây (Dự kiến: ~60 từ)
* **Blueprint Slide:**
  * **Hướng phát triển tương lai:**
    * Mở rộng bộ phân tích cấu trúc sang văn bản dưới luật (Nghị định, Thông tư).
    * Tự động hóa cơ chế cập nhật hiệu lực và sửa đổi văn bản pháp luật.
    * Hoàn thiện giải thuật duyệt đồ thị có ràng buộc (Constrained Traversal) để nâng cao Chain Exact Match.
  * **Lời cảm ơn:** Trân trọng cảm ơn Quý Thầy Cô trong Hội đồng khoa học và Giảng viên hướng dẫn TS. Nguyễn Mạnh Dũng.
* **Lời thoại trình bày:**
> *"Thời gian tới, nhóm hướng đến mở rộng bộ bóc tách sang Nghị định, Thông tư; tự động hóa cập nhật hiệu lực văn bản; và hoàn thiện giải thuật duyệt đồ thị có ràng buộc.  
> Thay mặt nhóm nghiên cứu, chúng em xin trân trọng cảm ơn Quý Thầy Cô đã chú ý lắng nghe. Nhóm kính mời Hội đồng đặt câu hỏi."*
* **Ghi chú hành vi:** Cả ba thành viên cùng đứng nghiêm túc, cúi đầu chào Hội đồng.

---

# PHẦN 3: BẢNG TỔNG HỢP ANCHOR NOTES 14 SLIDE (TRA CỨU TRÊN BỤC)

| Slide | Người nói | Số liệu mỏ neo (Anchor Metrics) | Căn cứ Báo cáo | Cảnh báo vùng cấm (Boundary Safeguard) |
|:---:|:---:|---|---|---|
| **1** | Lâm | 3 thành viên, GVHD: TS. Nguyễn Mạnh Dũng | Trang bìa | Đọc đúng tên đề tài, không nói lan man. |
| **2** | Lâm | Ảo giác AI pháp lý 17% – 33% | Magesh et al. (2025), *JELS* | Nêu rõ trong phạm vi công cụ khảo sát; bỏ cụm từ "kiểm chứng tuyệt đối". |
| **3** | Dương | Luật $\rightarrow$ Chương $\rightarrow$ Mục $\rightarrow$ Điều $\rightarrow$ Khoản $\rightarrow$ Điểm | Mục 1.7.1, 1.7.2 | Nêu đúng 3 vấn đề kiểm chứng thực nghiệm. |
| **4** | Dương | Naive (Dense), Hybrid (BM25+Dense+RRF), LightRAG (Graph) | Mục 1.4 – 1.6 | Trình bày trung tính, không dìm hệ thống đối chứng. |
| **5** | Dương | 4 câu hỏi nghiên cứu: RQ1, RQ2, RQ3, RQ4 | Mục 1.2 | Đọc đúng tên và phạm vi từng RQ. |
| **6** | Dương | Benchmark A (512 câu, Jaccard 0,68 $\rightarrow$ 0,31); Benchmark B (50 câu); Tier 1 (205 câu) | Mục 3.1, 3.2 | Giải thích rõ Tier 1 nằm trong 500 điều index của LightRAG; không quy chụp "cùng toàn bộ văn bản nguồn". |
| **7** | Lâm | Naive 32,59%, Hybrid 29,02%, LightRAG 13,71% Citation Acc | Bảng 3.4 | Nêu rõ Naive/Hybrid dùng Điều thô, LightRAG dùng chunk 1.200 token. Trình bày dưới dạng cơ chế giải thích. |
| **8** | Lâm | 12.754 phân đoạn vi mô, tiền tố phả hệ bất biến, Article MaxP | Mục 2.2, 2.3 | MaxP gom cụm cấp Điều, không làm mất liên kết ngữ cảnh. |
| **9** | Lâm | C5 Citation 0,9902 (+59,02 đpt, 98,4% đạt 1,0); Token giảm 79,9% (2.891 $\rightarrow$ 580) | Bảng 3.6, 3.7 | Làm rõ GĐ2 dùng LLM-Judge trên ngữ cảnh độc lập với việc sinh câu trả lời; alpha=0,8 là cấu hình cân bằng, không overclaim. |
| **10** | Minh | 2 tầng Physical/Semantic; M5 Qwen2.5-0.5B: Recall 96,85%, F1 0,8146, giảm 9,33% tải chuyển tiếp | Mục 2.6, Golden Set v2 N=193 | Giải thích đúng 9,33% là giảm tải chuyển tiếp (18 node), loại 14 thủ tục, chấp nhận 4 FN. Không khẳng định Causal Attention đã được cô lập. |
| **11** | Minh | Recall@5 Điều 0,9184 vs 0,7358; Precision Khoản 0,7757 vs 0,0435; Condition 0,7066 vs 0,8421; Exact Locator 0,5560 vs 0,8509 | Bảng 3.9, 3.11, 3.15, 3.16 | Không nói "gấp 18 lần". Đọc đủ footnote mẫu số 39/47 vs 47/47 và độ hạt ~15 locator/chunk. Nêu rõ LightRAG N/A ở Chain Exact Match. |
| **12** | Minh | Khép góc 4 RQ: RQ1 (Khoảng cách), RQ2 (Parser v2+MaxP), RQ3 (UKG ưu thế + ranh giới), RQ4 (58,67% đích) | Mục 3.4 – 3.7 | Khẳng định khách quan theo đúng số liệu thực nghiệm. |
| **13** | Minh | 3 đóng góp khoa học + 1 thông điệp triết lý cấu trúc | Kết luận báo cáo | Đọc chậm, đĩnh đạc, gói gọn trong 85 từ để tạo sức nặng. |
| **14** | Minh | Mở rộng Nghị định/Thông tư, cập nhật hiệu lực, Constrained Traversal | Hướng phát triển | Cảm ơn Hội đồng trang trọng và khiêm tốn. |

---

# PHẦN 4: HỆ THỐNG 18 KỊCH BẢN PHẢN BIỆN (Q&A PLAYBOOK)

### **Nhóm A: Tính hợp lệ thực nghiệm & Benchmark (Q1 – Q5)**

#### **Q1. Tại sao nhóm phải giảm Jaccard từ 0,68 xuống 0,31 ở Benchmark A?**
* **Người trả lời:** Ngô Thế Dương
* **Câu trả lời chuẩn:**
  > *"Dạ thưa Thầy Cô, khi câu hỏi của người dùng trùng lặp từ vựng quá lớn với văn bản luật (Jaccard > 0,5), các giải thuật tìm kiếm từ khóa cổ điển như BM25 sẽ đạt kết quả cao đột biến. Điều này che lấp khoảng cách năng lực hiểu ngữ nghĩa và phân tích cấu trúc của các mô hình RAG.  
  > Nhóm đã tiến hành diễn đạt lại có chọn lọc trên các câu có độ trùng lặp cao, đưa Jaccard trung bình từ 0,68 xuống 0,31. Mục tiêu là mô phỏng sát thực tế cách đặt câu hỏi bằng ngôn ngữ tự nhiên của người dân, từ đó kiểm định khách quan khả năng truy hồi ngữ nghĩa của từng kiến trúc."*

#### **Q2. Tập kiểm chuẩn Benchmark B chỉ có 50 câu hỏi thì có đủ ý nghĩa thống kê không?**
* **Người trả lời:** Ngô Thế Dương
* **Câu trả lời chuẩn:**
  > *"Dạ thưa Thầy Cô, Benchmark B được thiết kế chuyên biệt cho Giai đoạn 3 nhằm đánh giá sâu các quan hệ pháp lý phức tạp mà Benchmark A diện rộng chưa bao quát hết.  
  > 50 câu hỏi này tập trung trọn vẹn tại Chương III Luật Đất đai 2024, bao gồm 47 câu đơn tầng và 3 câu đa tầng với 7 câu hỏi ngoại lệ và điều cấm, cùng 10 câu hỏi dẫn chiếu (6 câu đơn bước, 4 câu đa bước). Việc giới hạn 50 câu cho phép nhóm kiểm toán thủ công chi tiết từng căn cứ Điều, Khoản, Điểm và chuỗi suy luận, bảo đảm tính xác thực tuyệt đối của ground-truth mà các bộ dữ liệu tự động quy mô lớn không thể đối soát tỉ mỉ được."*

#### **Q3. Thiết kế thực nghiệm Tier 1 ở Giai đoạn 1 có bảo đảm tính công bằng không?**
* **Người trả lời:** Ngô Thế Dương
* **Câu trả lời chuẩn:**
  > *"Dạ thưa Thầy Cô, trong Giai đoạn 1, do LightRAG trích xuất đồ thị bằng mô hình ngôn ngữ lớn đòi hỏi chi phí API cao, nhóm lập chỉ mục LightRAG trên phạm vi 500 điều luật trọng điểm.  
  > Để đảm bảo tính công bằng khi đối chuẩn, nhóm xây dựng tập Tier 1 gồm 205 câu hỏi mà toàn bộ căn cứ cần thiết đều nằm trọn trong 500 điều này. Nhờ đó, cả ba hệ thống đều có cơ hội truy hồi như nhau trên không gian chứa căn cứ. Các yếu tố khác như mô hình nhúng BGE-M3, mô hình sinh GPT-4o-mini và tham số K=5 đều được cố định thông qua Benchmark Harness."*

#### **Q4. Việc đánh giá bằng LLM-Judge (GPT-4o-mini) có đưa định kiến vào kết quả không?**
* **Người trả lời:** Lưu Thanh Lâm
* **Câu trả lời chuẩn:**
  > *"Dạ thưa Thầy Cô, nhóm nhận thức rõ LLM-Judge có thể tồn tại thiên vị về độ dài hoặc vị trí thông tin. Để kiểm soát điều này, nhóm đã áp dụng ba giải pháp kỹ thuật:  
  > Thứ nhất, chuẩn hóa prompt chấm điểm theo thang rubric nhị phân tường minh (0 hoặc 1) dựa trên căn cứ trích dẫn cụ thể.  
  > Thứ hai, ở Giai đoạn 2, nhóm thực hiện 3.072 lượt thẩm định độc lập.  
  > Thứ ba, ở Giai đoạn 3, nhóm kết hợp cả chỉ số tự động dựa trên quy tắc chuỗi ký tự (như Citation Precision cấp Điều, Khoản) lẫn đối soát thủ công của con người để kiểm chứng chéo, đảm bảo kết quả không phụ thuộc phiến diện vào một giám khảo AI."*

#### **Q5. Tại sao Naive Vector RAG ở Giai đoạn 1 lại có Context Precision cao (0,9673) nhưng Citation Accuracy lại thấp (0,3259)?**
* **Người trả lời:** Lưu Thanh Lâm
* **Câu trả lời chuẩn:**
  > *"Dạ thưa Thầy Cô, đây chính là phát hiện thực nghiệm quan trọng nhất của Giai đoạn 1:  
  > Context Precision đo lường việc tài liệu liên quan có xuất hiện trong Top-K hay không. Do nhúng toàn bộ văn bản Điều thô, vector dense rất dễ bắt trúng ngữ nghĩa đại thể của câu hỏi, đưa Điều luật vào top đầu.  
  > Tuy nhiên, Citation Accuracy đo lường việc câu trả lời của mô hình có chỉ ra chính xác căn cứ pháp lý hay không. Do văn bản thô thiếu cấu trúc phân cấp, LLM bị phân tâm bởi khối văn bản dài và trích dẫn mơ hồ, dẫn đến tỷ lệ ảo giác trích dẫn cao dù tài liệu liên quan đã được lấy về."*

---

### **Nhóm B: Phương pháp phân đoạn & Tối ưu hóa GĐ2 (Q6 – Q10)**

#### **Q6. Bộ phân tích Structure-Aware Parser v2 khác gì so với các công cụ chunking đệ quy phổ biến như RecursiveCharacterTextSplitter?**
* **Người trả lời:** Lưu Thanh Lâm
* **Câu trả lời chuẩn:**
  > *"Dạ thưa Thầy Cô, các bộ cắt đoạn như RecursiveCharacterTextSplitter dựa hoàn toàn vào độ dài ký tự và dấu ngắt đoạn hình thức, dễ cắt đôi một mệnh đề điều kiện hoặc tách rời Khoản khỏi Điều.  
  > Parser v2 của nhóm dựa trên văn phạm cấu trúc pháp luật Việt Nam: bóc tách đệ quy chuẩn xác theo từng cấp Điều, Khoản, Điểm; đồng thời tự động gắn tiền tố phả hệ bất biến chứa đầy đủ tên Luật, Chương, Điều vào từng phân đoạn vi mô. Nhờ đó, mỗi phân đoạn khi đứng độc lập trong không gian vector vẫn mang đầy đủ ngữ cảnh nguồn gốc mà không bị phân mảnh."*

#### **Q7. Tại sao lại cần giải thuật Article-Level Max-Pooling (MaxP) sau khi đã phân đoạn vi mô?**
* **Người trả lời:** Lưu Thanh Lâm
* **Câu trả lời chuẩn:**
  > *"Dạ thưa Thầy Cô, khi bóc tách nhỏ thành cấp Khoản, một Điều luật dài có thể tạo ra hàng chục phân đoạn. Nếu truy hồi thông thường, danh sách Top-K sẽ bị bão hòa bởi nhiều Khoản thuộc cùng một Điều, làm mất cơ hội xuất hiện của các Điều luật liên quan khác.  
  > Giải thuật MaxP giải quyết triệt để vấn đề này bằng cách gom cụm phân đoạn theo Điều và lấy điểm số cao nhất của phân đoạn đại diện để xếp hạng Top-K cấp Điều; sau đó mới thu thập các phân đoạn vi mô liên quan để nạp vào LLM. Cơ chế này vừa tối ưu độ phủ cấp Điều, vừa giữ ngữ cảnh tinh gọn."*

#### **Q8. Tại sao Condition Coverage của Hybrid UKG (0,7066) lại thấp hơn LightRAG (0,8421)?**
* **Người trả lời:** Nguyễn Bình Minh
* **Câu trả lời chuẩn:**
  > *"Dạ thưa Thầy Cô, nhóm xin thẳng thắn thừa nhận đây là một ranh giới đánh đổi kỹ thuật của hệ thống:  
  > Phân đoạn vi mô của UKG tập trung mạnh vào quy phạm lõi của từng phân đoạn, trong khi các điều kiện áp dụng pháp luật thường nằm rải rác ở nhiều Khoản hoặc các Điều quy định chung. LightRAG dùng chunk lớn 1.200 token nên vô tình ôm trọn các điều kiện bối cảnh xung quanh.  
  > Nhóm chưa đủ cơ sở quy toàn bộ chênh lệch này cho cơ chế phân đoạn, vì kết quả còn phụ thuộc quá trình mở rộng ngữ cảnh và mô hình sinh. Nhóm nhận định đây là hướng cần hoàn thiện thông qua cơ chế lan truyền ngữ cảnh điều kiện giữa các node liên quan."*

#### **Q9. Tại sao trọng số α = 0,8 được lựa chọn trong khảo sát RRF ở Giai đoạn 2?**
* **Người trả lời:** Lưu Thanh Lâm
* **Câu trả lời chuẩn:**
  > *"Dạ thưa Thầy Cô, tại Bảng 3.7, nhóm khảo sát 11 giá trị α từ 0,0 đến 1,0.  
  > Thực nghiệm cho thấy α = 1,0 (Dense thuần) đạt Recall cao nhất là 0,9316 và MRR 0,8602. Tuy nhiên, nhóm lựa chọn cấu hình α = 0,8 (Recall 0,9297, MRR 0,8220) để tiếp tục khảo sát vì cấu hình này duy trì được sự cân bằng: vừa bảo toàn được ưu thế vượt trội của vector dense trên tập câu hỏi đã diễn đạt lại, vừa giữ lại 20% tín hiệu từ khóa của BM25 để phòng thủ khi người dùng tra cứu các thuật ngữ định danh cứng."*

#### **Q10. Con số Citation Accuracy 0,9902 ở cấu hình C5 có phải là tỷ lệ trích dẫn chính xác của câu trả lời không?**
* **Người trả lời:** Lưu Thanh Lâm
* **Câu trả lời chuẩn:**
  > *"Dạ thưa Thầy Cô, nhóm xin làm rõ về phương pháp luận: Con số 0,9902 là điểm số LLM-Judge Citation Accuracy trung bình đánh giá trên ngữ cảnh truy hồi được nạp vào mô hình (với 504/512 câu đạt điểm tuyệt đối 1,0), chứ không phải độ chính xác trích dẫn trên câu trả lời sinh ra toàn trình.  
  > Mục tiêu của Giai đoạn 2 là đánh giá độc lập năng lực của bộ truy hồi cấu trúc trong việc đưa đúng và đủ căn cứ vào ngữ cảnh, tách biệt với năng lực sinh văn bản của mô hình ngôn ngữ lớn. Năng lực trích dẫn trên câu trả lời toàn trình được đánh giá khắt khe ở Giai đoạn 3."*

---

### **Nhóm C: Kiến trúc Đồ thị & Module 5 Router (Q11 – Q15)**

#### **Q11. Việc xây dựng đồ thị Hybrid UKG có làm tăng độ trễ khi người dùng gửi câu hỏi không?**
* **Người trả lời:** Nguyễn Bình Minh
* **Câu trả lời chuẩn:**
  > *"Dạ thưa Thầy Cô, hoàn toàn không làm tăng độ trễ thời gian thực.  
  > Toàn bộ quá trình phân tích cú pháp, trích xuất thực thể, dựng đồ thị vật lý và liên kết đồ thị ngữ nghĩa được thực hiện ngoại tuyến trong pha lập chỉ mục (Indexing time).  
  > Khi người dùng gửi câu hỏi trực tuyến (Query time), hệ thống chỉ thực hiện truy vấn vector để định vị node mỏ neo và duyệt theo các cạnh quan hệ có sẵn trên đồ thị. Do đó, thời gian đáp ứng tương đương với các hệ thống RAG thông thường nhưng độ chính xác căn cứ vượt trội hơn."*

#### **Q12. Tại sao nhóm lựa chọn mô hình Qwen2.5-0.5B và cơ chế Causal Attention cho Module 5?**
* **Người trả lời:** Nguyễn Bình Minh
* **Câu trả lời chuẩn:**
  > *"Dạ thưa Thầy Cô, nhóm lựa chọn Qwen2.5-0.5B nhằm khai thác năng lực biểu diễn ngữ nghĩa của mô hình ngôn ngữ tự hồi quy, sau đó kết hợp điểm ngữ nghĩa với tín hiệu Regex bằng toán tử Max-Fusion.  
  > Cơ sở lựa chọn là kết quả kiểm chuẩn toàn bộ cấu hình trên Golden Set v2 đạt F1 0,8146 với kích thước chỉ 0,5 tỷ tham số, tối ưu cho xử lý cục bộ. Nhóm nhận định hướng biểu diễn này phù hợp với văn bản quy phạm ngắn có trật tự logic điều kiện, dù chưa thực hiện ablation riêng lẻ để cô lập hoàn toàn đóng góp nhân quả của Causal Attention so với các yếu tố khác trong kiến trúc."*

#### **Q13. Tại sao chỉ số Exact Locator Recall@5 của UKG (0,5560) lại thấp hơn LightRAG (0,8509)?**
* **Người trả lời:** Nguyễn Bình Minh
* **Câu trả lời chuẩn:**
  > *"Dạ thưa Thầy Cô, đây là sự khác biệt bản chất về độ hạt phân đoạn giữa hai hệ thống:  
  > Thứ nhất, về số câu đo được: 0,5560 được tính trên 39 câu đo được của UKG (8 câu ở trạng thái not_measured), trong khi LightRAG đo trên 47 câu.  
  > Thứ hai, về độ hạt: Chunk 1.200 token của LightRAG chứa trung bình khoảng 15 locator (Điều/Khoản/Điểm), trong khi mỗi phân đoạn của UKG chỉ chứa đúng 1 locator vi mô duy nhất. Khối văn bản lớn của LightRAG có xác suất bao trùm locator cao hơn, nhưng dẫn đến việc mô hình không biết căn cứ nằm ở đâu, thể hiện qua việc Citation Precision cấp Khoản của LightRAG chỉ đạt 4,35%. UKG chấp nhận sự đánh đổi này để đạt Precision cấp Khoản 77,57%, gấp gần 18 lần đối thủ."*

#### **Q14. Toán tử Max-Fusion trong Module 5 hoạt động thế nào khi có xung đột giữa Regex và Vector?**
* **Người trả lời:** Nguyễn Bình Minh
* **Câu trả lời chuẩn:**
  > *"Dạ thưa Thầy Cô, Max-Fusion áp dụng logic OR mềm: $S_{final} = \max(S_{regex}, S_{vector})$.  
  > Khi một phân đoạn có cấu trúc hiển ngôn chứa từ khóa quy phạm rõ ràng, điểm Regex đạt 1,0 và phân đoạn được định tuyến ngay.  
  > Khi phân đoạn có điểm ngữ nghĩa cao từ mô hình ngôn ngữ nhưng tín hiệu Regex thấp do diễn đạt gián tiếp, điểm Vector sẽ bù đắp để giữ lại phân đoạn. Cơ chế lấy cực đại bảo đảm ưu tiên bắt giữ tối đa quy phạm pháp luật, giảm thiểu nguy cơ bỏ sót căn cứ quan trọng."*

#### **Q15. Tại sao Chain Exact Match của hệ thống lại ghi nhận 0,0000 trên 18 câu hỏi dẫn chiếu ở Giai đoạn 3?**
* **Người trả lời:** Nguyễn Bình Minh
* **Câu trả lời chuẩn:**
  > *"Dạ thưa Thầy Cô, đây là một đóng góp thực nghiệm rất quan trọng của đề tài:  
  > Trên 18 câu hỏi dẫn chiếu phức tạp, dù UKG đã định vị thành công 58,67% căn cứ đích đơn lẻ (Reference-target Recall), nhưng để tái dựng chính xác 100% chuỗi đường dẫn có thứ tự từ Điều khởi đầu qua các Điều trung gian đến Điều kết luận thì hệ thống ghi nhận 0,0000 (với LightRAG là N/A vì chưa hỗ trợ trích xuất đường dẫn theo giao thức này).  
  > Kết quả chứng minh rằng việc tìm kiếm ngữ nghĩa đơn thuần không thể giải quyết trọn vẹn bài toán dẫn chiếu nhiều bước; hệ thống bắt buộc phải tích hợp giải thuật duyệt đồ thị có ràng buộc (Constrained Graph Traversal) trong giai đoạn tiếp theo."*

---

### **Nhóm D: Giới hạn kỹ thuật & Triển khai thực tiễn (Q16 – Q18)**

#### **Q16. Hệ thống xử lý thế nào khi một văn bản luật được sửa đổi, bổ sung hoặc hết hiệu lực?**
* **Người trả lời:** Nguyễn Bình Minh
* **Câu trả lời chuẩn:**
  > *"Dạ thưa Thầy Cô, trong phạm vi đề tài hiện tại, hệ thống tập trung kiểm chuẩn trên văn bản có hiệu lực cố định là Luật Đất đai 2024.  
  > Tuy nhiên, về mặt kiến trúc, đồ thị Hybrid UKG được thiết kế theo dạng node-edge có thuộc tính thời gian (temporal metadata) và trạng thái hiệu lực. Khi có luật sửa đổi, hệ thống chỉ cần cập nhật trạng thái của các node Điều cụ thể và thêm cạnh `amended_by` mà không cần tái cấu trúc toàn bộ đồ thị. Đây là một hướng phát triển trọng tâm của nhóm trong thời gian tới."*

#### **Q17. Module Validation xử lý thế nào đối với các lỗi định dạng văn bản đầu vào?**
* **Người trả lời:** Nguyễn Bình Minh
* **Câu trả lời chuẩn:**
  > *"Dạ thưa Thầy Cô, Module Validation của nhóm thực hiện kiểm tra các lỗi cấu trúc có thể nhận diện được như sai lệch schema, đứt gãy quan hệ phân cấp hoặc trùng lặp định danh node. Các trường hợp vi phạm nghiêm trọng sẽ được cách ly vào hàng đợi xử lý riêng và ghi log cảnh báo để bảo vệ tính toàn vẹn của đồ thị.  
  > Nhóm xin lưu ý: Hệ thống hiện tại được thực nghiệm trên tập dữ liệu văn bản đã chuẩn hóa hình thức; khả năng xử lý các văn bản có độ nhiễu cao do quét OCR chưa được thực nghiệm chuyên biệt trong khuôn khổ nghiên cứu này."*

#### **Q18. Khả năng mở rộng (Scalability) của hệ thống khi áp dụng cho toàn bộ hệ thống pháp luật Việt Nam ra sao?**
* **Người trả lời:** Nguyễn Bình Minh
* **Câu trả lời chuẩn:**
  > *"Dạ thưa Thầy Cô, kiến trúc đề xuất hoàn toàn có tính khả thi khi mở rộng quy mô lớn:  
  > Thứ nhất, bộ phân tích Parser v2 hoạt động dựa trên biểu thức quy chuẩn nên tốc độ xử lý rất nhanh, đạt hàng nghìn điều luật mỗi phút.  
  > Thứ hai, Module 5 sử dụng mô hình Qwen2.5-0.5B cực kỳ gọn nhẹ, có thể chạy suy luận song song trên hạ tầng GPU phổ thông với chi phí vận hành thấp hơn rất nhiều so với việc gọi API đồ thị thương mại.  
  > Nhóm đã kiểm chứng giải pháp trên 7 đạo luật với hơn 12.000 phân đoạn và hệ thống vận hành hoàn toàn ổn định."*

---
