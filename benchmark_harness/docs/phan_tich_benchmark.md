# BÁO CÁO PHÂN TÍCH BENCHMARK TOÀN DIỆN (Dành cho Viết Luận văn)

Tài liệu này tổng hợp toàn bộ quy trình luận chứng, xây dựng dữ liệu, khắc phục sự cố kỹ thuật và phân tích kết quả thực nghiệm để đưa vào chương "Phương pháp nghiên cứu" và "Đánh giá kết quả" của báo cáo NCKH.

## PHẦN 1: PHƯƠNG PHÁP NGHIÊN CỨU & XÂY DỰNG DỮ LIỆU (DATASET)

### 1.1. Khởi nguồn dữ liệu & Quyết định loại bỏ các bộ Benchmark cũ
- **Vấn đề của bộ VMTEB (Vietnamese Massive Text Embedding Benchmark):** Ban đầu, nhóm dự định sử dụng tập dữ liệu chuẩn VMTEB. Tuy nhiên, qua quá trình kiểm toán (Audit Data), chúng tôi phát hiện lỗi Data Leakage nghiêm trọng (Câu hỏi chứa nguyên si câu trả lời), định dạng Parquet rườm rà, và các câu hỏi mang tính chất "nhồi nhét từ khóa" (Keyword-stuffed) thay vì câu hỏi tự nhiên của người dùng (Natural User Queries).
- **Vấn đề của các bộ dữ liệu nội bộ cũ:** Các file `qa_dataset.json` cũ được sinh ra tự động nhưng chứa nhiều câu trả lời (ground truth) bị rỗng hoặc trỏ sai ID bài viết, dẫn đến việc tính toán các chỉ số khắt khe như Recall và MRR sẽ bị sai lệch hoàn toàn.
- **Quyết định:** Loại bỏ (Reject) toàn bộ dữ liệu rác, chỉ giữ lại bộ Corpus gồm hơn 3.3 triệu ký tự văn bản Luật chuẩn, và tiến hành xây dựng lại tập câu hỏi từ đầu theo tiêu chuẩn khắt khe hơn.

### 1.2. Phân tích tập dữ liệu Benchmark hiện tại (Golden Dataset)
Để đảm bảo tính khách quan và sát thực tế, tập dữ liệu `benchmark_rewritten.json` (512 câu hỏi) đã được xây dựng theo tiêu chuẩn vàng (Golden Dataset):
- **Phân loại đa dạng:** Bao gồm cả câu hỏi Đơn luồng (Single-hop) đòi hỏi tra cứu trực tiếp một điều luật, và câu hỏi Đa luồng (Multi-hop) đòi hỏi hệ thống tổng hợp từ nhiều nguồn luật khác nhau (Hình sự, Dân sự, Doanh nghiệp).
- **Paraphrasing:** Các câu hỏi được viết lại (Rewritten) để mô phỏng cách hỏi đời thường của người dân (không chứa các từ khóa kỹ thuật pháp lý, dùng từ ngữ dân dã), nhằm thử thách khả năng "hiểu ngữ nghĩa sâu" (Semantic Search) của các hệ thống RAG thay vì chỉ đơn thuần là so khớp từ khóa.

---

## PHẦN 2: CÁC VẤN ĐỀ KỸ THUẬT VÀ NÚT THẮT CỔ CHAI (BOTTLENECKS) CỦA LIGHTRAG

Quá trình đưa hệ thống đồ thị tri thức (GraphRAG / LightRAG) vào thực nghiệm gặp phải vô vàn rào cản kỹ thuật. Đây là điểm nhấn quan trọng chứng minh nỗ lực kỹ thuật xuất sắc của nhóm:

### 2.1. Giải quyết các "Bug" chí mạng của LightRAG
- **Lỗi môi trường & Dependencies:** Trên nền tảng Python 3.13 (đời mới nhất), thư viện `tiktoken` (dùng để đếm token của OpenAI) không thể tự động build bằng Rust. Nhóm phải can thiệp sâu bằng lệnh `pip install --no-deps` và chuyển đổi sang nhánh mã nguồn `lightrag-hku` để hệ thống tương thích hoàn toàn.
- **Xung đột kiểu dữ liệu Cốt lõi (Numpy vs List):** Hàm Embedding BGE-M3 cục bộ trả về kiểu mảng `list`, nhưng cơ sở dữ liệu NanoVectorDB ẩn bên dưới LightRAG lại yêu cầu kiểu `numpy.ndarray` để tính toán khoảng cách vector (gọi thuộc tính `.size`). Nhóm đã phải trực tiếp chỉnh sửa Wrapper để ép kiểu dữ liệu chuẩn, cứu sống toàn bộ quá trình Indexing tránh khỏi lỗi Crash.
- **Lỗi mất trắng dữ liệu:** Kiến trúc bất đồng bộ của LightRAG yêu cầu phải chạy lệnh `asyncio.run(self.rag.initialize_storages())` trước khi nạp (insert) tài liệu. Nếu bỏ sót, hàng tiếng đồng hồ chạy đồ thị sẽ không được ghi vào ổ đĩa. Nhóm đã bổ sung cơ chế Auto-Backup nén thành file ZIP sau mỗi 50 documents để "sinh tồn" trước các rủi ro máy chủ.

### 2.2. Nút thắt cổ chai: Tại sao LightRAG Indexing & Benchmark quá chậm?
- **Vector / Hybrid RAG:** Việc lập chỉ mục (Indexing) 500 văn bản pháp luật lớn chỉ tốn vỏn vẹn **2 phút**. Lý do là mô hình nhúng BGE-M3 (Embedding) và BM25 chạy trực tiếp trên card đồ hoạ (GPU) và CPU nội bộ bằng các phép toán ma trận cực nhanh mà không cần kết nối mạng.
- **LightRAG:** Bị thắt cổ chai trầm trọng bởi **LLM Entity Extraction**. Với mỗi chunk văn bản, LightRAG phải gửi toàn bộ lên API của OpenAI (GPT-4o-mini) để ép LLM đọc, phân tích cú pháp, và trích xuất các Thực thể (Entities) cùng Mối quan hệ (Relations). 
- **Hệ quả thực tế:** Việc gọi API hàng ngàn lần qua internet, cộng thêm giới hạn Rate Limit (429) của nhà cung cấp, khiến thời gian Indexing kéo dài **hàng giờ đồng hồ**, tiêu tốn hàng triệu token. Điều này bộc lộ nhược điểm chí mạng của GraphRAG khi triển khai cho các kho dữ liệu pháp luật khổng lồ và cần cập nhật thường xuyên (Real-time update).

---

## PHẦN 3: KẾT QUẢ THỰC NGHIỆM VÀ PHÂN TÍCH CHUYÊN SÂU (EVALUATION RESULTS)

### 3.1. Bảng số liệu tổng quan (Benchmark Metrics)
| Hệ thống | Số câu hỏi | Faithfulness (Độ trung thực) | Recall@5 | MRR@5 | Tổng chi phí API |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Vector RAG** | 480 | 0.9348 (93.48%) | 0.9375 | 0.8407 | $0.2096 |
| **Hybrid RAG** | **512** | 0.9268 (92.68%) | 0.9316 | **0.8796** | $0.2108 |
| **LightRAG** | **512** | 0.3977 (39.77%) | N/A | N/A | $0.1101 |

*(Ghi chú: Recall và MRR của LightRAG được đánh dấu N/A do không thể áp dụng phương pháp đo lường ID văn bản thô).*

### 3.2. Phân tích chi tiết: Tại sao có sự chênh lệch khổng lồ?

