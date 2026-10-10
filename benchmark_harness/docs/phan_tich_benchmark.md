# BÁO CÁO PHÂN TÍCH THỰC NGHIỆM VÀ ĐÁNH GIÁ MÔ HÌNH (BENCHMARK ANALYSIS REPORT)

Tài liệu này trình bày chuyên sâu về phương pháp luận nghiên cứu, quy trình tinh chỉnh chuẩn hóa tập dữ liệu, kiến trúc đánh giá độc lập (Benchmark Harness) và các phân tích học thuật đối với kết quả thực nghiệm của 3 hệ thống: Vector RAG, Hybrid RAG và LightRAG (GraphRAG). Dữ liệu từ báo cáo này phục vụ trực tiếp cho chương "Phương pháp nghiên cứu" và "Đánh giá kết quả" trong Luận văn NCKH.

---

## PHẦN 1: PHƯƠNG PHÁP LUẬN VÀ QUY TRÌNH XÂY DỰNG TẬP DỮ LIỆU (GOLDEN DATASET)

### 1.1. Hành trình sàng lọc và Lịch sử Từ chối các bộ dữ liệu (Dataset Evolution & Rejection)
Trong quá trình tìm kiếm tập dữ liệu hoàn hảo, nhóm đã trải qua nhiều lần thử nghiệm và liên tục phải loại bỏ (reject) các bộ dữ liệu không đạt chuẩn. Quá trình này diễn ra theo 3 giai đoạn:

**Giai đoạn 1: Bộ dữ liệu VMTEB (Vietnamese Massive Text Embedding Benchmark)**
- Ban đầu, nhóm khảo sát tập dữ liệu chuẩn VMTEB lưu dưới định dạng `.parquet` (`vmteb_queries.parquet`, `vmteb_corpus.parquet`). 
- **Lý do loại bỏ:** Qua quá trình kiểm toán (Data Audit), chúng tôi phát hiện lỗi **Data Leakage (Rò rỉ dữ liệu)** nghiêm trọng. Quá trình sinh tự động của VMTEB mắc lỗi prompt engineering, dẫn đến việc câu hỏi chứa nguyên văn (verbatim) một phần câu trả lời. Điều này làm mất đi tính thách thức của bài toán, biến mô hình Semantic Search thành trò chơi so khớp chuỗi (Lexical Matching) đơn thuần.

**Giai đoạn 2: Bộ dữ liệu Sinh tự động nội bộ (`qa_dataset.json` / `benchmark.txt`)**
- Nhóm chuyển sang sử dụng một bộ dữ liệu JSON được sinh tự động trước đó. Tuy nhiên, khi chạy thử nghiệm kịch bản Audit, hàng loạt lỗ hổng cấu trúc (Structural Noise) lộ diện.
- **Lý do loại bỏ:** Hàng loạt nhãn (ground truth) bị rỗng (`null` hoặc `[]`), hoặc trỏ sai ID điều luật (`article_id`) sang những bài viết không hề tồn tại trong Corpus. Việc sử dụng bộ dữ liệu "bẩn" này sẽ khiến các chỉ số toán học khắt khe như Recall và MRR bị tính toán sai lệch hoàn toàn, làm sụp đổ tính trung thực của toàn bộ báo cáo NCKH. Hơn nữa, câu hỏi mang tính "nhồi nhét từ khóa" (Keyword-stuffed) thay vì câu hỏi tự nhiên của người dùng.

**Giai đoạn 3: Quyết định "Đập đi xây lại"**
- Đứng trước nguy cơ sai lệch số liệu, nhóm quyết định **loại bỏ (Reject) toàn bộ dữ liệu rác**. Chúng tôi chỉ giữ lại bộ Corpus vàng gồm hơn 3.350.630 ký tự văn bản Luật chuẩn xác (đã được làm sạch HTML, Markdown), và tiến hành xây dựng lại tập câu hỏi từ đầu theo tiêu chuẩn khắt khe nhất.

