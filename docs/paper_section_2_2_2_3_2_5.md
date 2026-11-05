# CHƯƠNG 2: THIẾT KẾ HỆ THỐNG VÀ PHƯƠNG PHÁP NGHIÊN CỨU

## 2.2. Kiến trúc Benchmark Harness

### 2.2.1. Kiến trúc Adapter Pattern và cơ chế trừu tượng hóa pipeline
Nhằm thiết lập một môi trường đối soát thực nghiệm khách quan giữa các kiến trúc RAG có nguyên lý vận hành khác biệt, nghiên cứu xây dựng khung kiểm thử Benchmark Harness dựa trên mẫu thiết kế Adapter Pattern. Khung kiểm thử đóng vai trò là một lớp trừu tượng hóa trung gian (Abstraction Layer), cho phép tách rời hoàn toàn giữa bộ điều phối đánh giá (Evaluation Orchestrator) với các thành phần thực thi nội bộ của từng mô hình (như chỉ mục BM25, đồ thị LightRAG hay bộ phân tích cấu trúc Parser).

Mọi hệ thống RAG tham gia đánh giá bắt buộc phải kế thừa lớp giao diện cơ sở `BaseRAGAdapter` và hiện thực hóa ba phương thức chuẩn tắc:
1. `index(documents)`: Tiếp nhận kho ngữ liệu đã chuẩn hóa và tiến hành xây dựng chỉ mục tìm kiếm tương ứng.
2. `retrieve(query, top_k)`: Tiếp nhận câu hỏi dạng ngôn ngữ tự nhiên và trả về danh sách $k$ tài liệu liên quan nhất kèm điểm số và thứ hạng.
3. `generate(query, retrieved_docs)`: Nhận câu hỏi và ngữ cảnh đã truy xuất để tổng hợp câu trả lời cuối cùng thông qua mô hình ngôn ngữ lớn (LLM).

Thiết kế này bảo đảm nguyên tắc kiểm soát biến độc lập: mọi hệ thống đều nhận cùng một tập dữ liệu đầu vào và chịu sự giám sát của cùng một bộ đo lường độc lập.

### 2.2.2. Chuẩn hóa giao diện hệ thống truy xuất
Giao diện `RAGSystem` chuẩn hóa luồng dữ liệu trao đổi giữa các tầng xử lý. Khi một truy vấn được kích hoạt, hệ thống tự động ghi nhận các mốc thời gian thực thi (timestamps) tại từng bước: thời gian tiền xử lý truy vấn, thời gian truy xuất vector hoặc từ khóa, thời gian dung hợp thứ hạng và thời gian sinh văn bản. Mọi dữ liệu trung gian đều được bảo toàn để phục vụ công tác phân tích lỗi (Error Analysis).

### 2.2.3. Chuẩn hóa dữ liệu bằng lược đồ Pydantic Schema
Để ngăn chặn hiện tượng sai lệch kiểu dữ liệu hoặc mất mát thông tin phân cấp trong quá trình chuyển đổi giữa các module, hệ thống áp dụng cơ chế xác thực dữ liệu tĩnh nghiêm ngặt thông qua thư viện Pydantic:
* `DocumentChunkSchema`: Định nghĩa cấu trúc của một đơn vị văn bản trong cơ sở dữ liệu, bao gồm các trường bắt buộc: `doc_id` (mã định danh duy nhất), `law_id` (mã văn bản luật), `article_id` (số hiệu điều luật), `clause_id` (số thứ tự khoản), `point_id` (ký hiệu điểm), `text` (nội dung nguyên văn), `context_prefix` (tiền tố phân cấp kế thừa) và `token_count` (độ dài token).
* `QueryResultSchema`: Chuẩn hóa kết quả truy hồi, bao gồm: `query_id` (mã câu hỏi), `rank` (thứ vị xếp hạng từ 1 đến $k$), `score` (điểm tương đồng), `ground_truth_matched` (nhãn trúng khớp căn cứ pháp lý) và `retrieved_locator` (tọa độ phân cấp được hệ thống trả về).

