# BÁO CÁO PHÂN TÍCH THỰC NGHIỆM VÀ ĐÁNH GIÁ MÔ HÌNH (BENCHMARK ANALYSIS REPORT)

Tài liệu này trình bày chuyên sâu về phương pháp luận nghiên cứu, quy trình tinh chỉnh chuẩn hóa tập dữ liệu, kiến trúc đánh giá độc lập (Benchmark Harness) và các phân tích học thuật đối với kết quả thực nghiệm của 3 hệ thống: Vector RAG, Hybrid RAG và LightRAG (GraphRAG). Dữ liệu từ báo cáo này phục vụ trực tiếp cho chương "Phương pháp nghiên cứu" và "Đánh giá kết quả" trong Luận văn NCKH.

---

## PHẦN 1: PHƯƠNG PHÁP LUẬN VÀ QUY TRÌNH XÂY DỰNG TẬP DỮ LIỆU (GOLDEN DATASET)

### 1.1. Từ chối các bộ dữ liệu sẵn có (Dataset Rejection Rationale)
Trong giai đoạn đầu của nghiên cứu, nhóm đã tiến hành khảo sát và kiểm toán (Data Audit) các bộ dữ liệu phổ biến như VMTEB (Vietnamese Massive Text Embedding Benchmark) và một số tập dữ liệu hỏi-đáp nội bộ sinh ra từ các pipeline tự động. Tuy nhiên, chúng tôi quyết định loại bỏ hoàn toàn các tập dữ liệu này dựa trên các cơ sở khoa học sau:
- **Hiện tượng Rò rỉ Dữ liệu (Data Leakage):** Quá trình sinh tự động của VMTEB mắc lỗi prompt engineering, dẫn đến việc câu hỏi chứa nguyên văn (verbatim) một phần câu trả lời hoặc các thuật ngữ chuyên môn hẹp. Điều này làm mất đi tính thách thức của bài toán, biến mô hình truy xuất ngữ nghĩa (Semantic Retrieval) thành bài toán so khớp chuỗi đơn thuần (Lexical Matching).
- **Thiếu tính đại diện thực tế (Lack of Real-world Representation):** Các câu hỏi cũ mang tính "nhồi nhét từ khóa" (Keyword-stuffed). Trong thực tế tư vấn pháp luật, người dân thường sử dụng ngôn ngữ đời thường, dân dã, đôi khi không chính xác về mặt thuật ngữ pháp lý.
- **Nhiễu cấu trúc (Structural Noise):** Các file định dạng Parquet hoặc JSON cũ chứa nhiều nhãn (ground truth) bị rỗng (`null`) hoặc trỏ sai ID điều luật (`article_id`), làm sai lệch nghiêm trọng các hàm mục tiêu đánh giá như Recall và MRR.

### 1.2. Kỹ thuật Xây dựng Golden Dataset (Paraphrasing & Multi-hop Reasoning)
Để giải quyết triệt để các rào cản trên, nhóm đã giữ lại kho ngữ liệu gốc (Corpus) gồm 3.350.630 ký tự văn bản Luật chuẩn xác, và tiến hành tái cấu trúc tập câu hỏi (512 câu) thông qua kỹ thuật **LLM-based Paraphrasing**:
1. **Khử từ khóa chuyên môn (De-jargonization):** Dùng LLM viết lại các câu hỏi pháp lý phức tạp thành ngôn ngữ sinh hoạt thường ngày, buộc các hệ thống RAG phải sử dụng năng lực "hiểu ngữ nghĩa sâu" (Deep Semantic Understanding) thay vì đối sánh từ khóa.
2. **Đa dạng hóa luồng suy luận:** Tập dữ liệu được thiết kế bao gồm **Single-hop Queries** (Truy xuất trực tiếp một điều luật) và **Multi-hop Queries** (Đòi hỏi hệ thống phải tổng hợp và suy luận chéo giữa nhiều nguồn luật khác nhau như Hình sự, Dân sự, Doanh nghiệp).

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
| **Vector RAG** | N=480 | 0.9348 | 0.9375 | 0.8407 | $0.2096 |
| **Hybrid RAG** | N=512 | 0.9268 | 0.9316 | **0.8796** | $0.2108 |
| **LightRAG** | N=512 | 0.3977 | N/A | N/A | $0.1101 |

*(Lưu ý: Chỉ số Recall và MRR của LightRAG mang giá trị N/A do sự khác biệt về bản chất định tuyến dữ liệu).*

