# Tóm tắt và Đánh giá Kiến trúc Module 10 (Graph Retrieval Engine)

Module 10 đóng vai trò là lõi truy xuất đồ thị (Retrieval Engine) trong kiến trúc RAG, làm cầu nối giữa kho tri thức pháp lý hợp nhất (Unified Knowledge Graph - UKG) trên Neo4j và mô hình ngôn ngữ sinh tạo (LLM). 

Mục tiêu cốt lõi của M10 là cung cấp cơ chế truy xuất có kiểm soát (Control Variable) để đối chứng hiệu năng giữa 2 phương pháp: Khai phá đồ thị định hướng theo cấu trúc quy phạm (Norm-aware - Mode A) và Khai phá vét cạn theo bán kính (Naïve K-hop - Mode B).

---

## I. Luồng Workflow Từng File

Module 10 được tổ chức theo kiến trúc Pipeline rành mạch, tuân thủ nguyên tắc Single Responsibility (Đơn nhiệm):

1. **`run_m10.py` (Entry Point):** 
   - Khởi tạo kết nối tới Neo4j và LLM (thông qua API Key).
   - Tiếp nhận câu hỏi pháp lý từ CLI (Terminal).
   - Kích hoạt `M10Pipeline` với chế độ mặc định `mode="AUTO"` (hoặc chỉ định A, B) và in kết quả (câu trả lời + ngữ cảnh) ra màn hình.

2. **`m10_pipeline.py` (Orchestrator):** 
   - Điều phối toàn bộ vòng đời của một truy vấn (Query Lifecycle).
   - Quy trình: Nhận câu hỏi $\rightarrow$ Gọi `AnchorSearch` tìm mỏ neo $\rightarrow$ Gọi `GraphQuery` khai phá đồ thị (hỗ trợ Adaptive Fallback ở chế độ AUTO) $\rightarrow$ Gọi `ContextAssembler` định dạng văn bản $\rightarrow$ Gọi `AnswerGenerator` sinh câu trả lời.
   - Ghi lại log (JSONL) toàn bộ quá trình để phục vụ cho Module 11 (Evaluation).

3. **`anchor_search.py` (Vector Search):** 
   - Chuyển đổi câu hỏi (Query) thành Vector nhúng (Embedding) bằng mô hình `SentenceTransformer`.
   - Thực thi Cypher `CALL db.index.vector.queryNodes` trên Neo4j để tìm ra Top-K các nút vật lý (`LegalNode`) có độ tương đồng ngữ nghĩa cao nhất làm mỏ neo (Anchor).

4. **`graph_query.py` (Cypher Graph Traversal):** 
   - Chịu trách nhiệm duyệt đồ thị từ các nút mỏ neo.
   - **Mode A (NormAssertion-Aware với Hierarchical Traversal):** Dùng Cypher để đi từ `LegalNode` (kể cả lần ngược/xuôi qua quan hệ phân cấp `[:BELONG_TO*0..3]`) lên `GLOBAL_NORM` tương ứng, rồi bóc tách cấu trúc 8 nhánh chuẩn Hohfeld (Chủ thể, Hành vi, Điều kiện, Ngoại lệ, Chế tài...).
   - **Mode B (K-hop):** Duyệt cơ học mọi nút lân cận trong bán kính `max_hops = 2` không màng đến cấu trúc logic.

5. **`context_assembler.py` (Context Formatting):** 
   - Chuyển hóa kết quả trả về từ đồ thị (JSON/Dict) thành văn bản tự nhiên (Plain Text Context) để nhồi vào Prompt cho LLM.
   - Cung cấp cơ chế tự động giới hạn chiều dài ngữ cảnh (`max_chars=16000`) để bảo vệ Context Window.
   - Trình bày mạch lạc theo dạng: "Chủ thể: ...", "Hành động: ...", "Điều kiện: ...".

6. **`answer_generator.py` (LLM Integration):** 
   - Sử dụng OpenAI API (mặc định là `gpt-4o-mini`, nhiệt độ $T=0$) để sinh câu trả lời.
   - Hệ thống Prompt tuân thủ "Four Corners Rule" (chỉ trả lời dựa trên ngữ cảnh, không bịa đặt).

---

## II. Cách thức Truy xuất Dữ liệu của M10

Cơ chế truy xuất của M10 kết hợp cả **Semantic Search (Tìm kiếm ngữ nghĩa)** và **Graph Traversal (Khai phá đồ thị)**, tạo ra hệ thống **Hybrid RAG**:

1. **Bước 1: Tìm Mỏ neo (Anchor Search - Tầng 1)**
   M10 không truy vấn trực tiếp vào các nút quy phạm (Tầng 2). Thay vào đó, nó tận dụng Vector Index trên Tầng 1 (các `LegalNode` chứa văn bản luật nguyên thủy) để dò tìm những đoạn luật liên quan đến câu hỏi.

2. **Bước 2: Mở rộng Ngữ cảnh (Graph Expansion - Tầng 2)**
   Sau khi đã có "tọa độ" (Anchor), M10 dùng Cypher để nội suy ngữ cảnh:
   - *Mode A:* Thuật toán thông minh leo lên Tầng 2 để lấy "Đầu não" (`GLOBAL_NORM`), tự động lần theo phân cấp cấu trúc `[:BELONG_TO*0..3]` nếu anchor là nút cấp cao, sau đó gom toàn bộ các nhánh logic (Điều kiện, Ngoại lệ). Cách này giải quyết triệt để tình trạng RAG truyền thống lấy được câu luật nhưng sót điều kiện ở Khoản/Điểm khác.
   - *Mode B:* Thuật toán láng giềng lấy tất cả các nút kết nối trực tiếp trong bán kính 1-2 bước nhảy.

