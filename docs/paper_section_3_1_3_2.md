# CHƯƠNG 3: THỰC NGHIỆM, KẾT QUẢ VÀ THẢO LUẬN

## 3.1. Thiết lập thực nghiệm

Nhằm bảo đảm tính khách quan, khả năng tái lập và kiểm soát chặt chẽ các biến độc lập, toàn bộ các phiên thực nghiệm trong đề tài được thực hiện trên môi trường tính toán chuẩn hóa với các thông số kỹ thuật được đóng băng cố định [9].

---

### 3.1.1. Môi trường tính toán phần cứng và phần mềm

Toàn bộ các chu trình lập chỉ mục vector, tính toán ma trận tương đồng Cosine song song và điều phối truy vấn được thực thi trên hạ tầng máy chủ ảo hóa với card đồ họa chuyên dụng [4]. Các thông số phần cứng và phiên bản thư viện cốt lõi được quy định tại Bảng 3.1a:

**Bảng 3.1a. Đặc tả môi trường phần cứng và nền tảng phần mềm thực nghiệm**

| Thành phần Hệ thống | Đặc tả Kỹ thuật Chi tiết | Vai trò trong Nghiên cứu |
| :--- | :--- | :--- |
| **Bộ xử lý đồ họa (GPU)** | NVIDIA Tesla T4 (2.560 nhân CUDA, 320 nhân Tensor) [4] | Tính toán song song nhúng vector BGE-M3 và truy hồi FAISS |
| **Dung lượng VRAM** | 14.56 GB GDDR6 khả dụng (16 GB vật lý) | Tải toàn bộ ma trận vector ngữ liệu vào bộ nhớ GPU |
| **Bộ vi xử lý trung tâm (CPU)** | Intel Xeon @ 2.20 GHz (4 vCPUs) | Xử lý bóc tách cấu trúc regex và lập chỉ mục nghịch đảo BM25 |
| **Bộ nhớ hệ thống (RAM)** | 32 GB DDR4 ECC | Lưu trữ dữ liệu ngữ liệu và cache trung gian |
| **Hệ điều hành & Driver** | Linux Ubuntu 22.04 LTS (Kernel 6.1), CUDA 12.2 | Môi trường vận hành chuẩn hóa trên máy ảo Kaggle |
| **Thư viện Deep Learning** | PyTorch 2.1.2+cu121, Transformers 4.38, FlagEmbedding [1] | Nạp và thực thi các mô hình Bi-Encoder và Cross-Encoder |
| **Thư viện NLP & Tìm kiếm** | `faiss-gpu` 1.7.4 [4], `rank-bm25` 0.2.2 [2], `pyvi` 0.1.1 [12] | Lập chỉ mục không gian vector và tìm kiếm từ vựng tiếng Việt |
| **Mô hình Ngôn ngữ Lớn** | `openai/gpt-4o-mini` qua giao thức OpenRouter API [10] | Sinh câu trả lời pháp lý và thực thi vai trò LLM Judge |

---

### 3.1.2. Thống kê tập ngữ liệu và bộ câu hỏi kiểm thử

Nghiên cứu sử dụng kho ngữ liệu văn bản quy phạm pháp luật quốc gia và bộ câu hỏi kiểm thử chuẩn hóa Benchmark A:

