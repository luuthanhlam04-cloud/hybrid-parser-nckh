# -*- coding: utf-8 -*-
import os

script_content = """# KỊCH BẢN THUYẾT TRÌNH BẢO VỆ ĐỀ TÀI NCKH
## ĐÁNH GIÁ VÀ TỐI ƯU HÓA CÁC KIẾN TRÚC RAG TRÊN NỀN TẢNG DỮ LIỆU CẤU TRÚC ĐẶC THÙ
**(Văn bản quy phạm pháp luật Việt Nam)**

---

* **Khung thời gian quy định:** Đúng 15 phút tổng thể.
  * **Phần 1 — Thuyết trình:** Đúng 10 phút (Thời lượng kịch bản: 09 phút 35 giây, đệm an toàn 25 giây).
  * **Phần 2 — Phản biện & Trả lời câu hỏi:** Đúng 05 phút (Sử dụng *Cẩm nang chuyên sâu 64 câu hỏi phản biện*).
* **Diễn giả:** Nhóm nghiên cứu gồm 03 sinh viên:
  * **Lưu Thanh Lâm** (Nhóm trưởng) — Trình bày Phần 1 (Slide 1–2) và Phần 3 (Slide 7–9).
  * **Ngô Thế Dương** — Trình bày Phần 2 (Slide 3–6).
  * **Nguyễn Bình Minh** — Trình bày Phần 4 (Slide 10–14).
* **Giáo viên hướng dẫn:** TS. Nguyễn Mạnh Dũng.
* **Đơn vị:** Đại học Bách khoa Hà Nội.

---

## BẢNG PHÂN BỔ THỜI LƯỢNG VÀ PHÂN VAI (3 DIỄN GIẢ)

| Khối nội dung | Diễn giả | Slide | Khung thời gian | Thời lượng | Trọng tâm nội dung |
|---|---|:---:|:---:|:---:|---|
| **Phần 1: Giới thiệu & Đặt vấn đề** | **Lưu Thanh Lâm** | Slide 1 – 2 | 00:00 – 00:55 | 55 giây | Giới thiệu đề tài; Bài toán thực tiễn từ ca Điều 34/46 (Luật Đất đai 2024). |
| **Phần 2: Cơ sở & Phương pháp** | **Ngô Thế Dương** | Slide 3 – 6 | 00:55 – 03:35 | 2 phút 40 giây | Đặc thù dữ liệu; Vì sao chọn 3 RAG; 4 câu hỏi nghiên cứu; Thiết kế 2 bộ Benchmark. |
| **Phần 3: Kết quả Benchmark A** | **Lưu Thanh Lâm** | Slide 7 – 9 | 03:35 – 06:00 | 2 phút 25 giây | Kết quả Giai đoạn 1 (Tier 1); Phương án Parser & MaxP; Kết quả Giai đoạn 2 (6 cấu hình). |
| **Phần 4: UKG, Kết quả & Kết luận** | **Nguyễn Bình Minh** | Slide 10 – 14 | 06:00 – 09:35 | 3 phút 35 giây | Workflow Hybrid Parser/UKG; Kết quả Benchmark B; Đối chiếu 4 RQ; Đóng góp & Hướng phát triển. |
| **Đệm chuyển slide & dự phòng** | **Cả 3 thành viên** | Toàn bài | 09:35 – 10:00 | 25 giây | Khoảng đệm an toàn điều phối nhịp độ trước tiếng chuông 10 phút. |
| **PHIÊN PHẢN BIỆN (Q&A)** | **Hội đồng & Nhóm** | Phụ lục | 10:00 – 15:00 | 05 phút | Đối thoại học thuật chuyên sâu (Sử dụng Cẩm nang 64 câu hỏi phản biện). |

---

## PHẦN 1 – LÂM: GIỚI THIỆU VÀ ĐẶT VẤN ĐỀ (SLIDE 1 – 2)

### [Slide 1] Giới thiệu đề tài
* **Người trình bày:** Lưu Thanh Lâm
* **Thời gian:** 00:00 – 00:15 (15 giây)
* **Visual Blueprint trên Slide:**
  * Tên đề tài: *Đánh giá và tối ưu hóa các kiến trúc RAG trên nền tảng dữ liệu cấu trúc đặc thù*.
  * Đối tượng nghiên cứu: Văn bản quy phạm pháp luật Việt Nam.
  * Giảng viên hướng dẫn: TS. Nguyễn Mạnh Dũng.
  * Sinh viên thực hiện: Lưu Thanh Lâm, Ngô Thế Dương, Nguyễn Bình Minh.
  * Đơn vị: Trường Công nghệ Thông tin & Truyền thông — Đại học Bách khoa Hà Nội.
* **Lời thoại trình bày:**
> *"Kính thưa quý thầy cô trong Hội đồng!  
> Chúng em là Lưu Thanh Lâm, Ngô Thế Dương và Nguyễn Bình Minh. Dưới sự hướng dẫn của thầy Nguyễn Mạnh Dũng, nhóm thực hiện đề tài “Đánh giá và tối ưu hóa các kiến trúc RAG trên nền tảng dữ liệu cấu trúc đặc thù”, với đối tượng nghiên cứu là văn bản pháp luật Việt Nam."*
* **Chỉ dẫn sân khấu & Tác phong:** Lâm đứng vị trí trung tâm, giữ tư thế thẳng, đĩnh đạc, mắt bao quát toàn bộ Hội đồng, chào mở đầu trang trọng và tự tin.

---

### [Slide 2] Bắt đầu từ một câu hỏi pháp lý
* **Người trình bày:** Lưu Thanh Lâm
* **Thời gian:** 00:15 – 00:55 (40 giây)
* **Visual Blueprint trên Slide:**
  * Sơ đồ ca pháp lý thực tiễn (Case B012):
    * Câu hỏi người dùng: *Tổ chức kinh tế thuê đất trả tiền hằng năm có được bán tài sản gắn liền với đất không, và cần đáp ứng điều kiện gì?*
    * Căn cứ thẩm quyền/quyền: Điểm c khoản 1 Điều 34 Luật Đất đai 2024 (*“Được bán tài sản... khi đáp ứng điều kiện quy định tại Điều 46”*).
    * Mũi tên dẫn chiếu sang: Điều 46 (Khoản 1 điều kiện chung, Khoản 2 điều kiện bồi thường/xây dựng).
  * Yêu cầu cốt lõi: Phải truy hồi đúng chuỗi dẫn chiếu, tổng hợp trọn vẹn điều kiện và định vị chính xác cấp Khoản – Điểm.
* **Lời thoại trình bày:**
> *"Chúng em xin bắt đầu bằng một ví dụ:  
> Tổ chức kinh tế thuê đất trả tiền hằng năm có được bán tài sản gắn liền với đất không, và cần đáp ứng điều kiện gì?  
> Để trả lời, hệ thống có thể tìm được quy định về quyền bán tài sản tại Điều 34 Luật Đất đai 2024. Tuy nhiên, quy định này còn dẫn chiếu đến Điều 46 về các điều kiện liên quan.  
> Nếu chỉ tìm được Điều 34, câu trả lời có thể chưa đầy đủ.  
> Vì vậy, hệ thống cần tiếp tục truy hồi các quy định được dẫn chiếu, tổng hợp điều kiện và viện dẫn đúng vị trí Điều–Khoản–Điểm.  
> Từ đó, nhóm tập trung nghiên cứu cách tổ chức dữ liệu, truy hồi và cung cấp căn cứ pháp lý cho RAG."*
* **Chỉ dẫn sân khấu & Chuyển giao:** Lâm chỉ tay về phía sơ đồ mũi tên nối Điều 34 sang Điều 46 trên màn chiếu để Hội đồng thấy rõ nút thắt của bài toán. Cuối câu, Lâm hướng tay về phía Dương và dõng dạc nói lời chuyển giao:
> *"Sau đây, bạn Dương sẽ giới thiệu cơ sở và phương pháp nghiên cứu của nhóm."*
* **Điểm tựa phản biện dự phòng:** Nếu Hội đồng hỏi sâu về ca này, nhóm sẽ giải thích chi tiết cơ chế phân tích case B012 theo Câu 20 trong Cẩm nang phản biện.

---

## PHẦN 2 – DƯƠNG: CƠ SỞ NGHIÊN CỨU VÀ THIẾT KẾ BENCHMARK (SLIDE 3 – 6)

### [Slide 3] Đặc thù văn bản pháp luật
* **Người trình bày:** Ngô Thế Dương
* **Thời gian:** 00:55 – 01:25 (30 giây)
* **Visual Blueprint trên Slide:**
  * Ba đặc thù cốt lõi của văn bản quy phạm pháp luật:
    1. **Cấu trúc phân cấp nghiêm ngặt:** Văn bản → Chương → Điều → Khoản → Điểm. (Nội dung pháp lý độc lập nằm ở cấp Khoản, Điểm; không phải toàn bộ Điều).
    2. **Mạng lưới dẫn chiếu chéo:** Quan hệ tham chiếu nội luật và liên luật phân tán khắp văn bản.
    3. **Khoảng cách từ vựng (Vocabulary Mismatch):** Ngôn ngữ tự nhiên của người hỏi khác xa văn phong hành chính pháp lý chuẩn mực.
  * Kết luận: Tìm văn bản tương tự là chưa đủ; hệ thống bắt buộc phải xác định đúng tọa độ, phạm vi áp dụng và các quy định kèm theo.
* **Lời thoại trình bày:**
> *"Kính thưa Hội đồng,  
> Văn bản pháp luật có ba đặc điểm ảnh hưởng đến quá trình truy hồi.  
> Thứ nhất là cấu trúc phân cấp Điều–Khoản–Điểm. Thứ hai là các quan hệ dẫn chiếu giữa những quy định. Thứ ba là sự khác biệt giữa cách người dùng đặt câu hỏi và ngôn ngữ chuyên môn của văn bản luật.  
> Do đó, tìm được một đoạn văn bản liên quan chưa đủ. Hệ thống còn cần xác định đúng vị trí, phạm vi áp dụng và các quy định có liên quan."*
* **Chỉ dẫn sân khấu:** Dương tiếp nhận lời dẫn một cách tự nhiên, phong thái chắc chắn, nói rõ từng ý với giọng điệu khúc chiết.

---

### [Slide 4] Vì sao chọn ba kiến trúc RAG?
* **Người trình bày:** Ngô Thế Dương
* **Thời gian:** 01:25 – 02:10 (45 giây)
* **Visual Blueprint trên Slide:**
  * Ba hướng tiếp cận cơ sở được khảo sát:
    * **Naive Vector RAG:** Đại diện cho truy hồi ngữ nghĩa thuần túy (Dense Retrieval bằng BGE-M3 / OpenAI text-embedding-3-small).
    * **Hybrid RAG:** Kết hợp từ khóa (BM25) + Ngữ nghĩa (Dense) + Tái xếp hạng (Cross-Encoder / bge-reranker-large).
    * **LightRAG:** Đại diện cho RAG đồ thị (Graph-based RAG), tự động trích xuất thực thể và quan hệ thông qua LLM.
  * Mục tiêu thiết kế: Khảo sát đối sánh ở cấp hệ thống (system-level comparison) để nhận diện ưu nhược điểm của các triết lý tổ chức dữ liệu khác nhau.
* **Lời thoại trình bày:**
> *"Ở giai đoạn đầu, nhóm lựa chọn ba kiến trúc đại diện cho ba hướng tiếp cận.  
> Naive Vector RAG sử dụng độ tương đồng ngữ nghĩa để tìm tài liệu liên quan.  
> Hybrid RAG kết hợp BM25, Dense Retrieval và Cross-Encoder, nhằm khảo sát hiệu quả của việc kết hợp nhiều tín hiệu truy hồi và tái xếp hạng.  
> LightRAG khai thác thực thể và quan hệ trong đồ thị để hỗ trợ truy hồi thông tin.  
> Việc lựa chọn ba kiến trúc này giúp nhóm so sánh hiệu năng giữa những cách tổ chức và truy hồi dữ liệu khác nhau.  
> Tuy nhiên, đây là đối sánh ở cấp hệ thống, chưa tách riêng mức đóng góp của từng thuật toán hay thành phần."*
* **Chỉ dẫn sân khấu:** Dương nhấn mạnh câu cuối cùng để thể hiện rõ tinh thần khoa học khách quan: nhóm nhận thức rõ giới hạn của thử nghiệm cấp hệ thống trước khi bước vào phân rã sâu.
* **Điểm tựa phản biện dự phòng:** Nếu Hội đồng hỏi lý do không chọn ColBERT hay GraphRAG gốc của Microsoft, Dương sử dụng Câu 04 trong Cẩm nang phản biện để trả lời.

---

### [Slide 5] Bốn câu hỏi nghiên cứu
* **Người trình bày:** Ngô Thế Dương
* **Thời gian:** 02:10 – 02:35 (25 giây)
* **Visual Blueprint trên Slide:**
  * Bốn câu hỏi nghiên cứu (RQ) tương ứng 3 giai đoạn:
    * **Giai đoạn 1 (RQ1):** Hiệu năng của các kiến trúc RAG cơ sở trên dữ liệu pháp lý ra sao?
    * **Giai đoạn 2 (RQ2):** Việc phân đoạn dữ liệu theo cấu trúc pháp lý (Parser, Validation, MaxP) tác động như thế nào đến truy hồi?
    * **Giai đoạn 3 (RQ3 & RQ4):** Kiến trúc đồ thị lai Hybrid Parser/UKG có cải thiện độ chính xác pháp lý và khả năng tái dựng chuỗi dẫn chiếu hay không?
* **Lời thoại trình bày:**
> *"Quá trình nghiên cứu được chia thành ba giai đoạn.  
> Giai đoạn một đánh giá ba kiến trúc RAG cơ sở, tương ứng RQ1.  
> Giai đoạn hai khảo sát phương án phân đoạn cấu trúc bằng Parser, Validation và MaxP, tương ứng RQ2.  
> Giai đoạn ba phát triển Hybrid Parser/UKG, đánh giá khả năng truy hồi, xử lý nội dung pháp lý và tái dựng chuỗi dẫn chiếu, tương ứng RQ3 và RQ4."*
* **Chỉ dẫn sân khấu:** Dương trình bày dứt khoát, chỉ tay lướt qua 3 giai đoạn để Hội đồng thấy được tính logic liền mạch trong cấu trúc luận văn.

---

### [Slide 6] Thiết kế và thực hiện Benchmark
* **Người trình bày:** Ngô Thế Dương
* **Thời gian:** 02:35 – 03:35 (1 phút 00 giây)
* **Visual Blueprint trên Slide:**
  * Bảng so sánh thiết kế 2 bộ Benchmark:
    * **Benchmark A:** 512 câu hỏi, 2.087 điều luật thuộc 7 văn bản luật. GĐ1 đánh giá trên tập Tier 1 (205 câu hỏi) do giới hạn lập chỉ mục của LightRAG (~500 điều); GĐ2 mở rộng đánh giá toàn bộ 512 câu trên 6 cấu hình.
    * **Benchmark B:** 50 câu hỏi chuyên sâu trên Chương III Luật Đất đai 2024; được chuyên gia pháp lý gắn nhãn chi tiết Ground-truth (Căn cứ, Điều kiện, Ngoại lệ, Chuỗi dẫn chiếu).
  * Khung đánh giá đa tầng:
    * *Tầng truy hồi:* Recall@5, MRR@5.
    * *Tầng câu trả lời:* Legal Correctness, Exception Coverage, Condition Coverage, Citation Recall và Chain Exact Match (kết hợp Rule-based và GPT-4o-mini).
* **Lời thoại trình bày:**
> *"Để kiểm chứng các phương án, nhóm xây dựng hai bộ benchmark và một khung đánh giá chung.  
> Benchmark A gồm 512 câu hỏi trên 2.087 điều luật thuộc bảy văn bản. Ở giai đoạn một, do LightRAG chỉ lập chỉ mục khoảng 500 điều luật, nhóm sử dụng tập Tier 1 gồm 205 câu có toàn bộ căn cứ nằm trong phạm vi này để đối sánh.  
> Sang giai đoạn hai, nhóm sử dụng toàn bộ 512 câu để đánh giá sáu cấu hình.  
> Benchmark B gồm 50 câu hỏi thuộc Chương III Luật Đất đai 2024, được gắn nhãn chi tiết về căn cứ, điều kiện, ngoại lệ và dẫn chiếu.  
> Quy trình đánh giá gồm ba bước: chuẩn bị câu hỏi và căn cứ tham chiếu, chạy các hệ thống để lưu kết quả, sau đó tính toán các chỉ số.  
> Ở tầng truy hồi, nhóm sử dụng Recall@5 và MRR@5. Ở tầng câu trả lời, nhóm sử dụng các tiêu chí về chất lượng nội dung, trích dẫn và quan hệ dẫn chiếu, trong đó có đánh giá bằng GPT-4o-mini."*
* **Chỉ dẫn sân khấu & Chuyển giao:** Dương kết thúc phần phương pháp, hướng người về phía Lâm và nói lời chuyển giao nhịp nhàng:
> *"Tiếp theo, bạn Lâm sẽ trình bày kết quả hai giai đoạn thực nghiệm đầu tiên."*

---

## PHẦN 3 – LÂM: KẾT QUẢ BENCHMARK A (SLIDE 7 – 9)

### [Slide 7] Giai đoạn 1 – Kết quả ba kiến trúc RAG
* **Người trình bày:** Lưu Thanh Lâm
* **Thời gian:** 03:35 – 04:25 (50 giây)
* **Visual Blueprint trên Slide:**
  * Bảng kết quả thực nghiệm Giai đoạn 1 trên Benchmark A Tier 1 (205 câu hỏi):
    * Naive Vector RAG: Recall@5 = `0,9561` | MRR@5 = `0,8870`
    * Hybrid RAG: Recall@5 = `0,9659` | MRR@5 = `0,9243`
    * LightRAG: Recall@5 = `0,9659` | MRR@5 = `0,8655`
  * Nhận xét chính: Cả 3 hệ thống đều đạt Recall@5 cao trên 0,95. Tuy nhiên Hybrid RAG vượt trội ở MRR@5 (`0,9243`), đưa tài liệu đúng lên thứ hạng đầu tốt nhất.
* **Lời thoại trình bày:**
> *"Trên tập Tier 1 gồm 205 câu hỏi, cả ba hệ thống đều đạt Recall@5 trên 0,95.  
> Cụ thể, Naive Vector đạt 0,9561, còn Hybrid RAG và LightRAG cùng đạt 0,9659.  
> Tuy nhiên, ở chỉ số MRR@5, Hybrid RAG đạt 0,9243, cao hơn hai hệ thống còn lại.  
> Điều này cho thấy Hybrid RAG có khả năng đưa căn cứ liên quan lên vị trí ưu tiên cao hơn trong tập kiểm thử.  
> Tuy vậy, kết quả truy hồi tốt chưa bảo đảm hệ thống viện dẫn đúng Khoản–Điểm hoặc cung cấp đầy đủ các điều kiện.  
> Từ đó, nhóm tiếp tục khảo sát ảnh hưởng của việc phân đoạn dữ liệu theo cấu trúc pháp lý."*
* **Chỉ dẫn sân khấu:** Lâm chỉ rõ vào con số MRR@5 `0,9243` của Hybrid RAG, làm nổi bật khoảng cách với Naive Vector (`0,8870`) và LightRAG (`0,8655`).
* **Điểm tựa phản biện dự phòng:** Nếu Hội đồng hỏi tại sao Naive Vector cũng đạt Recall cao thế, xem Câu 14 trong Cẩm nang phản biện (do tập Tier 1 và câu hỏi pháp lý rõ ràng).

---

### [Slide 8] Giai đoạn 2 – Parser và Article-level MaxP
* **Người trình bày:** Lưu Thanh Lâm
* **Thời gian:** 04:25 – 05:10 (45 giây)
* **Visual Blueprint trên Slide:**
  * Giải pháp xử lý dữ liệu cấu trúc pháp lý:
    * **Parser & Validation:** Phân rã 2.087 Điều luật thành 12.754 phân đoạn ngữ pháp chuẩn hóa (chủ yếu ở cấp Khoản và Điểm).
    * **Bổ sung Parent Context:** Mỗi phân đoạn mang theo metadata tiêu đề Luật, Chương, Tên Điều để không mất ngữ cảnh gốc.
    * **Article-level MaxP (Cơ chế gom điểm tối đa):** Gom các phân đoạn thuộc cùng một Điều luật, lấy điểm cao nhất đại diện cho Điều đó. Ngăn chặn hiện tượng một Điều chiếm trọn cả Top-5 kết quả.
* **Lời thoại trình bày:**
> *"Ở giai đoạn hai, nhóm triển khai Parser và Validation để tách 2.087 điều luật thành 12.754 phân đoạn, chủ yếu ở cấp Khoản và Điểm.  
> Mỗi phân đoạn được bổ sung thông tin cấp cha để giữ được vị trí trong văn bản gốc.  
> Tuy nhiên, khi tách nhỏ, nhiều kết quả Top-5 có thể thuộc cùng một Điều luật.  
> Vì vậy, nhóm sử dụng Article-level MaxP, lấy điểm cao nhất của các phân đoạn thuộc cùng một Điều để đại diện cho Điều đó.  
> Cách này giúp hệ thống xếp hạng ở cấp Điều nhưng vẫn giữ được phân đoạn chi tiết làm căn cứ."*
* **Chỉ dẫn sân khấu:** Lâm dùng tay minh họa việc gom các nhánh Khoản/Điểm về một gốc Điều duy nhất, giúp Hội đồng hình dung cơ chế MaxP tức thì.
* **Điểm tựa phản biện dự phòng:** Xem Câu 18 và Câu 19 trong Cẩm nang phản biện.

---

### [Slide 9] Giai đoạn 2 – Kết quả sáu cấu hình
* **Người trình bày:** Lưu Thanh Lâm
* **Thời gian:** 05:10 – 06:00 (50 giây)
* **Visual Blueprint trên Slide:**
  * Bảng so sánh 6 cấu hình trên toàn bộ 512 câu Benchmark A:
    * C1 (BM25 Full Điều) vs C4 (BM25 Chunk + MaxP): Recall giảm nhẹ (`0,8945` → `0,8418`).
    * C2 (Dense Full Điều) vs C5 (Dense Chunk + Parent Context + MaxP):
      * Recall@5 tăng từ `0,9141` lên `0,9316` (+1,75%).
      * MRR@5 tăng mạnh từ `0,8129` lên `0,8602` (+4,73%).
      * Tiết kiệm ngữ cảnh LLM: Giảm `79,9%` độ dài token đầu vào (từ 1.250 từ xuống 252 từ).
      * LLM-Judge Citation Accuracy: Đạt `0,9902` trên ngữ cảnh được cung cấp.
* **Lời thoại trình bày:**
> *"Để kiểm chứng phương án trên, nhóm khảo sát sáu cấu hình gồm hai cách tổ chức dữ liệu và ba phương thức truy hồi: BM25, Dense và Hybrid.  
> Đáng chú ý, khi chuyển từ C2 sang C5, Recall@5 tăng từ 0,9141 lên 0,9316, còn MRR@5 tăng từ 0,8129 lên 0,8602.  
> C5 cũng đạt điểm LLM-Judge Citation Accuracy trung bình 0,9902, đồng thời giảm gần 79,9% độ dài ngữ cảnh.  
> Đây là điểm đánh giá tự động theo giao thức thực nghiệm, chưa phải tỷ lệ câu trả lời được xác nhận chính xác tuyệt đối.  
> Kết quả cho thấy phương án Parser kết hợp ngữ cảnh cấp cha và MaxP mang lại những cải thiện nhất định.  
> Tuy nhiên, phương án này chủ yếu xử lý việc tìm từng đơn vị văn bản. Để khai thác quan hệ giữa các quy định, nhóm tiếp tục xây dựng Hybrid Parser/UKG."*
* **Chỉ dẫn sân khấu & Chuyển giao:** Lâm chỉ vào hàng C5, nhấn mạnh sự cân bằng giữa độ chính xác truy hồi và chi phí ngữ cảnh. Sau đó, Lâm hướng về Minh và chuyển giao:
> *"Sau đây, bạn Minh sẽ trình bày kiến trúc đề xuất và kết quả Benchmark B."*
* **Điểm tựa phản biện dự phòng:** Nếu Hội đồng hỏi vì sao BM25 lại tụt từ C1 sang C4, xem Câu 21. Nếu hỏi con số 0,9902 có phải độ chính xác câu trả lời cuối cùng không, xem Câu 22 trong Cẩm nang phản biện.

---

## PHẦN 4 – MINH: HYBRID PARSER/UKG, BENCHMARK B VÀ KẾT LUẬN (SLIDE 10 – 14)

### [Slide 10] Kiến trúc Hybrid Parser/UKG – Workflow
* **Người trình bày:** Nguyễn Bình Minh
* **Thời gian:** 06:00 – 06:50 (50 giây)
* **Visual Blueprint trên Slide:**
  * Sơ đồ luồng 10 Module của hệ thống Hybrid Parser/UKG chia thành 5 nhóm chức năng:
    1. *Phân tích cấu trúc vật lý:* M1 (Preprocess) → M2 (Parser) → M3 (Validation) → M4 (Physical Graph: Điều–Khoản–Điểm trên Neo4j).
    2. *Định tuyến & Xử lý ngữ nghĩa:* M5 (Semantic Router) → M6 (LLM Semantic Extraction: trích xuất quyền, nghĩa vụ, điều kiện, dẫn chiếu).
    3. *Hợp nhất đồ thị tri thức:* M7 (Entity Resolution) → M8 (UKG Fusion: liên kết thực thể ngữ nghĩa với nút vật lý).
    4. *Lưu trữ cơ sở tri thức:* M9 (Graph Database Neo4j).
    5. *Truy vấn & Trả lời:* M10 (Hybrid Retrieval, Citation Reasoning & LLM Synthesis).
* **Lời thoại trình bày:**
> *"Kính thưa Hội đồng,  
> Hybrid Parser/UKG gồm mười module, được chia thành năm nhóm xử lý như trên sơ đồ.  
> Đầu tiên, M1 đến M4 thực hiện tiền xử lý, phân tích cấu trúc và xây dựng Physical Graph để lưu giữ các đơn vị Điều–Khoản–Điểm.  
> Tiếp theo, M5 và M6 định tuyến các phân đoạn cần xử lý và sử dụng LLM để trích xuất thông tin ngữ nghĩa.  
> M7 và M8 chuẩn hóa, hợp nhất dữ liệu vật lý với dữ liệu ngữ nghĩa thành Unified Knowledge Graph.  
> M9 lưu trữ đồ thị trên Neo4j.  
> Cuối cùng, M10 thực hiện truy hồi, mở rộng căn cứ liên quan, lựa chọn ngữ cảnh và sinh câu trả lời có trích dẫn nguồn.  
> Điểm chính của kiến trúc là kết hợp thông tin cấu trúc và ngữ nghĩa, đồng thời giữ liên kết với văn bản pháp lý gốc."*
* **Chỉ dẫn sân khấu:** Minh trình bày với giọng tự tin, chỉ tay theo đúng luồng từ M1 sang M10 trên slide để người nghe nắm bắt mạch lạc kiến trúc kỹ thuật.
* **Điểm tựa phản biện dự phòng:** Xem Câu 25 – 30 trong Cẩm nang phản biện nếu Hội đồng hỏi sâu vào router M5 hoặc cách hợp nhất M7/M8.

---

### [Slide 11] Benchmark B – Kết quả và giới hạn
* **Người trình bày:** Nguyễn Bình Minh
* **Thời gian:** 06:50 – 08:20 (1 phút 30 giây)
* **Visual Blueprint trên Slide:**
  * Bảng so sánh toàn diện giữa Hybrid Parser/UKG và LightRAG trên Benchmark B:
    * **Tầng truy hồi (47 câu đủ căn cứ):**
      * Recall@5: Hybrid Parser/UKG đạt `0,9184` vs LightRAG `0,7358` (+18,26%).
      * MRR@5: Hybrid Parser/UKG đạt `0,8848` vs LightRAG `0,5539` (+33,09%).
    * **Tầng chất lượng câu trả lời:**
      * Legal Correctness: `0,8777` vs `0,8160`.
      * Exception Coverage: `0,6786` vs `0,5357`.
      * Citation Recall cấp Khoản: `0,8170` vs `0,0435` (vượt trội hoàn toàn).
      * Condition Coverage: `0,7066` vs `0,8421` (Thấp hơn LightRAG — Hạn chế được ghi nhận).
      * Exact Locator Recall@5: LightRAG điểm số hiển thị cao hơn, nhưng đơn vị truy hồi (Entity vs Chunk) khác nhau nên không kết luận định vị tốt hơn.
    * **Tầng chuỗi dẫn chiếu (18 câu có nhãn dẫn chiếu):**
      * Reference-target Recall: `0,5867`.
      * Chain Exact Match: `0/18` (`0,0000`).
* **Lời thoại trình bày:**
> *"Để đánh giá kiến trúc đề xuất, nhóm sử dụng Benchmark B và đối sánh Hybrid Parser/UKG với LightRAG.  
> Kết quả được chia thành ba tầng.  
> Thứ nhất, về truy hồi: Trên 47 câu hỏi đủ căn cứ, Hybrid Parser/UKG đạt Recall@5 bằng 0,9184, cao hơn LightRAG ở mức 0,7358. MRR@5 cũng cao hơn, lần lượt là 0,8848 và 0,5539.  
> Thứ hai, về chất lượng câu trả lời: Hybrid Parser/UKG đạt Legal Correctness bằng 0,8777 và Exception Coverage bằng 0,6786, đều cao hơn LightRAG.  
> Citation Recall cấp Khoản cũng đạt 0,8170, so với 0,0435 của LightRAG.  
> Tuy nhiên, Condition Coverage của Hybrid Parser/UKG chỉ đạt 0,7066, thấp hơn LightRAG ở mức 0,8421. Điều này cho thấy hệ thống vẫn còn hạn chế trong việc tổng hợp đầy đủ các điều kiện pháp lý.  
> Ở phép đo Exact Locator Recall@5, LightRAG có điểm cao hơn, nhưng hai hệ thống có đơn vị truy hồi và số mẫu hợp lệ khác nhau, nên nhóm chưa đưa ra kết luận bên nào định vị chính xác hơn từ chỉ số này.  
> Thứ ba, về dẫn chiếu: Trên 18 câu có nhãn chuỗi, Reference-target Recall đạt 0,5867, nhưng Chain Exact Match bằng 0/18.  
> Như vậy, hệ thống có kết quả tích cực ở truy hồi và một số tiêu chí câu trả lời, nhưng chưa giải quyết đầy đủ bài toán tổng hợp điều kiện và tái dựng chuỗi dẫn chiếu."*
* **Chỉ dẫn sân khấu:** Minh nhấn mạnh tính trung thực học thuật: không giấu giếm con số `0,7066` và `0/18`, thể hiện sự hiểu biết sâu sắc về dữ liệu và thuật toán.
* **Điểm tựa phản biện dự phòng:** Nếu Hội đồng xoáy vào lý do Condition Coverage thấp hơn, xem Câu 31; nếu hỏi về Chain Exact Match bằng 0, xem Câu 35; nếu hỏi ca B012, xem Câu 20 trong Cẩm nang phản biện.

---

### [Slide 12] Đối chiếu bốn câu hỏi nghiên cứu
* **Người trình bày:** Nguyễn Bình Minh
* **Thời gian:** 08:20 – 08:50 (30 giây)
* **Visual Blueprint trên Slide:**
  * Bảng tổng kết câu trả lời cho 4 RQ:
    * **RQ1 (Kiến trúc cơ sở):** Hybrid RAG vượt trội về thứ hạng truy hồi (MRR@5 = 0,9243), nhưng Naive Vector và LightRAG thiếu cơ chế định vị trích dẫn sâu cấp Khoản/Điểm.
    * **RQ2 (Phân đoạn cấu trúc & MaxP):** Parser kết hợp Parent Context và MaxP cải thiện rõ rệt ở cấu hình Dense (C5 Recall `0,9316`, MRR `0,8602`, giảm 79,9% context length).
    * **RQ3 (Khả năng Hybrid Parser/UKG):** Nâng cao vượt bậc độ chính xác pháp lý (`0,8777`), ngoại lệ (`0,6786`) và trích dẫn cấp Khoản (`0,8170`), nhưng cần hoàn thiện thêm về tổng hợp điều kiện.
    * **RQ4 (Tái dựng dẫn chiếu):** Thu hồi được 58,67% căn cứ đích, nhưng chưa giải quyết được chuỗi suy luận hoàn chỉnh (`0/18`).
* **Lời thoại trình bày:**
> *"Từ ba giai đoạn, nhóm rút ra các kết quả chính.  
> Với RQ1, Hybrid RAG cải thiện thứ hạng truy hồi nhưng chất lượng trích dẫn vẫn còn hạn chế.  
> Với RQ2, phương án Parser, Validation và MaxP mang lại kết quả tích cực ở cấu hình Dense.  
> Với RQ3, Hybrid Parser/UKG cải thiện một số chỉ số, nhưng chưa vượt LightRAG ở tất cả tiêu chí.  
> Còn với RQ4, hệ thống tìm được một phần căn cứ đích, nhưng chưa tái dựng được chuỗi dẫn chiếu hoàn chỉnh."*
* **Chỉ dẫn sân khấu:** Minh tóm tắt cô đọng, dứt khoát, đi thẳng vào trọng tâm kết luận của từng câu hỏi nghiên cứu.

---

### [Slide 13] Đóng góp chính của đề tài
* **Người trình bày:** Nguyễn Bình Minh
* **Thời gian:** 08:50 – 09:15 (25 giây)
* **Visual Blueprint trên Slide:**
  * Ba đóng góp khoa học chính:
    1. **Thiết kế Benchmark thực nghiệm:** Xây dựng Benchmark A (512 câu) và Benchmark B (50 câu gắn nhãn sâu) cùng quy trình đánh giá chuẩn hóa cho RAG pháp luật Việt Nam.
    2. **Phương pháp phân đoạn cấu trúc:** Đề xuất và kiểm chứng quy trình Parser, Validation kết hợp Article-level MaxP cho dữ liệu văn bản phân cấp.
    3. **Kiến trúc tích hợp Hybrid Parser/UKG:** Thiết kế và kiểm chứng hệ thống kết hợp đồ thị cấu trúc vật lý với đồ thị ngữ nghĩa, bảo toàn nguồn gốc văn bản gốc.
  * Tinh thần khoa học: Kế thừa thuật toán nền tảng, tập trung vào đóng góp thiết kế kiến trúc, tích hợp hệ thống và kiểm chứng thực nghiệm nghiêm ngặt.
* **Lời thoại trình bày:**
> *"Nhóm tổng hợp ba đóng góp chính.  
> Thứ nhất, xây dựng và tổ chức Benchmark A, Benchmark B cùng khung đánh giá để đối sánh các hệ thống RAG.  
> Thứ hai, triển khai và khảo sát phương án phân đoạn cấu trúc bằng Parser, Validation và MaxP.  
> Thứ ba, thiết kế và tích hợp kiến trúc Hybrid Parser/UKG, kết hợp đồ thị cấu trúc với dữ liệu ngữ nghĩa.  
> Các thuật toán nền tảng được nhóm kế thừa; đóng góp tập trung vào thiết kế, tích hợp và kiểm chứng thực nghiệm."*
* **Chỉ dẫn sân khấu:** Minh nói với giọng điệu trang trọng, nhấn mạnh giá trị đóng góp thực chất của nhóm sinh viên.

---

### [Slide 14] Hướng phát triển và kết thúc
* **Người trình bày:** Nguyễn Bình Minh (Cùng Lâm & Dương kết thúc)
* **Thời gian:** 09:15 – 09:35 (20 giây)
* **Visual Blueprint trên Slide:**
  * Ba hướng nghiên cứu tiếp theo:
    1. Mở rộng kiểm thử độc lập trên toàn bộ các bộ luật lớn (Luật Doanh nghiệp, Bộ luật Dân sự).
    2. Nghiên cứu cơ chế quản lý hiệu lực văn bản theo trục thời gian (Temporal Legal KG).
    3. Tối ưu hóa chuỗi suy luận đa bước để giải quyết trọn vẹn bài toán tái dựng dẫn chiếu (Multi-hop Reasoning).
  * Lời cảm ơn Hội đồng và Thầy hướng dẫn TS. Nguyễn Mạnh Dũng.
* **Lời thoại trình bày:**
> *"Trong thời gian tới, nhóm định hướng mở rộng đánh giá trên dữ liệu độc lập, nghiên cứu quản lý hiệu lực văn bản và cải thiện khả năng tổng hợp điều kiện, tái dựng dẫn chiếu nhiều bước.  
> Nhóm nhận thấy truy hồi đúng căn cứ là cần thiết, nhưng chưa đủ để bảo đảm câu trả lời pháp lý đầy đủ và chính xác.  
> Chúng em xin trân trọng cảm ơn các thầy trong Hội đồng đã lắng nghe!"*
* **Chỉ dẫn sân khấu & Chuyển sang Phiên phản biện:** 
  * Đúng giây thứ 09:35, Minh dứt lời.
  * Cả 3 thành viên Lưu Thanh Lâm, Ngô Thế Dương, Nguyễn Bình Minh cùng đứng nghiêm trang, cúi đầu chào Hội đồng.
  * Nhóm chuyển sang tư thế sẵn sàng: Lâm cầm micro mở đầu phần tiếp thu, Dương và Minh mở sẵn tài liệu *Cẩm nang chuyên sâu 64 câu hỏi chuẩn bị phản biện* để bước vào 5 phút phản biện của Hội đồng.
"""

output_path = r"c:\Users\luuth\NCKH\Benchmark\docs\kich_ban_thuyet_trinh_15p.md"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(script_content.strip() + "\n")

print(f"[+] Successfully written updated presentation script to: {output_path}")
print(f"[+] File size: {len(script_content)} characters")
