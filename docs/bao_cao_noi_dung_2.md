# HỌC VIỆN CÔNG NGHỆ BƯU CHÍNH VIỄN THÔNG
# VIỆN KHOA HỌC KỸ THUẬT BƯU ĐIỆN

---

### BÁO CÁO NỘI DUNG NGHIÊN CỨU

## NỘI DUNG 2: XÂY DỰNG HỆ THỐNG CƠ SỞ - LẬP TRÌNH MÔI TRƯỜNG ĐỐI CHỨNG (BASELINE 1: NAIVE CHUNKING & BASELINE 2: PURE REGEX)

**ĐỀ TÀI:** ĐÁNH GIÁ VÀ TỐI ƯU HÓA CÁC KIẾN TRÚC RAG TRÊN NỀN TẢNG DỮ LIỆU CẤU TRÚC ĐẶC THÙ  
**Mã số đề tài:** 014-SV-2026-RIPT  
**Thuộc nhóm ngành khoa học:** Công nghệ thông tin  
**Chủ trì đề tài:** Lưu Thanh Lâm  
**Thành viên thực hiện:** Nguyễn Bình Minh, Nguyễn Thùy Linh  
**Giảng viên hướng dẫn:** TS. Nguyễn Mạnh Dũng  

*Hà Nội – 2026*

---

### MỤC LỤC

