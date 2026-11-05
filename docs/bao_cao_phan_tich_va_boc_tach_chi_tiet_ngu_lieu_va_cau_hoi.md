# BÁO CÁO PHÂN TÍCH VÀ BÓC TÁCH CHI TIẾT NGỮ LIỆU & CÂU HỎI
## (DATA DISTRIBUTION & TAXONOMY REPORT: BENCHMARK A & BENCHMARK B)
**Tài liệu Thẩm định Dữ liệu Nghiên cứu Khoa học (NCKH)**  
*Mã tài liệu:* `DOC-DATA-AUDIT-TAXONOMY-2026`  
*Hệ thống:* Hybrid Parser Funnel RAG vs. GraphRAG (LightRAG)  
*Ngày cập nhật:* 04/11/2026  

---

## 1. TỔNG QUAN PHÂN BỐ NGỮ LIỆU ĐIỀU LUẬT (CORPUS ANALYSIS)

Toàn bộ hệ thống thực nghiệm được xây dựng trên kho văn bản quy phạm pháp luật chuẩn hóa gồm **2.087 Điều luật** (tương ứng **12.754 chunks vi mô** ở bộ Parser M1-M3), trong đó phân vùng **500 điều luật** được nạp vào đồ thị tri thức LightRAG phục vụ đối chuẩn công bằng.

### Bảng 1: Phân bố Chi tiết các Văn bản Luật trong 2.087 Điều và 500 Điều (LightRAG)

| STT | Ký hiệu / Mã văn bản | Tên Văn bản Quy phạm Pháp luật | Số Điều trong Toàn bộ Corpus (2.087 Điều) | Số Điều nạp vào LightRAG (500 Điều) | Tỷ lệ nạp vào LightRAG | Ghi chú & Lĩnh vực |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| 1 | `91/2015/QH13` | **Bộ luật Dân sự 2015** | **689 điều** (33.01%) | **0 điều** (0.0%) | 0.0% | Luật chung về tài sản, hợp đồng, bồi thường |
| 2 | `01/VBHN-VPQH` | **Bộ luật Hình sự hợp nhất** | **426 điều** (20.41%) | **425 điều** (85.0%) | 99.8% | Tội phạm, khung hình phạt, trách nhiệm hình sự |
| 3 | `31/2024/QH15` | **Luật Đất đai 2024** | **260 điều** (12.46%) | **0 điều** (0.0%) | 0.0% | Chế độ quản lý và sử dụng đất đai |
| 4 | `45/2019/QH14` | **Bộ luật Lao động 2019** | **220 điều** (10.54%) | **75 điều** (15.0%) | 34.1% | Quan hệ lao động, kỷ luật, tiền lương |
| 5 | `59/2020/QH14` | **Luật Doanh nghiệp 2020** | **217 điều** (10.40%) | **0 điều** (0.0%) | 0.0% | Thành lập, quản trị, giải thể doanh nghiệp |
| 6 | `73/VBHN-VPQH` | **Luật Xử lý Vi phạm Hành chính** | **142 điều** (6.80%) | **0 điều** (0.0%) | 0.0% | Xử phạt vi phạm hành chính, thẩm quyền |
| 7 | `52/2014/QH13` | **Luật Hôn nhân và Gia đình 2014** | **133 điều** (6.37%) | **0 điều** (0.0%) | 0.0% | Kết hôn, ly hôn, tài sản chung/riêng |
| **Tổng** | — | **Toàn bộ Ngữ liệu Pháp luật** | **2.087 điều (100%)** | **500 điều (100%)** | **24.0%** | **7 Văn bản Luật Trọng yếu** |

> **Nhận xét chuyên sâu:**
> - Trong 500 điều của LightRAG: **85.0% là Luật Hình sự** (425 điều) và **15.0% là Luật Lao động** (75 điều).
> - Hoàn toàn vắng bóng 5 bộ luật lớn: **Dân sự (689 điều), Đất đai (260 điều), Doanh nghiệp (217 điều), Hành chính (142 điều), Hôn nhân & Gia đình (133 điều)**.
> - Điều này phản ánh rõ ràng **Rào cản Mở rộng (Scalability Bottleneck)** của LightRAG: do chi phí LLM trích xuất đồ thị quá lớn nên LightRAG chỉ nạp được 500 điều, tạo ra sự thiên lệch rất lớn về mặt ngữ liệu.