### 2.2.4. Quy trình điều phối thực nghiệm và ghi nhận kết quả tự động
Bộ điều phối `BenchmarkRunner` thực thi tuần tự các truy vấn kiểm thử theo mô hình đường ống tự động. Với mỗi câu hỏi trong bộ dữ liệu, hệ thống gửi truy vấn đến bộ điều hợp tương ứng, thu thập danh sách Top-$k$ ứng viên, tính toán các chỉ số truy hồi tức thời (Recall@$k$, MRR@$k$, NDCG@$k$) và xuất dữ liệu thô ra các tập tin log định dạng JSON Lines (JSONL). Toàn bộ quá trình đánh giá được thực hiện khép kín nhằm loại trừ hoàn toàn sự can thiệp thủ công của con người vào kết quả đo kiểm.

### 2.2.5. Cơ chế kiểm soát lỗi và lưu vết an toàn (Fail-safe Checkpointing)
Nhằm đối phó với rủi ro đứt gãy kết nối mạng API hoặc lỗi tràn bộ nhớ (Out-of-Memory) trong các phiên thực nghiệm quy mô lớn trên môi trường tính toán đám mây (Kaggle/Colab), Benchmark Harness được trang bị cơ chế lưu vết an toàn:
* Cơ chế ghi nhận điểm kiểm tra (Checkpointing): Hệ thống tự động đồng bộ kết quả đánh giá xuống đĩa cứng sau mỗi lô 25 câu hỏi (`batch_size = 25`).
* Khôi phục trạng thái (State Recovery): Khi xảy ra sự cố ngắt quãng, hệ thống có khả năng tự động đọc file checkpoint gần nhất và tiếp tục thực thi từ câu hỏi bị gián đoạn mà không phải chạy lại từ đầu.
* Ghi vết giao dịch kiểm toán: Đối với các tác vụ sử dụng mô hình ngôn ngữ lớn làm giám khảo (LLM-as-a-Judge), hệ thống ghi nhận đầy đủ mã giao dịch toàn cầu `generation_id`, số lượng token tiêu thụ và chi phí API tương ứng cho từng lượt đánh giá.

### 2.2.6. Tích hợp các hệ thống và biến thể nghiên cứu
Khung kiểm thử được thiết kế mở, cho phép tích hợp linh hoạt 6 cấu hình đối sánh thuộc Giai đoạn 2 và mô hình đồ thị tri thức LightRAG thuộc Giai đoạn 1. Các tham số phần cứng (bộ nhớ VRAM, dung lượng RAM hệ thống, luồng CPU) được giám sát liên tục để bảo đảm tính ổn định xuyên suốt quá trình thực thi.

---

## 2.3. Thiết kế hai bộ dữ liệu kiểm thử của Benchmark A

### 2.3.1. Nguồn dữ liệu và phạm vi ngữ liệu
Bộ ngữ liệu nền của Benchmark A bao gồm **2.087 Điều luật toàn văn** được thu thập từ nguồn dữ liệu công khai trên Cổng thông tin điện tử Chính phủ và Cơ sở dữ liệu quốc gia về văn bản pháp luật. Ngữ liệu bao quát các chế định pháp lý quan trọng nhất của hệ thống pháp luật Việt Nam, bao gồm:
* Bộ luật Dân sự 2015 (689 Điều);
* Bộ luật Hình sự 2015, sửa đổi bổ sung 2017 (426 Điều);
* Bộ luật Tố tụng Hình sự 2015 (510 Điều);
* Bộ luật Lao động 2019 (220 Điều);
* Luật Hôn nhân và Gia đình 2014 (133 Điều);
* Chương III Luật Đất đai 2024 (quy định về địa giới hành chính, điều tra cơ bản và quy hoạch sử dụng đất).