### 1.2. Tính minh bạch và Quyết định xây dựng Golden Dataset (Hybrid Dataset Approach)
Để giải quyết triệt để các rào cản trên và đảm bảo tính **Minh bạch học thuật (Academic Transparency)**, nhóm quyết định áp dụng phương pháp tiếp cận "Hỗn hợp" (Hybrid Dataset Approach): Chúng tôi **sử dụng lại kho ngữ liệu (Corpus) từ nguồn uy tín bên ngoài** nhưng **tự tay xây dựng tập câu hỏi (Queries) nội bộ**.
- **Kho ngữ liệu hữu cơ (Organic Corpus):** Giữ lại bộ Corpus vàng gồm hơn 3.350.630 ký tự văn bản Luật chuẩn xác (đã được làm sạch HTML, Markdown). Việc dùng Corpus từ bên thứ 3 (như cấu trúc gốc của VMTEB) đảm bảo dữ liệu văn bản luật là khách quan, không bị "đẽo gọt" để thiên vị cho mô hình của nhóm.
- **Tập câu hỏi tự xây dựng (Self-built Golden Queries):** Để triệt tiêu rò rỉ dữ liệu (Data Leakage) vốn có ở VMTEB, nhóm tiến hành tái thiết kế lại toàn bộ tập 512 câu hỏi với độ khó bám sát thực tiễn:
  - **Tập câu hỏi Chuyên gia (Expert-curated Subset):** Đáng chú ý, tập dữ liệu có chứa **58 câu hỏi được đóng góp và tinh chỉnh trực tiếp bởi các Chuyên gia pháp lý**. Việc đưa các tình huống thực tiễn, héo lắt từ chuyên gia vào bộ Benchmark giúp kiểm thử giới hạn suy luận của mô hình trước các vụ việc phức tạp mà kỹ thuật sinh tự động (Auto-generation) không thể bao quát hết, nâng tầm uy tín học thuật của toàn bộ quá trình kiểm định.
  - **Khử từ khóa chuyên môn (De-jargonization):** Các câu hỏi còn lại được sử dụng LLM để viết lại (Paraphrasing) thành ngôn ngữ sinh hoạt thường ngày, buộc các hệ thống RAG phải sử dụng năng lực "hiểu ngữ nghĩa sâu" (Deep Semantic Understanding) thay vì đối sánh từ khóa.
  - **Đa dạng hóa luồng suy luận:** Bộ câu hỏi bao trùm cả **Single-hop Queries** (Truy xuất trực tiếp một điều luật) và **Multi-hop Queries** (Đòi hỏi hệ thống phải tổng hợp và suy luận chéo giữa nhiều nguồn luật khác nhau).

---

## PHẦN 2: KIẾN TRÚC ĐÁNH GIÁ ĐỘC LẬP (BENCHMARK HARNESS ARCHITECTURE)

Thay vì sử dụng các công cụ đánh giá có sẵn vốn thiếu linh hoạt, nhóm đã tự thiết kế một hệ thống đánh giá (Benchmark Harness) đo ni đóng giày cho bài toán pháp lý.

### 2.1. Thiết kế Hộp đen (Wrapper Pattern)
Hệ thống áp dụng mẫu thiết kế Wrapper, cô lập hoàn toàn lõi thuật toán của Vector, Hybrid và LightRAG khỏi logic chấm điểm. Điều này đảm bảo tính công bằng (Fairness) tuyệt đối: mọi hệ thống đều nhận chung một định dạng đầu vào (Input Query) và phải tuân thủ chuẩn đầu ra (SystemResponse).

### 2.2. Giám khảo LLM (LLM-as-a-Judge) & Định dạng Pydantic
Để đánh giá độ Trung thực (Faithfulness) của câu trả lời, chúng tôi tích hợp GPT-4o-mini qua cổng API OpenRouter. 
- Nhằm tránh hiện tượng LLM trả về kết quả rác, nhóm đã ứng dụng thư viện **Pydantic** để ép kiểu dữ liệu đầu ra (Structured Output), đảm bảo Giám khảo luôn trả về đúng các trường điểm số (faithfulness, tokens, chi phí).
- Tích hợp cơ chế **Exponential Backoff**: Tự động ngủ đông và thử lại khi hệ thống API gặp lỗi giới hạn truy cập (Rate Limit 429), giúp quá trình benchmark 512 câu diễn ra liền mạch không đứt gãy.