* **Kho ngữ liệu nền (Corpus):** Bao gồm **2.087 Điều luật toàn văn** được thu thập từ Cơ sở dữ liệu quốc gia về văn bản pháp luật, bao quát 6 đạo luật trụ cột: Bộ luật Dân sự 2015 (689 Điều), Bộ luật Hình sự 2015/2017 (426 Điều), Bộ luật Tố tụng Hình sự 2015 (510 Điều), Bộ luật Lao động 2019 (220 Điều), Luật Hôn nhân và Gia đình 2014 (133 Điều) và Chương III Luật Đất đai 2024. Toàn bộ dữ liệu được chuẩn hóa bảng mã Unicode dựng sẵn (NFC) và định dạng đề mục theo quy chuẩn lập pháp.
* **Tập kiểm thử toàn diện Benchmark A (512 câu hỏi):** Tập câu hỏi (`benchmark_rewritten.json`) được phân tầng theo bốn nhóm độ phức tạp nghiệp vụ luật học:
  1. *Nhóm tra cứu sự kiện trực tiếp (`clean-factoid`):* 307 câu (chiếm 59.96%), yêu cầu xác định các quy định tường minh về điều kiện, thời hạn hoặc chế tài cụ thể.
  2. *Nhóm có điều kiện và ngoại lệ (`conditional`):* 123 câu (chiếm 24.02%), chứa các tình huống pháp lý phức tạp có yếu tố loại trừ hoặc điều kiện tiên quyết.
  3. *Nhóm suy luận đa bước (`multi-hop`):* 67 câu (chiếm 13.09%), đòi hỏi phải liên kết nhiều điều luật khác nhau hoặc giải quyết các quan hệ dẫn chiếu chéo.
  4. *Nhóm câu hỏi ngoài phạm vi (`negative`):* 15 câu (chiếm 2.93%), kiểm tra năng lực từ chối trả lời của hệ thống nhằm chống ảo giác pháp lý.
* **Tập đối chuẩn công bằng (Tier 1 Fair Subset — 205 câu hỏi):** Nhằm đối soát công bằng với LightRAG [5] trong điều kiện nguồn lực API bị giới hạn, phân vùng này bao gồm đúng 205 câu hỏi mà 100% căn cứ pháp lý cần thiết nằm trọn vẹn trong 500 Điều luật đã được nạp vào chỉ mục đồ thị của LightRAG.

---

### 3.1.3. Cấu hình siêu tham số đóng băng của ba pipeline cơ sở

Nhằm triệt tiêu các yếu tố gây nhiễu từ việc tinh chỉnh tham số tùy tiện, các siêu tham số vận hành của ba hệ thống trong Giai đoạn 1 được đóng băng cố định theo Bảng 3.1b:

**Bảng 3.1b. Cấu hình siêu tham số đóng băng của ba pipeline cơ sở**

| Siêu tham số | Giá trị Thiết lập | Ý nghĩa Kỹ thuật và Phạm vi Áp dụng |
| :--- | :---: | :--- |
| **Kích thước cửa sổ Top-$k$** | $k = 5$ | Số lượng Điều luật tối đa được trích xuất làm ngữ cảnh gửi sang LLM |
| **Ứng viên trước dung hợp ($N$)** | $N = 50$ | Số lượng tài liệu trích xuất từ mỗi nhánh BM25 [2] và Dense [1] trước khi RRF |
| **Hệ số làm mịn RRF ($k_{\text{rrf}}$)** | $60$ | Tham số làm mịn thứ bậc chuẩn tắc của giải thuật Cormack RRF [3] |
| **Mô hình nhúng dense** | `BAAI/bge-m3` [1] | Vector hóa câu hỏi và văn bản điều luật (1024 chiều, chuẩn hóa $L_2$) |
| **Mô hình tái xếp hạng** | `bge-reranker-v2-m3` [1] | Tính toán điểm tương tác chéo cho Top-50 ứng viên sau RRF |
| **Nhiệt độ tạo sinh ($\text{temperature}$)** | $0.0$ | Thiết lập tất định nhằm triệt tiêu tính bất định ngẫu nhiên của LLM |
| **Giới hạn token tạo sinh** | $1.024$ tokens | Độ dài tối đa cho văn bản câu trả lời giải thích pháp lý |

---

### 3.1.4. Hệ thống chỉ số đo lường và phương pháp kiểm định thống kê

Hiệu năng của các hệ thống được đánh giá đồng thời trên hai tầng:
1. **Tầng truy hồi thông tin (Information Retrieval Metrics):**
   * *Recall@5:* Tỷ lệ số điều luật đúng trong Ground Truth ($GT$) xuất hiện trong danh sách $Top\text{-}5$ tài liệu được truy xuất:
     $$\text{Recall@5} = \frac{|Retrieved_{Top-5} \cap GT|}{|GT|}$$
   * *Mean Reciprocal Rank (MRR@5):* Đo lường thứ vị của tài liệu đúng đầu tiên xuất hiện trong danh sách kết quả (bằng $1/\text{rank}$ nếu nằm trong Top-5, và bằng $0$ nếu trượt):
     $$\text{MRR@5} = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{\text{rank}_i}$$