#### 1. Sự "Sụp hầm" của LightRAG (Faithfulness = 39.7%)
LightRAG vốn là một kiến trúc tiên tiến, nhưng tại sao độ trung thực (Faithfulness) lại rớt thảm hại xuống mức ~39.7%, trong khi Vector/Hybrid đạt mức xuất sắc >92%?
- **Đặc thù của Dữ liệu Pháp luật:** Luật pháp Việt Nam đòi hỏi sự **chính xác tuyệt đối về mặt từ ngữ, cấu trúc và tính nguyên vẹn của văn bản**. Một điều luật chỉ có giá trị khi nó đi kèm với các điều kiện loại trừ, khoản, điểm được liệt kê rõ ràng trong cùng một văn bản.
- **Điểm yếu chí mạng của GraphRAG trong miền Pháp lý:** Khi LightRAG tiến hành "băm" điều luật ra để tạo Đồ thị Tri thức (Knowledge Graph), nó đã phá vỡ hoàn toàn cấu trúc ngữ pháp và tính nguyên vẹn của văn bản luật pháp. Ngữ cảnh mà hệ thống nhặt ra từ Đồ thị và cung cấp cho LLM trả lời chỉ là các mảnh ghép rời rạc (Ví dụ: *Tội phạm -> Bị phạt -> 5 năm*), thiếu đi bối cảnh ràng buộc. Hậu quả là LLM sinh ra ảo giác (Hallucination), tự chắp vá thông tin sai lệch dẫn đến điểm Trung thực chạm đáy.

#### 2. Tại sao LightRAG không có Recall và MRR?
Việc thiết kế phương pháp luận đo lường Recall và MRR đối với LightRAG là bất khả thi:
- **Vector & Hybrid:** Các hệ thống này truy xuất và trả về nguyên khối văn bản (chunks) được gán mã số `article_id` cụ thể. Do đó, thuật toán đánh giá có thể đối chiếu trực tiếp tập `retrieved_ids` với tập đáp án `ground_truth_ids` để tính Recall và MRR một cách toán học.
- **LightRAG (GraphRAG):** Thuật toán này không truy xuất văn bản thô. Thay vào đó, nó duyệt qua Đồ thị để gom nhặt các **Entities** và **Relations**, sau đó trộn chúng lại thành một đoạn văn cảnh tổng hợp (Synthesized Context). Không tồn tại một ánh xạ 1-1 nào giữa đoạn văn cảnh nhân tạo này với các `article_id` ban đầu. Do đó, việc ép đo lường Recall/MRR trên LightRAG là sai lệch về mặt khoa học.

#### 3. Sự Vượt Trội Của Hybrid RAG (Vô địch MRR)
Cả Vector RAG và Hybrid RAG đều cung cấp nguyên văn điều luật cho LLM, do đó duy trì mức độ chính xác cực cao (>92%). Tuy nhiên, **Hybrid RAG chứng tỏ sự vượt trội hoàn toàn về chỉ số MRR (0.8796 so với 0.8407 của Vector)**.
- **Lý giải:** Vector RAG (Semantic Search) vượt trội trong việc hiểu ý nghĩa, nhưng đôi khi bị "bối rối" trước các điều luật có ý nghĩa na ná nhau nằm rải rác ở các bộ Luật/Nghị định khác nhau. Hybrid RAG khắc phục triệt để điểm mù này nhờ sự bổ trợ của thuật toán **BM25 (Đối sánh Từ khóa)**. Khi người dùng đưa ra các từ khoá hẹp (như số hiệu Nghị định, mức phạt cụ thể, mã số điều luật), BM25 lập tức tính toán độ hiếm (IDF) và ép bài viết đúng nhất lên thẳng **vị trí Top 1**. Việc ưu tiên đẩy đáp án đúng lên đầu tiên chính là lý do khiến chỉ số MRR của Hybrid đạt mức tối ưu.

### 3.3. TỔNG KẾT (Conclusion)
Dữ liệu từ thực nghiệm quy mô lớn đã chứng minh một cách định lượng và học thuật rằng: **Đối với miền tri thức Pháp luật** - nơi đòi hỏi tính chính xác tuyệt đối về mặt văn bản, cấu trúc nguyên vẹn và tốc độ cập nhật Real-time - **Hybrid RAG là giải pháp toàn diện và tối ưu nhất**. 
Trong khi đó, GraphRAG/LightRAG, mặc dù mang lại tiềm năng kết nối thông tin đa luồng trong các văn bản mở (tiểu thuyết, báo chí), lại hoàn toàn không phù hợp với văn bản pháp lý. Rào cản khổng lồ về chi phí Indexing kết hợp với việc làm suy giảm cấu trúc ngôn ngữ luật gốc đã khiến hệ thống này sinh ra hiện tượng Hallucination nghiêm trọng, không đáp ứng được tiêu chuẩn khắt khe của hệ thống trợ lý pháp lý AI.