### 2.3.2. Quy trình rà soát và chuẩn hóa dữ liệu
Dữ liệu thô sau khi thu thập được xử lý qua quy trình chuẩn hóa gồm ba bước:
1. Chuẩn hóa mã hóa ký tự UTF-8 và bảng mã Unicode dựng sẵn (NFC), xử lý triệt để các ký tự khoảng trắng đặc biệt (non-breaking spaces `\u00a0`) và ký tự điều khiển.
2. Chuẩn hóa định dạng đề mục pháp lý theo quy chuẩn kỹ thuật lập pháp (Nghị định số 34/2016/NĐ-CP và Nghị định số 154/2020/NĐ-CP): nhận diện thống nhất các từ khóa *"Điều"*, *"Khoản"*, *"Điểm"*.
3. Loại bỏ các thành phần văn bản phi quy phạm như số trang, tiêu đề đầu trang/chân trang (header/footer) và các chú thích biên tập không thuộc nội dung văn bản luật chính thức.

### 2.3.3. Tập đối chuẩn công bằng 205 câu hỏi (Tier 1 Fair Subset — Giai đoạn 1)
Trong Giai đoạn 1 của đề tài, nghiên cứu thực hiện đối sánh giữa các kiến trúc RAG cơ sở và kiến trúc đồ thị tri thức LightRAG. Tuy nhiên, việc áp dụng LightRAG trên toàn văn 2.087 Điều luật gặp phải rào cản chi phí tính toán rất lớn: do LightRAG phụ thuộc vào mô hình ngôn ngữ lớn để trích xuất thực thể và quan hệ trên từng đoạn cắt văn bản ($O(N \cdot \text{Cost}_{\text{LLM}})$), kinh phí gọi API thương mại cho toàn bộ kho dữ liệu vượt quá giới hạn nguồn lực của đề tài.

Để khắc phục rào cản này mà vẫn bảo đảm tính khoa học, nhóm nghiên cứu đã triển khai LightRAG trên một phân vùng gồm **500 Điều luật trọng điểm** (thuộc Bộ luật Hình sự và Bộ luật Lao động). Khi đối soát với tập câu hỏi, nhóm xác lập **Tập đối chuẩn công bằng (Tier 1 Fair Subset)** gồm **205 câu hỏi**. Điều kiện ràng buộc tiên quyết của tập này là: **100% căn cứ pháp lý cần thiết để giải quyết câu hỏi đều phải nằm trọn vẹn trong 500 điều luật đã được nạp vào chỉ mục của LightRAG**.

Việc thiết lập tập 205 câu tuân thủ nguyên tắc phương pháp luận **Đánh giá trên Phạm vi Công bằng (Equal Scope Evaluation)**:
* Loại bỏ hoàn toàn nguy cơ LightRAG bị trượt oan do tài liệu chưa được nạp vào hệ thống (Out-of-Index penalty).
* Tạo ra một môi trường đối đầu sòng phẳng giữa Naive Vector RAG, Hybrid RAG, LightRAG và kiến trúc đề xuất Parser RAG trên cùng một điều kiện biên dữ liệu.

### 2.3.4. Tập kiểm thử toàn diện 512 câu hỏi (Giai đoạn 2)
Để đánh giá khả năng mở rộng quy mô (Scalability) và độ bền vững của bộ phân tích cấu trúc Parser trên toàn bộ kho luật quốc gia, Giai đoạn 2 sử dụng **Tập kiểm thử toàn diện gồm 512 câu hỏi pháp lý** (`benchmark_rewritten.json`). Bộ câu hỏi được phân tầng theo bốn nhóm độ phức tạp nghiệp vụ:
1. Câu hỏi tra cứu dữ kiện trực tiếp (`clean_factoid`): 307 câu, yêu cầu xác định các quy định tường minh về điều kiện, độ tuổi, thời hạn hoặc chế tài cụ thể.
2. Câu hỏi chứa điều kiện và ngoại lệ (`conditional`): 123 câu, đòi hỏi hệ thống phải xác định cả quy định chung và các trường hợp loại trừ hoặc miễn trừ trách nhiệm.
3. Câu hỏi suy luận nhiều bước (`multi_hop`): 67 câu, đòi hỏi liên kết căn cứ pháp lý giữa nhiều điều khoản khác nhau trong cùng một đạo luật.
4. Câu hỏi phủ định hoặc ngoài phạm vi (`negative`): 15 câu, kiểm tra khả năng từ chối trả lời của hệ thống khi không có căn cứ pháp lý điều chỉnh.

