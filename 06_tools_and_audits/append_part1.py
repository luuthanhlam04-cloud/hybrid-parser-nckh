# -*- coding: utf-8 -*-
md_path = r"c:\Users\luuth\NCKH\Benchmark\docs\cam_nang_chuyen_sau_chuan_bi_phan_bien.md"

p1 = r"""# CẨM NANG CHUYÊN SÂU CHUẨN BỊ PHẢN BIỆN BẢO VỆ NCKH
## HỆ THỐNG LÝ LUẬN 5 TẦNG, GIẢI MÃ SỐ LIỆU VÀ BỘ 64 KỊCH BẢN PHẢN BIỆN THỰC CHIẾN (UNIFIED MASTER EDITION)
**ĐỀ TÀI:** ĐÁNH GIÁ VÀ TỐI ƯU HÓA CÁC KIẾN TRÚC RAG TRÊN NỀN TẢNG DỮ LIỆU CẤU TRÚC ĐẶC THÙ  
**HỘI ĐỒNG BẢO VỆ ĐỀ TÀI NGHIÊN CỨU KHOA HỌC SINH VIÊN**  
**NHÓM TÁC GIẢ:** LƯU THANH LÂM – NGÔ THẾ DƯƠNG – NGUYỄN BÌNH MINH  
**GIẢNG VIÊN HƯỚNG DẪN:** TS. NGUYỄN MẠNH DŨNG  

---

> **MỤC ĐÍCH VÀ NGUYÊN TẮC SỬ DỤNG TÀI LIỆU:**  
> 1. **Bản Master Thống nhất:** Đây là tài liệu duy nhất tích hợp toàn bộ tinh hoa lý thuyết, phương pháp luận đo lường từ báo cáo gốc `bancuoi.docx` (48.677 từ, 30 bảng số liệu) và các đợt phản biện chéo đa chiều.  
> 2. **Cấu trúc 2 Phần độc lập:**  
>    - **Phần 1: Kiến thức nền 5 Tầng** — Giúp 3 thành viên hiểu tận gốc rễ cơ chế kỹ thuật, bản chất từng con số và ranh giới nghiên cứu, tuyệt đối không học vẹt.  
>    - **Phần 2: 64 Kịch bản Q&A Thực chiến (8 Nhóm A–H)** — Thiết kế theo format 6 thành phần: *Mức độ nguy hiểm*, *Người phụ trách*, *Căn cứ báo cáo*, *Cái bẫy của Thầy*, *Kịch bản trả lời chuẩn 3 bước*, *Câu hỏi vặn tiếp theo (Follow-up)*, và *Điều cấm kỵ*.  
> 3. **Nguyên tắc Liêm chính số liệu:** 100% con số trong tài liệu này khớp chính xác từng ô với `bancuoi.docx`.

---

# PHẦN 1: KIẾN THỨC NỀN TẢNG CHUYÊN SÂU (5 TẦNG LÝ LUẬN)

## TẦNG 1: BỨC TRANH LỚN (BIG PICTURE)

### 1.1. Bài toán gốc và bối cảnh nghiên cứu
* **Yêu cầu lĩnh vực pháp lý:** Trong tra cứu văn bản quy phạm pháp luật, câu trả lời không chỉ cần đúng nội dung đại thể mà bắt buộc phải có **căn cứ có thể truy vết và kiểm chứng chính xác đến từng Điều, Khoản, Điểm**.
* **Thực trạng thế giới:** Nghiên cứu của Magesh và cs. (2025) trên tạp chí *Journal of Empirical Legal Studies (JELS)* chỉ ra các công cụ AI nghiên cứu pháp lý thương mại hàng đầu vẫn gặp tỷ lệ thông tin sai lệch từ 17% đến 33% trong điều kiện khảo sát.
* **Hệ quả thực tế:** Chỉ cần trích dẫn đúng số Điều nhưng sai một Khoản, hoặc bỏ sót một ngoại lệ tại một Điểm, hệ quả pháp lý của hành vi có thể bị đảo lộn hoàn toàn từ hợp pháp sang vi phạm pháp luật.
* **Phát hiện cốt lõi:** Các kiến trúc RAG phổ thông hiện nay tìm kiếm tài liệu rất tốt (Recall@5 > 95%), nhưng khả năng trích dẫn căn cứ vi mô sụt giảm nghiêm trọng xuống chỉ còn 13% – 33%. Đây là **khoảng cách giữa tìm kiếm và trích dẫn (Retrieval-Citation Gap)** do việc cắt đoạn văn bản thô làm đứt gãy phả hệ cấu trúc.

### 1.2. Bốn câu hỏi nghiên cứu (RQ1 – RQ4) và Mạch truyện 3 giai đoạn
| RQ | Trọng tâm nghiên cứu | Giai đoạn | Phát hiện & Đóng góp chính |
|---|---|:---:|---|
| **RQ1** | Hiệu năng truy hồi và độ chính xác trích dẫn của các RAG cơ sở khác biệt thế nào khi cắt đoạn thô? | **GĐ1** | Cả 3 hệ thống (Naive, Hybrid, LightRAG) đều đạt Recall@5 > 95% nhưng Citation Accuracy chỉ đạt 13% – 33%. Xác lập thực nghiệm sự tồn tại của khoảng cách tìm kiếm – trích dẫn. |
| **RQ2** | Bộ phân tích cấu trúc Parser v2 và giải thuật MaxP cải thiện trích dẫn ngữ cảnh và dung lượng ra sao? | **GĐ2** | Cấu hình C5 nâng In-context Citation Accuracy lên **0,9902** (+59,02 đpt so với C2), giảm **79,9%** dung lượng ngữ cảnh (từ 2.891 xuống 580 token). Khảo sát α=0,8 là điểm cân bằng thực tiễn. |
| **RQ3** | Kiến trúc đồ thị hai tầng Hybrid UKG nâng cao hiệu quả truy hồi và xử lý ngoại lệ thế nào khi đối sánh với LightRAG? | **GĐ3** | UKG vượt trội LightRAG ở Recall@5 cấp Điều (+18,26 đpt), MRR (+33,09 đpt), Citation Precision Khoản (0,7757 vs 0,0435) và Exception Coverage (0,6786 vs 0,3929, +28,57 đpt). Nhận diện ranh giới ở Condition Coverage (0,7066 vs 0,8421). |
| **RQ4** | Khả năng định vị đích dẫn chiếu và tái dựng chuỗi quan hệ có thứ tự đạt mức độ nào? | **GĐ3** | UKG định vị được 58,67% căn cứ đích đơn lẻ; chỉ số Chain Exact Match đạt 0,0000 trên 18 câu đa bước (LightRAG N/A). Đóng góp: Chứng minh tìm kiếm ngữ nghĩa đơn thuần không thể giải quyết dẫn chiếu, bắt buộc phải có Constrained Graph Traversal. |

### 1.3. Mạch truyện tổng thể & Elevator Pitch 30 giây
* **Mạch truyện logic xuyên suốt:**  
  $$\text{Phát hiện khoảng cách (GĐ1)} \longrightarrow \text{Đề xuất giải pháp cấu trúc (GĐ2)} \longrightarrow \text{Nâng cấp đồ thị hai tầng (GĐ3)} \longrightarrow \text{Minh bạch ranh giới (Kết luận)}$$
* **Elevator Pitch 30 giây:**  
  *"Đề tài giải quyết bài toán: RAG hiện nay tìm đúng Điều luật nhưng trích dẫn sai Khoản/Điểm do cắt đoạn thô làm mất phả hệ pháp lý. Nhóm đề xuất bộ phân tích Parser v2 gắn tiền tố cấu trúc bất biến kết hợp Article MaxP, giúp nâng Citation Accuracy ngữ cảnh lên 0,9902 và giảm 80% dung lượng token. Sau đó, nhóm phát triển kiến trúc đồ thị hai tầng Hybrid UKG, vượt trội LightRAG 28,57 điểm phần trăm ở khả năng xử lý quy phạm ngoại lệ. Hạn chế còn lại là điều kiện phân tán và chuỗi dẫn chiếu đa bước."*

---

## TẦNG 2: CƠ CHẾ KỸ THUẬT (TECHNICAL MECHANISMS)

### 2.1. BM25 (Truy hồi từ vựng)
* **Nguyên lý:** Đánh giá độ liên quan dựa trên tần suất xuất hiện của từ khóa trong tài liệu kết hợp với nghịch đảo tần suất tài liệu trong kho ngữ liệu (IDF).
* **Công thức Okapi BM25:**  
  $$\text{Score}(D, Q) = \sum_{q_i \in Q} \text{IDF}(q_i) \cdot \frac{f(q_i, D) \cdot (k_1 + 1)}{f(q_i, D) + k_1 \cdot \left(1 - b + b \cdot \frac{|D|}{\text{avgdl}}\right)}$$
* **Tham số chuẩn hóa:** $k_1 = 1,5$ (độ bão hòa tần suất từ), $b = 0,75$ (mức độ phạt độ dài văn bản).
* **Tại sao phải tách từ tiếng Việt:** Tiếng Việt là ngôn ngữ đơn lập, ranh giới từ không trùng với dấu cách trắng. Cụm *"hợp đồng lao động"* phải được nhận diện là một từ tổ có nghĩa trọn vẹn, nếu không bộ tách từ sẽ coi là 4 âm tiết rời rạc, làm sai lệch điểm IDF. Nhóm sử dụng thư viện `pyvi.ViTokenizer`.
* **Điểm yếu cốt tử:** Bất lực trước hiện tượng lệch pha từ vựng (*Paraphrase / Vocabulary Mismatch*) — người dùng hỏi *"bị phạt nguội"* thì BM25 không thể tìm ra *"xử phạt vi phạm hành chính qua phương tiện kỹ thuật nghiệp vụ"*.

### 2.2. Dense Retrieval (Truy hồi ngữ nghĩa dày đặc)
* **Nguyên lý Bi-encoder:** Sử dụng mô hình Transformer mã hóa câu hỏi $q$ và văn bản $d$ độc lập thành hai vector 1.024 chiều trong không gian ngữ nghĩa, sau đó tính độ tương đồng Cosine:  
  $$\text{CosineSim}(q, d) = \frac{\mathbf{e}_q \cdot \mathbf{e}_d}{\|\mathbf{e}_q\| \|\mathbf{e}_d\|}$$
* **Mô hình nhúng BGE-M3 (BAAI):** Hỗ trợ đa ngôn ngữ, độ dài ngữ cảnh tối đa 8.192 token, biểu diễn 1.024 chiều ở định dạng FP16. Trong đề tài, nhóm sử dụng chế độ nhúng dày đặc (Dense mode).
* **Chỉ mục FAISS IndexFlatIP:** Nhóm sử dụng giải thuật tìm kiếm tích vô hướng chính xác tuyệt đối (Exhaustive Inner Product Search) trên GPU Tesla T4, không dùng xấp xỉ lượng tử hóa (IVF/HNSW) vì quy mô ngữ liệu 2.087 điều luật hoàn toàn nằm gọn trong bộ nhớ VRAM, bảo đảm kết quả truy hồi chính xác 100%.
* **Điểm yếu cốt tử:** Dễ bị trôi ngữ nghĩa trước các từ khóa định danh cụ thể (số Điều, mã hiệu văn bản, từ viết tắt).

### 2.3. RRF (Reciprocal Rank Fusion - Dung hợp thứ hạng nghịch đảo)
* **Công thức Cormack (2009):**  
  $$\text{RRF}(d) = \sum_{m \in M} \frac{1}{k + \text{rank}_m(d)}$$
* **Tại sao dùng thứ hạng mà không cộng điểm trực tiếp:** Điểm BM25 không có cận trên $[0, +\infty)$, trong khi điểm Cosine nằm trong đoạn $[-1, 1]$. Việc chuẩn hóa Min-Max rất nhạy cảm với các điểm ngoại lai (outliers). RRF biến điểm số thành thứ tự xếp hạng (1, 2, 3...), triệt tiêu sự bất tương thích về thang đo.
* **Ý nghĩa của hằng số $k = 60$:** Hằng số làm mịn kinh nghiệm. Nếu $k$ quá nhỏ (ví dụ $k=1$), tài liệu đứng hạng 1 của một nhánh sẽ áp đảo hoàn toàn các tài liệu khác; nếu $k$ quá lớn, sự khác biệt giữa hạng 1 và hạng 10 bị triệt tiêu. Giá trị $k=60$ tạo ra đường suy giảm hài hòa đã được kiểm chứng chuẩn mực trong cộng đồng IR.

### 2.4. Cross-Encoder Reranker (Tái xếp hạng chéo)
* **Khác biệt với Bi-encoder:** Đưa đồng thời cặp $(q, d)$ vào cùng một mô hình Transformer qua chuỗi `[CLS] query [SEP] document [EOS]`. Các tầng Self-Attention cho phép từng từ trong câu hỏi tương tác trực tiếp với từng từ trong văn bản.
* **Tại sao chỉ đặt sau RRF:** Cross-Encoder cho độ chính xác cực cao nhưng chi phí tính toán rất lớn ($O(N)$ lượt suy luận nặng). Do đó, hệ thống chỉ dùng RRF lọc lấy Top-50 ứng viên tiềm năng nhất, rồi mới đưa qua Cross-Encoder (`bge-reranker-v2-m3`) để tái xếp hạng chọn ra Top-5 cuối cùng.

### 2.5. Structure-Aware Parser v2 & Module 3 Validation
* **Quy tắc phân đoạn văn phạm pháp lý:**  
  - Cấp Điều: `^Điều\s+(\d+)\.`
  - Cấp Khoản: `^(\d+)\.`
  - Cấp Điểm: `^([a-zđ])\)`
* **Tiền tố cấu trúc bất biến (Invariant Structural Prefix):**  
  Tự động gắn chuỗi phả hệ `[Luật Đất đai 2024 > Chương III > Điều 45 > Khoản 1 > Điểm a]` vào đầu mỗi phân đoạn vi mô. Khi phân đoạn này đứng độc lập trong không gian vector, nó luôn mang theo ngữ cảnh xuất xứ, không bao giờ bị biến thành văn bản mồ côi.
* **Module 3 Validation:** Thực hiện kiểm tra tính toàn vẹn schema, phát hiện ID trùng lặp, kiểm tra quan hệ cha-con (`parent_id` của Điểm phải trỏ đúng về Khoản chứa nó). Các node vi phạm nghiêm trọng được cách ly vào hàng đợi cảnh báo, không nạp vào đồ thị.
* **Kết quả:** Bóc tách 2.087 Điều luật thành **12.754 phân đoạn vi mô**.

### 2.6. Giải thuật Article-Level Max-Pooling (MaxP)
* **Vấn đề bão hòa Top-K:** Một Điều luật dài có thể sinh ra hàng chục phân đoạn vi mô. Nếu truy hồi thông thường, Top-5 có thể bị chiếm trọn bởi Khoản 1, 2, 3, 4 của cùng một Điều, đẩy các Điều luật liên quan khác văng khỏi ngữ cảnh.
* **Công thức MaxP:** Điểm số đại diện của Điều $d_i$ là điểm cực đại của phân đoạn con $c$ thuộc Điều đó:  
  $$S(d_i, q) = \max_{c \in d_i} s(c, q)$$
* **Tại sao dùng Max mà không dùng Mean:** Trong pháp luật, chỉ cần một Khoản trúng khớp với câu hỏi thì toàn bộ Điều luật đó đã có giá trị pháp lý làm căn cứ. Nếu dùng Mean (trung bình cộng), điểm số của Khoản trúng sẽ bị hàng loạt Khoản râu ria khác kéo tụt xuống, khiến Điều luật bị loại oan.

### 2.7. Kiến trúc Hybrid UKG hai tầng (Physical vs Semantic)
* **Tầng 1 - Physical Graph (Đồ thị vật lý):**  
  Xây dựng bằng **quy tắc tất định (Deterministic Regex)**. Node là Điều, Khoản, Điểm; Cạnh là quan hệ cấu trúc hình thức: `BELONG_TO`, `CONTAINS`, `NEXT`, `PREVIOUS`. Tầng này chạy cực nhanh, bảo toàn 100% phả hệ văn bản, không dùng LLM nên không bao giờ ảo giác.
* **Tầng 2 - Semantic Graph (Đồ thị ngữ nghĩa):**  
  Trích xuất động các quan hệ pháp lý: `SUBJECT`, `ACTION`, `CONDITION`, `EXCEPTION`, `REFERENCE_TO`.
* **Tại sao phải tách hai tầng:** Nếu phó mặc toàn bộ cho LLM tự trích xuất đồ thị như LightRAG, mạng lưới thực thể sẽ bị băm nát và mất định vị Điều Khoản Điểm. Nếu chỉ dùng cây cấu trúc cứng, hệ thống sẽ mù trước các quan hệ dẫn chiếu và ngoại lệ. Tách 2 tầng là giải pháp dung hợp tối ưu.

### 2.8. Module 5 Semantic Router & Toán tử Max-Fusion
* **Nhiệm vụ:** Phân loại và định tuyến các node phân đoạn trước khi gửi sang LLM trích xuất ngữ nghĩa (M6), nhằm giảm tải chi phí API.
* **Mô hình Qwen2.5-0.5B:** Mô hình ngôn ngữ tự hồi quy (Autoregressive) 0,5 tỷ tham số. Cơ chế Causal Attention xử lý tuần tự từ trái sang phải, bảo toàn logic điều kiện pháp lý tốt hơn phép gộp trung bình của Bi-encoder trên văn bản ngắn.
* **Toán tử Max-Fusion (Soft-OR):**  
  $$S_{\text{fusion}} = \max(S_{\text{regex}}, S_{\text{vector}})$$  
  Tránh bẫy *"Average Penalty Trap"* (nếu trung bình cộng, node có Regex=0 nhưng Semantic=0,94 sẽ bị kéo tụt xuống 0,47 và bị loại nhầm).
* **Số liệu Golden Set v2 ($N=193$):**  
  Tại ngưỡng θ = 0,85, hệ thống đạt Recall 96,85%, Precision 70,29%, F1 0,8146. Giảm chuyển tiếp 18 node ($18/193 = 9,33\%$ giảm tải xử lý). Trong 18 node này: **14 node thủ tục được lọc đúng** và **4 node quy phạm bị đánh đổi (False Negatives)**.

---

## TẦNG 3: PHƯƠNG PHÁP LUẬN (METHODOLOGY & VALIDITY)

### 3.1. Thiết kế 2 bộ kiểm chuẩn độc lập (Benchmark A & B)
* **Benchmark A ($N=512$, 7 đạo luật, 2.087 điều):** Đánh giá trên quy mô rộng (Breadth Evaluation) về năng lực truy hồi của các RAG cơ sở và ma trận 6 cấu hình phân đoạn cấu trúc.
* **Benchmark B ($N=50$, Chương III Luật Đất đai 2024):** Đánh giá chẩn đoán chuyên sâu (Deep Diagnostic Benchmark) về lý luận đa điều kiện, ngoại lệ và chuỗi dẫn chiếu giữa UKG và LightRAG.
* **Tại sao không gộp làm một:** Để đánh giá ngoại lệ và dẫn chiếu, 100% câu hỏi trong Benchmark B phải được kiểm toán thủ công từng Điều, Khoản, Điểm và đường đi suy luận. Quy trình kiểm toán chuyên gia này bất khả thi khi thực hiện trên hàng nghìn câu của Benchmark A.

### 3.2. Diễn đạt lại câu hỏi có chọn lọc (Jaccard 0,68 $\rightarrow$ 0,31)
* **Vấn đề rò rỉ từ vựng (Vocabulary Leakage):** Câu hỏi nguyên bản thường copy cụm từ trong luật, khiến chỉ số Jaccard overlap > 0,5 $\rightarrow$ BM25 thắng áp đảo một cách giả tạo.
* **Cách khắc phục:** Nhóm lọc các câu có Jaccard > 0,5 để viết lại bằng ngôn ngữ tự nhiên đời thường của người dân, thay thế thuật ngữ bằng tình huống cụ thể, kéo Jaccard trung bình từ 0,68 xuống 0,31.
* **Lưu ý liêm chính:** Báo cáo ghi nhận nhóm diễn đạt lại có chọn lọc, chưa có nhật ký xác nhận 100% 512 câu đều viết lại thành công.

### 3.3. Quy chuẩn đối soát Tier 1 (205 câu / 500 điều)
* Do LightRAG trích xuất đồ thị bằng LLM tốn chi phí lớn, LightRAG chỉ được index trên 500 điều luật của Bộ luật Hình sự và Bộ luật Lao động.
* Tập Tier 1 gồm 205 câu hỏi được lọc sao cho toàn bộ căn cứ cần thiết đều nằm trong 500 điều này. Đây là nguyên tắc **Equal Scope Evaluation** bảo đảm đối chuẩn công bằng về không gian chứa đáp án.

### 3.4. Ma trận 2×3 (C1 – C6)
* 2 chiến lược phân đoạn (Điều thô vs Parser v2 micro-chunk) kết hợp với 3 phương thức truy hồi (BM25, Dense, Hybrid RRF).
* Thiết kế giai thừa đối xứng giúp phân tích rõ tác động tương tác giữa cách cắt văn bản và giải thuật truy hồi.

### 3.5. Phương pháp đánh giá LLM-Judge (GPT-4o-mini)
* **Áp dụng:** Đánh giá Citation Accuracy ở GĐ1, GĐ2; Legal Correctness, Condition/Exception Coverage ở GĐ3.
* **Kiểm soát thiên lệch (Bias Control):** Chuẩn hóa rubric chấm nhị phân (0 hoặc 1), kiểm tra JSON schema đầu ra, ghi log 1.024 lượt, retry 3 lần.
* **Điểm tiến bộ ở GĐ3:** Chuyển đổi các chỉ số Citation Precision và Citation Recall (Bảng 3.16) sang hoàn toàn dựa trên quy tắc so khớp chuỗi ký tự (Rule-based), không phụ thuộc vào LLM chấm.

### 3.6. Hiểu đúng về "Isolation of Variables"
* Nhóm **tách biệt tầng sinh câu trả lời** ra khỏi vòng đánh giá ở GĐ2 để đo thuần túy năng lực của bộ truy hồi Retriever, không để hallucination của LLM sinh làm nhiễu.
* Không được tuyên bố "loại bỏ hoàn toàn nhiễu LLM", vì LLM-Judge vẫn dùng GPT-4o-mini nên nhiễu của giám khảo AI vẫn tồn tại.

### 3.7. Bốn loại giá trị thực nghiệm (Validity - Mục 3.9)
1. **Giá trị nội tại (Internal Validity):** Kiểm soát bias của LLM-Judge, rò rỉ từ vựng Jaccard, câu hỏi out-of-index.
2. **Giá trị cấu trúc (Construct Validity):** Phân định rạch ròi giữa phép đo thành phần (In-context) và phép đo toàn trình (End-to-end); ma trận đối xứng 2x3.
3. **Giá trị ngoại tại (External Validity):** 7 đạo luật đại diện cho các quan hệ dân sự phổ biến, nhưng chưa đại diện cho toàn bộ hệ thống pháp luật; kết quả có thể dao động nếu đổi LLM nền.
4. **Giá trị kết luận thống kê (Statistical Validity):** Kiểm định Wilcoxon signed-rank test ($W=526,5; p=9,11 \times 10^{-20}$ cho C5 vs baseline); tập 512 câu là tập cố định có chủ đích nên p-value chỉ dùng bác bỏ giả thuyết không trong tập, không suy rộng xác suất toàn thể.

---

## TẦNG 4: CON SỐ VÀ BẢN CHẤT ĐO LƯỜNG (NUMBERS & MEANINGS)

### 4.1. Phân biệt 3 loại Citation (Tuyệt đối không so sánh chéo)
1. **Citation Accuracy (GĐ1 - Bảng 3.4):** Đo trên câu trả lời sinh ra hoàn chỉnh. Tỷ lệ câu trả lời có trích dẫn đúng số Điều, Khoản trong ground-truth (Naive 32,59%, Hybrid 29,02%, LightRAG 13,71%).
2. **In-context Citation Accuracy (GĐ2 - Bảng 3.6):** Đo trên ngữ cảnh truy hồi. Tỷ lệ phân đoạn nạp vào LLM có chứa đúng căn cứ pháp lý theo đánh giá của LLM-Judge (C5 đạt 0,9902; 504/512 câu đạt điểm tuyệt đối 1,0).
3. **Citation Precision & Recall (GĐ3 - Bảng 3.16):** Đo bằng quy tắc so khớp ký tự trên câu trả lời Benchmark B. Cấp Điều: Precision 0,8369 / Recall 0,9078. Cấp Khoản: Precision 0,7757 / Recall 0,8170. Cấp Điểm: Precision 0,6797 / Recall 0,5517.

### 4.2. Bảng đối soát Giai đoạn 1 (Tier 1 Fair Subset, $N=205$, Bảng 3.3 & 3.4)
| Hệ thống | Recall@5 (Bảng 3.3) | MRR@5 (Bảng 3.3) | Context Precision (Bảng 3.4) | Citation Accuracy (Bảng 3.4) |
|---|:---:|:---:|:---:|:---:|
| **Naive Vector RAG** | 0,9561 | 0,8589 | 0,9659 | 0,3259 |
| **Hybrid RAG** | **0,9659** | **0,9243** | **0,9660** | 0,2902 |
| **LightRAG** | **0,9659** | 0,8687 | 0,8829 | 0,1371 |

### 4.3. Bảng đối soát Giai đoạn 2 (Benchmark A, $N=512$, Bảng 3.5 & 3.6)
| Mã | Cấu hình | Recall@5 | MRR@5 | Citation Accuracy (LLM-Judge) | Token ngữ cảnh |
|---|---|:---:|:---:|:---:|:---:|
| **C1** | Naive BM25 | 0,7051 | 0,5794 | 0,7490 | ~2.500 |
| **C2** | Naive Dense (BGE-M3) | 0,9141 | 0,8129 | 0,4000 | ~2.898 |
| **C3** | Naive Hybrid RRF | 0,9316 | 0,8796 | 0,3986 | ~2.898 |
| **C4** | Parser v2 BM25 + MaxP | 0,7402 | 0,6052 | 0,9028 | ~580 |
| **C5** | **Parser v2 Dense + MaxP** | **0,9316** | **0,8602** | **0,9902** | **~580** |
| **C6** | Parser v2 Hybrid RRF + MaxP | 0,8730 | 0,7615 | 0,9786 | ~580 |
| **C6-0.8**| Weighted RRF (α=0,8) | 0,9297 | 0,8220 | — | ~580 |

### 4.4. Bảng quét trọng số α (Bảng 3.7)
* α = 0,0 (BM25 thuần): Recall 0,7402 | MRR 0,6052.
* α = 0,5 (RRF bằng nhau): Recall 0,8730 | MRR 0,7615 (suy giảm do xung đột thứ hạng).
* α = 0,8 (Cấu hình cân bằng được chọn): Recall **0,9297** | MRR **0,8220**.
* α = 1,0 (Dense thuần - Cao nhất): Recall **0,9316** | MRR **0,8602**.

### 4.5. Bảng đối soát Giai đoạn 3 (Benchmark B, Chương III Luật Đất đai 2024)
| Chỉ số | Mẫu số $N$ | LightRAG | Hybrid UKG | Chênh lệch | Căn cứ Báo cáo |
|---|:---:|:---:|:---:|:---:|---|
| **Recall@5 (Điều)** | 47 | 0,7358 | **0,9184** | **+18,26 đpt** | Bảng 3.9 |
| **MRR@5 (Điều)** | 47 | 0,5539 | **0,8848** | **+33,09 đpt** | Bảng 3.9 |
| **Citation Precision (Điều)** | 47 | 0,3333 | **0,8369** | **+50,36 đpt** | Bảng 3.16 |
| **Citation Recall (Điều)** | 47 | 0,2961 | **0,9078** | **+61,17 đpt** | Bảng 3.16 |
| **Citation Precision (Khoản)**| 46 | 0,0435 | **0,7757** | **+73,22 đpt** | Bảng 3.16 |
| **Citation Recall (Khoản)** | 46 | 0,0435 | **0,8170** | **+77,35 đpt** | Bảng 3.16 |
| **Citation Precision (Điểm)** | 37 | 0,0270 | **0,6797** | **+65,27 đpt** | Bảng 3.16 |
| **Legal Correctness** | 50 | 0,8210 | **0,8777** | **+5,67 đpt** | Bảng 3.15 |
| **Exception Coverage** | 14 | 0,3929 | **0,6786** | **+28,57 đpt** | Bảng 3.15 |
| **Subject-Scope Accuracy** | 18 | 0,7639 | **0,8889** | **+12,50 đpt** | Bảng 3.15 |
| **Atomic Fact Coverage** | 47 | 0,8551 | **0,8686** | **+1,35 đpt** | Bảng 3.15 |
| **Condition Coverage** | 19 | **0,8421** | 0,7066 | **−13,55 đpt** | Bảng 3.15 (UKG thấp hơn) |
| **Exact Locator Recall@5** | 39 vs 47 | **0,8509** | 0,5560* | **−29,49 đpt** | Bảng 3.11 (*39/47 câu đo được; Độ hạt)* |
| **Chain Exact Match** | 18 | N/A | **0,0000** | Ranh giới | Bảng 3.14 (Reference-target 58,67%) |

---

## TẦNG 5: GIỚI HẠN VÀ ĐÁNH ĐỔI KỸ THUẬT (BOUNDARIES & TRADE-OFFS)

### 5.1. Phân định rõ: Đánh đổi có chủ đích vs Hạn chế thực sự
* **Đánh đổi có chủ đích (Intentional Engineering Trade-offs):**
  - *Micro-chunk vs Chunk lớn:* Chọn micro-chunk để đạt Citation Precision Khoản 77,57% và tiết kiệm 80% token, chấp nhận giảm Exact Locator bao trùm diện rộng.
  - *MaxP vs Mean-pooling:* Chọn MaxP để bảo toàn tín hiệu của Khoản quan trọng, chấp nhận không phản ánh điểm số trung bình của toàn bộ Điều.
  - *Physical Graph tất định:* Dùng regex cứng thay vì LLM trích xuất để bảo đảm cấu trúc không bao giờ bị ảo giác.
* **Hạn chế thực sự (Genuine Research Boundaries):**
  - Chưa ablation từng thành phần trong gói Parser v2.
  - Condition Coverage thấp hơn LightRAG do thiếu cơ chế lan truyền điều kiện.
  - Chain Exact Match = 0 trên 18 câu do chưa có giải thuật duyệt đồ thị có ràng buộc.
  - Chưa thử nghiệm trên tài liệu quét OCR nhiễu cao.

### 5.2. Mẫu câu phát biểu chuẩn mực về hạn chế
> *"Dạ thưa Quý Thầy Cô, đây chính là hạn chế kỹ thuật mà nhóm đã ghi nhận tường minh tại Mục 3.9 của báo cáo. Cơ chế giải thích là [...]. Nhóm xác định đây là bài toán trọng tâm và đã đề xuất lộ trình giải quyết bằng giải thuật [...] trong giai đoạn nghiên cứu tiếp theo."*

---
"""

with open(md_path, 'w', encoding='utf-8') as f:
    f.write(p1)

print("[+] Successfully wrote Part 1.")