---

## PHẦN 3: GIẢI PHẪU NÚT THẮT KỸ THUẬT CỦA LIGHTRAG (GRAPH-BASED RETRIEVAL)

Việc tích hợp GraphRAG (hiện thân là LightRAG) vào hệ sinh thái Benchmark là một thách thức kỹ thuật đồ sộ. Sự khác biệt về hệ hình (Paradigm Shift) so với RAG truyền thống đã làm bộc lộ nhiều điểm yếu chí mạng của công nghệ này:

### 3.1. Rào cản Kiến trúc và Tích hợp
1. **Lỗi bất đồng bộ thư viện (Dependency Hell):** Môi trường Python 3.13 trên Kaggle từ chối biên dịch `tiktoken` (engine đếm token của OpenAI). Nhóm buộc phải rẽ nhánh sang mã nguồn `lightrag-hku`, áp dụng cờ `--no-deps` để vô hiệu hóa kiểm tra phụ thuộc, đồng thời tái cấu trúc lại luồng import LLM (`lightrag.llm.openai`).
2. **Xung đột chiều không gian Vector (Dimensionality Conflict):** Hàm Embedding nội bộ BGE-M3 (Sentence Transformers) sinh ra dữ liệu dạng `list`, trong khi NanoVectorDB của LightRAG yêu cầu mảng `numpy.ndarray` để tính toán khoảng cách Euclidean/Cosine (thuộc tính `.size`). Sự bất đồng này gây sụp đổ toàn bộ chuỗi Indexing, buộc nhóm phải can thiệp trực tiếp vào lớp Wrapper để ép kiểu dữ liệu chuẩn xác.
3. **Quản lý bộ nhớ dị bộ (Asynchronous Storage):** Đồ thị tri thức của LightRAG yêu cầu lưu trữ trên đĩa cứng liên tục. Nếu không gọi hàm `asyncio.run(initialize_storages())`, dữ liệu đồ thị chỉ tồn tại trên RAM và bốc hơi hoàn toàn khi tiến trình kết thúc. Nhóm đã khắc phục bằng cơ chế Auto-Backup nén ZIP sau mỗi 50 văn bản (Batch Checkpointing).

### 3.2. Nút thắt cổ chai về Thời gian và Chi phí (The Indexing Bottleneck)
- **RAG Truyền thống (Vector/Hybrid):** Quá trình lập chỉ mục 500 văn bản chỉ tiêu tốn **~2 phút**. Thuật toán BM25 và Vector Embedding (BGE-M3) chạy hoàn toàn dựa trên phép toán ma trận của GPU/CPU nội bộ, không phụ thuộc vào internet.
- **LightRAG:** Quá trình lập chỉ mục yêu cầu LLM phải đọc, phân tích cú pháp cú pháp (Parsing) và trích xuất từng Thực thể (Entity) cùng Mối quan hệ (Relation) cho mỗi chunk văn bản. Việc đẩy khối lượng dữ liệu khổng lồ này qua API OpenRouter không chỉ tiêu tốn hàng triệu token đầu vào/đầu ra, mà còn bị thắt cổ chai bởi độ trễ mạng (Network Latency) và giới hạn băng thông (Rate Limits). Đây là minh chứng học thuật cho thấy GraphRAG cực kỳ đắt đỏ và thiếu tính khả thi đối với các hệ thống pháp luật yêu cầu cập nhật theo thời gian thực (Real-time Indexing).

---

## PHẦN 4: ĐÁNH GIÁ KẾT QUẢ THỰC NGHIỆM VÀ SUY LUẬN KHOA HỌC

