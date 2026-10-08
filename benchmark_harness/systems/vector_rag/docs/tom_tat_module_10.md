# Tóm tắt và Đánh giá Kiến trúc Module 10 (Graph Retrieval Engine)

Module 10 đóng vai trò là lõi truy xuất đồ thị (Retrieval Engine) trong kiến trúc RAG, làm cầu nối giữa kho tri thức pháp lý hợp nhất (Unified Knowledge Graph - UKG) trên Neo4j và mô hình ngôn ngữ sinh tạo (LLM). 

Mục tiêu cốt lõi của M10 là cung cấp cơ chế truy xuất có kiểm soát (Control Variable) để đối chứng hiệu năng giữa 2 phương pháp: Khai phá đồ thị định hướng theo cấu trúc quy phạm (Norm-aware - Mode A) và Khai phá vét cạn theo bán kính (Naïve K-hop - Mode B).

---

## I. Luồng Workflow Từng File

Module 10 được tổ chức theo kiến trúc Pipeline rành mạch, tuân thủ nguyên tắc Single Responsibility (Đơn nhiệm):

1. **`run_m10.py` (Entry Point):** 
   - Khởi tạo kết nối tới Neo4j và LLM (thông qua API Key).
   - Tiếp nhận câu hỏi pháp lý từ CLI (Terminal).
   - Kích hoạt `M10Pipeline` và in kết quả (câu trả lời + ngữ cảnh) ra màn hình.

2. **`m10_pipeline.py` (Orchestrator):** 
   - Điều phối toàn bộ vòng đời của một truy vấn (Query Lifecycle).
   - Quy trình: Nhận câu hỏi $\rightarrow$ Gọi `AnchorSearch` tìm mỏ neo $\rightarrow$ Gọi `GraphQuery` khai phá đồ thị (Mode A/B) $\rightarrow$ Gọi `ContextAssembler` định dạng văn bản $\rightarrow$ Gọi `AnswerGenerator` sinh câu trả lời.
   - Ghi lại log (JSONL) toàn bộ quá trình để phục vụ cho Module 11 (Evaluation).

3. **`anchor_search.py` (Vector Search):** 
   - Chuyển đổi câu hỏi (Query) thành Vector nhúng (Embedding) bằng mô hình `SentenceTransformer`.
   - Thực thi Cypher `CALL db.index.vector.queryNodes` trên Neo4j để tìm ra Top-K các nút vật lý (`LegalNode`) có độ tương đồng ngữ nghĩa cao nhất làm mỏ neo (Anchor).

4. **`graph_query.py` (Cypher Graph Traversal):** 
   - Chịu trách nhiệm duyệt đồ thị từ các nút mỏ neo.
   - **Mode A (NormAssertion-Aware):** Dùng Cypher để đi từ `LegalNode` lên `GLOBAL_NORM` tương ứng, rồi bóc tách cấu trúc 8 nhánh chuẩn Hohfeld (Chủ thể, Hành vi, Điều kiện, Ngoại lệ, Chế tài...).
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
   - *Mode A:* Thuật toán thông minh tự động leo lên Tầng 2 để lấy cái "Đầu não" (Nút `GLOBAL_NORM`), sau đó "bắt" toàn bộ các cánh tay của nó (Điều kiện, Ngoại lệ). Cách này triệt tiêu tình trạng RAG thông thường lấy được câu luật nhưng bỏ sót câu điều kiện nằm ở Khoản/Điểm khác.
   - *Mode B:* Thuật toán "ngây thơ" lấy tất cả các nút nối trực tiếp với độ sâu 1-2 bước.

3. **Bước 3: Lấy bằng chứng (Evidence Retrieval)**
   Sau khi dựng xong sơ đồ logic pháp lý, M10 truy ngược về Tầng 1 để lấy nguyên văn đoạn luật thô (`anchor_text`) làm bằng chứng cho LLM.

---

## III. Các Vấn đề Tồn đọng & Cách M10 Giải quyết