- [MỞ ĐẦU](#mở-đầu)
- [CHƯƠNG 1. THIẾT KẾ VÀ HIỆN THỰC HÓA HAI BỘ PHÂN ĐOẠN CƠ SỞ](#chương-1-thiết-kế-và-hiện-thực-hóa-hai-bộ-phân-đoạn-cơ-sở)
  - [1.1. Mục tiêu và yêu cầu kỹ thuật của môi trường đối chứng](#11-mục-tiêu-và-yêu-cầu-kỹ-thuật-của-môi-trường-đối-chứng)
  - [1.2. Hiện thực hóa Baseline 1: Phân đoạn theo kích thước cố định (Naive Chunking)](#12-hiện-thực-hóa-baseline-1-phân-đoạn-theo-kích-thước-cố-định-naive-chunking)
  - [1.3. Hiện thực hóa Baseline 2: Phân tách dựa trên mẫu hình thể thức (Pure Regex)](#13-hiện-thực-hóa-baseline-2-phân-tách-dựa-trên-mẫu-hình-thể-thức-pure-regex)
- [CHƯƠNG 2. THỰC NGHIỆM ĐỐI SÁNH VÀ PHÂN TÍCH GIỚI HẠN CỦA REGEX THUẦN](#chương-2-thực-nghiệm-đối-sánh-và-phân-tích-giới-hạn-của-regex-thuần)
  - [2.1. Thiết lập ngữ liệu kiểm thử thực nghiệm](#21-thiết-lập-ngữ-liệu-kiểm-thử-thực-nghiệm)
  - [2.2. Kết quả đối sánh hiệu năng và độ toàn vẹn ranh giới](#22-kết-quả-đối-sánh-hiệu-năng-và-độ-toàn-vẹn-ranh-giới)
  - [2.3. Nhận diện các giới hạn chí mạng của phương pháp Regex thuần](#23-nhận-diện-các-giới-hạn-chí-mạng-của-phương-pháp-regex-thuần)
- [CHƯƠNG 3. KẾT LUẬN VÀ ĐỊNH HƯỚNG PHÁT TRIỂN HỆ THỐNG LÕI](#chương-3-kết-luận-và-định-hướng-phát-triển-hệ-thống-lõi)
  - [3.1. Đánh giá mức độ hoàn thành so với đề cương](#31-đánh-giá-mức-độ-hoàn-thành-so-với-đề-cương)
  - [3.2. Yêu cầu chuyển giao sang kiến trúc Hybrid Parser](#32-yêu-cầu-chuyển-giao-sang-kiến-trúc-hybrid-parser)
- [TÀI LIỆU THAM KHẢO](#tài-liệu-tham-khảo)

---

### DANH MỤC BẢNG BIỂU

- Bảng 1.1: Thông số kỹ thuật của hai bộ phân đoạn cơ sở.
- Bảng 2.1: Quy mô ngữ liệu kiểm thử Chương III Luật Đất đai 2024.
- Bảng 2.2: So sánh kết quả phân đoạn giữa Naive Chunking và Pure Regex.
- Bảng 2.3: Thống kê các dạng lỗi thực tế của bộ phân đoạn Pure Regex trên ngữ liệu kiểm thử.

---

### MỞ ĐẦU

Trong các hệ thống truy hồi tăng cường sinh (Retrieval-Augmented Generation - RAG), tầng tiền xử lý và phân đoạn dữ liệu (data ingestion & chunking) quyết định trực tiếp đến ranh giới ngữ cảnh được nạp vào mô hình ngôn ngữ lớn. Đối với văn bản quy phạm pháp luật Việt Nam, các quy định mang tính phân cấp cao (Chương, Mục, Điều, Khoản, Điểm) và chứa đựng mạng lưới dẫn chiếu chéo phức tạp. 

Theo tiến độ thực hiện đã đăng ký tại Mục 11 của Thuyết minh Đề cương nghiên cứu khoa học số 014-SV-2026-RIPT, Nội dung 2 tập trung vào nhiệm vụ: *"Xây dựng hệ thống cơ sở: Lập trình môi trường đối chứng (Baseline 1: Naive Chunking & Baseline 2: Pure Regex)"*, với sản phẩm cam kết là: *"Các Parser cơ sở hoạt động; nhận diện được các giới hạn của Regex thuần"*. 

Báo cáo chuyên đề này trình bày chi tiết quy trình thiết kế, hiện thực hóa mã nguồn cho hai bộ phân đoạn cơ sở, tiến hành kiểm thử thực nghiệm trên ngữ liệu thực tế (Chương III Luật Đất đai số 31/2024/QH15), đồng thời phân tích định lượng và định tính các giới hạn chí mạng của phương pháp biểu thức chính quy thuần túy, qua đó xác lập luận cứ khoa học để phát triển hệ thống lõi Hybrid Parser ở các giai đoạn tiếp theo.

---

### CHƯƠNG 1. THIẾT KẾ VÀ HIỆN THỰC HÓA HAI BỘ PHÂN ĐOẠN CƠ SỞ

#### 1.1. Mục tiêu và yêu cầu kỹ thuật của môi trường đối chứng

Mục tiêu của Nội dung 2 là thiết lập hai đường cơ sở độc lập nhằm phục vụ việc đánh giá đối sánh các chiến lược phân đoạn văn bản pháp luật:
1. **Tính độc lập và khả năng tái lập:** Hai parser cơ sở phải được đóng gói thành các module xử lý dữ liệu chuẩn hóa, có khả năng nhận đầu vào là văn bản thô hoặc văn bản có cấu trúc và trả về danh sách các phân đoạn (chunks/nodes) kèm siêu dữ liệu (metadata) xác định.
2. **Đại diện cho hai trường phái tiền xử lý truyền thống:**
   - Trường phái phân đoạn cơ học phi ngữ nghĩa (Sliding Window / Fixed-size Chunking), vốn là cấu hình mặc định trong phần lớn khung phát triển RAG nguồn mở.
   - Trường phái phân tích dựa trên luật hình thức (Rule-based / Regular Expressions), khai thác các quy chuẩn trình bày thể thức văn bản pháp luật để cắt văn bản theo ranh giới ký tự.

*Bảng 1.1. Thông số kỹ thuật của hai bộ phân đoạn cơ sở.*

| Tham số kỹ thuật | Baseline 1: Naive Chunking | Baseline 2: Pure Regex Parser |
| :--- | :--- | :--- |
| **Nguyên lý phân đoạn** | Chiều dài token cố định (Fixed-token window) | Khớp mẫu cú pháp (Syntactic pattern matching) |
| **Kích thước đoạn (Window size)** | 512 tokens (phiên bản tiêu chuẩn) / 1.200 tokens | Động theo ranh giới quy phạm (Điều / Khoản / Điểm) |
| **Độ trượt gối đầu (Overlap)** | 100 tokens | 0 token (cắt rời rạc theo ranh giới quy chuẩn) |
| **Căn cứ phân tách** | Đếm số lượng từ/token | Mẫu quy chuẩn thể thức (Nghị định 34/2016/NĐ-CP) |
| **Ngữ cảnh phả hệ (Hierarchy)** | Không có (chỉ lưu số thứ tự chunk) | Cố định theo chuỗi ký tự cục bộ |
| **Chi phí tính toán** | Thấp ($O(N)$, đếm từ) | Rất thấp ($O(N)$, quét regex) |

#### 1.2. Hiện thực hóa Baseline 1: Phân đoạn theo kích thước cố định (Naive Chunking)

Bộ phân đoạn Naive Chunking được lập trình bằng ngôn ngữ Python, sử dụng công cụ tách từ tiếng Việt PyVi kết hợp với bộ đếm token chuẩn hóa. Thuật toán phân đoạn được mô tả theo các bước:
1. Tiếp nhận chuỗi ký tự thô của toàn bộ văn bản sau khi đã loại bỏ các khoảng trắng thừa.
2. Áp dụng cửa sổ trượt có kích thước $W = 512$ tokens và độ dịch chuyển (step) $S = W - O = 412$ tokens (tương ứng độ chồng lấn $O = 100$ tokens).
3. Mỗi phân đoạn sinh ra được cấp một mã định danh duy nhất (`chunk_id`), lưu kèm vị trí ký tự bắt đầu (`start_char`) và vị trí ký tự kết thúc (`end_char`) trên văn bản nguồn.

Đặc trưng cơ bản của Baseline 1 là hoàn toàn bất khả tri trước cấu trúc pháp lý. Ranh giới cắt đoạn phụ thuộc hoàn toàn vào ngưỡng đếm từ số học, dẫn đến việc các câu văn quy phạm có thể bị cắt đôi ở giữa, hoặc hai quy định thuộc hai điều luật khác nhau bị gom chung vào một phân đoạn.

#### 1.3. Hiện thực hóa Baseline 2: Phân tách dựa trên mẫu hình thể thức (Pure Regex)

Khác với Baseline 1, Baseline 2 khai thác các đặc trưng hình thức của văn bản quy phạm pháp luật Việt Nam. Theo quy định tại Luật Ban hành văn bản quy phạm pháp luật và Nghị định số 34/2016/NĐ-CP (được sửa đổi, bổ sung bởi Nghị định số 154/2020/NĐ-CP), cấu trúc văn bản pháp luật được tổ chức theo trật tự phân cấp nghiêm ngặt: Phần, Chương, Mục, Điều, Khoản, Điểm.

Nhóm nghiên cứu đã xây dựng một bộ đăng ký mẫu hình (Pattern Registry) sử dụng biểu thức chính quy (regular expressions) nhằm nhận diện các ranh giới quy phạm:

```python
# Trích đoạn định nghĩa mẫu biểu thức chính quy của Baseline 2
import re

PATTERNS = {
    "CHAPTER": re.compile(r"^Chương\s+([IVXLCDM]+)\.?\s*(.*)$", re.IGNORECASE | re.MULTILINE),
    "SECTION": re.compile(r"^Mục\s+(\d+)\.?\s*(.*)$", re.IGNORECASE | re.MULTILINE),
    "ARTICLE": re.compile(r"^Điều\s+(\d+)\.\s*(.*)$", re.MULTILINE),
    "CLAUSE":  re.compile(r"^(\d+)\.\s+(.*)$", re.MULTILINE),
    "POINT":   re.compile(r"^([a-zđ])\)\s+(.*)$", re.MULTILINE),
}
```

Quy trình vận hành của bộ phân đoạn Pure Regex:
1. **Dò quét ranh giới (Boundary Scanning):** Sử dụng hàm tìm kiếm lặp để xác định chỉ số bắt đầu của các dòng văn bản khớp với mẫu hình `Điều`, `Khoản`, `Điểm`.
2. **Cắt đoạn cơ học (Linear Slicing):** Nội dung của một đơn vị pháp lý được xác định từ vị trí bắt đầu của mẫu hình khớp đến vị trí bắt đầu của mẫu hình tiếp theo trong văn bản.
3. **Gán nhãn cấu trúc cục bộ:** Trích xuất chỉ số định danh (ví dụ: số điều, số khoản, ký tự điểm) và lưu trữ thành các đối tượng dữ liệu sơ bộ (`raw_nodes`).

---

### CHƯƠNG 2. THỰC NGHIỆM ĐỐI SÁNH VÀ PHÂN TÍCH GIỚI HẠN CỦA REGEX THUẦN

#### 2.1. Thiết lập ngữ liệu kiểm thử thực nghiệm

Ngữ liệu kiểm thử phục vụ việc đánh giá hai bộ phân đoạn cơ sở là Chương III Luật Đất đai số 31/2024/QH15 ("Quyền và nghĩa vụ của người sử dụng đất"). Đây là chương có tính quy phạm phức tạp cao, bao gồm nhiều nhóm chủ thể, các quyền định đoạt tài sản và các chuỗi dẫn chiếu chéo chằng chịt.

*Bảng 2.1. Quy mô ngữ liệu kiểm thử Chương III Luật Đất đai 2024.*

| Chỉ số định lượng | Giá trị thực tế |
| :--- | :--- |
| **Phạm vi điều luật** | Từ Điều 26 đến Điều 48 (23 điều luật) |
| **Tổng số khoản** | 72 khoản |
| **Tổng số điểm** | 102 điểm |
| **Tổng dung lượng văn bản** | Khoảng 11.800 từ (tương đương 16.500 tokens) |
| **Số lượng dẫn chiếu nội bộ** | 41 trường hợp dẫn chiếu điều/khoản |

#### 2.2. Kết quả đối sánh hiệu năng và độ toàn vẹn ranh giới

Hai bộ phân đoạn được thực thi trên cùng một tệp văn bản nguồn. Kết quả xử lý được tổng hợp tại Bảng 2.2.

*Bảng 2.2. So sánh kết quả phân đoạn giữa Naive Chunking và Pure Regex.*

| Tiêu chí đánh giá | Baseline 1: Naive Chunking (512 tokens) | Baseline 2: Pure Regex Parser |
| :--- | :--- | :--- |
| **Tổng số đoạn sinh ra** | 38 chunks | 175 đơn vị (23 Điều, 68 Khoản, 84 Điểm) |
| **Thời gian thực thi (Latency)** | 0,085 giây | 0,012 giây |
| **Tỷ lệ cắt đứt quy phạm (Boundary Clipping)** | **31,6%** (12/38 đoạn cắt ngang giữa câu hoặc điều) | **0%** (luôn cắt theo đầu dòng quy chuẩn) |
| **Mất ngữ cảnh cha (Parent Loss)** | Toàn bộ (các chunk chỉ chứa văn bản rời rạc) | Xuất hiện ở 14 điểm và 4 khoản lỗi |
| **Chi phí gọi mô hình ngôn ngữ** | 0 VNĐ | 0 VNĐ |

Thực nghiệm cho thấy:
- **Baseline 1 (Naive Chunking)** có tốc độ nhanh nhưng bộc lộ nhược điểm cố hữu: 31,6% số phân đoạn làm rách ranh giới điều luật. Khi một điều luật bị tách làm hai phân đoạn, các điều kiện tiên quyết ở đầu điều bị chia cắt khỏi các chế tài áp dụng ở cuối điều, làm suy giảm nghiêm trọng khả năng suy luận của mô hình ngôn ngữ lớn ở các tầng truy hồi sau.
- **Baseline 2 (Pure Regex)** khắc phục được hiện tượng cắt đứt ranh giới quy phạm bằng cách bám theo các ký tự mở đầu Điều/Khoản/Điểm, đồng thời đạt tốc độ xử lý vượt trội (0,012 giây cho toàn bộ chương luật).

#### 2.3. Nhận diện các giới hạn chí mạng của phương pháp Regex thuần

Mặc dù khắc phục được nhược điểm cắt xẻ cơ học của Naive Chunking, quá trình đối soát chi tiết dữ liệu đầu ra của Baseline 2 cho thấy phương pháp Regex thuần túy bộc lộ **ba giới hạn chí mạng** khiến nó không thể sử dụng độc lập để xây dựng đồ thị tri thức pháp lý:

*Bảng 2.3. Thống kê các dạng lỗi thực tế của bộ phân đoạn Pure Regex trên ngữ liệu kiểm thử.*

| Dạng giới hạn / Lỗi thực tế | Số lượng phát hiện | Tỷ lệ ảnh hưởng | Minh chứng điển hình trong văn bản luật |
| :--- | :--- | :--- | :--- |
| **1. Nhận diện sai do biến thể thể thức (False Positive)** | 6 trường hợp | 3,4% tổng số node | Các đoạn giải thích liệt kê có đánh số "1.", "2." bên trong một khoản bị Regex nhận nhầm thành Khoản độc lập. |
| **2. Đứt gãy phả hệ cha - con (Hierarchy Gap / Orphan Nodes)** | 14 trường hợp | 8,0% tổng số node | Điểm a, b xuất hiện nhưng không gán được vào Khoản cha do Khoản cha không có đánh số rõ ràng (chỉ có đoạn văn mở đầu). |
| **3. Bất lực trước dẫn chiếu chéo ngầm định (Implicit Reference Blindness)** | 41/41 trường hợp | **100%** dẫn chiếu | Bỏ sót hoàn toàn các cụm từ: "theo quy định tại khoản này", "trừ trường hợp quy định tại điểm c Điều nêu trên". |

##### Giới hạn 1: Tính bất định của định dạng văn bản thực tế
Trong văn bản quy phạm pháp luật, mẫu hình cú pháp không phải lúc nào cũng tuân thủ cấu trúc phẳng. Tại một số điều luật, bên trong một Khoản hoặc một Điểm có xuất hiện danh sách liệt kê con được đánh số tương tự như số thứ tự của Khoản (ví dụ: `1.`, `2.`) hoặc chữ cái (ví dụ: `a)`, `b)`). Regex thuần khi chỉ quét mẫu hình dòng đơn lập tức phân tách các dòng liệt kê này thành một Khoản độc lập thuộc Điều, gây xáo trộn hoàn toàn cấu trúc thực tế của điều luật.

##### Giới hạn 2: Sự đứt gãy phả hệ cha - con do thiếu cơ chế kiểm định logic
Regex thuần túy chỉ thực hiện thao tác so khớp chuỗi (string matching) mà không sở hữu mô hình biểu diễn dữ liệu hướng trạng thái (state machine). Do đó:
- Khi gặp một Điều không phân chia thành các Khoản mà chỉ có nội dung văn bản trực tiếp (thể thức điều đơn), Regex không xác định được cấp độ phụ thuộc.
- Khi xuất hiện các Điểm mồ côi (orphan points) — tức là các điểm nằm ngay sau lời dẫn của Điều mà không có tiêu đề Khoản 1 — Regex thuần cắt rời các điểm này và không thiết lập được liên kết phân cấp logic `(Điểm) -> [THUỘC_VỀ] -> (Khoản) -> [THUỘC_VỀ] -> (Điều)`.

##### Giới hạn 3: Sự bất lực hoàn toàn trước mạng lưới dẫn chiếu chéo ngầm định
Đây là giới hạn nghiêm trọng nhất được nhận diện trong Nội dung 2. Regex chỉ có thể phát hiện được các chuỗi dẫn chiếu tường minh có cấu trúc cố định như `Điều (\d+)`. Tuy nhiên, trong ngôn ngữ pháp lý Việt Nam, phần lớn các mối liên kết ràng buộc lại được diễn đạt dưới dạng dẫn chiếu ngầm định ngữ cảnh:
- Dẫn chiếu nội bộ điều: *"Quyền quy định tại điểm này được thực hiện khi..."*, *"theo quy định tại khoản này"*.
- Dẫn chiếu ngoại lệ và điều kiện: *"Trừ trường hợp pháp luật có quy định khác"*, *"Đối với trường hợp quy định tại khoản 2 Điều này thì áp dụng theo..."*.

Regex thuần túy hoàn toàn không có khả năng hiểu ngữ nghĩa để bóc tách chủ thể thực sự của hành vi hay xác định điều khoản mục tiêu mà cụm từ "khoản này" đang trỏ tới. Kết quả là toàn bộ mạng lưới quan hệ pháp lý ngữ nghĩa bị bỏ trống.

---

### CHƯƠNG 3. KẾT LUẬN VÀ ĐỊNH HƯỚNG PHÁT TRIỂN HỆ THỐNG LÕI

#### 3.1. Đánh giá mức độ hoàn thành so với đề cương

Đối chiếu với các chỉ tiêu đã đăng ký trong Thuyết minh Đề cương đề tài số 014-SV-2026-RIPT:
1. **Lập trình môi trường đối chứng:** Nhóm nghiên cứu đã hoàn thành việc xây dựng và đóng gói mã nguồn của Baseline 1 (Naive Chunking 512/1.200 tokens) và Baseline 2 (Pure Regex Parser).
2. **Sản phẩm đạt được:** Cả hai parser cơ sở đều vận hành ổn định trên ngữ liệu kiểm thử thực tế, cung cấp dữ liệu đầu vào cho các thử nghiệm đối sánh.
3. **Nhận diện giới hạn của Regex thuần:** Đã thống kê và phân loại định lượng được 3 giới hạn cốt lõi: tỷ lệ nhận nhầm thể thức (3,4%), tỷ lệ đứt gãy phả hệ (8,0%) và tỷ lệ bỏ sót dẫn chiếu chéo ngầm định (100%).

Như vậy, **Nội dung 2 đã hoàn thành 100% khối lượng công việc và đạt đúng kết quả cam kết** theo đề cương được duyệt.

#### 3.2. Yêu cầu chuyển giao sang kiến trúc Hybrid Parser

Các phát hiện thực nghiệm từ Nội dung 2 xác nhận giả thuyết khoa học ban đầu của nhóm:
- Không thể sử dụng Naive Chunking đơn thuần vì nó phá vỡ ranh giới thể thức pháp luật.
- Cũng không thể phụ thuộc vào một mình Regex thuần túy vì nó bất lực trước sự biến thiên ngữ nghĩa và dẫn chiếu chéo ngầm định.

Từ đó, nhóm nghiên cứu xác định yêu cầu tất yếu đối với hệ thống lõi ở **Nội dung 3**: Cần xây dựng một kiến trúc lai (Hybrid Parser) vận hành theo nguyên lý *Neuro-Symbolic*. Trong đó:
- Tầng biểu thức chính quy và quy tắc cấu trúc đóng vai trò **phễu lọc thô vật lý** (Physical Coarse Filter), kết hợp với bộ kiểm tra tính toàn vẹn phả hệ (Validation Engine) để bảo đảm 100% ranh giới điều khoản mà không tốn chi phí mô hình ngôn ngữ lớn.
- Tầng mô hình ngôn ngữ lớn kết hợp bộ định tuyến ngữ nghĩa (Semantic Router & Few-shot LLM) chỉ được kích hoạt có chọn lọc tại những vị trí có tín hiệu dẫn chiếu phức tạp, nhằm trích xuất chính xác các thực thể và quan hệ pháp lý với chi phí tối ưu nhất.

---

### TÀI LIỆU THAM KHẢO

[1] P. Lewis et al., “Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks,” in *Advances in Neural Information Processing Systems*, vol. 33, pp. 9459–9474, 2020.  
[2] Quốc hội nước Cộng hòa Xã hội Chủ nghĩa Việt Nam, *Luật Ban hành văn bản quy phạm pháp luật*, Luật số 80/2015/QH13 và Luật sửa đổi, bổ sung số 63/2020/QH14.  
[3] Chính phủ nước Cộng hòa Xã hội Chủ nghĩa Việt Nam, *Nghị định số 34/2016/NĐ-CP ngày 14 tháng 5 năm 2016 quy định chi tiết một số điều và biện pháp thi hành Luật Ban hành văn bản quy phạm pháp luật*.  
[4] Chính phủ nước Cộng hòa Xã hội Chủ nghĩa Việt Nam, *Nghị định số 154/2020/NĐ-CP ngày 31 tháng 12 năm 2020 sửa đổi, bổ sung một số điều của Nghị định số 34/2016/NĐ-CP*.  
[5] Quốc hội nước Cộng hòa Xã hội Chủ nghĩa Việt Nam, *Luật Đất đai*, Luật số 31/2024/QH15, ngày 18 tháng 01 năm 2024.  
[6] Viet-Trung Tran, “PyVi: Python Vietnamese Core NLP Toolkit,” 2016. [Online]. Available: https://github.com/trungtv/pyvi.  