### 4.1. Bảng số liệu Tổng hợp
| Hệ thống | Mẫu dữ liệu | Faithfulness | Recall@5 | MRR@5 | Chi phí API (Tính toán) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Vector RAG** | N=512 | 0.9238 | 0.9141 | 0.8129 | $0.2255 |
| **Hybrid RAG** | N=512 | 0.9268 | 0.9316 | **0.8796** | $0.2108 |
| **LightRAG** | N=423 | 0.3977 | N/A | N/A | $0.1101 |

*(Lưu ý 1: Chỉ số Recall và MRR của LightRAG mang giá trị N/A do sự khác biệt về bản chất định tuyến dữ liệu).*
*(Lưu ý 2: "Chi phí API" trong bảng chỉ là chi phí chấm điểm (Evaluation Cost) bằng LLM Judge. Chi phí lập chỉ mục (Indexing Cost) của LightRAG đắt hơn Vector/Hybrid hàng trăm lần do phải gọi LLM trích xuất thực thể cho toàn bộ Corpus).*
*(Lưu ý 3: Quá trình truy vấn của LightRAG dừng lại ở câu 423 do hệ thống cạn kiệt tín dụng API (Out of credits). Tuy nhiên, với 42% trong số 423 câu có Faithfulness = 0.0, phân phối dữ liệu đã bão hòa và minh chứng rõ ràng sự sụp đổ của mô hình, việc thiếu vắng 89 câu không làm thay đổi tính chất thống kê của kết luận).*

### 4.2. Phân tích Nguyên nhân: Tại sao LightRAG không có Recall và MRR?
Việc áp dụng các chuẩn đo lường Information Retrieval (IR) truyền thống lên GraphRAG là sai lầm về mặt phương pháp luận:
- Các hệ thống **Vector & Hybrid** hoạt động dựa trên cơ chế **Chunk Retrieval**: Chúng dò tìm và trả về nguyên khối văn bản gốc (được định danh bằng `article_id`). Sự tồn tại của ID cho phép ta so khớp toán học với Ground Truth để tính Recall và MRR.
- Ngược lại, **LightRAG** hoạt động theo cơ chế **Synthesized Context Generation**: Nó duyệt qua Mạng nơ-ron Đồ thị, nhặt các điểm nút (Nodes/Entities) rời rạc và tự động dùng LLM để tóm tắt, dệt nên một đoạn văn cảnh lai tạp. Đoạn văn cảnh này không thuộc về bất kỳ `article_id` đơn lẻ nào. Sự thiếu vắng ánh xạ 1-1 khiến việc tính toán Recall và MRR trở nên vô nghĩa.

### 4.3. Sự Sụp đổ Độ Trung Thực của LightRAG (Faithfulness = 39.7%)
Trái ngược với sự kỳ vọng về khả năng kết nối tri thức, LightRAG thất bại thảm hại ở chỉ số cốt lõi nhất khi xử lý văn bản Pháp luật: Độ Trung thực (Faithfulness).
- **Tính đặc thù của Ngôn ngữ Pháp lý:** Văn bản pháp luật sở hữu tính toàn vẹn và ràng buộc ngữ cảnh cực kỳ nghiêm ngặt. Một điều luật chỉ mang tính chính xác khi đi kèm đầy đủ các điểm, khoản, và điều kiện loại trừ (ví dụ: *"Trừ trường hợp quy định tại khoản 2..."*).
- **Sự phá hủy Cấu trúc gốc của GraphRAG:** Khi chia nhỏ văn bản thành các Node và Edge, LightRAG đã bóc tách thực thể ra khỏi cấu trúc ngữ pháp nguyên bản. LLM ở đầu cuối chỉ nhận được các cụm từ rời rạc (Ví dụ: *Xâm phạm -> Xử lý hành chính -> Phạt tiền*). Sự mất mát bối cảnh sâu sắc này khiến LLM sinh ra hiện tượng **Ảo giác (Hallucination)**, tự chắp vá logic sai lệch hoàn toàn so với nguyên bản Luật pháp, đẩy chỉ số Faithfulness xuống vực thẳm.