Dưới góc nhìn kiến trúc, M10 đã lường trước và xử lý một số bài toán, đồng thời vẫn còn tồn tại các vấn đề phát sinh từ môi trường:

### 1. Vấn đề Tràn Ngữ cảnh (Context Overflow)
* **Vấn đề:** Nếu một mỏ neo có quá nhiều nút lân cận, lượng Text sinh ra từ đồ thị sẽ vượt quá giới hạn Token của LLM, gây lỗi API hoặc làm giảm khả năng tập trung (Lost-in-the-middle).
* **Cách M10 giải quyết:** `ContextAssembler` áp dụng cơ chế Hard-bound (Cắt cụt cứng) thông qua thuộc tính `max_chars = 16000`. Khi vượt ngưỡng, hệ thống sẽ tự động chèn cờ `[Ngữ cảnh đã được giới hạn.]` để LLM biết.

### 2. Vấn đề Ảo giác Quy phạm (Normative Hallucination)
* **Vấn đề:** LLM rất dễ nhầm lẫn Giữa "Bị Cấm" (Prohibit) và "Được phép" (Allow) nếu đọc văn bản luật rườm rà.
* **Cách M10 giải quyết:** Ở Mode A, `ContextAssembler` đã "nhai sẵn" cấu trúc và gán nhãn rõ ràng: `Quy tắc 1: ĐƯỢC PHÉP / BỊ CẤM / BẮT BUỘC`, giúp LLM định hình tư duy logic trước khi sinh câu trả lời. LLM được set `temperature = 0.0`.

### 3. Cảnh báo Cú pháp Cypher Cũ (`warn: feature deprecat`)
* **Vấn đề:** Trong log bạn gửi, Neo4j ném ra thông báo `gql_status='01N00', status_description='warn: feature deprecat'`.
* **Nguyên nhân:** Lệnh `CALL db.index.vector.queryNodes` trong `anchor_search.py` (dòng 74) là cú pháp cũ. 
* **Tác động:** Đây chỉ là cảnh báo (Warning), không làm sập luồng chạy, dữ liệu vẫn được truy xuất bình thường (nếu có).

### 4. Vấn đề 0 Nodes / Trống Dữ liệu & Lỗi Encoding PowerShell (Lỗi Hiện tại của bạn)
* **Vấn đề:** M10 trả về `0 nodes` và LLM trả lời "Không tìm thấy quy phạm". 
* **Nguyên nhân 1 (Lệch Dimension của Vector Index):** Lần trước M9 đã đẩy embedding 896 chiều lên Neo4j. Nhưng Neo4j của bạn vẫn đang ôm khư khư cái Vector Index cũ (768 chiều). Vì dùng lệnh `CREATE INDEX ... IF NOT EXISTS` nên Neo4j đã từ chối cập nhật cái mới. Do đó, Vector Search không tìm thấy gì cả.
* **Nguyên nhân 2 (Lỗi Encoding Terminal):** Trong log, câu hỏi của bạn bị biến thành `"Di?u ki?n d? bán..."`. Dấu hỏi (`?`) xuất hiện do PowerShell không dùng mã hóa UTF-8 chuẩn, khiến mô hình SentenceTransformer đọc thành một câu vô nghĩa, sinh ra vector rác $\rightarrow$ Không tìm được Anchor tương đồng.

**💡 Giải pháp cho 2 vấn đề trên:**
1. **Fix Vector Index:** Vào Neo4j Browser chạy lệnh sau để xóa Index cũ, sau đó chạy lại `run_neo4j_ingestion.py`:
   ```cypher
   DROP INDEX legal_node_vector_idx
   ```
2. **Fix PowerShell Encoding:** Trước khi chạy `run_m10.py`, hãy gõ lệnh này vào Terminal để ép UTF-8:
   ```powershell
   [console]::InputEncoding = [console]::OutputEncoding = New-Object System.Text.UTF8Encoding
   ```
