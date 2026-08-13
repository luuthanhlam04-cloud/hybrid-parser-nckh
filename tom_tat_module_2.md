# Tổng kết Module 2 - Regex Parser

Module 2 đóng vai trò là lõi trích xuất cấu trúc (Structural Parser) cho hệ thống Hybrid Parser của GraphRAG Văn bản Pháp luật Việt Nam. Nhiệm vụ chính của module là chuyển đổi văn bản luật thô (đã qua làm sạch) thành một mảng các node JSON có cấu trúc phân cấp chặt chẽ, phục vụ cho việc xây dựng đồ thị ở các module sau.

## 1. Công nghệ và Nguyên tắc thiết kế
- **Ngôn ngữ & Thư viện:** Python 3, `pydantic` (để Data Modeling và Validation), `re` (Regex tiêu chuẩn của Python).
- **Nguyên tắc:** 
  - **100% Rule-based & Deterministic:** Không sử dụng AI/LLM hay mô hình nhúng (Embeddings) để đảm bảo độ chính xác tuyệt đối, tốc độ cao và tính lặp lại.
  - **Lenient Parser, Strict Data Model:** Chấp nhận đầu vào có thể có chút bất thường (như nhiều Điểm trên cùng 1 dòng, ngắt dòng tự do), nhưng đầu ra bắt buộc tuân thủ Data Contract của Pydantic.
  - **Bảo toàn nguyên bản:** KHÔNG thay đổi text gốc, KHÔNG xóa ký tự ngắt dòng `\n` bên trong nội dung, vị trí offset tuyệt đối.

## 2. Vai trò và Workflow của từng file

Luồng xử lý dữ liệu đi qua các file theo trình tự: `parser.py` -> `boundary_detector.py` (dùng `regex_engine.py`) -> `hierarchy_builder.py` (dùng `node_generator.py`).

- **`node_generator.py`**:
  - *Vai trò:* Trái tim của Data Contract. Định nghĩa các Pydantic models (`NodeType`, `Position`, `LegalNode`).
  - *Workflow:* Mọi Node trước khi được xuất ra JSON đều phải khởi tạo qua class `LegalNode` để hệ thống tự động kiểm tra kiểu dữ liệu và tính hợp lệ.

- **`regex_engine.py`**:
  - *Vai trò:* Từ điển chứa các mẫu Regex (Compiled Patterns) đã được tối ưu hóa để nhận diện các dấu hiệu cấu trúc (Structural Markers) của luật pháp Việt Nam (Phần, Chương, Mục, Điều, Khoản, Điểm).
  - *Workflow:* Được import vào `boundary_detector.py`. Đặc biệt, mẫu `POINT_PATTERN` được thiết kế linh hoạt (không ép mỏ neo đầu dòng) để quét được cả chữ `đ` và nhiều Điểm trên cùng một dòng.

- **`boundary_detector.py`**:
  - *Vai trò:* Cỗ máy cắt lớp văn bản (Text Slicer) và theo dõi vị trí tuyệt đối.
  - *Workflow:* 
    - Duyệt qua từng dòng văn bản, cộng dồn `current_char_index` để tính toán chính xác `position` (`start`, `end`).
    - Dùng các regex patterns để nhận diện Marker. Tách Marker vào trường `title` (ví dụ: `"a)"`, `"2."`) và phần còn lại vào trường `text`.
    - Duy trì một `pending_chunk` để gom các dòng text liên tiếp (hoặc các dòng rỗng) vào Node đang xử lý.
    - Xử lý gom dòng tiêu đề (Title Continuation) cho các cấp Phần, Chương, Mục (vd: dòng "Chương III" và dòng "QUYỀN VÀ NGHĨA VỤ" được gộp thành 1 title).

- **`hierarchy_builder.py`**:
  - *Vai trò:* State Machine (Máy trạng thái) để xây dựng cây phân cấp và cấp phát ID.
  - *Workflow:*
    - Nhận danh sách các "Chunks thô" từ Boundary Detector.
    - Duy trì `active_nodes` (Context Memory) để biết ta đang đứng ở Phần nào, Chương nào, Điều nào, Khoản nào, Điểm nào.
    - Tự động reset các cấp thấp khi gặp cấp cao (vd: gặp Điều mới thì reset Khoản, Điểm).
    - Sinh `id` phân cấp logic (vd: `article_27_clause_2_point_a`).
    - Gắn `parent_id` cho Node. Nếu có Node mồ côi, gán parent là `None` và bắn log cảnh báo. Lọc bỏ các TEXT node rỗng rác.

- **`parser.py`**:
  - *Vai trò:* Nhạc trưởng (Orchestrator).
  - *Workflow:* Nhận input text, gọi `detect_boundaries()`, truyền kết quả qua `build_hierarchy()`, sau đó xuất ra chuỗi JSON hoặc ghi thẳng ra file.

## 3. Các vấn đề kỹ thuật hóc búa đã giải quyết (Challenges)

Trong quá trình xây dựng, tôi đã đối mặt và xử lý triệt để 5 vấn đề cốt lõi:

1. **Vấn đề "Nhiều Điểm (Point) trên cùng 1 dòng" (Multiple points per line):** 
   - *Thực trạng:* Văn bản luật thường viết gộp `a) ...; b) ...; đ) ...` trên 1 dòng. Regex bình thường chỉ bắt được Điểm đầu tiên.
   - *Giải quyết:* Phải sử dụng `re.finditer()` để tìm mọi match trên dòng. Sau đó dùng toán học tính toán index để cắt 1 dòng vật lý thành nhiều Node Điểm tách biệt hoàn toàn.

2. **Đứt gãy Parent ID và Context của Điểm (Point Continuation):**
   - *Thực trạng:* Một Điểm có thể chứa nhiều đoạn văn (ngắt bởi `\n`). Nếu không cẩn thận, đoạn văn thứ 2 sẽ bị biến thành một Node TEXT mồ côi hoặc trỏ nhầm lên Khoản.
   - *Giải quyết:* Bổ sung `POINT` vào hệ thống Context Memory của `HierarchyBuilder`. Trong `BoundaryDetector`, giữ Node Điểm ở trạng thái `pending` để nó tự động "hút" (absorb) mọi dòng text tiếp theo cho đến khi đụng độ Marker mới.

3. **Chồng lấp Vị trí Ký tự (Position Overlap):**
   - *Thực trạng:* Rất dễ xảy ra lỗi `end` của Khoản 2 đè lên `start` của Điểm a do độ trễ khi chốt sổ node.
   - *Giải quyết:* Tinh chỉnh hàm `flush_pending(end_index)` để ép nó chốt `position.end` bằng đúng `line_start_idx` của dòng chứa node con tiếp theo, đảm bảo tính liên tục tuyệt đối, không thiếu không thừa ký tự nào.

4. **Trùng lặp Title và Text:**
   - *Thực trạng:* Parser ban đầu đưa toàn bộ câu vào cả title và text.
   - *Giải quyết:* Viết logic tách chuỗi: Cắt chính xác phần neo số/chữ (như `"2."`) để làm `title`, và slice chuỗi đằng sau điểm cuối của regex match để lấy `text` nội dung nguyên bản.

5. **Sinh Node Rác (Empty Nodes):**
   - *Thực trạng:* Các ngắt dòng dư thừa tạo ra các node TEXT chỉ chứa `\n`.
   - *Giải quyết:* Chặn đánh chặn ở lớp `hierarchy_builder`, nếu `chunk.type == NodeType.TEXT` và `.strip()` trả về rỗng thì lập tức loại bỏ.
