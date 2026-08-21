# Tổng kết Module 2 - Regex Parser (Cập nhật mới nhất)

Module 2 đóng vai trò là lõi trích xuất cấu trúc (Structural Parser) cho hệ thống Hybrid Parser của GraphRAG Văn bản Pháp luật Việt Nam. Nhiệm vụ chính của module là chuyển đổi văn bản luật thô (đã qua làm sạch) hoặc văn bản DOCX thành một mảng các node JSON có cấu trúc phân cấp chặt chẽ, phục vụ cho việc xây dựng đồ thị ở các module sau.

## 1. Công nghệ và Nguyên tắc thiết kế
- **Ngôn ngữ & Thư viện:** Python 3, `pydantic` (để Data Modeling và Validation), `re` (Regex tiêu chuẩn của Python).
- **Nguyên tắc:** 
  - **100% Rule-based & Deterministic:** Không sử dụng AI/LLM hay mô hình nhúng (Embeddings) để đảm bảo độ chính xác tuyệt đối, tốc độ cao và tính lặp lại.
  - **Lenient Parser, Strict Data Model:** Chấp nhận đầu vào có thể có chút bất thường (như mất định dạng số), nhưng đầu ra bắt buộc tuân thủ Data Contract của Pydantic.
  - **Pattern Taxonomy & Metadata:** Các rules Regex đều được phân loại dựa trên Corpus thực tế (vd: `[CORPUS: Ch3-LDD]`) và có độ tin cậy rõ ràng (`HIGH`, `HYPOTHESIS`).

## 2. Vai trò và Workflow của từng file

Kiến trúc mới (sau khi refactor nhánh `lâm_module_2`) phân tách trách nhiệm (Separation of Concerns) cực kỳ rõ ràng theo mô hình Pipeline:
`parser.py` -> `regex_engine.py` -> `boundary_detector.py` -> `hierarchy_builder.py` -> `node_generator.py`

- **`regex_engine.py`**:
  - *Vai trò:* Lớp 2 (Text Signal) nhận diện dấu hiệu. Chứa `Pattern Registry` (từ điển mẫu) và `DOCX_NUMBERING_HINTS`. Định nghĩa `NodeType` (CHAPTER, SECTION, ARTICLE, CLAUSE, POINT).
  - *Workflow:* Quét qua từng dòng văn bản hoặc paragraph, kết hợp cả Regex và tín hiệu từ Word Style/Numbering (nếu có) để trả về `MatchResult` (chứa vị trí, marker, text, node_type).

- **`boundary_detector.py`**:
  - *Vai trò:* Xác định ranh giới vật lý (start/end) của các Node.
  - *Workflow:* Sử dụng thuật toán Stack-based. Khi gặp một marker mới, nếu depth của nó nhỏ hơn hoặc bằng node hiện tại thì đóng node cũ và mở node mới. Nếu không có marker, dòng text sẽ được gộp vào `content_lines` của node đang mở.
  - *Cập nhật mới:* Tính toán chính xác vị trí ký tự tuyệt đối (`char_start` - zero-based absolute offset) cộng dồn từ toàn bộ văn bản để phục vụ cấp phát Hybrid ID.

- **`hierarchy_builder.py`**:
  - *Vai trò:* Linear text → Tree structure. Xây dựng quan hệ Parent-Child.
  - *Workflow:* Tiếp tục dùng Stack để track parent theo depth. Pop stack cho đến khi tìm được parent có depth hợp lệ. Thiết lập `parent_node` (object reference để tránh nhầm lẫn ID sau này), gán `position` (thứ tự anh em) và cập nhật `children_ids`.

- **`node_generator.py`**:
  - *Vai trò:* Trái tim của Data Contract. Đóng gói object thành `LegalNode` (Pydantic model) và sinh **Hybrid ID**.
  - *Workflow:* Dựa vào `parent_node` reference, hệ thống tự động sinh ID mà không sợ collision (xem phần Hybrid ID bên dưới). Xuất ra dữ liệu chuẩn để serialize thành JSON.

- **`parser.py` (Main Orchestrator)**:
  - *Vai trò:* Nhạc trưởng điều phối. Hỗ trợ CLI chuẩn mực (`argparse`).
  - *Workflow:* Đọc toàn bộ thư mục (Batch Processing) hoặc 1 file lẻ (`parse_docx`, `parse_text`). Tự động kết hợp 4 module trên, in ra Summary Report và cuối cùng chạy **Fail-Fast Duplicate ID Check** trước khi ghi file JSON ra `outputs/physical_graphs`.

## 3. Các bước tiến lớn và Vấn đề kỹ thuật đã giải quyết (Challenges)

1. **Hỗ trợ Batch Processing và CLI (Mới nhất):**
   - Hệ thống giờ đây có thể quét toàn bộ thư mục `outputs/clean_texts` và tự động sinh ra hàng loạt file JSON trong `outputs/physical_graphs` chỉ bằng 1 lệnh duy nhất. Tự động bỏ qua các file không liên quan.

2. **Chuyển đổi từ Heuristic sang Metadata-driven (Lớp 1 & Lớp 2):**
   - *Thực trạng:* Code cũ đoán mò Node dựa vào regex thuần túy.
   - *Giải quyết:* Tận dụng tối đa tín hiệu từ file DOCX gốc (`ilvl`, `num_fmt`, `Word Style`) kết hợp Regex, giúp bắt được cả những Khoản/Điểm bị "mất số" do lỗi format của Word.

3. **Ngăn chặn triệt để Bug nối nhầm Node (Stack-based Architecture):**
   - Thay vì dùng biến trạng thái lỏng lẻo (`active_nodes`), toàn bộ `boundary_detector` và `hierarchy_builder` đều dùng thuật toán cấu trúc dữ liệu Stack (ngăn xếp), đảm bảo cứ gặp node cùng cấp hoặc cấp cao hơn là đóng chính xác node cũ lại, không bao giờ có hiện tượng text bị nuốt nhầm.

4. **Nâng cấp Hybrid ID Generation chống ID Collision (KL-02) (Mới nhất):**
   - *Thực trạng:* Ở văn bản lỗi cấu trúc (vd: mất tầng Khoản), mô hình "Hierarchical ID thuần túy" sẽ sinh ID giống hệt nhau cho 2 Điểm đ) cùng nhận Điều làm cha, dẫn đến ghi đè mất dữ liệu.
   - *Giải quyết:* Nâng cấp lên kiến trúc **Hybrid ID (Position Offset Suffix)** với công thức: `Hybrid_ID = {Hierarchical_Prefix}_p{char_start_index}`. 
   - Node Generator tự động trích xuất `pure_prefix` của cha bằng strict regex `re.sub(r"_p\d+$", "", active_parent_id)`, sau đó gắn chặt offset ký tự tuyệt đối (`char_start`) vào cuối.
   - Kết quả (vd: `doc_chuong-iii_muc-1_dieu-27_diem-d_p1859` và `doc_chuong-iii_muc-1_dieu-27_diem-d_p2306`): ID đảm bảo tính **duy nhất tuyệt đối 100% (Uniqueness)** mà vẫn giữ nguyên **tính giải thích được phân cấp (Explainability)**. Downstream modules (Validation, Neo4j) không hề bị ảnh hưởng.