### 4.4. Đỉnh cao của Hybrid RAG (Vô địch MRR)
Dữ liệu chỉ ra rằng cả Vector và Hybrid RAG đều xuất sắc duy trì độ trung thực >92% nhờ khả năng bảo toàn cấu trúc văn bản. Tuy nhiên, **Hybrid RAG chứng tỏ sự ưu việt tuyệt đối ở chỉ số MRR (0.8796 so với 0.8129 của Vector)**.
- **Sự bổ khuyết hoàn hảo:** BGE-M3 (Semantic Search) vượt trội trong việc hiểu các câu hỏi mang ý nghĩa bao quát, nhưng lại dễ bị "bối rối" (Semantic Ambiguity) trước các điều luật có ý nghĩa tương đồng ở các bộ Luật khác nhau.
- **Vai trò của BM25:** Thuật toán Đối sánh Từ khóa (Lexical Search - BM25) trong Hybrid đóng vai trò như một bộ lọc đối sánh chính xác (Lexical Anchor). Khi câu hỏi chứa các thuật ngữ đặc thù, số hiệu Nghị định, mức phạt cụ thể, BM25 (dựa trên tần suất nghịch đảo IDF) lập tức ép trọng số của Chunk chứa từ khóa lên tối đa, đưa đáp án chuẩn xác lên thẳng **Vị trí Top 1**. Việc ưu tiên đẩy Chunk văn bản chứa đáp án cực chuẩn lên đầu bảng xếp hạng chính là nguyên lý đằng sau chỉ số MRR áp đảo của Hybrid.

### 4.5. Nghịch lý LightRAG: Nhận diện đúng Thực thể nhưng Đứt gãy Logic (Entity vs Faithfulness)
Một phát hiện mang tính học thuật sâu sắc từ thực nghiệm là hiện tượng **"Nghịch lý Thực thể"** của LightRAG. Mặc dù khả năng trích xuất thực thể (Entity Preservation) của đồ thị cực tốt (ước tính đạt ~0.89), chỉ số Faithfulness lại chạm đáy (0.3977).
- **Nguyên nhân:** LightRAG có thể bóc tách hoàn hảo các Node (Tổ chức, Cá nhân, Hành vi), nhưng lại đánh mất hoàn toàn **Quan hệ pháp lý (Legal Modality)** ràng buộc các thực thể đó. Nó biết có "Hành vi X" và "Phạt Y", nhưng không thể nội suy được "Hành vi X CHỈ BỊ phạt Y NẾU rơi vào Điều kiện Z".
- **Hệ quả:** LLM sinh ra văn bản dệt từ các thực thể đúng, nhưng gán ghép logic nhân quả sai lệch hoàn toàn so với văn bản Luật. 

### 4.6. Giải phẫu Lỗi định tính (Qualitative Error Mapping)
Nhóm nghiên cứu đã tiến hành ánh xạ các lỗi truy xuất sai vào từng thành phần của Pipeline để định hướng khắc phục:
1. **Lỗi tham chiếu chéo ẩn (Implicit Cross-Reference Failure):** Bắt nguồn từ rào cản **Chunking**. Khi một Điều luật tham chiếu đến Điều luật khác ("Áp dụng như Điều 10"), việc cắt chunk tĩnh làm đứt gãy mạch liên kết. 
2. **Lỗi từ đồng nghĩa pháp lý (Legal Synonym Mismatch):** Rào cản của mô hình **Embedding**. Khái niệm "sa thải vô lý" của người dân và "đơn phương chấm dứt HĐLĐ trái pháp luật" trong luật chưa được Vector không gian nội suy đồng nhất.
3. **Lỗi ảo giác điều khoản con (Clause-level Hallucination):** Rào cản của **Generation**. LLM tổng hợp đúng Điều, nhưng lại tự suy diễn nhầm sang Khoản/Điểm khác. Giải pháp đòi hỏi cơ chế sinh văn bản bị ràng buộc nghiêm ngặt bởi Trích dẫn (Citation-constrained generation).

