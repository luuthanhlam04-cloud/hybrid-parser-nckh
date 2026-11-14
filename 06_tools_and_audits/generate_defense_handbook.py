# -*- coding: utf-8 -*-
"""
generate_defense_handbook.py
Tạo tài liệu Cẩm nang chuyên sâu chuẩn bị phản biện bảo vệ NCKH:
- Phần 1: Tổng hợp kiến thức đúc kết chuyên sâu phục vụ phản biện.
- Phần 2: Nhóm câu hỏi phản biện giả định và kịch bản trả lời mẫu.
"""

import os
import re

md_path = r"c:\Users\luuth\NCKH\Benchmark\docs\cam_nang_chuyen_sau_chuan_bi_phan_bien.md"

content = r"""# CẨM NANG CHUYÊN SÂU CHUẨN BỊ PHẢN BIỆN BẢO VỆ NCKH
**ĐỀ TÀI:** ĐÁNH GIÁ VÀ TỐI ƯU HÓA CÁC KIẾN TRÚC RAG TRÊN NỀN TẢNG DỮ LIỆU CẤU TRÚC ĐẶC THÙ  
**HỘI ĐỒNG BẢO VỆ ĐỀ TÀI NGHIÊN CỨU KHOA HỌC SINH VIÊN**  
**NHÓM TÁC GIẢ:** LƯU THANH LÂM – NGÔ THẾ DƯƠNG – NGUYỄN BÌNH MINH  
**GIẢNG VIÊN HƯỚNG DẪN:** TS. NGUYỄN MẠNH DŨNG  

---

> **MỤC ĐÍCH TÀI LIỆU:**  
> Tài liệu này được đúc kết từ toàn bộ quá trình tranh luận, kiểm toán thực nghiệm và phản biện đa chiều giữa các mô hình AI độc lập (Antigravity, GPT, DeepSeek) đối chiếu với chân lý thực nghiệm trong báo cáo toàn văn `bancuoi.docx`.  
> Tài liệu gồm hai phần:  
> 1. **Phần 1: Tổng hợp kiến thức đúc kết chuyên sâu phục vụ phản biện** — trang bị bản chất lý luận, cơ chế đằng sau từng con số, ranh giới kỹ thuật và triết lý bảo vệ vững chắc.  
> 2. **Phần 2: Hệ thống câu hỏi giả định và kịch bản đối thoại phản biện đỉnh cao** — mô phỏng các đòn vặn hiểm hóc nhất từ 5 góc nhìn của Hội đồng khoa học và hướng dẫn cách trả lời theo công thức 3 bước.

---

# PHẦN 1: TỔNG HỢP KIẾN THỨC ĐÚC KẾT CHUYÊN SÂU PHỤC VỤ PHẢN BIỆN

## I. TRIẾT LÝ PHÒNG THỦ KHOA HỌC: "MINH BẠCH THEO TRỌNG TÂM"

### 1. Tại sao giấu số liệu là "tử huyệt" trước Hội đồng chuyên môn?
* **Bản chất của Hội đồng bảo vệ:** Các Thầy/Cô phản biện là những chuyên gia đầu ngành. Họ không chấm điểm xem hệ thống của bạn có "toàn năng 100%" hay không, mà chấm **phương pháp luận nghiên cứu (Methodology)**, **độ tin cậy của bằng chứng (Evidence Reliability)** và **tính liêm chính học thuật (Scientific Integrity)**.
* **Sai lầm chết người:** Nếu nhóm giấu các chỉ số UKG thua (như *Exact Locator Recall@5* hay *Condition Coverage*) khỏi slide mà trong báo cáo lại có in ra, bất kỳ Thầy nào lật đúng trang Bảng 3.11 hay Bảng 3.15 sẽ lập tức đặt câu hỏi: *"Tại sao số này trong báo cáo nhóm lại cắt khỏi slide?"*. Lúc này, câu hỏi chuyển từ tranh luận kỹ thuật sang **nghi vấn về liêm chính dữ liệu**. Khi đã mất uy tín về sự trung thực, mọi con số thắng lợi khác của nhóm đều bị nghi ngờ là thiên vị (cherry-picking).
* **Chiến lược tối ưu: "Visual Inclusion, Spoken Reframing" (Đưa lên mắt thấy, dùng lời định khung):**
  - Đưa trung thực kết quả bất lợi lên slide (kèm footnote chú thích điều kiện thực nghiệm).
  - Không đọc lướt sợ hãi, mà chủ động trình bày dưới lăng kính **sự đánh đổi kỹ thuật (Engineering Trade-off)**. Biến điểm yếu bề mặt thành minh chứng cho thấy nhóm hiểu sâu sắc bản chất hệ thống.

### 2. Ba cấp bậc thông tin trong phản biện (Relevance-based Transparency)
* **Cấp 1 – Kết quả trọng tâm (Core Contributions):** Phải nêu rõ số liệu, đối tượng đánh giá, trả lời trực tiếp cho 4 câu hỏi nghiên cứu (RQ1 – RQ4).
* **Cấp 2 – Hạn chế có ảnh hưởng đến kết luận (Controlled Boundaries):** Trình bày có kiểm soát, đi kèm cơ chế kỹ thuật giải thích nguyên nhân, không để tạo ấn tượng hệ thống đã hoàn hảo tuyệt đối.
* **Cấp 3 – Chi tiết kỹ thuật nội bộ (Internal Nuances):** Dành cho phần Q&A khi Thầy/Cô hỏi sâu vào chi tiết (như phân tích ablation Causal Attention, lỗi schema, ngưỡng động $\theta$,...).

### 3. Phong thái "Precise Confidence" (Tự tin chính xác)
* Không dùng từ ngữ cảm xúc, kịch tính hóa (*"sụp đổ", "chấn động", "vượt trội tuyệt đối"*).
* Luôn phân biệt rạch ròi giữa **kết quả thực nghiệm quan sát được (Observed Result)** và **giả thuyết cơ chế giải thích (Hypothesized Mechanism)**. Không tùy tiện tuyên bố "nguyên nhân nhân quả" nếu chưa thực hiện thí nghiệm cô lập (Ablation).

---

## II. GIẢI MÃ BẢN CHẤT CÁC THƯỚC ĐO & RANH GIỚI THỰC NGHIỆM TỪNG GIAI ĐOẠN

```
                ┌──────────────────────────────────────────────────────────┐
                │          3 GIAI ĐOẠN THỰC NGHIỆM TRONG BÁO CÁO           │
                └──────────────────────────────────────────────────────────┘
                                             │
         ┌───────────────────────────────────┼──────────────────────────────────┐
         ▼                                   ▼                                  ▼
┌──────────────────┐               ┌──────────────────┐               ┌──────────────────┐
│   GIAI ĐOẠN 1    │               │   GIAI ĐOẠN 2    │               │   GIAI ĐOẠN 3    │
│  Baseline RAGs   │               │ Parser v2 + MaxP │               │    Hybrid UKG    │
│ (Tier 1, N=205)  │               │ (Bench A, N=512) │               │ (Bench B, N=50)  │
└──────────────────┘               └──────────────────┘               └──────────────────┘
  Context Prec > 0.96                C5 Citation = 0.9902               Recall@5 = 0.9184
  Citation Acc: 13% - 33%            Token: -79.9% (580 tok)            Prec Khoản = 0.7757
  (Nghịch lý tìm kiếm/trích dẫn)     α=0.8 (Cân bằng thực tiễn)         Exact Locator: Trade-off
```

### 1. Giai đoạn 1: Nghịch lý Tìm kiếm – Trích dẫn (Tier 1 Fair Subset, $N=205$)
* **Bối cảnh thiết kế Tier 1:** LightRAG đòi hỏi trích xuất thực thể bằng LLM nên chi phí API rất lớn, chỉ index trên **500 điều luật**. Nhóm xây dựng Tier 1 gồm 205 câu hỏi mà 100% căn cứ pháp lý nằm trong 500 điều này. Đây là thiết kế **Equal Scope Evaluation** chuẩn mực, không phải thiên vị.
* **Số liệu Bảng 3.3 & 3.4:**
  - *Recall@5:* Naive Vector: **0,9561** | Hybrid RAG: **0,9659** | LightRAG: **0,9659**.
  - *Context Precision:* Naive Vector: **0,9659** | Hybrid RAG: **0,9660** | LightRAG: **0,8829**.
  - *Citation Accuracy:* Naive Vector: **0,3259** | Hybrid RAG: **0,2902** | LightRAG: **0,1371**.
* **Bản chất khoa học:** 
  - Tại sao Context Precision rất cao (>0,96) mà Citation Accuracy lại sụt sâu (13% – 33%)?
  - Vì Context Precision chỉ đo việc Điều luật có xuất hiện trong Top-5 hay không. Do nạp cả khối Điều thô dài (~2.898 tokens), vector dense dễ dàng khớp với ngữ nghĩa tổng quát của câu hỏi.
  - Nhưng khi mô hình ngôn ngữ (GPT-4o-mini) đọc một khối văn bản thô dài thiếu cấu trúc phân cấp, nó gặp hiện tượng **pha loãng ngữ cảnh (Context Dilution)**: không thể xác định được căn cứ vi mô nằm ở Khoản nào, Điểm nào, dẫn đến ảo giác trích dẫn.
  - Riêng LightRAG chia chunk cố định 1.200 token, cắt ngang các ranh giới điều luật, làm mất hoàn toàn locator gốc nên Citation Accuracy thấp nhất (13,71%).

### 2. Giai đoạn 2: Tối ưu hóa cấu trúc (Benchmark A, $N=512$, 3.072 lượt LLM-Judge)
* **Bản chất của chỉ số C5 Citation Accuracy = 0,9902:**
  - Đây là **LLM-Judge Citation Accuracy trên ngữ cảnh truy hồi (In-context Citation Accuracy)**, KHÔNG PHẢI độ chính xác trích dẫn trên câu trả lời sinh ra hoàn chỉnh.
  - 504/512 câu hỏi được giám khảo AI chấm điểm tuyệt đối 1,0 về việc ngữ cảnh nạp vào có chứa đầy đủ và chính xác căn cứ cần viện dẫn.
  - Việc đánh giá này nhằm kiểm định độc lập hiệu năng của bộ truy hồi cấu trúc (Retriever) mà không bị nhiễu bởi năng lực diễn đạt của bộ tạo sinh (Generator).
* **Hiệu quả nén token:** Parser v2 + Article MaxP giúp giảm **79,9% dung lượng ngữ cảnh** (từ 2.891 token ở C2 xuống chỉ còn 580 token ở C5), giải quyết triệt để bài toán bùng nổ chi phí và pha loãng thông tin.
* **Bản chất của khảo sát trọng số RRF ($\alpha$ tại Bảng 3.7):**
  - Khi quét 11 giá trị $\alpha$ từ 0,0 đến 1,0:
    * $\alpha = 0,0$ (BM25 thuần): Recall 0,7402, MRR 0,6052.
    * $\alpha = 1,0$ (Dense thuần): Recall **0,9316**, MRR **0,8602** (ĐẠT ĐIỂM CAO NHẤT).
    * $\alpha = 0,8$: Recall **0,9297**, MRR **0,8220**.
  - **Tại sao nhóm không chọn $\alpha=1,0$ mà lại chọn $\alpha=0,8$?**
  - Trả lời phản biện: $\alpha=1,0$ đạt điểm cao nhất trên Benchmark A vì bộ câu hỏi đã được diễn đạt lại (Jaccard giảm từ 0,68 xuống 0,31), khiến Dense vượt trội. Tuy nhiên, trong thực tiễn tra cứu pháp luật, người dùng thường nhập các thuật ngữ định danh cứng (tên tội danh, số hiệu, mức phạt,...). Cấu hình $\alpha=0,8$ là **điểm cân bằng thực tiễn (Engineering Robustness)**: hy sinh chưa đầy 0,2% Recall của Dense để giữ lại 20% trọng số BM25 làm chốt chặn an toàn khi gặp từ khóa định danh.

### 3. Giai đoạn 3: Đối đầu trực diện Hybrid UKG vs LightRAG (Benchmark B, $N=50$)
* **Cơ cấu 50 câu hỏi Benchmark B (Bảng 2.6):**
  - Quyền và nghĩa vụ trực tiếp: 8 câu.
  - Nhiều điều kiện: 10 câu.
  - Ngoại lệ và điều cấm: 7 câu.
  - Dẫn chiếu một bước: 6 câu.
  - Dẫn chiếu nhiều bước: 4 câu.
  - Phân biệt chủ thể: 5 câu.
  - Tổng hợp cha-con: 4 câu.
  - Tình huống pháp lý: 3 câu.
  - Không đủ căn cứ trong corpus: 3 câu.
  - *(Ghi nhớ: 47 câu đơn tầng + 3 câu đa tầng; 7 câu ngoại lệ; 10 câu dẫn chiếu).*
* **Các chỉ số UKG vượt trội:**
  - *Recall@5 cấp Điều:* 0,9184 vs 0,7358 (**+18,26 đpt**).
  - *MRR@5 cấp Điều:* 0,8848 vs 0,5539 (**+33,09 đpt**).
  - *Citation Precision Điều:* 0,8369 vs 0,3333 (**+50,36 đpt**).
  - *Citation Precision Khoản:* 0,7757 vs 0,0435 (**+73,22 đpt**).
  - *Legal Correctness:* 0,8777 vs 0,8210 (**+5,67 đpt**).
  - *Exception Coverage:* 0,6786 vs 0,3929 (**+28,57 đpt**).
* **Bóc tách 3 "vùng nhạy cảm" kỹ thuật:**

#### (1) Exact Locator Recall@5: 0,5560 (UKG) vs 0,8509 (LightRAG)
* **Bản chất 1 - Mẫu số đo lường:** 0,5560 của UKG tính trên **39 câu đo được** (8 câu ở trạng thái `not_measured` do định dạng câu hỏi hoặc contract chưa bóc tách locator, không phải hệ thống trả lời sai). Còn LightRAG đo trên đủ **47 câu**.
* **Bản chất 2 - Khác biệt về độ hạt (Granularity Trade-off):**
  - Chunk 1.200 token của LightRAG chứa trung bình **~15 locator** (Điều/Khoản/Điểm) trong một khối văn bản lớn. Xác suất để khối văn bản này "chạm" vào locator cần tìm là rất cao (85,09%).
  - Ngược lại, mỗi phân đoạn của UKG chỉ chứa đúng **1 locator vi mô** duy nhất.
  - Hậu quả của LightRAG: Bao trùm locator rất cao nhưng mô hình không biết căn cứ thực sự nằm ở đâu $\rightarrow$ Citation Precision cấp Khoản chỉ đạt **4,35%**.
  - UKG chấp nhận đánh đổi: Độ phủ locator trên diện rộng đạt 55,60% nhưng đạt Citation Precision cấp Khoản lên tới **77,57%** (gần 18 lần so với LightRAG) và giữ ngữ cảnh siêu tinh gọn 580 token.

#### (2) Condition Coverage: 0,7066 (UKG) vs 0,8421 (LightRAG)
* **Bản chất:** LightRAG gom chunk lớn nên vô tình ôm trọn các điều kiện bối cảnh nằm rải rác xung quanh. UKG cắt nhỏ vi mô tập trung vào quy phạm lõi, nên khi điều kiện nằm ở các Khoản khác hoặc Điều quy định chung, hệ thống chưa gom đủ nếu thiếu cơ chế lan truyền đồ thị.
* **Thái độ trả lời:** Thừa nhận đây là hạn chế của phân đoạn vi mô đơn lẻ; nhấn mạnh việc cải thiện cần cơ chế Context Expansion và Graph Traversal chứ không chỉ phụ thuộc vào retriever.

#### (3) Chain Exact Match = 0,0000 trên 18 câu đa bước
* **Bản chất:** 
  - UKG đạt *Reference-target Recall* = **58,67%** (định vị được hơn một nửa số node đích của quan hệ dẫn chiếu).
  - Nhưng để tái dựng hoàn hảo 100% chuỗi đường dẫn có thứ tự `A -> B -> C` thì tỷ lệ khớp chính xác là **0,0000** (với LightRAG là `N/A` vì chưa hỗ trợ trích xuất đường dẫn theo giao thức này).
* **Đóng góp khoa học:** Đây là bằng chứng thực nghiệm giá trị nhất khẳng định: **Tìm kiếm ngữ nghĩa đơn thuần hoàn toàn bất lực trước bài toán dẫn chiếu nhiều bước**. Muốn giải bài toán này, bắt buộc phải có giải thuật duyệt đồ thị có ràng buộc (*Constrained Graph Traversal*).

---

## III. KIẾN TRÚC HỆ THỐNG & RANH GIỚI KỸ THUẬT MODULE

### 1. Triết lý hai tầng: Physical Graph vs Semantic Graph
* **Physical Graph (Đồ thị vật lý):** 
  - Xây dựng bằng **quy tắc tất định (Deterministic Regex Rules)** dựa trên cấu trúc hình thức: Luật $\rightarrow$ Chương $\rightarrow$ Mục $\rightarrow$ Điều $\rightarrow$ Khoản $\rightarrow$ Điểm.
  - Không dùng LLM ở tầng này $\rightarrow$ Tốc độ cực nhanh, bảo toàn 100% phả hệ cấu trúc, chi phí tính toán bằng 0.
  - **Module 3 Validation:** Kiểm tra tính toàn vẹn của schema, phát hiện ID trùng lặp, đứt gãy cha-con. Các node lỗi nghiêm trọng được cách ly vào hàng đợi cảnh báo. *Lưu ý: Hệ thống chạy trên dữ liệu văn bản đã chuẩn hóa, chưa thử nghiệm trên văn bản lỗi OCR.*
* **Semantic Graph (Đồ thị ngữ nghĩa):**
  - Trích xuất quan hệ dẫn chiếu, điều kiện, ngoại lệ bằng mô hình ngôn ngữ kết hợp regex.
  - Toàn bộ việc xây dựng đồ thị thực hiện ở **Indexing Time**. Ở **Query Time**, hệ thống chỉ duyệt các cạnh đã có $\rightarrow$ Không làm tăng độ trễ truy vấn trực tuyến.

### 2. Module 5 Semantic Router & Ranh giới số liệu 9,33%
* **Mô hình:** Qwen2.5-0.5B (0,5 tỷ tham số) kết hợp toán tử Max-Fusion:  
  $$S_{final} = \max(S_{regex}, S_{vector})$$
* **Số liệu Golden Set v2 ($N=193$ node quy phạm):**
  - Tại ngưỡng $\theta = 0,85$: Recall = **96,85%**, Precision = **70,29%**, F1 = **0,8146**.
  - So với ngưỡng $\theta = 0,80$, số node phải chuyển tiếp xử lý giảm từ 193 xuống 175 node (giảm đúng 18 node, tương đương **giảm 9,33% khối lượng xử lý chuyển tiếp**).
  - Trong 18 node được cắt giảm đó: có **14 node thủ tục** được loại bỏ chính xác (True Negatives) và **4 node quy phạm** bị bỏ sót (False Negatives).
* **Causal Attention:** Qwen2.5-0.5B là mô hình ngôn ngữ tự hồi quy (Autoregressive), cơ chế Causal Attention xử lý tuần tự từ trái qua phải, phù hợp với mệnh đề quy phạm ngắn có trật tự logic: *Chủ thể $\rightarrow$ Điều kiện $\rightarrow$ Chế tài*. Tuy nhiên, nhóm thừa nhận đây là **lựa chọn thiết kế kiến trúc**, chưa có thí nghiệm ablation độc lập để cô lập riêng tác động nhân quả của Causal Attention so với các yếu tố khác.

---

# PHẦN 2: BỘ GIẢ ĐỊNH CÂU HỎI PHẢN BIỆN & KỊCH BẢN TRẢ LỜI ĐỈNH CAO (25 TÌNH HUỐNG)

> **CÔNG THỨC TRẢ LỜI 3 BƯỚC CHUẨN MỰC:**  
> 1. **Bước 1 - Khẳng định thực tế (Acknowledge & Assert Fact):** Điềm tĩnh cảm ơn, nhắc lại con số thực nghiệm chính xác, không vòng vo né tránh.  
> 2. **Bước 2 - Giải thích cơ chế / Đánh đổi kỹ thuật (Explain Mechanism & Trade-off):** Nêu rõ bối cảnh đo lường, nguyên nhân gốc rễ và sự đánh đổi có chủ đích.  
> 3. **Bước 3 - Đóng khung kết luận / Hướng giải quyết (Frame as Contribution / Road Ahead):** Biến vấn đề thành một phát hiện khoa học hoặc chỉ rõ giải pháp khắc phục trong lộ trình tiếp theo.

---

## GÓC A: THẦY PHẢN BIỆN PHƯƠNG PHÁP LUẬN & TÍNH HỢP LỆ THỰC NGHIỆM

### Câu 1: "Tại sao ở Giai đoạn 1 nhóm lại lập chỉ mục LightRAG trên 500 điều luật, trong khi Naive và Hybrid chạy trên toàn bộ văn bản? Như vậy có bất công cho LightRAG không?"
* **Cái bẫy của Thầy:** Bắt thóp việc không đồng nhất phạm vi corpus (Equal Scope Bias).
* **Kịch bản trả lời mẫu:**
  > *"Em xin cảm ơn Thầy/Cô về câu hỏi rất sâu sắc về phương pháp luận!  
  > Dạ thưa Thầy Cô, nhóm xin báo cáo rõ: Trong Giai đoạn 1, do LightRAG sử dụng mô hình ngôn ngữ lớn để trích xuất toàn bộ thực thể và quan hệ nên chi phí tính toán và gọi API rất cao, nhóm chỉ đủ tài nguyên lập chỉ mục trên 500 điều luật trọng điểm của Bộ luật Hình sự và Bộ luật Lao động.  
  > Để đảm bảo tính công bằng tuyệt đối khi đối chuẩn (Equal Scope Evaluation), nhóm không đánh giá trên toàn bộ 512 câu hỏi mà xây dựng riêng tập Tier 1 gồm 205 câu hỏi. 100% câu hỏi trong Tier 1 được kiểm soát để căn cứ pháp lý cần viện dẫn nằm trọn trong 500 điều luật mà LightRAG đã lập chỉ mục.  
  > Như vậy, cả ba hệ thống đều đứng trước cơ hội truy hồi như nhau trên cùng một không gian chứa đáp án. Việc này được nhóm nêu rõ tại Mục 3.1 và Bảng 2.4 của báo cáo nhằm bảo vệ tính liêm chính thực nghiệm."*

### Câu 2: "Tại sao nhóm lại dùng LLM-Judge (GPT-4o-mini) để chấm điểm? Liệu việc 'AI chấm AI' có tạo ra sự thiên vị hoặc rò rỉ prompt không?"
* **Cái bẫy của Thầy:** Nghi ngờ tính khách quan của bộ đánh giá tự động.
* **Kịch bản trả lời mẫu:**
  > *"Dạ thưa Quý Thầy Cô, nhóm nhận thức rất rõ nguy cơ thiên vị của LLM-Judge, đặc biệt là thiên vị độ dài (verbosity bias) và thiên vị vị trí. Để kiểm soát chặt chẽ biến số này, nhóm đã thực hiện ba biện pháp kỹ thuật:  
  > Thứ nhất, chuẩn hóa rubric chấm điểm nhị phân (0 hoặc 1) tường minh: mô hình chỉ chấm đạt khi câu trả lời chỉ ra đúng số Điều, Khoản cụ thể khớp với ground-truth, không chấm điểm cảm tính theo độ mượt của văn phong.  
  > Thứ hai, ở Giai đoạn 2, nhóm chạy 3.072 lượt thẩm định độc lập để triệt tiêu phương sai ngẫu nhiên.  
  > Thứ ba và quan trọng nhất, ở Giai đoạn 3, nhóm không phụ thuộc hoàn toàn vào LLM-Judge mà đối soát chéo với các chỉ số đo lường dựa trên quy tắc chuỗi ký tự chính xác (như Citation Precision Điều, Khoản tại Bảng 3.16) và thẩm định thủ công của con người trên 50 câu Benchmark B. Kết quả giữa các phương pháp đánh giá cho thấy xu hướng đồng thuận cao."*

### Câu 3: "Tại sao Giai đoạn 2 cấu hình C5 đạt Citation Accuracy tới 0,9902 mà sang Giai đoạn 3 Citation Precision của UKG chỉ còn 0,8369 (Điều) và 0,7757 (Khoản)? Có sự mâu thuẫn số liệu ở đây không?"
* **Cái bẫy của Thầy:** Nhầm lẫn giữa In-context Evaluation (GĐ2) và End-to-end Evaluation (GĐ3).
* **Kịch bản trả lời mẫu:**
  > *"Dạ thưa Thầy Cô, hai con số này hoàn toàn nhất quán và phản ánh hai tầng đánh giá khác nhau trong phương pháp luận:  
  > Ở Giai đoạn 2, con số 0,9902 là In-context Citation Accuracy đo lường trên ngữ cảnh truy hồi: tức là kiểm tra xem các phân đoạn vi mô nạp vào mô hình có chứa đúng căn cứ pháp lý hay không, độc lập với việc sinh văn bản của LLM.  
  > Sang Giai đoạn 3, hệ thống đánh giá câu trả lời toàn trình (End-to-end Generation) trên Benchmark B với 50 câu hỏi phân tầng phức tạp có nhiều điều kiện và ngoại lệ. Khi LLM phải tự tổng hợp câu trả lời từ ngữ cảnh, nó vẫn có xác suất ảo giác hoặc bỏ sót định danh, khiến Citation Precision câu trả lời đạt 0,8369 ở cấp Điều và 0,7757 ở cấp Khoản.  
  > Sự phân tách này giúp nhóm khẳng định: Bộ phân tích cấu trúc Parser v2 đã hoàn thành xuất sắc nhiệm vụ gom căn cứ (đạt 99%), và khoảng cách còn lại nằm ở năng lực diễn giải của mô hình ngôn ngữ thế hệ."*

### Câu 4: "Tại sao Benchmark B chỉ có 50 câu hỏi? Cỡ mẫu này có quá nhỏ để đưa ra kết luận khoa học có ý nghĩa thống kê không?"
* **Cái bẫy của Thầy:** Bắt bẻ về độ tin cậy thống kê của tập dữ liệu nhỏ.
* **Kịch bản trả lời mẫu:**
  > *"Dạ thưa Quý Thầy Cô, Benchmark B được thiết kế theo định hướng chẩn đoán chuyên sâu (Deep Diagnostic Benchmark), tương tự cách tiếp cận của LegalBench hay CaseHOLD trên thế giới khi đánh giá các tác vụ lý luận phức tạp:  
  > Đối với Benchmark A diện rộng (512 câu), nhóm đã kiểm chứng năng lực truy hồi trên quy mô lớn của 7 đạo luật.  
  > Tuy nhiên, để đánh giá đa điều kiện, mệnh đề ngoại lệ và dẫn chiếu chéo nhiều bước, nhóm bắt buộc phải kiểm toán thủ công 100% từng Điều, Khoản, Điểm và đường đi suy luận trong ground-truth. Nếu mở rộng hàng nghìn câu, việc gán nhãn thủ công với độ chính xác chuyên gia là bất khả thi. 50 câu hỏi phân tầng tại Chương III Luật Đất đai 2024 (Bảng 2.6) đại diện đầy đủ cho 9 tình huống pháp lý điển hình, cho phép nhóm mổ xẻ tường minh từng trường hợp thành công và thất bại của hệ thống."*

### Câu 5: "Nhóm giảm Jaccard từ 0,68 xuống 0,31 bằng cách nào? Liệu có phải nhóm đã sửa toàn bộ 512 câu không?"
* **Cái bẫy của Thầy:** Kiểm tra tính xác thực của quy trình biên soạn Benchmark A.
* **Kịch bản trả lời mẫu:**
  > *"Dạ thưa Thầy Cô, nhóm thực hiện diễn đạt lại có chọn lọc (Selective Paraphrasing), chứ không viết lại toàn bộ 512 câu:  
  > Ban đầu, nhóm đo lường hệ số trùng lặp từ vựng Jaccard giữa câu hỏi và văn bản luật. Các câu có Jaccard > 0,5 (chứa quá nhiều từ khóa nguyên văn trong luật) được nhóm chọn lọc để viết lại bằng ngôn ngữ tự nhiên đời thường, thay thế từ ngữ chuyên môn bằng các tình huống cụ thể của người dân.  
  > Kết quả giúp kéo phân phối Jaccard trung bình của toàn bộ 512 câu từ 0,68 xuống 0,31. Điều này giúp loại bỏ lợi thế không mong muốn của các giải thuật so khớp từ khóa thô như BM25, tạo môi trường kiểm định công bằng cho khả năng hiểu ngữ nghĩa của các mô hình vector và đồ thị."*

---

## GÓC B: THẦY PHẢN BIỆN KỸ THUẬT AI, NLP & EMBEDDING

### Câu 6: "Tại sao nhóm lại dùng Qwen2.5-0.5B cho Module 5 mà không dùng BERT hay RoBERTa vốn rất mạnh về phân loại câu?"
* **Cái bẫy của Thầy:** Vặn về việc chọn mô hình Causal LLM cho bài toán định tuyến phân loại.
* **Kịch bản trả lời mẫu:**
  > *"Dạ thưa Thầy Cô, ban đầu nhóm đã cân nhắc các mô hình Bi-encoder dạng BERT. Tuy nhiên, dữ liệu quy phạm pháp luật có một đặc tính rất khác biệt: trật tự logic tuần tự của mệnh đề quy phạm (*Nếu có điều kiện A $\rightarrow$ Thì chủ thể B $\rightarrow$ Được phép hoặc Không được phép làm C*).  
  > Các mô hình tự hồi quy (Autoregressive) như Qwen2.5 sử dụng Causal Attention xử lý văn bản tuần tự từ trái qua phải, giúp duy trì sự phụ thuộc giữa điều kiện và chế tài tốt hơn phép gộp trung bình (Mean-pooling) của Bi-encoder trên các đoạn văn bản ngắn.  
  > Hơn nữa, với kích thước chỉ 0,5 tỷ tham số, Qwen2.5-0.5B chạy suy luận cực nhanh trên phần cứng tiêu chuẩn, kết hợp cùng Max-Fusion đạt F1 0,8146 trên Golden Set v2 mà không làm nghẽn luồng xử lý của hệ thống."*

### Câu 7: "Nhóm có làm thí nghiệm Ablation riêng nào để chứng minh Causal Attention tạo ra sự vượt trội hơn Masked Attention không?"
* **Cái bẫy của Thầy:** Bắt bẻ về việc tuyên bố nguyên nhân chưa có kiểm chứng cô lập biến số.
* **Kịch bản trả lời mẫu:**
  > *"Dạ thưa Thầy, nhóm xin thẳng thắn báo cáo: Trong phạm vi đề tài, nhóm lựa chọn Qwen2.5-0.5B như một gói giải pháp kiến trúc tổng thể dựa trên kết quả kiểm chuẩn thực nghiệm trên Golden Set v2, chứ chưa tiến hành một thí nghiệm ablation riêng biệt để cô lập độc lập tác động của Causal Attention so với Masked Attention của BERT trên cùng một kích thước tham số.  
  > Nhận định về lợi thế trật tự tuần tự của Causal Attention là giả thuyết thiết kế kiến trúc của nhóm. Nhóm xin tiếp thu ý kiến của Thầy để thực hiện một nghiên cứu thực nghiệm ablation sâu hơn về cơ chế chú ý trong công bố khoa học tiếp theo."*

### Câu 8: "Tại sao trong Bảng 3.7 về tỷ lệ dung hợp RRF, $\alpha = 1,0$ (Dense thuần) đạt Recall và MRR cao nhất mà nhóm lại chọn $\alpha = 0,8$?"
* **Cái bẫy của Thầy:** Vặn về tính tối ưu của việc chọn tham số.
* **Kịch bản trả lời mẫu:**
  > *"Dạ thưa Thầy Cô, thực nghiệm tại Bảng 3.7 ghi nhận rất rõ: $\alpha = 1,0$ đạt Recall 0,9316 và MRR 0,8602, cao hơn so với $\alpha = 0,8$ (Recall 0,9297, MRR 0,8220).  
  > Tuy nhiên, nhóm không lựa chọn $\alpha = 1,0$ vì đó là cấu hình Dense thuần túy. Trên tập Benchmark A, do câu hỏi đã được diễn đạt lại (Jaccard 0,31), vector dense phát huy tối đa ưu thế. Nhưng trong ứng dụng pháp lý thực tế, người dùng rất hay tra cứu bằng số hiệu văn bản, từ viết tắt hoặc tên tội danh nguyên văn (ví dụ: 'Điều 132', 'tội cố ý gây thương tích'). Trong các trường hợp đó, Dense rất dễ bị trôi ngữ nghĩa, trong khi BM25 bắt từ khóa chính xác tuyệt đối.  
  > Nhóm chọn $\alpha = 0,8$ như một cấu hình cân bằng thực tiễn: chấp nhận giảm 0,19 đpt Recall để giữ lại 20% tín hiệu từ vựng của BM25, bảo đảm hệ thống vận hành bền bỉ trước mọi dạng câu hỏi của người dùng."*

### Câu 9: "Toán tử Max-Fusion giữa Regex và Vector trong Module 5 hoạt động thế nào? Nếu Regex sai mà Vector đúng thì sao?"
* **Cái bẫy của Thầy:** Bắt bẻ cơ chế hợp nhất điểm số và rủi ro xung đột tín hiệu.
* **Kịch bản trả lời mẫu:**
  > *"Dạ thưa Thầy Cô, toán tử Max-Fusion hoạt động theo nguyên lý Soft-OR: điểm số cuối cùng là giá trị cực đại giữa điểm Regex và điểm tương đồng Vector: $S_{final} = \max(S_{regex}, S_{vector})$.  
  > Bản chất của bài toán lọc quy phạm pháp luật là ưu tiên bắt giữ tối đa, giảm thiểu bỏ sót căn cứ quan trọng.  
  > - Nếu một phân đoạn có từ khóa quy phạm tường minh (như 'phải', 'không được', 'bị phạt tù'), Regex nhận diện chắc chắn và gán điểm 1,0.  
  > - Nếu phân đoạn có cách diễn đạt gián tiếp không chứa từ khóa cứng nhưng mang ngữ nghĩa quy phạm, Regex cho điểm 0 nhưng mô hình vector sẽ cho điểm cao (ví dụ 0,88). Phép lấy Max sẽ bảo toàn điểm vector này để vượt ngưỡng $\theta = 0,85$.  
  > Ngược lại, chỉ khi cả Regex không thấy từ khóa VÀ Vector đánh giá ngữ nghĩa là văn bản thủ tục thuần túy thì phân đoạn mới bị loại bỏ."*

### Câu 10: "Hệ thống có gặp vấn đề 'Lost in the Middle' khi đưa Top-5 điều luật vào LLM không?"
* **Cái bẫy của Thầy:** Kiểm tra kiến thức về hiện tượng suy giảm khả năng tập trung của LLM trên ngữ cảnh dài.
* **Kịch bản trả lời mẫu:**
  > *"Dạ thưa Thầy Cô, hiện tượng 'Lost in the Middle' xảy ra rất trầm trọng ở Giai đoạn 1 khi hệ thống nạp các khối văn bản thô dài gần 2.900 token. LLM thường chỉ chú ý đến đoạn đầu và đoạn cuối, dẫn đến việc bỏ sót căn cứ ở giữa và gây ra tỷ lệ ảo giác trích dẫn cao.  
  > Đây chính là động lực để nhóm xây dựng Parser v2 và giải thuật Article MaxP ở Giai đoạn 2. Nhờ bóc tách vi mô cấp Khoản và chỉ gom các phân đoạn liên quan nhất của Điều, ngữ cảnh nạp vào LLM ở C5 chỉ còn 580 token (giảm 79,9%). Với độ dài tinh gọn dưới 600 token, thông tin tập trung hoàn toàn vào cửa sổ chú ý tối ưu của GPT-4o-mini, triệt tiêu hoàn toàn hiện tượng Lost in the Middle."*

---

## GÓC C: THẦY PHẢN BIỆN CƠ SỞ DỮ LIỆU & ĐỒ THỊ TRI THỨC

### Câu 11: "Việc xây dựng đồ thị Hybrid UKG phức tạp như vậy có làm bùng nổ thời gian đáp ứng (Latency) khi người dùng tra cứu trực tuyến không?"
* **Cái bẫy của Thầy:** Vấn đề chi phí vận hành và độ trễ hệ thống.
* **Kịch bản trả lời mẫu:**
  > *"Dạ thưa Thầy Cô, hoàn toàn không làm tăng độ trễ truy vấn trực tuyến của người dùng:  
  > Toàn bộ các tác vụ nặng nhất gồm phân tích cú pháp đệ quy, trích xuất thực thể, dựng cây phân cấp Physical Graph và liên kết Semantic Graph đều được thực hiện ngoại tuyến một lần duy nhất trong pha lập chỉ mục (Indexing Phase).  
  > Khi người dùng gửi câu hỏi (Query Phase), hệ thống chỉ thực hiện một lượt tìm kiếm vector để xác định node mỏ neo, sau đó duyệt theo các cạnh quan hệ có sẵn trên đồ thị bộ nhớ. Thời gian duyệt đồ thị chỉ tính bằng mili-giây, tổng thời gian đáp ứng tương đương với một hệ thống RAG vector thông thường nhưng thông tin truy xuất có cấu trúc và căn cứ rõ ràng hơn."*

### Câu 12: "Tại sao chỉ số Chain Exact Match trên 18 câu hỏi dẫn chiếu ở Giai đoạn 3 lại bằng 0,0000? Xây dựng đồ thị tri thức để làm gì khi mà tái dựng đường dẫn bằng 0?"
* **Cái bẫy của Thầy:** Công kích trực diện vào điểm số 0,0000 của chỉ số đồ thị.
* **Kịch bản trả lời mẫu:**
  > *"Dạ thưa Quý Thầy Cô, nhóm xin khẳng định con số 0,0000 này không phải là sự thất bại vô nghĩa, mà là một phát hiện thực nghiệm mang giá trị đóng góp rất lớn của đề tài:  
  > Trên 18 câu hỏi dẫn chiếu phức tạp, hệ thống Hybrid UKG đã định vị thành công 58,67% căn cứ đích đơn lẻ (Reference-target Recall). Tuy nhiên, chỉ số Chain Exact Match đòi hỏi hệ thống phải tái dựng hoàn hảo 100% trật tự chuỗi đường dẫn từ Điều khởi đầu qua các Điều trung gian đến Điều kết luận.  
  > Kết quả 0,0000 chứng minh một chân lý khoa học: Việc truy hồi ngữ nghĩa kết hợp duyệt đồ thị tham lam (Greedy Traversal) hoàn toàn bất lực trong việc khép kín chuỗi suy luận pháp lý nhiều bước. Để giải quyết triệt để bài toán này, hệ thống bắt buộc phải tích hợp giải thuật duyệt đồ thị có ràng buộc logic (Constrained Graph Traversal với thuật toán A* hoặc BFS có kiểm soát kiểu quan hệ). Đây chính là cơ sở phương pháp luận để nhóm định hình hướng nghiên cứu tiếp theo."*

### Câu 13: "Đồ thị của nhóm khác gì so với Knowledge Graph truyền thống hay đồ thị của LightRAG?"
* **Cái bẫy của Thầy:** Kiểm tra tính mới của kiến trúc Hybrid UKG.
* **Kịch bản trả lời mẫu:**
  > *"Dạ thưa Thầy Cô, điểm khác biệt cốt lõi nằm ở triết lý tổ chức dữ liệu:  
  > 1. Knowledge Graph truyền thống tập trung vào bộ ba thực thể phẳng `(Chủ thể - Vị ngữ - Khách thể)`, làm mất đi cấu trúc phả hệ văn bản luật.  
  > 2. Đồ thị LightRAG dùng LLM trích xuất thực thể từ các chunk văn bản phi cấu trúc, tạo ra một mạng lưới liên kết tự do hai tầng nhưng không định danh được vị trí pháp lý chính xác của Điều, Khoản, Điểm.  
  > 3. Hybrid UKG của nhóm tách bạch hai tầng rõ ràng: Tầng 1 là Physical Graph bất biến bảo toàn nguyên vẹn phả hệ pháp luật bằng quy tắc tất định; Tầng 2 là Semantic Graph trích xuất quan hệ quy phạm động. Nhờ cấu trúc phân tầng này, hệ thống vừa nắm giữ được ngữ nghĩa liên kết, vừa truy vết chính xác nguồn gốc căn cứ vi mô đến từng ký tự."*

### Câu 14: "Module 3 Validation của nhóm xử lý thế nào khi văn bản đầu vào bị lỗi quét OCR, sai số Điều, hoặc mất định dạng phân cấp?"
* **Cái bẫy của Thầy:** Vặn về độ bền vững trước dữ liệu nhiễu thực tế.
* **Kịch bản trả lời mẫu:**
  > *"Dạ thưa Thầy Cô, nhóm xin báo cáo rõ phạm vi:  
  > Module 3 Validation của nhóm được thiết kế để kiểm tra các lỗi cấu trúc có thể phát hiện được bằng quy tắc: sai lệch cấu trúc dữ liệu schema, trùng lặp định danh node_id, hoặc đứt gãy quan hệ cha-con (ví dụ có Điểm nhưng không tìm thấy Khoản chứa nó). Khi phát hiện vi phạm, hệ thống tự động cách ly node lỗi vào hàng đợi riêng và ghi log cảnh báo, không để node lỗi làm sai lệch cây đồ thị.  
  > Tuy nhiên, nhóm xin thẳng thắn thừa nhận: trong khuôn khổ đề tài, hệ thống được kiểm chuẩn trên kho dữ liệu văn bản pháp luật đã qua chuẩn hóa định dạng văn bản điện tử; nhóm chưa thực nghiệm chuyên biệt trên các tài liệu quét OCR có độ nhiễu cao. Đây là ranh giới kỹ thuật mà nhóm dự kiến mở rộng bộ lọc tiền xử lý trong giai đoạn tới."*

---

## GÓC D: THẦY PHẢN BIỆN KIỂM TOÁN SỐ LIỆU & LIÊM CHÍNH KHOA HỌC

### Câu 15: "Tại sao trên Slide 11, chỉ số Exact Locator Recall@5 của UKG chỉ đạt 0,5560, thua xa con số 0,8509 của LightRAG? Có phải UKG định vị vị trí kém hơn LightRAG?"
* **Cái bẫy của Thầy:** Bẫy so sánh số học thuần túy bỏ qua điều kiện đo lường.
* **Kịch bản trả lời mẫu:**
  > *"Dạ thưa Quý Thầy Cô, nếu chỉ nhìn thuần túy vào con số 0,5560 so với 0,8509, thoạt nhìn LightRAG có vẻ định vị tốt hơn. Nhưng khi phân tích sâu bản chất đo lường, đây là một sự đánh đổi kỹ thuật hoàn toàn có chủ đích:  
  > Thứ nhất về mẫu số: 0,5560 của UKG được đo trên 39 câu đo được (8 câu ở trạng thái not_measured do định dạng hợp đồng dữ liệu chưa ánh xạ), trong khi LightRAG đo trên 47 câu.  
  > Thứ hai về độ hạt: Chunk của LightRAG có độ dài cố định 1.200 token, trung bình chứa khoảng 15 locator (Điều/Khoản/Điểm) trong một khối văn bản. Một khối văn bản lớn như vậy có xác suất bao trùm trúng locator cần tìm là rất cao (85%). Nhưng hệ quả là mô hình hoàn toàn không biết căn cứ thực sự nằm ở đâu, thể hiện qua việc Citation Precision cấp Khoản của LightRAG chỉ đạt vỏn vẹn 4,35%!  
  > Ngược lại, mỗi phân đoạn của UKG chỉ chứa đúng 1 locator duy nhất. Hệ thống chấp nhận độ phủ locator ở mức 55,60% để đổi lại độ chính xác trích dẫn cấp Khoản đạt 77,57% (gấp gần 18 lần LightRAG) và dung lượng ngữ cảnh siêu tinh gọn 580 token. Đây là sự đánh đổi hoàn toàn chính đáng trong bài toán pháp lý."*

### Câu 16: "Tại sao chỉ số Condition Coverage của UKG (0,7066) lại thấp hơn LightRAG (0,8421) tới 13,55 điểm phần trăm?"
* **Cái bẫy của Thầy:** Bắt bẻ về điểm yếu bao phủ điều kiện pháp lý.
* **Kịch bản trả lời mẫu:**
  > *"Dạ thưa Thầy Cô, nhóm xin thẳng thắn thừa nhận đây là một ranh giới kỹ thuật có thật của hệ thống:  
  > Trong văn bản luật, các điều kiện áp dụng pháp luật thường phân tán ở nhiều Khoản khác nhau hoặc nằm ở các Điều quy định chung của Chương. Phân đoạn vi mô của UKG bóc tách nhỏ theo từng Khoản nên tập trung rất sâu vào quy phạm lõi của Khoản đó, nhưng nếu câu hỏi đòi hỏi tổng hợp nhiều điều kiện nằm rải rác mà hệ thống chưa kích hoạt cơ chế mở rộng ngữ cảnh, câu trả lời sẽ bị khuyết điều kiện.  
  > LightRAG nhờ nạp khối chunk lớn 1.200 token nên vô tình ôm trọn các điều kiện nằm xung quanh. Tuy nhiên, nhóm cũng nhận định sự chênh lệch này không hoàn toàn do bộ phân đoạn, mà còn phụ thuộc vào cơ chế chọn lọc ngữ cảnh và năng lực tổng hợp của mô hình sinh GPT-4o-mini. Nhóm đã định hình việc khắc phục hạn chế này bằng cơ chế lan truyền ngữ cảnh điều kiện giữa các node liên kết."*

### Câu 17: "Trong Module 5, tại sao nhóm dám chấp nhận 4 False Negatives (bỏ sót 4 node quy phạm)? Trong ngành luật, bỏ sót một điều cấm có thể dẫn đến hậu quả pháp lý nghiêm trọng!"
* **Cái bẫy của Thầy:** Công kích vào tính an toàn của hệ thống AI pháp lý.
* **Kịch bản trả lời mẫu:**
  > *"Dạ thưa Thầy Cô, câu hỏi của Thầy chạm đúng vào bài toán cốt lõi của công nghệ AI trong lĩnh vực luật pháp:  
  > Trên Golden Set v2 gồm 193 node, tại ngưỡng $\theta = 0,85$, hệ thống đạt Recall 96,85%, F1 0,8146, giảm 9,33% khối lượng xử lý chuyển tiếp, loại bỏ chính xác 14 node thủ tục hành chính thuần túy. Tuy nhiên, hệ thống ghi nhận 4 False Negatives.  
  > Nhóm đã tiến hành kiểm toán chi tiết 4 trường hợp này: Đây là các phân đoạn nằm ở vùng ranh giới xám giữa quy định nội dung và thủ tục hồ sơ (ví dụ: quy định về thời hạn nộp giấy tờ kèm theo điều kiện).  
  > Trong thiết kế hệ thống thực tế, nhóm không phó mặc việc ra quyết định cho AI. 4 phân đoạn này được hệ thống gắn nhãn cảnh báo độ tin cậy biên (Marginal Confidence) để chuyển sang luồng rà soát của chuyên gia pháp lý (Human-in-the-loop). Việc dám công khai 4 False Negatives thể hiện sự trung thực khoa học và nhận thức rõ ranh giới an toàn của mô hình."*

### Câu 18: "Tại sao trong Bảng Slide 7 không đưa cột Chi phí API hay thời gian đáp ứng vào đối sánh?"
* **Cái bẫy của Thầy:** Kiểm tra việc lược bỏ thông tin.
* **Kịch bản trả lời mẫu:**
  > *"Dạ thưa Thầy Cô, nhóm xin báo cáo rõ: Trong báo cáo toàn văn, Bảng 3.3 và Bảng 3.4 tập trung đối soát thuần túy về hiệu năng truy hồi và chất lượng tạo sinh căn cứ pháp lý theo các thước đo chuẩn mực (Recall, MRR, Context Precision, Citation Accuracy).  
  > Các chỉ số về chi phí API và độ trễ được nhóm phân tích định tính ở phần thảo luận của Chương 3. Để đảm bảo tính chặt chẽ và liêm chính dữ liệu, mọi bảng số liệu trên slide thuyết trình đều được nhóm trích xuất nguyên văn khớp 100% từng ô từ các bảng chính thức trong báo cáo, không tự ý ghép nối các cột số liệu không nằm trong cùng một thiết kế kiểm chuẩn."*

---

## GÓC E: THẦY PHẢN BIỆN ỨNG DỤNG THỰC TIỄN & KHẢ NĂNG MỞ RỘNG

### Câu 19: "Hệ thống mới chỉ thử nghiệm trên Luật Đất đai 2024. Khi áp dụng cho toàn bộ hệ thống pháp luật Việt Nam với hàng trăm Nghị định, Thông tư hướng dẫn thì có bị vỡ trận không?"
* **Cái bẫy của Thầy:** Nghi ngờ khả năng mở rộng (Scalability) của công trình.
* **Kịch bản trả lời mẫu:**
  > *"Dạ thưa Quý Thầy Cô, kiến trúc đề xuất của nhóm được thiết kế theo nguyên lý mô-đun hóa cao, hoàn toàn có khả năng mở rộng sang các văn bản dưới luật:  
  > Thứ nhất, văn phạm lập quy của Việt Nam có tính chuẩn mực rất cao theo Luật Ban hành văn bản quy phạm pháp luật: các Nghị định, Thông tư đều tuân thủ chặt chẽ cấu trúc phân cấp Điều, Khoản, Điểm. Do đó, bộ phân tích Parser v2 có thể tái sử dụng tới 90% các quy tắc bóc tách cú pháp.  
  > Thứ hai, trên Benchmark A, nhóm đã chứng minh giải pháp hoạt động ổn định trên 7 đạo luật lớn với 2.087 điều luật và hơn 12.000 phân đoạn vi mô.  
  > Thách thức lớn nhất khi mở rộng sang Nghị định, Thông tư là xử lý các quan hệ dẫn chiếu thi hành (ví dụ: 'giao Chính phủ quy định chi tiết'). Đây chính là lý do nhóm đề xuất phát triển thêm các cạnh quan hệ ngữ nghĩa `elaborates` và `implements` trong lộ trình tương lai."*

### Câu 20: "Khi một văn bản luật được sửa đổi, bổ sung hoặc hết hiệu lực, hệ thống cập nhật thế nào? Có phải cào lại dữ liệu và lập chỉ mục lại từ đầu không?"
* **Cái bẫy của Thầy:** Đánh vào bài toán cập nhật dữ liệu động (Dynamic Data Updates).
* **Kịch bản trả lời mẫu:**
  > *"Dạ thưa Thầy Cô, đây chính là ưu điểm vượt trội của kiến trúc đồ thị Hybrid UKG so với các hệ thống RAG chunking truyền thống:  
  > Trong các hệ thống vector truyền thống, khi một văn bản sửa đổi, việc thay đổi ranh giới chunk buộc người dùng phải re-index lại toàn bộ kho dữ liệu.  
  > Trong khi đó, Hybrid UKG quản lý dữ liệu theo từng node Điều, Khoản độc lập có gắn định danh ID và siêu dữ liệu thời gian (temporal metadata). Khi có một luật sửa đổi ban hành, hệ thống chỉ cần:  
  > 1. Cập nhật trạng thái hiệu lực (`valid`, `amended`, `expired`) của đúng node Điều bị sửa đổi.  
  > 2. Thêm một cạnh quan hệ `amended_by` trỏ tới node của văn bản mới.  
  > Toàn bộ phần còn lại của đồ thị được giữ nguyên vẹn mà không cần tính toán lại, bảo đảm khả năng cập nhật tri thức động với chi phí tính toán tối thiểu."*

### Câu 21: "Nếu một người dân hỏi một câu bằng ngôn ngữ địa phương hoặc dùng từ ngữ đời thường sai thuật ngữ luật (ví dụ: 'sổ đỏ', 'sổ hồng' thay vì 'Giấy chứng nhận quyền sử dụng đất') thì hệ thống xử lý ra sao?"
* **Cái bẫy của Thầy:** Kiểm tra khả năng xử lý bài toán lệch pha từ vựng trong thực tiễn.
* **Kịch bản trả lời mẫu:**
  > *"Dạ thưa Thầy Cô, đây chính là đặc thù thứ ba của văn bản luật Việt Nam mà nhóm đã đặt ra ở Slide 3:  
  > Các từ ngữ đời thường như 'sổ đỏ', 'sổ hồng', 'bị phạt nguội' hoàn toàn không xuất hiện trong văn bản quy phạm pháp luật. Nếu dùng BM25 hoặc tìm kiếm từ khóa, hệ thống sẽ thất bại 100%.  
  > Hybrid UKG xử lý bài toán này qua hai lớp bảo vệ:  
  > Lớp 1: Mô hình nhúng ngữ nghĩa BGE-M3 có khả năng ánh xạ các khái niệm tương đồng trong không gian vector đa chiều (đã được kiểm chứng qua việc giảm Jaccard xuống 0,31 ở Benchmark A nhưng Recall vẫn đạt trên 92%).  
  > Lớp 2: Trong Semantic Graph, nhóm xây dựng từ điển thực thể đồng nghĩa (Synonym Entity Nodes), tự động liên kết các thuật ngữ thông dụng đời thường với định danh pháp lý chuẩn tắc, giúp đưa người dùng về đúng căn cứ pháp lý quy chuẩn."*

### Câu 22: "Tại sao nhóm chọn Luật Đất đai 2024 làm đối tượng nghiên cứu trọng tâm cho Benchmark B mà không phải Bộ luật Dân sự hay Hình sự?"
* **Cái bẫy của Thầy:** Kiểm tra tính thời sự và tính đại diện của ngữ liệu nghiên cứu.
* **Kịch bản trả lời mẫu:**
  > *"Dạ thưa Thầy Cô, nhóm lựa chọn Chương III Luật Đất đai 2024 vì ba lý do khoa học và thực tiễn:  
  > Thứ nhất về tính thời sự: Luật Đất đai 2024 là đạo luật có tác động sâu rộng nhất đến đời sống kinh tế - xã hội, có hiệu lực sớm từ ngày 01/8/2024 với rất nhiều điểm mới cần được tra cứu, giải thích chính xác.  
  > Thứ hai về độ phức tạp kỹ thuật: Chương III (Điều 26 đến Điều 48) về 'Quyền và nghĩa vụ của người sử dụng đất' có mật độ dẫn chiếu chéo cao nhất, chứa nhiều phân tầng chủ thể phức tạp (cá nhân, hộ gia đình, tổ chức kinh tế, người Việt Nam định cư ở nước ngoài) cùng hàng loạt điều kiện và ngoại lệ kèm theo.  
  > Đây là môi trường thử thách khắc nghiệt nhất (stress-test) để kiểm định xem một hệ thống RAG có thể xử lý được lý luận pháp lý phức tạp hay không."*

### Câu 23: "Nếu hệ thống đưa ra câu trả lời sai dẫn đến người dân áp dụng sai pháp luật thì trách nhiệm thuộc về ai? Nhóm có giải pháp an toàn nào?"
* **Cái bẫy của Thầy:** Đặt câu hỏi về đạo đức AI và an toàn pháp lý (AI Ethics & Safety).
* **Kịch bản trả lời mẫu:**
  > *"Dạ thưa Quý Thầy Cô, nhóm xác định rất rõ ranh giới của đề tài: Hệ thống Hybrid UKG là **công cụ hỗ trợ tra cứu và kiểm chứng căn cứ (Decision Support Tool)**, không phải là cơ quan tài phán hay thay thế tư vấn của luật sư.  
  > Về mặt an toàn kỹ thuật, hệ thống tích hợp hai cơ chế bảo vệ:  
  > 1. Cơ chế Provenance Tường minh: Mọi câu trả lời bắt buộc phải trích dẫn kèm theo đường dẫn căn cứ vi mô (Điều, Khoản, Điểm) để người dùng có thể nhấp chuột kiểm chứng trực tiếp văn bản gốc.  
  > 2. Cơ chế Từ chối Trả lời (Refusal Mechanism): Khi điểm tương đồng của các phân đoạn truy hồi không vượt qua ngưỡng an toàn hoặc rơi vào 3 câu hỏi không đủ căn cứ trong corpus (như Bảng 2.6), hệ thống chủ động đưa ra thông báo không đủ căn cứ thay vì bịa đặt câu trả lời."*

### Câu 24: "So với các giải pháp thương mại hiện nay như vLaw hay các chatbot pháp luật trên thị trường, công trình của nhóm có điểm gì vượt trội?"
* **Cái bẫy của Thầy:** Thử thách giá trị thực tiễn và tính cạnh tranh của đề tài.
* **Kịch bản trả lời mẫu:**
  > *"Dạ thưa Thầy Cô, phần lớn các chatbot pháp luật thương mại hiện nay trên thị trường vận hành theo hai dạng: hoặc là Naive RAG cắt văn bản thô theo kích thước cố định, hoặc là gọi API của các mô hình thương mại lớn đóng kín. Điểm yếu chung là tỷ lệ ảo giác trích dẫn cao, không kiểm soát được nguồn gốc căn cứ vi mô và chi phí vận hành rất đắt đỏ.  
  > Đề tài của nhóm mang lại ba giá trị vượt trội:  
  > 1. Về học thuật: Cung cấp một khung phương pháp kiểm chuẩn mở, độc lập (Benchmark A, B) với giao diện Adapter Pattern để cộng đồng có thể đối soát công bằng các kiến trúc RAG trên dữ liệu luật Việt Nam.  
  > 2. Về kỹ thuật: Giải pháp Parser v2 kết hợp Article MaxP giúp giảm tới 79,9% dung lượng ngữ cảnh, nâng Citation Accuracy ngữ cảnh lên 99%, tiết kiệm chi phí tính toán đáng kể.  
  > 3. Về kiến trúc: Mô hình Hybrid UKG hai tầng làm chủ hoàn toàn công nghệ từ bóc tách cấu trúc đến định tuyến quy phạm bằng mô hình mã nguồn mở cục bộ (Qwen2.5-0.5B), bảo đảm tính tự chủ công nghệ và an toàn dữ liệu."*

### Câu 25: "Nếu được tiếp tục phát triển đề tài này trong 6 tháng tới, nhóm sẽ ưu tiên làm điều gì nhất?"
* **Cái bẫy của Thầy:** Đánh giá tầm nhìn và sự hiểu biết của nhóm về hạn chế công trình.
* **Kịch bản trả lời mẫu:**
  > *"Dạ thưa Quý Thầy Cô, nếu có thêm 6 tháng nghiên cứu, nhóm sẽ tập trung giải quyết dứt điểm hai nút thắt kỹ thuật lớn nhất đã được chỉ ra trong báo cáo:  
  > Thứ nhất: Hoàn thiện giải thuật duyệt đồ thị có ràng buộc (Constrained Graph Traversal) để nâng chỉ số Chain Exact Match từ 0,0000 lên mức có thể ứng dụng, khép kín trọn vẹn chuỗi dẫn chiếu suy luận nhiều bước.  
  > Thứ hai: Nghiên cứu cơ chế lan truyền điều kiện (Condition Propagation) giữa các node liên kết để khắc phục triệt để khoảng cách của chỉ số Condition Coverage (hiện đang thấp hơn LightRAG 13,55 đpt).  
  > Nhóm tin rằng việc giải quyết hai bài toán này sẽ đưa kiến trúc Hybrid UKG trở thành một giải pháp hoàn chỉnh, có thể chuyển giao ứng dụng vào thực tiễn tra cứu pháp luật cho các cơ quan quản lý và người dân."*

---
"""

with open(md_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"[+] Successfully generated Markdown handbook: {md_path}")