### 4.2. Phân tích Nguyên nhân: Tại sao LightRAG không có Recall và MRR?
Việc áp dụng các chuẩn đo lường Information Retrieval (IR) truyền thống lên GraphRAG là sai lầm về mặt phương pháp luận:
- Các hệ thống **Vector & Hybrid** hoạt động dựa trên cơ chế **Chunk Retrieval**: Chúng dò tìm và trả về nguyên khối văn bản gốc (được định danh bằng `article_id`). Sự tồn tại của ID cho phép ta so khớp toán học với Ground Truth để tính Recall và MRR.
- Ngược lại, **LightRAG** hoạt động theo cơ chế **Synthesized Context Generation**: Nó duyệt qua Mạng nơ-ron Đồ thị, nhặt các điểm nút (Nodes/Entities) rời rạc và tự động dùng LLM để tóm tắt, dệt nên một đoạn văn cảnh lai tạp. Đoạn văn cảnh này không thuộc về bất kỳ `article_id` đơn lẻ nào. Sự thiếu vắng ánh xạ 1-1 khiến việc tính toán Recall và MRR trở nên vô nghĩa.

### 4.3. Sự Sụp đổ Độ Trung Thực của LightRAG (Faithfulness = 39.7%)
Trái ngược với sự kỳ vọng về khả năng kết nối tri thức, LightRAG thất bại thảm hại ở chỉ số cốt lõi nhất của AI Pháp lý: Độ Trung thực (Faithfulness).
- **Tính đặc thù của Ngôn ngữ Pháp lý:** Văn bản pháp luật sở hữu tính toàn vẹn và ràng buộc ngữ cảnh cực kỳ nghiêm ngặt. Một điều luật chỉ mang tính chính xác khi đi kèm đầy đủ các điểm, khoản, và điều kiện loại trừ (ví dụ: *"Trừ trường hợp quy định tại khoản 2..."*).
- **Sự phá hủy Cấu trúc gốc của GraphRAG:** Khi chia nhỏ văn bản thành các Node và Edge, LightRAG đã bóc tách thực thể ra khỏi cấu trúc ngữ pháp nguyên bản. LLM ở đầu cuối chỉ nhận được các cụm từ rời rạc (Ví dụ: *Xâm phạm -> Xử lý hành chính -> Phạt tiền*). Sự mất mát bối cảnh sâu sắc này khiến LLM sinh ra hiện tượng **Ảo giác (Hallucination)**, tự chắp vá logic sai lệch hoàn toàn so với nguyên bản Luật pháp, đẩy chỉ số Faithfulness xuống vực thẳm.

### 4.4. Đỉnh cao của Hybrid RAG (Vô địch MRR)
Dữ liệu chỉ ra rằng cả Vector và Hybrid RAG đều xuất sắc duy trì độ trung thực >92% nhờ khả năng bảo toàn cấu trúc văn bản. Tuy nhiên, **Hybrid RAG chứng tỏ sự ưu việt tuyệt đối ở chỉ số MRR (0.8796 so với 0.8407)**.
- **Sự bổ khuyết hoàn hảo:** BGE-M3 (Semantic Search) vượt trội trong việc hiểu các câu hỏi mang ý nghĩa bao quát, nhưng lại dễ bị "bối rối" (Semantic Ambiguity) trước các điều luật có ý nghĩa tương đồng ở các bộ Luật khác nhau.
- **Vai trò của BM25:** Thuật toán Đối sánh Từ khóa (Lexical Search - BM25) trong Hybrid đóng vai trò như một mỏ neo. Khi câu hỏi chứa các thuật ngữ đặc thù, số hiệu Nghị định, mức phạt cụ thể, BM25 (dựa trên tần suất nghịch đảo IDF) lập tức tính điểm trọng số khổng lồ, ép tài liệu chính xác nhất lên thẳng **Vị trí Top 1**. Việc ưu tiên đẩy đáp án cực chuẩn lên đầu bảng xếp hạng chính là nguyên lý đằng sau chỉ số MRR áp đảo của Hybrid.

### 4.5. TỔNG KẾT (Conclusion)
Từ các luận cứ định lượng và định tính trên, nghiên cứu đi đến kết luận vững chắc: **Trong lĩnh vực Trợ lý AI Pháp lý (Legal Tech) - nơi tính toàn vẹn của văn bản, độ chính xác tuyệt đối và khả năng cập nhật theo thời gian thực là tiên quyết - Hybrid RAG là giải pháp kiến trúc tối ưu và toàn diện nhất hiện nay.** GraphRAG (LightRAG), mặc dù mang giá trị học thuật cao trong việc tổng hợp tri thức mở, lại bộc lộ những nhược điểm chí mạng về chi phí tính toán và làm suy biến tính trung thực của văn bản luật.