2. **Tầng chất lượng tạo sinh và căn cứ pháp lý (LLM-as-a-Judge Metrics) [10]:**
   Được thẩm định độc lập thông qua mô hình giám khảo `openai/gpt-4o-mini` theo ba tiêu chí chuẩn hóa (thang điểm $0.0$ đến $1.0$) [11]:
   * *Context Precision:* Đo lường tỷ lệ các tài liệu truy xuất thực sự chứa căn cứ pháp lý giải quyết câu hỏi [11].
   * *Faithfulness:* Đánh giá tính trung thực, bảo đảm câu trả lời hoàn toàn dựa trên ngữ cảnh được cung cấp, không bịa đặt thông tin [11].
   * *Citation Accuracy:* Đánh giá mức độ chuẩn xác của các trích dẫn pháp lý (số hiệu Điều, Khoản, Điểm) xuất hiện trong câu trả lời so với nguồn luật gốc.
3. **Phương pháp kiểm định thống kê:**
   Để xác thực các chênh lệch hiệu năng không phải do ngẫu nhiên, nghiên cứu áp dụng đồng thời phép kiểm định phi tham số **Wilcoxon signed-rank test** (phù hợp với phân bố điểm phi chuẩn của dữ liệu truy hồi) và kiểm định **Paired Student's t-test** trên các cặp câu hỏi đối ứng ($N = 512$), với ngưỡng ý nghĩa thống kê chuẩn $\alpha = 0.05$.

---

## 3.2. Giai đoạn 1 — Đánh giá ba kiến trúc RAG cơ sở

Giai đoạn 1 tiến hành đối soát thực nghiệm giữa ba kiến trúc đại diện cho ba trường phái: Naive Vector RAG, Hybrid RAG và LightRAG trên tập kiểm thử Benchmark A.

---

### 3.2.1. Hiệu năng truy hồi của Naive Vector và Hybrid RAG

Kết quả đo kiểm hiệu năng truy hồi trên toàn bộ 512 câu hỏi được tổng hợp tại Bảng 3.2a:

**Bảng 3.2a. Đối soát hiệu năng truy hồi trên toàn bộ 512 câu hỏi (Benchmark A)**

| Cấu hình Hệ thống | Phương thức Truy xuất Cốt lõi | Recall@5 | MRR@5 | Tổng Ngữ cảnh Top-5 nạp LLM |
| :--- | :--- | :---: | :---: | :---: |
| **BM25 Độc lập (PyVi)** | Từ khóa Okapi BM25 thuần túy [2, 12] | 0.7051 | 0.5794 | ~2.500 tokens |
| **Naive Vector RAG** | Dense Embedding (`BAAI/bge-m3`) [1] | 0.9141 | 0.8129 | ~2.898 tokens |
| **Hybrid RAG** | Dung hợp BM25 + Dense + RRF + Cross-Encoder [1, 2, 3] | **0.9316** | **0.8796** | **~2.898 tokens** |
| **LightRAG (Toàn bộ)** | Đồ thị phi cấu trúc (Index phủ ~500 điều) [5] | 0.3867\* | 0.3478\* | — |

*\*Ghi chú: Điểm số của LightRAG được đo kiểm qua phép kiểm định truy hồi hậu kiểm (Verified Approximate Retrieval) dựa trên ma trận nhúng của 519 chunks đồ thị, phản ánh trạng thái giới hạn khi index chưa phủ toàn bộ 2.087 điều luật.*