Mỗi câu hỏi đều được gán nhãn căn cứ pháp lý chuẩn mực (Ground Truth Locators) tới cấp Điều, Khoản và Điểm cụ thể bởi các chuyên gia có chuyên môn luật học.

### 2.3.5. Kiểm soát trùng lặp từ vựng (Paraphrasing và Lexical Overlap)
Trong các bài toán truy xuất thông tin pháp lý, hiện tượng rò rỉ từ vựng (Lexical Leakage) – khi câu hỏi sao chép nguyên văn các cụm từ trong điều luật – thường làm sai lệch kết quả thực nghiệm theo hướng thiên vị có lợi cho các giải thuật so khớp từ khóa như BM25. Để loại trừ yếu tố gây nhiễu này, toàn bộ 512 câu hỏi đã được diễn đạt lại (Paraphrasing) theo ngôn ngữ đời thường mà người dân hoặc doanh nghiệp thường sử dụng khi tìm kiếm tư vấn, trong khi vẫn bảo toàn bản chất pháp lý của tình huống.

Đo kiểm thực nghiệm xác nhận hệ số trùng lặp từ vựng Jaccard trung bình giữa câu hỏi và điều luật căn cứ giảm từ $0.68 \pm 0.11$ (ở bản câu hỏi thô) xuống còn **$0.31 \pm 0.09$** (ở bản câu hỏi diễn đạt lại).

### 2.3.6. Bảng đặc tả so sánh hai bộ dữ liệu kiểm thử của Benchmark A
Bảng 2.1 tổng hợp các đặc tính kỹ thuật phân tầng giữa hai tập dữ liệu kiểm thử được sử dụng xuyên suốt đề tài:

**Bảng 2.1. Đặc tả phân tầng hai tập dữ liệu kiểm thử thuộc Benchmark A**

| Tiêu chí So sánh | Tập Đối chuẩn Công bằng (Tier 1 Fair Subset) | Tập Kiểm thử Toàn diện (Full-Scale Benchmark A) |
| :--- | :---: | :---: |
| **Giai đoạn nghiên cứu áp dụng** | **Giai đoạn 1** (Đánh giá Baseline và Đối chuẩn LightRAG) | **Giai đoạn 2** (Ma trận Ablation 6 Cấu hình) |
| **Quy mô ngữ liệu nền (Corpus)** | 500 Điều luật (Bộ luật Hình sự & Bộ luật Lao động) | 2.087 Điều luật (Toàn văn 6 văn bản luật) |
| **Số lượng câu hỏi kiểm thử** | **205 câu hỏi** | **512 câu hỏi** |
| **Điều kiện bao phủ căn cứ** | 100% căn cứ pháp lý nằm trong 500 điều luật của LightRAG | Bao phủ toàn diện mọi chế định pháp luật trong kho ngữ liệu |
| **Mục đích phương pháp luận** | Đảm bảo nguyên tắc Equal Scope Evaluation với GraphRAG | Kiểm chứng khả năng mở rộng quy mô và triệt tiêu sụp đổ trích dẫn |
| **Các hệ thống tham gia đánh giá** | Naive Vector, Naive Hybrid, LightRAG, Parser Dense | 6 Cấu hình giai thừa đối xứng (C1 đến C6) + Biến thể $\alpha=0.8$ |
| **Hệ số trùng lặp từ vựng Jaccard** | $0.32 \pm 0.08$ | $0.31 \pm 0.09$ |
| **Các chỉ số đo lường trọng tâm** | Recall@5, MRR@5, Citation Accuracy (LLM Judge) | Recall@5, MRR@5, Citation Accuracy (LLM Judge), $\alpha$-Sweep |