---

## 2. PHÂN BỐ CÂU HỎI THEO NGÀNH LUẬT (BENCHMARK A: 512 VS. 205 CÂU)

Từ kho ngữ liệu trên, tập kiểm thử Benchmark A gồm **512 câu hỏi** và tập kiểm soát công bằng **205 câu hỏi (Fair Subset)** có phân bố theo ngành luật như sau:

### Bảng 2: Phân bố Câu hỏi theo Ngành luật giữa Tập 512 câu và Tập 205 câu

| STT | Lĩnh vực Pháp luật | Số câu trong Tập Đầy đủ (512 câu) | Tỷ lệ (%) | Số câu trong Fair Subset (205 câu) | Tỷ lệ (%) | Chênh lệch Tỷ lệ đại diện |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| 1 | **Bộ luật Dân sự** | **221 câu** | **43.16%** | **0 câu** | **0.00%** | $\mathbf{-43.16\%}$ *(Mất trắng)* |
| 2 | **Bộ luật Hình sự** | **169 câu** | **33.01%** | **168 câu** | **81.95%** | $\mathbf{+48.94\%}$ *(Thiên lệch nặng)* |
| 3 | **Bộ luật Lao động** | **84 câu** | **16.41%** | **37 câu** | **18.05%** | $+1.64\%$ |
| 4 | **Luật Hôn nhân & Gia đình** | **19 câu** | **3.71%** | **0 câu** | **0.00%** | $\mathbf{-3.71\%}$ *(Mất trắng)* |
| 5 | **Luật Doanh nghiệp** | **13 câu** | **2.54%** | **0 câu** | **0.00%** | $\mathbf{-2.54\%}$ *(Mất trắng)* |
| 6 | **Xử lý Vi phạm Hành chính** | **5 câu** | **0.98%** | **0 câu** | **0.00%** | $\mathbf{-0.98\%}$ *(Mất trắng)* |
| 7 | **Luật Đất đai** | **1 câu** | **0.20%** | **0 câu** | **0.00%** | $\mathbf{-0.20\%}$ *(Mất trắng)* |
| **Tổng** | **Toàn bộ Lĩnh vực** | **512 câu** | **100%** | **205 câu** | **100%** | — |

> **Phát hiện học thuật quan trọng:**
> - Nếu chỉ đánh giá trên 205 câu, **81.95% câu hỏi là Hình sự** và **18.05% là Lao động**. Nhóm nghiên cứu bắt buộc phải mở rộng ra **512 câu** để kiểm chứng trên **Bộ luật Dân sự (221 câu, 43.16%)**, khẳng định tính tổng quát hóa (Generalization) của bộ Hybrid Parser trên các văn bản có tính trừu tượng cao.

---

## 3. PHÂN LOẠI DẠNG CÂU HỎI THEO BẢN CHẤT SUY LUẬN

### 3.1. Phân loại 4 Nhóm Câu hỏi trong Benchmark A (512 câu vs. 205 câu)

| Dạng câu hỏi | Định nghĩa học thuật | Số câu trong 512 câu | Tỷ lệ (%) | Số câu trong 205 câu | Tỷ lệ (%) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Clean Factoid** | Câu hỏi sự kiện đơn tuyến, tra cứu trực tiếp mức phạt, thẩm quyền, độ tuổi, định nghĩa rõ ràng. | **307 câu** | **59.96%** | **133 câu** | **64.88%** |
| **Conditional** | Câu hỏi chứa bẫy điều kiện, ngoại lệ: *"trừ trường hợp...", "nếu các bên không có thỏa thuận..."*. | **123 câu** | **24.02%** | **24 câu** | **11.71%** |
| **Multi-hop** | Câu hỏi đòi hỏi tổng hợp, xâu chuỗi thông tin từ nhiều khoản hoặc nhiều điều luật độc lập. | **67 câu** | **13.09%** | **43 câu** | **20.98%** |
| **Negative (Abstention)** | Câu hỏi bẫy không có quy định trong luật, kiểm tra khả năng từ chối trả lời (chống bịa đặt). | **15 câu** | **2.93%** | **5 câu** | **2.44%** |
| **Tổng cộng** | — | **512 câu** | **100%** | **205 câu** | **100%** |