Từ Bảng 3.2a, các phát hiện thực nghiệm quan trọng được xác lập:
* **Sức mạnh vượt trội của ngữ nghĩa dày (Dense vs BM25):** Naive Vector RAG đạt Recall@5 = 0.9141, vượt trội kênh từ vựng cơ sở BM25 (0.7051) tới **+20.9 điểm phần trăm**. Điều này chứng minh rằng trong ngôn ngữ luật học tiếng Việt, việc diễn đạt lại câu hỏi bằng từ ngữ đời thường khiến tìm kiếm từ khóa thô bị trượt rất nặng, trong khi mô hình nhúng BGE-M3 [1] nắm bắt ngữ nghĩa khái niệm xuất sắc.
* **Lợi thế của kiến trúc Hybrid RAG:** Khi kết hợp cả hai nhánh và áp dụng Cross-Encoder reranker [1], Hybrid RAG nâng Recall@5 lên **0.9316** (+1.75 điểm phần trăm) và đưa MRR@5 tăng vọt từ 0.8129 lên **0.8796** (+6.67 điểm phần trăm, tương đương mức tăng tương đối +8.2%).
* **Kiểm định thống kê:** Kiểm định Wilcoxon signed-rank test xác nhận sự cải thiện về thứ bậc của MRR@5 giữa Hybrid RAG và Naive Vector RAG có ý nghĩa thống kê rất cao ($W = 1.245,0, p = 3.12 \times 10^{-6} < 0.001$). Điều này chỉ ra rằng giá trị cốt lõi của tầng Cross-Encoder không chỉ là kéo thêm tài liệu mới vào Top-5, mà là đẩy mạnh các điều luật đúng lên thẳng vị trí số 1 (Rank 1).

---

### 3.2.2. Kết quả đánh giá LightRAG và Phép kiểm định Hậu kiểm

Do thư viện LightRAG [5] nguyên bản không xuất danh sách định danh tài liệu (`article_id`) trong luồng trả lời mặc định, nhóm nghiên cứu đã xây dựng công cụ trích xuất ma trận vector nội bộ (`lightrag_vdb_matrix.npy`, gồm 519 vector) và bảng ánh xạ chunk-to-article (`lightrag_chunk_to_article_id.json`) để thực hiện phép kiểm định hậu kiểm khách quan:

1. **Trên toàn bộ 512 câu hỏi:** Do chỉ mục đồ thị của LightRAG mới phủ được khoảng 500/2.087 Điều luật (chi phí API giới hạn), hệ thống chỉ đạt Recall@5 = 0.3867 và MRR@5 = 0.3478. Trong đó, có tới 307 câu hỏi có căn cứ pháp lý nằm ngoài phạm vi 500 điều luật này.
2. **Trên Tập đối chuẩn công bằng (Tier 1 Fair Subset — 205 câu hỏi):** Khi loại trừ hoàn toàn các câu hỏi ngoài chỉ mục và chỉ đo kiểm trên 205 câu mà 100% tài liệu đúng đã nằm trong đồ thị của LightRAG, hiệu năng của hệ thống tăng lên rõ rệt: **Recall@5 đạt 0.7358** và **MRR@5 đạt 0.6542**.
3. **Nhận định kỹ thuật:** Mặc dù trên phân vùng công bằng LightRAG đã thể hiện năng lực kết nối đồ thị, mức Recall@5 (0.7358) vẫn thấp hơn đáng kể so với Naive Vector RAG (0.9141) và Hybrid RAG (0.9316). Nguyên nhân bắt nguồn từ hiện tượng **Pha loãng Đồ thị (Graph Dilution)**: cơ chế trích xuất thực thể tự do không có ràng buộc luật học [6] đã phân mảnh văn bản pháp lý thành hàng nghìn node thực thể nhỏ lẻ, làm mất đi tính toàn vẹn của một điều khoản quy phạm.

---

### 3.2.3. Chất lượng câu trả lời và Phát hiện Bước ngoặt: Hiện tượng Sụp đổ Trích dẫn (Citation Collapse)

Bảng 3.2b trình bày kết quả đánh giá chất lượng câu trả lời do mô hình ngôn ngữ lớn `openai/gpt-4o-mini` sinh ra dưới sự thẩm định của LLM Judge độc lập [10]:

**Bảng 3.2b. Đánh giá chất lượng tạo sinh và căn cứ pháp lý trên 512 câu hỏi**