### 2.3.7. Chất lượng bộ dữ liệu và các giới hạn phạm vi
Bộ dữ liệu Benchmark A phản ánh trung thực phân bố câu hỏi trong thực tế tra cứu pháp luật tại Việt Nam. Tuy nhiên, nghiên cứu xác định rõ hai giới hạn phạm vi:
1. Bộ dữ liệu chủ yếu tập trung vào các câu hỏi đơn văn bản hoặc liên kết nội bộ trong cùng một đạo luật, chưa mở rộng ra các bài toán xung đột pháp luật phức tạp giữa luật chung và luật chuyên ngành.
2. Quy mô 500 điều ở Giai đoạn 1 là một giải pháp thỏa hiệp bắt buộc do rào cản chi phí tính toán của LightRAG, song đã được kiểm soát chặt chẽ thông qua nguyên tắc lọc tập con công bằng.

---

## 2.5. Thiết kế phương pháp mở rộng bằng Parser và Validation — Giai đoạn 2

### 2.5.1. Động cơ bổ sung Structure-aware Parsing
Kết quả thực nghiệm ở Giai đoạn 1 chỉ ra hai điểm nghẽn nghiêm trọng của các phương pháp phân đoạn văn bản truyền thống khi áp dụng vào văn bản quy phạm pháp luật:
1. Hiện tượng mồ côi ngữ cảnh (Context Orphanage): Khi văn bản bị cắt theo độ dài cố định hoặc tách rời từng Khoản/Điểm một cách cơ học, các quy phạm thành phần bị mất đi câu dẫn chủ thể hoặc điều kiện tiên quyết ở cấp Điều cha, khiến mô hình ngôn ngữ không thể xác định phạm vi áp dụng.
2. Hiện tượng ảo giác ranh giới (Boundary Smearing): Khi gom các khối văn bản thô lớn (toàn văn Điều luật dài hàng nghìn từ) để đưa vào mô hình tạo sinh, hiện tượng ngợp ngữ cảnh dài (Context Dilution / Lost in the Middle) xảy ra, khiến mô hình trả lời chung chung và làm tỷ lệ trích dẫn chính xác sụp đổ.

Để giải quyết triệt để các hạn chế trên, Giai đoạn 2 đề xuất giải pháp bóc tách cấu trúc chuyên biệt thông qua Module `StructureAwareParser` v2 và quy trình kiểm thực `Validation`.

### 2.5.2. Structure-Aware Regex Parser v2
Module `StructureAwareParser` v2 thực thi quy trình phân tách cấu trúc pháp lý dựa trên hệ thống biểu thức quy chuẩn (Regular Expressions) được tối ưu hóa cho ngữ pháp lập pháp Việt Nam:
* Nhận diện và khôi phục tiêu đề thực tế: Tự động phân tích dòng đầu tiên của điều luật bằng mẫu quy chuẩn `^Điều\s+(\d+)\.\s*(.+)$` để trích xuất chính xác tên gọi quy phạm, loại bỏ hoàn toàn các đoạn cắt rác rỗng (`_p0`).
* Phân tách đệ quy ba cấp: Bóc tách văn bản tuần tự từ cấp Điều xuống cấp Khoản (mẫu `^(\d+)\.\s*(.+)$`) và cấp Điểm (mẫu `^([a-zđ])\)\s*(.+)$`).
* Bơm tiền tố định danh bất biến (Invariant Context Prefix Injection): Bơm trực tiếp chuỗi định danh phân cấp vào phần đầu của 100% các phân đoạn vi mô (*micro-chunks*, độ dài 50–150 từ):
  $$\text{Prefix} = \text{"[Luật " } + \text{law\_id} + \text{ " \| Điều " } + \text{article\_id} + \text{ ": " } + \text{title} + \text{] > [Khoản " } + \text{clause\_id} + \text{]"}$$