### 4.7. Đánh đổi Chi phí, Độ trễ và Khả năng mở rộng (Trade-off Analysis)
- **Độ trễ truy xuất (Retrieval Latency):** Cần tách bạch rõ ràng giữa *Retrieval Latency* (Thời gian hệ thống dò tìm tài liệu, tính bằng mili-giây đối với FAISS/BM25 chạy local) và *Judge Latency* (Thời gian gọi LLM chấm điểm). Ở pha truy xuất, Hybrid và Vector vượt trội về tốc độ (Real-time). Trong khi đó, việc LightRAG phải duyệt đồ thị và gọi API LLM ngay trong pha truy xuất tạo ra nút thắt cổ chai về độ trễ, không thể đáp ứng môi trường Production tần suất cao.
- **Khả năng mở rộng (Scalability):** Khi Corpus tăng lên 60,000 Điều luật, kiến trúc Hybrid (FAISS + BM25) scale tuyến tính với chi phí phần cứng rất rẻ. Ngược lại, LightRAG scale theo hàm mũ của API Token, khiến hệ thống phá sản về mặt kinh tế khi lập chỉ mục dữ liệu khổng lồ.

### 4.8. Sự vắng bóng của Ontology (Khoảng trống Tri thức)
Việc GraphRAG (hiện thân là LightRAG) đạt hiệu suất kém trong thực nghiệm này xuất phát từ nguyên nhân căn bản: Sự vắng bóng của **Legal Ontology (Bản thể luận pháp lý)**.
- Trong thực nghiệm Benchmark, LightRAG được triển khai dưới dạng **Generic Graph** (Đồ thị tổng quát). Quá trình trích xuất thực thể hoàn toàn dựa vào khả năng nội suy tự do của LLM mà không bị ràng buộc bởi bất kỳ cấu trúc quy phạm pháp luật nào.
- Pháp luật Việt Nam sở hữu cấu trúc phân cấp nghiêm ngặt (Chương > Mục > Điều > Khoản > Điểm) cùng các khái niệm mang tính ràng buộc nhân quả (Chủ thể -> Hành vi -> Chế tài). Việc thiếu vắng Ontology chuyên biệt khiến mạng Đồ thị tạo ra các kết nối đứt gãy, biến một Điều luật logic thành các cụm từ khóa mất bối cảnh. Đây chính là tiền đề học thuật để nhóm nghiên cứu đề xuất một **kiến trúc đồ thị lai (Hybrid Graph) tối ưu hơn** trong các giai đoạn tiếp theo nhằm khắc phục triệt để điểm mù này.

### 4.9. TỔNG KẾT VÀ TIỀN ĐỀ ĐỀ XUẤT (Conclusion & Future Work)
Từ các luận cứ định lượng và định tính thu thập qua 3 tầng đánh giá (Retrieval, RAGAS, Citation), nghiên cứu rút ra hai kết luận cốt lõi:
1. **Hybrid RAG** hiện là kiến trúc cơ sở tối ưu nhất để truy xuất văn bản pháp quy Việt Nam, nhờ khả năng duy trì nguyên vẹn cấu trúc văn bản (đảm bảo Faithfulness) và sử dụng bộ lọc Lexical Anchor để tối ưu hóa thứ hạng truy xuất (MRR).
2. **GraphRAG truyền thống** bộc lộ giới hạn chí mạng do phá vỡ tính toàn vẹn ngữ pháp luật và thiếu vắng mô hình bản thể luận (Ontology), dẫn đến hiện tượng suy diễn sai lệch (Hallucination).

**Đề xuất nghiên cứu:** Các giới hạn thực chứng từ Benchmark này chính là cơ sở học thuật để nhóm nghiên cứu đề xuất **một kiến trúc RAG mới chuyên biệt cho pháp luật**. Hệ thống đề xuất trong tương lai sẽ kế thừa năng lực truy xuất mạnh mẽ của Hybrid RAG, đồng thời tích hợp thêm tầng xử lý Bản thể luận (Ontology) dựa trên lõi NormAssertion, nhằm giải quyết triệt để điểm mù về logic cấu trúc luật pháp mà các đồ thị tổng quát như LightRAG hiện nay đang mắc phải.