| Cấu hình Hệ thống | Context Precision [11] | Faithfulness [11] | Citation Accuracy | Nhận xét Chất lượng Tạo sinh |
| :--- | :---: | :---: | :---: | :--- |
| **Naive Vector RAG** | 0.9396 | 0.9238 | **0.4000** | Trích dẫn sụp đổ do ngợp ngữ cảnh văn bản thô [7] |
| **Hybrid RAG** | **0.9547** | **0.9268** | **0.3986** | Context sạch hơn nhưng trích dẫn vẫn sụp đổ [7] |
| **LightRAG Verified** | 0.4004 | 0.4164 | 0.1129 | Bị ảnh hưởng bởi chỉ mục đồ thị chưa toàn diện [5] |

Từ Bảng 3.2b, một phát hiện học thuật mang tính **bước ngoặt phương pháp luận** của toàn bộ đề tài đã được phơi bày:

* **Nghịch lý giữa Độ trung thực và Độ chính xác Trích dẫn:** Cả Naive Vector RAG và Hybrid RAG đều đạt điểm số Context Precision (0.9396 – 0.9547) và Faithfulness (0.9238 – 0.9268) rất cao. Điều này chứng minh LLM hiểu đúng ngữ cảnh và trả lời rất trung thực với thông tin được cấp [11].
* **Hiện tượng Sụp đổ Trích dẫn (Citation Collapse):** Trái ngược hoàn toàn với độ trung thực, chỉ số **Citation Accuracy của cả hai hệ thống đều sụp đổ nghiêm trọng, chỉ đạt mức ~0.3986 – 0.4000 (tức là khoảng 60% số câu hỏi bị trích dẫn sai hoặc không thể chỉ ra căn cứ điều khoản cụ thể)**. Đáng chú ý, dù Hybrid RAG vượt trội Vector RAG ở tầng truy hồi, điểm Citation của Hybrid RAG (0.3986) thậm chí không hề cải thiện so với Vector RAG (0.4000).

---

### 3.2.4. Phân tích nguyên nhân kỹ thuật và các dạng lỗi điển hình

Phân tích sâu các bản ghi lỗi thực nghiệm chỉ ra hai cơ chế kỹ thuật cốt lõi dẫn đến hiện tượng sụp đổ trích dẫn:

1. **Hiệu ứng Ngợp ngữ cảnh dài (Context Flooding) và Lãng quên ở giữa (Lost in the Middle) [7]:**  
   Do cả Naive Vector và Hybrid RAG đều nạp toàn bộ khối văn bản của 5 Điều luật thô vào prompt, độ dài ngữ cảnh trung bình gửi sang LLM lên tới **~2.898 tokens**. Trong các điều luật dài có cấu trúc phức tạp (chẳng hạn Điều 357 BLDS hoặc các điều luật hình sự có hàng chục khoản), thông tin mấu chốt để trả lời câu hỏi thường chỉ nằm ở một hoặc hai dòng của một Điểm hẹp. Khi bị bao vây bởi hàng nghìn token văn bản quy phạm khác, cơ chế chú ý (Attention) của LLM bị phân tán [7], dẫn đến việc mô hình trả lời đúng nội dung nhưng "quên" không trích dẫn hoặc trích dẫn chung chung cấp Điều mà không chỉ rõ Khoản/Điểm.
2. **Hiện tượng Mồ côi Ngữ cảnh (Context Orphanage):**  
   Văn bản thô của Naive RAG hoàn toàn không có các thẻ metadata cấu trúc dạng `[Luật > Điều > Khoản > Điểm]`. Khi LLM phải tự bóc tách văn bản, nó thường xuyên mắc lỗi "ảo giác toạ độ" (Hallucinated Coordinates): ghép nội dung của Khoản 2 Điều này vào tiêu đề của Điều khác, hoặc tự suy diễn số hiệu khoản không có thực trong văn bản luật.
3. **Bế tắc trước câu hỏi dẫn chiếu chéo (Multi-hop Blindness):**  
   Đối với các câu hỏi đòi hỏi phải đọc qua điều khoản dẫn chiếu (ví dụ: Điều 113 dẫn chiếu sang Điều 115 Bộ luật Lao động), cả Vector RAG và Hybrid RAG đều bất lực nếu điều khoản dẫn chiếu không chứa từ khóa trùng khớp với câu hỏi. Ngữ cảnh trả về bị khuyết thiếu một nửa căn cứ, khiến câu trả lời bị cụt và trích dẫn thiếu sót.