Dữ liệu toàn văn 2.087 Điều luật sau khi đi qua bộ phân tích cấu trúc được chuyển đổi thành **12.754 phân đoạn vi mô chuẩn hóa**.

### 2.5.3. Module Validation kiểm định tính toàn vẹn phân cấp văn bản
Dữ liệu sau khi trích xuất được đưa qua Module Validation để kiểm tra tính toàn vẹn cấu trúc văn bản trước khi lập chỉ mục. Cần nhấn mạnh rằng ở Giai đoạn 2, hệ thống **chưa xây dựng cơ sở dữ liệu đồ thị vật lý (Physical Graph)** mà tập trung kiểm định tính toàn vẹn của **cây phân cấp tài liệu (Hierarchical Document Tree)**:
1. Kiểm tra tính liên kết phân cấp: Xác thực rằng mọi phân đoạn thành phần con (Khoản, Điểm) đều lưu trữ chính xác mã tham chiếu định danh (`parent_id`) trỏ về đơn vị cấu trúc cha (Điều luật).
2. Kiểm tra độ phủ tiền tố: Bảo đảm 100% các phân đoạn vi mô đều được gắn tiền tố định vị hợp lệ, không có trường hợp nào bị khuyết tiêu đề Điều.
3. Bảo tồn ký tự đặc thù tiếng Việt: Kiểm tra tính nguyên vẹn của các ký tự Điểm mang dấu tiếng Việt (chẳng hạn Điểm đ) không bị chuyển đổi sai lệch trong quá trình xử lý chuỗi.

### 2.5.4. Biến thể Naive RAG + Parser và Thuật toán Article-level MaxP Aggregation
Khi đưa 12.754 phân đoạn vi mô vào không gian vector của mô hình BGE-M3 (1024 chiều), số lượng đơn vị tìm kiếm tăng gấp hơn 6 lần so với kho 2.087 điều ban đầu. Nếu thực hiện truy xuất Top-5 theo cách ngây thơ, hiện tượng **bội thực cục bộ (Redundancy Collapse)** sẽ xuất hiện: năm kết quả trả về có thể là năm Khoản khác nhau của cùng một Điều luật, khiến người dùng chỉ nhận được duy nhất một quy phạm và làm suy giảm nghiêm trọng chỉ số Recall ở cấp Điều.

Để khắc phục hiện tượng này, nghiên cứu đề xuất thuật toán **Gom điểm Cực đại cấp Điều luật (Article-level MaxP Aggregation)**:
$$\text{Score}(\text{Article}_A) = \max_{c_j \in \text{Article}_A} \text{CosineSim}(\mathbf{q}, \mathbf{c}_j)$$

Trong đó $\mathbf{q}$ là vector nhúng của truy vấn và $\mathbf{c}_j$ là vector nhúng của phân đoạn vi mô thứ $j$ thuộc Điều luật $A$. 

Thuật toán này vận hành theo **Nguyên lý Chống pha loãng tín hiệu (Anti-Dilution Principle)**: trong khoa học pháp lý, chỉ cần duy nhất một khoản vi mô trúng khớp câu hỏi là toàn bộ Điều luật đó có đầy đủ giá trị hiệu lực để làm căn cứ áp dụng. Phép toán cực đại $\max$ bảo toàn nguyên vẹn tín hiệu tương đồng cao nhất của phân đoạn đúng mà không bị các khoản râu ria khác kéo tụt điểm số như hàm trung bình cộng. Sau khi gom điểm, hệ thống xếp hạng các Điều luật và trích xuất Top-5 Điều luật độc nhất.