---

### 3.2. Phân loại Chi tiết 9 Nhóm Câu hỏi Chuyên sâu trong Benchmark B (Chương III Luật Đất đai 2024 - 50 câu)

Được thiết kế theo cấu trúc chuẩn mực tại mục **2.7.2 (Phân loại các câu hỏi)** để thử thách năng lực phân giải quan hệ pháp lý phức tạp của đồ thị:

| STT | Nhóm câu hỏi (Category) | Số câu | Tỷ lệ (%) | Mục tiêu kiểm thử chuyên sâu |
| :---: | :--- | :---: | :---: | :--- |
| 1 | **Quyền và nghĩa vụ trực tiếp** | 8 | 16.0% | Truy xuất quyền hạn hoặc nghĩa vụ trực diện của người sử dụng đất (Ví dụ: Điều 26, 27, 28, 31). |
| 2 | **Nhiều điều kiện (Multi-condition)** | 10 | 20.0% | Xử lý các điều khoản phức hợp đòi hỏi thỏa mãn đồng thời nhiều tiêu chuẩn pháp lý (Ví dụ: Điều 45). |
| 3 | **Ngoại lệ và điều cấm** | 7 | 14.0% | Cô lập các trường hợp bị cấm chuyển nhượng, thế chấp hoặc quy định ngoại trừ đặc thù. |
| 4 | **Dẫn chiếu một bước (Cross-ref 1-hop)** | 6 | 12.0% | Điều luật A dẫn chiếu sang Điều luật B (Ví dụ: quyền chuyển nhượng phải tuân thủ điều kiện tại Điều 45). |
| 5 | **Dẫn chiếu nhiều bước (Cross-ref Multi-hop)** | 4 | 8.0% | Chuỗi dẫn chiếu qua nhiều nấc pháp lý trung gian (A $\rightarrow$ B $\rightarrow$ C). |
| 6 | **Phân biệt chủ thể (Subject Disambiguation)** | 5 | 10.0% | Phân định rạch ròi giữa các nhóm chủ thể khác nhau (Cá nhân, Doanh nghiệp FDI, Hộ gia đình). |
| 7 | **Tổng hợp cha - con (Parent-Child Synthesis)** | 4 | 8.0% | Yêu cầu tổng hợp toàn diện nội dung từ quy định khung cấp Điều xuống từng Khoản/Điểm chi tiết. |
| 8 | **Tình huống pháp lý (Legal Scenario)** | 3 | 6.0% | Tình huống giả định phức tạp trong đời sống đòi hỏi kết hợp nhiều căn cứ pháp luật để giải quyết. |
| 9 | **Không đủ căn cứ trong corpus (Negative)** | 3 | 6.0% | Thử thách khả năng phát hiện câu hỏi nằm ngoài phạm vi Chương III Luật Đất đai để từ chối trả lời. |
| **Tổng** | **Toàn bộ Benchmark B** | **50 câu** | **100%** | **Khung Đánh giá 9 Nhóm Chuyên sâu** |

---

## 4. Ý NGHĨA KẾT NỐI VÀO LUẬN VĂN & BẢO VỆ PHẢN BIỆN

1. **Minh chứng tính khách quan của tập 500 điều / 205 câu:** 
   - LightRAG chỉ nạp được 500 điều (thuộc Hình sự & Lao động) do rào cản chi phí Graph. Tập 205 câu là tập con duy nhất đảm bảo 100% căn cứ có sẵn trong 500 điều này.
2. **Minh chứng tính cấp thiết phải mở rộng ra 2.087 điều / 512 câu:**
   - Để khẳng định hệ thống Parser đề xuất không bị "học vẹt" trên khuôn mẫu tội phạm Hình sự, mà xử lý xuất sắc trên cả 689 điều Dân sự (chiếm 43.16% câu hỏi) và các luật kinh tế, hành chính.
3. **Phân hóa rõ rệt ở Benchmark B:**
   - Benchmark B (50 câu) đánh đúng vào tử huyệt của Generic GraphRAG (LightRAG) ở các dạng câu hỏi *Tổng hợp cha-con*, *Phân biệt chủ thể*, *Ngoại lệ và điều cấm*, nơi mà **Hybrid Parser / Domain UKG** đạt độ chính xác áp đảo từ **80% đến 100%**.