---

### 3.2.5. Kết luận Giai đoạn 1 và Động lực Chuyển giao Phương pháp luận

Tổng kết Giai đoạn 1 cho phép nghiên cứu rút ra kết luận khoa học có giá trị then chốt:

> **Kết luận then chốt:** *Việc tối ưu hóa thuật toán truy hồi ở cấp độ khối văn bản thô (chuyển đổi từ Bi-Encoder sang Hybrid RRF kết hợp Cross-Encoder) [1, 3] đã chạm đến ngưỡng giới hạn trần: nó chỉ giúp cải thiện nhẹ tỷ lệ tìm thấy tài liệu (+1.75 pp Recall@5) nhưng hoàn toàn bất lực trong việc giải quyết hiện tượng Sụp đổ Trích dẫn (Citation Collapse) và Lãng phí Tài nguyên Ngữ cảnh (~2.898 tokens) [7].*

Phát hiện này xác lập cơ sở lý luận vững chắc bác bỏ quan điểm cho rằng *"chỉ cần mô hình embedding mạnh hơn hoặc thêm reranker là đủ cho RAG pháp lý"*. Nó tạo thành **động lực học thuật tiên quyết** thúc đẩy đề tài triển khai hai bước đột phá kiến trúc tiếp theo:
* **Chuyển giao sang Giai đoạn 2 (Mục 3.3):** Xây dựng **Bộ phân giải cấu trúc phân cấp (Structure-Aware Regex Parser v2)** kết hợp cơ chế gom điểm cực đại **Article-level MaxP** [8] nhằm triệt tiêu hiện tượng mồ côi điều khoản, thu gọn ngữ cảnh xuống ~580 tokens và nâng Citation Accuracy lên đỉnh cao thực nghiệm.
* **Chuyển giao sang Giai đoạn 3 (Mục 3.4):** Xây dựng **Kiến trúc Đồ thị Tri thức Hợp nhất (Hybrid Parser/UKG 10 module)** nhằm giải quyết dứt điểm bài toán suy luận đa bước, xung đột quan hệ và bẫy ngoại lệ trên bộ dữ liệu chuyên sâu Benchmark B.

---

### TÀI LIỆU THAM KHẢO TRÍCH NGUỒN (REFERENCES)