### 2.5.5. Biến thể Hybrid RAG + Parser và Giải thuật Dung hợp Thứ hạng Có trọng số (Weighted RRF)
Đối với biến thể kết hợp giữa tìm kiếm từ khóa và tìm kiếm ngữ nghĩa trên các phân đoạn vi mô, hệ thống áp dụng giải thuật Dung hợp Thứ hạng Có trọng số (Weighted Reciprocal Rank Fusion):
$$\text{RRF}_{\text{weighted}}(A) = \alpha \cdot \frac{1}{k + r_{\text{dense}}(A)} + (1 - \alpha) \cdot \frac{1}{k + r_{\text{bm25}}(A)}$$

Trong đó:
* $r_{\text{dense}}(A)$ và $r_{\text{bm25}}(A)$ lần lượt là thứ hạng của Điều luật $A$ sau khi đã gom điểm MaxP ở kênh Dense và kênh BM25;
* $k = 60$ là hằng số làm mịn chuẩn hóa theo nghiên cứu kinh điển của Cormack và cộng sự (SIGIR 2009);
* $\alpha \in [0.0, 1.0]$ là hệ số điều tiết tỷ trọng ngữ nghĩa.

Thiết kế này thiết lập một không gian tìm kiếm tham số liên tục, cho phép hệ thống khảo sát thực nghiệm sự dịch chuyển hiệu năng từ cấu hình thuần từ khóa ($\alpha = 0.0$), qua cấu hình dung hợp cào bằng ($\alpha = 0.5$), tới các cấu hình ưu tiên ngữ nghĩa ($\alpha > 0.5$) và cấu hình thuần vector ($\alpha = 1.0$).

### 2.5.6. Thiết kế ma trận thực nghiệm đối xứng $2 \times 3$ (Ablation Matrix)
Nhằm kiểm chứng giả thuyết H2 một cách nghiêm ngặt, thực nghiệm Giai đoạn 2 được thiết kế đối xứng hoàn toàn theo mô hình giai thừa 2 nhân tố ($2 \text{ Chunking Strategies} \times 3 \text{ Retrieval Methods}$), hình thành 6 cấu hình đối sánh trên cùng kho 2.087 điều luật và 512 câu hỏi:
* **Cấu hình 1 (C1 - Naive BM25):** Điều luật thô, truy xuất bằng Okapi BM25.
* **Cấu hình 2 (C2 - Naive Dense):** Điều luật thô, truy xuất bằng mô hình BGE-M3 Dense.
* **Cấu hình 3 (C3 - Naive Hybrid):** Điều luật thô, dung hợp Cormack RRF tiêu chuẩn ($\alpha = 0.5$).
* **Cấu hình 4 (C4 - Parser BM25):** 12.754 phân đoạn vi mô, truy xuất bằng BM25 kết hợp Article-level MaxP.
* **Cấu hình 5 (C5 - Parser Dense):** 12.754 phân đoạn vi mô, truy xuất bằng BGE-M3 kết hợp Article-level MaxP.
* **Cấu hình 6 (C6 - Parser Hybrid):** 12.754 phân đoạn vi mô, dung hợp Cormack RRF tiêu chuẩn ($\alpha = 0.5$) kết hợp MaxP.

### 2.5.7. Các biến được kiểm soát và nguyên tắc đối chứng độc lập
Thiết kế thực nghiệm tuân thủ chặt chẽ nguyên tắc kiểm soát biến khoa học:
* Biến độc lập duy nhất được thay đổi giữa các cặp đối chứng là **Phương thức phân đoạn văn bản (Chunking Strategy)**: từ biểu diễn Điều thô chuyển sang phân đoạn vi mô mang tiền tố.
* Các biến kiểm soát được giữ cố định tuyệt đối: cùng bộ mã hóa nhúng BGE-M3 (FP16, pooling cls/mean), cùng thuật toán Okapi BM25 ($k_1=1.5, b=0.75$), cùng hằng số $k=60$ và cùng tập 512 câu hỏi kiểm thử.
* Thiết kế này bảo đảm mọi sự biến thiên về Recall@5, MRR@5 và Citation Accuracy đều phản ánh trung thực giá trị đóng góp nội tại của bộ phân tích cấu trúc pháp lý.
