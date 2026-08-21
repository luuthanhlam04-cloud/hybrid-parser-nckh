# Tổng Kết Module 1: Tiền Xử Lý Văn Bản (Document Preprocessing)

## 1. Tổng quan những gì đã thực hiện
Module 1 được xây dựng nhằm mục đích chuẩn hóa các văn bản quy phạm pháp luật định dạng `.docx` thô thành định dạng UTF-8 thuần túy (plain text), sạch sẽ và có cấu trúc rõ ràng. Kết quả đầu ra của Module này là dữ liệu đầu vào trực tiếp cho **Module 2 (Rule-based Regex Parser)** để xây dựng Đồ thị Tri thức (Knowledge Graph). 

Điểm nhấn quan trọng nhất trong quá trình phát triển là **giải quyết triệt để vấn đề mất mát số tự động (Auto-numbering)** của MS Word — một bài toán cực kỳ phổ biến nhưng rất khó xử lý trong tài liệu pháp luật Việt Nam.

## 2. Cấu trúc thư mục và Workflow các file Code
Toàn bộ logic tiền xử lý được tổ chức theo Pipeline 4 bước khép kín trong thư mục `src/preprocessing/`:

- **`clean_document.py`**: Script chạy chính (Main pipeline). Nó điều phối luồng dữ liệu đi qua tuần tự 4 bước, ghi log thời gian thực và quản lý input/output.
- **`document_loader.py`**: (Bước 1) Đọc file `.docx` và trích xuất toàn bộ nội dung văn bản. Chịu trách nhiệm phân tích mã XML (OOXML) để khôi phục lại các ký tự đánh số tự động (Khoản 1, 2, 3 và Điểm a, b, c) vốn bị các thư viện Python thông thường bỏ qua.
- **`text_cleaner.py`**: (Bước 2) Làm sạch nhiễu số hóa. Chịu trách nhiệm xóa số trang, tiêu đề đầu/cuối trang, các khoảng trắng thừa, và xử lý các dòng treo (dangling clauses) do lỗi rớt dòng khi soạn thảo.
- **`unicode_normalizer.py`**: (Bước 3) Chuẩn hóa toàn bộ văn bản về mã Unicode NFC. Đảm bảo chữ tiếng Việt (như `đ`, `ẽ`, `ợ`) được mã hóa đồng nhất, tránh lỗi RegEx không nhận diện được chữ có dấu ở các bước sau.
- **`formatter.py`**: (Bước 4) Định dạng lại cấu trúc. Sử dụng RegEx chuyên sâu để nhận diện các ranh giới kiến trúc luật (Chương, Mục, Điều, Khoản, Điểm) và tự động chèn khoảng trắng/dòng trống, giúp cấu trúc văn bản trở nên chuẩn mực.

## 3. Công nghệ và Thư viện sử dụng
- **Python Standard Libraries (`zipfile`, `xml.etree.ElementTree`)**: Dùng để mổ xẻ trực tiếp file mã nguồn `.docx` (vốn là một file ZIP chứa XML).
- **`re` (Regular Expressions)**: Công cụ cốt lõi dùng để nhận diện cấu trúc luật (Pattern matching) và làm sạch văn bản một cách cực kỳ khắt khe.
- **`logging`**: Quản lý xuất log tiến trình xử lý.

## 4. Quyết định Kiến trúc: Vì sao loại bỏ `pypandoc` và chỉ dùng Custom XML Parser?

Ban đầu, hệ thống dự định dùng `pypandoc` vì nó là một chuẩn quốc tế trong việc convert định dạng. Tuy nhiên, qua quá trình gỡ lỗi thực tế, chúng ta đã quyết định **loại bỏ hoàn toàn pypandoc** và thay bằng trình phân tích **XML OOXML tự code (`_load_via_xml`)** vì các nguyên nhân cốt lõi sau:

1. **Bản chất "hack" định dạng của MS Word trong Tiếng Việt:** 
   MS Word sử dụng mặc định bảng chữ cái tiếng Anh (`a,b,c,d,e,f...`) cho thẻ đánh số `lowerLetter`. Tuy nhiên, văn bản pháp luật Việt Nam yêu cầu thứ tự `a, b, c, d, đ, e, g...`. Vì Word không hỗ trợ tự động chữ `đ)`, người soạn thảo thường áp dụng "thủ thuật": 
   - Họ tắt đánh số, **gõ tay chữ `đ)`**.
   - Dòng tiếp theo bật lại đánh số, Word sinh ra chữ `e)` (là phần tử thứ 5 tiếng Anh).
   - Đến chữ `g)` (phần tử thứ 7 tiếng Anh), họ lại phải tự set giá trị `start=7` trên một List XML mới (`w:numId` mới).
2. **Sự sai lệch của Pandoc:** Pandoc cố gắng thông minh chuẩn hóa các danh sách này nhưng nó làm mất hoặc biến dạng các vị trí gõ tay và các chỗ đứt gãy cấu trúc danh sách, dẫn đến việc mất hẳn một số khoản/điểm trong văn bản xuất ra.
3. **Sự kiểm soát tuyệt đối bằng XML:** Việc tự đọc `word/document.xml` và `word/numbering.xml` cho phép chúng ta kiểm soát chính xác từng mã `w:numId`, `w:ilvl`, `w:abstractNumId`. Bằng cách **cố định `_ALPHA_LOWER` của Python về chuẩn tiếng Anh nguyên thủy (`abcdefghijklmnopqrstuvwxyz`)**, bộ XML Parser của chúng ta đã mô phỏng lại *chính xác 100%* thuật toán hiển thị của MS Word. Các chữ gõ tay như `đ)` được giữ nguyên, và các chữ tự động nhảy (như `e`, `g`) được sinh ra khớp hoàn toàn với những gì người dùng nhìn thấy trên màn hình Word.
4. **Giảm rủi ro triển khai:** Xóa bỏ sự phụ thuộc vào Pandoc giúp phần mềm chạy độc lập (Standalone) hoàn toàn trên môi trường máy chủ mà không cần cài đặt thêm phần mềm binary bên ngoài hệ sinh thái Python. 
