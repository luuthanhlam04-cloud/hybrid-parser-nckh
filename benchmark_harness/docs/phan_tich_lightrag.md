# Phân Tích Chuyên Sâu Về Hệ Thống LightRAG (Hạn Chế & Lỗi Kỹ Thuật)

Tài liệu này tổng hợp các phân tích về hệ thống LightRAG trong quá trình triển khai thực tế trên môi trường Kaggle cho đồ án NCKH, bao gồm các rào cản kỹ thuật đã giải quyết và đánh giá khách quan về hiệu năng.

## 1. Phân Tích Các Vấn Đề Kỹ Thuật (Bugs) Đã Vượt Qua

Trong quá trình đưa LightRAG vào Benchmark, chúng ta đã gặp và giải quyết một loạt các vấn đề nghiêm trọng phản ánh tính thiếu ổn định của các thư viện đồ thị tri thức mới nổi:

### 1.1. Bất đồng bộ môi trường (Lỗi `tiktoken` trên Python 3.13)
- **Vấn đề:** Bản gốc của thư viện `lightrag` sử dụng `tiktoken` phiên bản cũ. Trên Kaggle (sử dụng Python 3.13 rất mới), `tiktoken` không có sẵn file `.wheel` biên dịch sẵn, dẫn đến việc pip phải tự build bằng Rust. Tuy nhiên quá trình biên dịch liên tục thất bại.
- **Giải pháp:** Phải từ bỏ bản `lightrag` cũ, chuyển sang bản fork gốc và được cập nhật liên tục là `lightrag-hku`. Đồng thời, cài đặt trực tiếp bản `tiktoken` mới nhất (đã hỗ trợ Python 3.13) và ép cài `lightrag-hku` bỏ qua phụ thuộc (`--no-deps`).

### 1.2. Phân mảnh kiến trúc (Lỗi import `openai_complete_if_cache`)
- **Vấn đề:** Kiến trúc của `lightrag-hku` thay đổi rất nhanh. Các module xử lý LLM bị chia tách nhỏ gọn hơn. Việc gọi hàm `from lightrag.llm import openai_complete_if_cache` gây ra lỗi `ImportError`.
- **Giải pháp:** Cập nhật lại đường dẫn import chuẩn xác thành `from lightrag.llm.openai import openai_complete_if_cache`.

### 1.3. Khác biệt kiểu dữ liệu ngầm (Lỗi chí mạng `list` vs `numpy.ndarray`)
- **Vấn đề:** Khi tuỳ chỉnh hàm băm vector (`EmbeddingFunc`) cho LightRAG bằng mô hình BGE-M3 (chạy local trên GPU), hàm trả về kiểu `list[list[float]]`. Tuy nhiên, cơ sở dữ liệu nội bộ của LightRAG (NanoVectorDB) lại được hardcode (lập trình cứng) để tính toán số chiều vector bằng thuộc tính `.size` của `numpy.ndarray`. Điều này khiến toàn bộ quá trình Indexing sụp đổ với lỗi `'list' object has no attribute 'size'`.
- **Giải pháp:** Bỏ thao tác ép kiểu `.tolist()` và đảm bảo hàm `embedding_func` trả về nguyên bản một mảng Numpy 2D.

## 2. Phân Tích Điểm Yếu Cốt Lõi: Tốc Độ & Chi Phí (Indexing Bottleneck)

Bên cạnh các vấn đề về kỹ thuật phần mềm, bản thân thuật toán của LightRAG bộc lộ một nhược điểm chí mạng về mặt hiệu suất khi áp dụng vào thực tế: **Nút thắt cổ chai ở khâu Xây dựng Đồ thị (Indexing).**

### 2.1. Cơ chế hoạt động tốn kém
Khác với VectorRAG hay HybridRAG (chỉ sử dụng thuật toán toán học TF-IDF/BM25 hoặc mạng nén Vector cực nhanh trên GPU nội bộ), LightRAG phải trải qua bước Trích xuất Thực thể (Entity Extraction).
- Với mỗi một đoạn văn bản (chunk) của văn bản luật, LightRAG **bắt buộc phải gửi toàn bộ đoạn văn bản đó lên LLM (GPT-4o-mini)**.
- LLM sau đó phải đọc hiểu, suy luận và nhả ra các danh từ (Entity) và mối liên hệ (Relation) giữa chúng.

### 2.2. Hậu quả thực tế
- **Thời gian (Chậm):** Việc nạp 500 điều luật bằng VectorRAG chỉ mất vỏn vẹn **2 phút** do GPU xử lý cục bộ. Ngược lại, LightRAG phải chờ API của OpenAI/OpenRouter phản hồi hàng ngàn lần. Quá trình này rất chậm, có thể mất hàng giờ đồng hồ cho một tập dữ liệu trung bình.
- **Chi phí (Đắt đỏ):** Kể cả khi chưa hỏi bất kỳ câu hỏi nào, hệ thống đã tiêu tốn hàng triệu token đầu vào và đầu ra chỉ để "học" dữ liệu. Nếu sử dụng các mô hình cấp cao (như GPT-4o), chi phí để Indexing có thể lên tới hàng trăm đô la cho một kho dữ liệu doanh nghiệp nhỏ. (Rất may mắn trong NCKH này, chúng ta dùng GPT-4o-mini nên chi phí chỉ ở mức $0.5 - $1.0).

## 3. Cơ Chế Lưu Trữ & "Cứu Cánh" Của LightRAG

Mặc dù việc xây dựng đồ thị ban đầu vô cùng gian nan, LightRAG có một cơ chế **Caching thông minh** để bù đắp:

1. **Lưu trữ cục bộ:** Mọi thực thể, vector, và đồ thị sau khi tốn tiền gọi LLM đều được lưu cứng vào ổ đĩa (thư mục `lightrag_workspace`).
2. **Tránh lặp việc (Deduplication):** Khi hệ thống khởi động lại và được lệnh nạp (Insert) lại 500 điều luật cũ, hàm băm (Hash) của LightRAG sẽ kiểm tra. Nếu phát hiện văn bản không thay đổi, nó sẽ **bỏ qua toàn bộ bước gọi LLM tốn kém**, giúp tiết kiệm 100% chi phí và thời gian ở các lần khởi động sau.
3. **Hiệu suất truy vấn:** Một khi đã xây xong đồ thị, thời gian trả lời 1 câu hỏi (Query) của LightRAG diễn ra rất nhanh, hoàn toàn có thể so sánh ngang ngửa với VectorRAG, nhưng chất lượng ngữ cảnh (Context) mang lại có tính kết nối cao cấp hơn hẳn.

## 4. Kết Luận
Đưa LightRAG vào bài Benchmark là một quyết định vô cùng đắt giá cho báo cáo NCKH. Dữ liệu từ thực nghiệm này sẽ chứng minh một luận điểm quan trọng trong báo cáo:
> *"GraphRAG/LightRAG mang lại tiềm năng kết nối thông tin tuyệt vời, nhưng rào cản quá lớn về chi phí và thời gian Indexing (cần LLM trích xuất) khiến nó khó trở thành giải pháp thay thế hoàn toàn cho VectorRAG trong các hệ thống cần cập nhật dữ liệu pháp luật thời gian thực (Real-time update)."*

## 5. Phân Tích Sự Chênh Lệch Dữ Liệu Thực Nghiệm (Benchmark Analysis)

Sau khi chạy toàn vẹn bộ 512 câu hỏi, kết quả thu về gây bất ngờ lớn nhưng lại cực kỳ có giá trị để bảo vệ luận án khoa học:

### 5.1. Tại sao LightRAG KHÔNG THỂ đo lường Recall và MRR?
Trong kết quả đo lường, chỉ số Recall@5 và MRR@5 của LightRAG đều bị gán là **N/A**. Lý do cốt lõi xuất phát từ kiến trúc của GraphRAG:
- **Vector & Hybrid:** Tìm kiếm và trả về nguyên bản các đoạn văn bản (chunks) chứa `article_id` cụ thể. Do đó, ta có thể đối chiếu trực tiếp `retrieved_ids` với `ground_truth_ids` để tính Recall và MRR.
- **LightRAG (GraphRAG):** Không truy xuất văn bản thô. Thay vào đó, nó duyệt qua Đồ thị Tri thức để nhặt ra các **Thực thể (Entities)** và **Mối quan hệ (Relations)**, sau đó trộn chúng lại thành một đoạn văn cảnh tổng hợp (Synthesized Context). Không tồn tại một ánh xạ 1-1 nào giữa đoạn văn cảnh này với `article_id` ban đầu. Việc ép đo lường Recall/MRR trên LightRAG là sai về mặt phương pháp học khoa học.

### 5.2. Giải mã sự "Sụp hầm" của LightRAG (Faithfulness = 39.7%)
LightRAG vốn được quảng cáo rất mạnh, nhưng tại sao độ trung thực (Faithfulness) lại rớt thảm hại xuống mức ~39.7%, trong khi Vector/Hybrid đạt >92%?
- **Bản chất của Dữ liệu Pháp luật:** Luật pháp Việt Nam (và thế giới nói chung) đòi hỏi sự **chính xác tuyệt đối về mặt từ ngữ, cấu trúc và ngữ cảnh**. Một điều luật chỉ có tác dụng khi nó đi kèm với các điều kiện loại trừ, khoản, điểm rõ ràng.
- **Điểm yếu của GraphRAG trong miền Pháp luật:** Khi LightRAG "băm" điều luật ra để trích xuất thực thể, nó đã phá vỡ hoàn toàn cấu trúc ngữ pháp và tính ràng buộc chặt chẽ của văn bản luật pháp. Ngữ cảnh LLM nhận được từ Đồ thị chỉ là các cụm từ chắp vá (ví dụ: *Tội phạm -> Bị phạt -> 5 năm*), thiếu đi bối cảnh nguyên vẹn. Hậu quả là LLM sinh ra câu trả lời sai lệch, ảo giác (Hallucination), hoặc không bám sát luật, dẫn đến điểm Faithfulness cực thấp.

### 5.3. Tại sao Hybrid RAG nhỉnh hơn Vector RAG ở MRR?
Mặc dù cả hai đều có độ trung thực cực cao (trên 92%), Hybrid RAG đạt **MRR@5 = 0.8796**, vượt trội hơn Vector RAG (0.8407).
- **Lý do:** Vector RAG (Semantic Search) thỉnh thoảng bị "nhầm lẫn" khi các điều luật có ý nghĩa na ná nhau nhưng khác số hiệu. Khi kết hợp thêm thuật toán từ khoá BM25 (đặc trưng của Hybrid), hệ thống bắt đúng chính xác số hiệu Điều/Luật hoặc các thuật ngữ chuyên ngành hẹp, giúp đẩy tài liệu chính xác nhất lên ngay vị trí Top 1 (tối ưu chỉ số MRR). Điều này chứng minh Hybrid là phương pháp cân bằng và tối ưu nhất cho văn bản pháp luật hiện tại.