* **[1]** Chen, J., Xiao, S., Zhang, P., Luo, K., Lian, D., & Liu, Z. (2024). *BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation*. arXiv preprint arXiv:2402.03216. [https://arxiv.org/abs/2402.03216](https://arxiv.org/abs/2402.03216)
* **[2]** Robertson, S., & Zaragoza, H. (2009). *The Probabilistic Relevance Framework: BM25 and Beyond*. Foundations and Trends in Information Retrieval, 3(4), 333-389. DOI: 10.1561/1500000019. [https://doi.org/10.1561/1500000019](https://doi.org/10.1561/1500000019)
* **[3]** Cormack, G. V., Clarke, C. L., & Buettcher, S. (2009). *Reciprocal rank fusion outperforms Condorcet and individual rank learning methods*. In Proceedings of the 32nd international ACM SIGIR conference on Research and development in information retrieval (SIGIR '09), 758-759. DOI: 10.1145/1571941.1572114. [https://doi.org/10.1145/1571941.1572114](https://doi.org/10.1145/1571941.1572114)
* **[4]** Johnson, J., Douze, M., & Jégou, H. (2019). *Billion-scale similarity search with GPUs*. IEEE Transactions on Big Data, 7(3), 535-547. DOI: 10.1109/TBDATA.2019.2921572. [https://doi.org/10.1109/TBDATA.2019.2921572](https://doi.org/10.1109/TBDATA.2019.2921572)
* **[5]** Guo, Z., Zhuang, Y., Dong, L., et al. (2024). *LightRAG: Simple and Fast Retrieval-Augmented Generation*. arXiv preprint arXiv:2410.05779. [https://arxiv.org/abs/2410.05779](https://arxiv.org/abs/2410.05779)
* **[6]** Edge, D., Trinh, H., Cheng, N., et al. (2024). *From Local to Global: A Graph RAG Approach to Query-Focused Summarization*. arXiv preprint arXiv:2404.16130. [https://arxiv.org/abs/2404.16130](https://arxiv.org/abs/2404.16130)
* **[7]** Liu, N. F., Lin, K., Hewitt, J., Paranjape, A., Bevilacqua, M., Petroni, F., & Liang, P. (2024). *Lost in the Middle: How Language Models Use Long Contexts*. Transactions of the Association for Computational Linguistics (TACL), 12, 157-173. DOI: 10.1162/tacl_a_00638. [https://doi.org/10.1162/tacl_a_00638](https://doi.org/10.1162/tacl_a_00638)
* **[8]** Dai, Z., & Callan, J. (2019). *Deeper Text Understanding for IR with Contextual Neural Language Modeling*. In Proceedings of the 42nd International ACM SIGIR Conference on Research and Development in Information Retrieval (SIGIR '19), 385-394. DOI: 10.1145/3331184.3331202. [https://doi.org/10.1145/3331184.3331202](https://doi.org/10.1145/3331184.3331202)
* **[9]** Lewis, P., Perez, E., Piktus, A., et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. In Advances in Neural Information Processing Systems (NeurIPS 2020), 33, 9459-9474. [https://arxiv.org/abs/2005.11401](https://arxiv.org/abs/2005.11401)
* **[10]** Zheng, L., Chiang, W. L., Sheng, Y., et al. (2024). *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*. In Advances in Neural Information Processing Systems (NeurIPS 2023), 36. [https://arxiv.org/abs/2306.05685](https://arxiv.org/abs/2306.05685)
* **[11]** Es, S., James, J., Espinosa-Anke, L., & Schockaert, S. (2024). *Ragas: Automated Evaluation of Retrieval Augmented Generation*. In Proceedings of EACL 2024: System Demonstrations, 150-158. [https://arxiv.org/abs/2309.15217](https://arxiv.org/abs/2309.15217)
* **[12]** Nguyen, T. (2016). *PyVi: Python Vietnamese Core NLP Toolkit*. GitHub repository. [https://github.com/trungtv/pyvi](https://github.com/trungtv/pyvi)
* **[13]** Wu, S., & Crestani, F. (2015). *Data Fusion in Information Retrieval*. The Information Retrieval Series, vol 33. Springer, Berlin, Heidelberg. DOI: 10.1007/978-3-662-48092-2. [https://doi.org/10.1007/978-3-662-48092-2](https://doi.org/10.1007/978-3-662-48092-2)
* **[14]** Wohlin, C., Runeson, P., Höst, M., Ohlsson, M. C., Regnell, B., & Wesslén, A. (2012). *Experimentation in Software Engineering*. Springer Science & Business Media. DOI: 10.1007/978-3-642-29044-2. [https://doi.org/10.1007/978-3-642-29044-2](https://doi.org/10.1007/978-3-642-29044-2)
* **[15]** Karpukhin, V., Oğuz, B., Min, S., et al. (2020). *Dense Passage Retrieval for Open-Domain Question Answering*. In Proceedings of EMNLP 2020, 6769-6781. [https://arxiv.org/abs/2004.04906](https://arxiv.org/abs/2004.04906)
* **[16]** Nogueira, R., & Cho, K. (2019). *Passage Re-ranking with BERT*. arXiv preprint arXiv:1901.04085. [https://arxiv.org/abs/1901.04085](https://arxiv.org/abs/1901.04085)
* **[17]** Chalkidis, I., Fergadiotis, M., Malakasiotis, P., et al. (2020). *LEGAL-BERT: The Muppets straight out of Law School*. In Findings of the Association for Computational Linguistics: EMNLP 2020, 2898-2904. [https://arxiv.org/abs/2010.02559](https://arxiv.org/abs/2010.02559)
* **[18]** Gao, T., Yen, H., Yu, J., & Chen, D. (2023). *Enabling Large Language Models to Generate Text with Citations*. In Proceedings of EMNLP 2023, 6465-6488. [https://arxiv.org/abs/2305.14627](https://arxiv.org/abs/2305.14627)
* **[19]** Huang, L., Yu, W., Ma, W., et al. (2023). *A Survey on Hallucination in Large Language Models: Principles, Taxonomy, Challenges, and Open Questions*. ACM Computing Surveys. DOI: 10.1145/3600211. [https://doi.org/10.1145/3600211](https://doi.org/10.1145/3600211)
* **[20]** Hogan, A., Blomqvist, E., Cochez, M., et al. (2021). *Knowledge Graphs*. ACM Computing Surveys (CSUR), 54(4), 1-37. DOI: 10.1145/3447772. [https://doi.org/10.1145/3447772](https://doi.org/10.1145/3447772)
* **[21]** Zhong, H., Xiao, C., Tu, C., et al. (2020). *How Does NLP Benefit Legal System: A Summary of Legal Artificial Intelligence*. In Proceedings of ACL 2020, 5218-5230. [https://arxiv.org/abs/2004.12158](https://arxiv.org/abs/2004.12158)
* **[22]** Nguyen, H. T., Tran, V., et al. (2021). *Overview of the Automated Legal Question Answering Challenge (ALQAC 2021)*. In Forum for Information Retrieval Evaluation (FIRE 2021). [https://ceur-ws.org/Vol-3158/](https://ceur-ws.org/Vol-3158/)
* **[23]** Wilcoxon, F. (1945). *Individual Comparisons by Ranking Methods*. Biometrics Bulletin, 1(6), 80-83. DOI: 10.2307/3001968. [https://doi.org/10.2307/3001968](https://doi.org/10.2307/3001968)
* **[24]** Manning, C. D., Raghavan, P., & Schütze, H. (2008). *Introduction to Information Retrieval*. Cambridge University Press. DOI: 10.1017/CBO9780511809071. [https://nlp.stanford.edu/IR-book/](https://nlp.stanford.edu/IR-book/)
* **[25]** Brown, T., Mann, B., Ryder, N., et al. (2020). *Language Models are Few-Shot Learners*. In Advances in Neural Information Processing Systems (NeurIPS 2020), 33, 1877-1901. [https://arxiv.org/abs/2005.14165](https://arxiv.org/abs/2005.14165)
* **[26]** Wei, J., Wang, X., Schuurmans, D., et al. (2022). *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models*. In Advances in Neural Information Processing Systems (NeurIPS 2022), 35. [https://arxiv.org/abs/2201.11903](https://arxiv.org/abs/2201.11903)
* **[27]** Formal, T., Lassance, C., Piwowarski, B., & Clinchant, S. (2021). *SPLADE v2: Sparse Lexical and Expansion Model for Information Retrieval*. arXiv preprint arXiv:2109.10086. [https://arxiv.org/abs/2109.10086](https://arxiv.org/abs/2109.10086)
* **[28]** Kuzi, S., Shtok, A., & Kurland, O. (2020). *Leveraging Semantic and Lexical Matching to Improve Diversity in Information Retrieval*. In Proceedings of the 43rd International ACM SIGIR Conference (SIGIR '20), 2029-2032. DOI: 10.1145/3397271.3401243. [https://doi.org/10.1145/3397271.3401243](https://doi.org/10.1145/3397271.3401243)
* **[29]** Casellas, N. (2011). *Legal Ontology Engineering: Methodologies, Modelling Trends, and the Ontology of Professional Judicial Knowledge*. Law, Governance and Technology Series, Vol. 3, Springer. DOI: 10.1007/978-94-007-1479-3. [https://doi.org/10.1007/978-94-007-1479-3](https://doi.org/10.1007/978-94-007-1479-3)
* **[30]** Gao, L., & Callan, J. (2021). *Condenser: a Pre-training Architecture for Dense Retrieval*. In Proceedings of EMNLP 2021, 981-993. [https://arxiv.org/abs/2104.08836](https://arxiv.org/abs/2104.08836)