3. **Bước 3: Lấy bằng chứng (Evidence Retrieval)**
   Sau khi dựng xong sơ đồ logic pháp lý, M10 truy ngược về Tầng 1 để lấy nguyên văn đoạn luật thô (`anchor_text` / `evidence`) làm bằng chứng cho LLM.

---

## III. Các Vấn đề Tồn đọng & Cách M10 Giải quyết

Dưới góc nhìn kiến trúc, M10 đã lường trước và xử lý các bài toán cốt lõi:

### 1. Vấn đề Tràn Ngữ cảnh (Context Overflow)
* **Vấn đề:** Nếu một mỏ neo có quá nhiều nút lân cận, lượng Text sinh ra từ đồ thị sẽ vượt quá giới hạn Token của LLM, gây lỗi API hoặc làm giảm khả năng tập trung (Lost-in-the-middle).
* **Cách M10 giải quyết:** `ContextAssembler` áp dụng cơ chế Hard-bound (Cắt cụt cứng) thông qua thuộc tính `max_chars = 16000`. Khi vượt ngưỡng, hệ thống sẽ tự động chèn cờ `[Ngữ cảnh đã được giới hạn.]` để LLM biết.

### 2. Vấn đề Ảo giác Quy phạm (Normative Hallucination)
* **Vấn đề:** LLM rất dễ nhầm lẫn giữa "Bị cấm" (Prohibit) và "Được phép" (Allow) nếu đọc văn bản luật rườm rà.
* **Cách M10 giải quyết:** Ở Mode A, `ContextAssembler` đã cấu trúc hóa và gán nhãn rõ ràng: `Quy tắc 1: ĐƯỢC PHÉP / BỊ CẤM / BẮT BUỘC`, giúp LLM định hình tư duy logic trước khi sinh câu trả lời. LLM được set `temperature = 0.0`.

### 3. Cảnh báo Cú pháp Cypher Cũ (`warn: 01N00`) & Thuộc tính Không Tồn Tại (`01N52`)
* **Vấn đề:** 
  - Neo4j ném cảnh báo deprecation `01N00` do subquery CALL thiếu khai báo biến scope (`CALL { WITH norm ... }`).
  - Cảnh báo `01N52` do thuộc tính `preferred_name` không tồn tại đồng nhất trên các node thực thể.
* **Cách M10 giải quyết (Đã cập nhật tại `src/retrieval/graph_query.py`):**
  - Chuẩn hóa toàn bộ subquery sang cú pháp Neo4j mới: `CALL (norm) { ... }`, loại bỏ hoàn toàn cảnh báo `01N00`.
  - Thay thế việc truy xuất cứng bằng hàm an toàn đa tầng: `coalesce(entity.canonical_text, entity.name, entity.id)`, khắc phục triệt để lỗi `preferred_name`.

### 4. Vấn đề Mỏ Neo Cấp Cao Bị Trống Quy Phạm (Hierarchical Traversal)
* **Vấn đề:** Khi vector search trả về một node mỏ neo là node phân cấp cao (như Chương, Mục, hoặc Điều), bản thân node này thường không gắn trực tiếp nhãn `GLOBAL_NORM` (vốn được trích xuất ở cấp Khoản/Điểm), dẫn đến Mode A trả về 0 nodes.
* **Cách M10 giải quyết (Đã cập nhật tại `src/retrieval/graph_query.py`):**
  - Nâng cấp `MODE_A_QUERY` với cơ chế **Hierarchical Traversal**: Sử dụng quan hệ phân cấp `[:BELONG_TO*0..3]` để tự động lần xuống các node con cháu (Khoản, Điểm) của Anchor Node và gom trọn vẹn các `GLOBAL_NORM` liên đới.

### 5. Cơ chế Thích ứng Dự phòng: Chế độ `AUTO` (Adaptive Fallback)
* **Vấn đề:** Trong thực tế, có những phân đoạn luật chưa được trích xuất hoàn thiện quan hệ quy phạm Norm Assertion hoặc câu hỏi mang tính tổng quan cấu trúc, khiến Mode A trả về 0 nodes và LLM thụ động kết luận "chưa đủ căn cứ".
* **Cách M10 giải quyết (Đã cập nhật tại `src/retrieval/m10_pipeline.py` & `run_m10.py`):**
  - Bổ sung và đặt chế độ mặc định là `mode="AUTO"`.
  - **Quy trình hoạt động:**
    1. Ưu tiên thực thi **Mode A** (Norm-aware) để bóc tách tri thức logic quy phạm chuẩn xác nhất.
    2. Nếu Mode A tìm thấy quy phạm $\rightarrow$ Trả lời ngay theo Mode A.
    3. Nếu Mode A trả về 0 nodes $\rightarrow$ Tự động Fallback tức thì sang **Mode B** (K-hop Structural Traversal) để lấy ngữ cảnh láng giềng.
    4. Cơ chế này đảm bảo hệ thống luôn có câu trả lời đầy đủ, khai thác tối đa cấu trúc đồ thị và triệt tiêu tình trạng rỗng ngữ cảnh.

---

## IV. Các Lưu Ý Về Môi Trường & Thực Thi

1. **Đồng bộ Vector Index với Model Embedding:**
   - Nếu thay đổi model embedding (ví dụ chuyển giữa 768 chiều và 896 chiều), cần drop index cũ trên Neo4j bằng lệnh `DROP INDEX legal_node_vector_idx` trước khi chạy ingestion mới.
2. **Thiết lập UTF-8 trên Windows PowerShell:**
   - Cần kích hoạt môi trường UTF-8 để tránh câu hỏi tiếng Việt bị lỗi font (biến thành ký tự `?` gây sai lệch embedding):
     ```powershell
     $env:PYTHONUTF8=1
     ```
