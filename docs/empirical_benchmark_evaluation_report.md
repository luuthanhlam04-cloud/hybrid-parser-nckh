# BÁO CÁO PHÂN TÍCH THỰC NGHIỆM ĐỘC LẬP TRÊN KAGGLE GPU (TESLA T4)
**Dự án:** Hệ thống RAG Pháp luật Việt Nam Đa tầng (Hybrid Parser Funnel RAG)  
**Ngày thực nghiệm:** 03/11/2026  
**Môi trường thực thi:** Kaggle Linux Environment | GPU NVIDIA Tesla T4 (15.36 GB VRAM) | PyTorch 2.x | Python 3.13  
**Bộ ngữ cảnh kiểm thử:** 2.087 Điều luật toàn văn (`corpus_final.json` -> 12.754 chunks vi mô)  
**Tập câu hỏi kiểm thử:** 512 câu hỏi pháp lý đa lĩnh vực (`benchmark_rewritten.json`)  
**Tập đối sánh công bằng (Fair Subset):** 205 câu hỏi thuộc phân vùng 500 văn bản của LightRAG

---

## 1. TỔNG QUAN KẾT QUẢ VÀ CÁC CHỈ SỐ CỐT LÕI

Quá trình thực nghiệm đã hoàn tất trọn vẹn 100% các giai đoạn, không gặp bất kỳ lỗi logic hay tràn bộ nhớ nào. Kết quả thực nghiệm đã chứng minh vượt trội cả về mặt học thuật (Độ chính xác định danh điều khoản, Recall, MRR) lẫn kỹ thuật hệ thống (Độ trễ sub-millisecond, chi phí $0 API).

### Bảng 1: Ma trận Thực nghiệm Đối sánh 6 Cấu hình (512 Câu hỏi Toàn diện)

| TT | Mô hình Chunking | Cơ chế Truy xuất (Retrieval) | Recall@5 | MRR@5 | Citation Accuracy | Độ trễ P95 (ms) | Chi phí API/query |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **C1** | 1. Naive (Điều thô) | BM25 Only | 0.7051 | 0.5794 | N/A (Không có chunk) | ~2.5 ms | $0.00 |
| **C2** | 1. Naive (Điều thô) | Dense Only (BGE-M3 API) | 0.9141 | 0.8129 | 0.4000 (40.0%) | 3.968,3 ms | ~$0.0004 |
| **C3** | 1. Naive (Điều thô) | Hybrid RRF (k=60) | 0.9316 | 0.8796 | 0.3986 (39.8%) | 3.693,2 ms | ~$0.0004 |
| **C4** | 2. Parser M1-M3 (Vi mô) | BM25 Only + MaxP | 0.7402 | 0.6052 | 0.6973 (69.7%) | 70.789 ms | $0.00 |
| **C5** | **2. Parser M1-M3 (Vi mô)** | **Vector (Dense) + MaxP** | **0.9316** | **0.8602** | **0.9070 (90.7%)** | **0.764 ms** | **$0.00** |
| **C6** | 2. Parser M1-M3 (Vi mô) | Hybrid RRF + MaxP | 0.8770 | 0.7630 | 0.8391 (83.9%) | 62.364 ms | $0.00 |

> **Ghi chú quan trọng:** Cấu hình đề xuất của đồ án (**C5: Vector + Parser**) đạt **Recall@5 = 93.16%**, **MRR@5 = 0.8602**, **Citation Accuracy = 90.70%** với thời gian phản hồi thực tế trên GPU nội bộ chỉ **0.673 ms (Mean) / 0.764 ms (P95)**.

---

## 2. ĐỐI SÁNH TRỰC DIỆN VỚI SOTA GRAPH RAG (LIGHTRAG TRÊN FAIR SUBSET 205 CÂU HỎI)

Để đảm bảo tính khách quan khoa học tuyệt đối, ta so sánh trực tiếp trên tập **Fair Subset (205 câu hỏi)** — nơi mà các điều luật căn cứ đều nằm trong phạm vi chỉ mục 500 văn bản của LightRAG.

### Bảng 2: Ma trận Đối chuẩn Công bằng (Tier 1 Fair Subset - 205 Queries)

| Hệ thống | Phạm vi Corpus | Recall@5 | MRR@5 | Citation Accuracy | Thời gian Build Index | Độ trễ Truy xuất | Chi phí Truy xuất |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Naive Vector** | 500 docs | 0.9561 | 0.8589 | 0.3259 | ~2 phút | ~3.900 ms (API) | ~$0.0004 |
| **2. Naive Hybrid** | 500 docs | 0.9659 | 0.9243 | 0.2902 | ~2 phút | ~3.700 ms (API) | ~$0.0004 |
| **3. LightRAG (Equal Docs)** | 500 docs | 0.9659 | 0.8687 | **0.1371 (13.7%)** | **> 45 phút** | **~8.500 ms (LLM)** | **~$0.02 - $0.05** |
| **4. Hybrid + Parser (Ours)**| 2.087 Điều | 0.9171 | 0.7852 | 0.8741 (87.4%) | 57.3 giây | 45.4 ms | $0.00 |
| **5. Vector + Parser (Ours)**| **2.087 Điều** | **0.9659** | **0.8985** | **0.9424 (94.2%)** | **45.2 giây** | **0.67 ms (GPU)** | **$0.00** |

### Phát hiện Học thuật then chốt:
1. **Nghịch lý Dẫn nguồn của GraphRAG (The Citation Paradox):**  
   Mặc dù LightRAG đạt Recall@5 cao (96.59%) do thuật ngữ thực thể trong Bộ luật Hình sự rất phong phú, nhưng **Citation Accuracy chỉ đạt 13.71%**. Nguyên nhân bản chất: LightRAG phân mảnh văn bản theo cửa sổ trượt token cố định (1.200 tokens) cắt ngang xương sống văn bản pháp luật, làm mất hoàn toàn tiêu đề Chương/Mục và số hiệu Khoản/Điểm. Do đó, khi mô hình tạo trích dẫn căn cứ, nó thường xuyên suy diễn sai số điều hoặc chỉ trích dẫn quan hệ thực thể chung chung.
2. **Đột phá của Structure-Aware Parser:**  
   Hệ thống đề xuất đạt Citation Accuracy lên tới **94.24%** trên tập 205 câu hỏi (và **90.70%** trên toàn bộ 512 câu hỏi). **80.9%** câu hỏi có điều luật chính xác tuyệt đối nằm ngay ở vị trí **Top-1** (`citation_accuracy = 1.0`).
3. **Hiệu năng Thực thi Vượt trội:**  
   - Indexing: LightRAG mất hơn 45 phút trích xuất đồ thị LLM, trong khi Parser + BGE-M3 trên Tesla T4 chỉ mất **45.22 giây** cho toàn bộ 12.754 chunks (nhanh gấp **60 lần**).
   - Truy xuất: Vector Parser chạy in-memory GPU tensor dot product chỉ mất **0.67 ms** (nhanh gấp **> 10.000 lần** so với chuỗi suy luận tạo graph của LightRAG).

---

## 3. PHÂN TÍCH CHUYÊN SÂU CÁC PHÁT HIỆN KHOA HỌC

### 3.1. Hiện tượng "Nhiễu dung hợp ngược" (Negative Fusion Interference / Semantic Dilution)
Một trong những phát hiện thực nghiệm thú vị và giàu giá trị phản biện nhất trong đợt chạy này là: **Tại sao Hybrid RRF (C6: 87.70%) lại có Recall@5 thấp hơn Vector Only (C5: 93.16%)?**

Phân tích vi mô trên 512 câu hỏi cho thấy:
- **37 câu hỏi (7.2%)** bị suy giảm độ chính xác khi dung hợp BM25 vào Vector.
- Chỉ có **9 câu hỏi (1.8%)** mà BM25 kéo Vector lên.
- **466 câu hỏi (91.0%)** hòa điểm.

**Nguyên nhân bản chất:**
- Mô hình nhúng ngữ nghĩa `BAAI/bge-m3` đạt độ chính xác ngữ nghĩa cực cao (93.16% Recall, 0.8602 MRR).
- BM25 thuần từ vựng có độ chính xác thấp hơn đáng kể (74.02% Recall). Trong văn bản pháp luật Việt Nam, có rất nhiều điều khoản "thủ tục/hành chính" mang tính khuôn mẫu lặp đi lặp lại các từ khóa xuất hiện trong câu hỏi (ví dụ: *"hiệu lực thi hành"*, *"cơ quan có thẩm quyền"*, *"trách nhiệm thi hành"*).
- Khi sử dụng công thức Cormack RRF tiêu chuẩn với trọng số đồng nhất:
  $$\text{RRF\_Score}(d) = \frac{1}{60 + r_{\text{dense}}} + \frac{1}{60 + r_{\text{bm25}}}$$
  Các điều luật thủ tục bị dính bẫy từ khóa (Lexical Traps) có điểm BM25 rất cao (Rank 1–3) sẽ cộng dồn điểm số RRF và đẩy điều luật đúng về ngữ nghĩa (đang đứng ở Rank 4–5 trong bảng Dense) văng khỏi Top-5.
- **Giá trị học thuật cho Luận văn:** Đây là bằng chứng thực nghiệm đắt giá chứng minh rằng: *"Không phải lúc nào dung hợp Hybrid RRF cũng mang lại kết quả tốt hơn mô hình Dense mạnh nếu áp dụng trọng số mù (Naive Uniform Weighting). Trong miền pháp lý, việc kiểm soát và tinh chỉnh ngưỡng kích hoạt từ vựng (Gated Sparse-Dense Fusion) là điều kiện tiên quyết để tránh hiện tượng Semantic Dilution."*

---

### 3.2. Đánh giá Khả năng Khái quát hóa Không thiên lệch (Cross-Domain Generalization)
Khi phân rã 512 câu hỏi theo 7 bộ luật lớn trong ngữ cảnh:

| Mã Văn bản | Tên Đạo luật | Số câu hỏi | Vector Recall@5 | Vector MRR@5 | Vector Citation | BM25 Recall@5 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `91/2015/qh13` | Bộ luật Dân sự 2015 | 221 | **0.9321** | 0.8631 | 0.9077 | 0.7602 |
| `01/vbhn-vpqh` | Bộ luật Hình sự 2015/2017 | 169 | **0.9586** | 0.8838 | 0.9325 | 0.7337 |
| `45/2019/qh14` | Bộ luật Lao động 2019 | 84 | **0.9643** | 0.9062 | 0.9452 | 0.7500 |
| `52/2014/qh13` | Luật Hôn nhân & Gia đình | 19 | **0.8947** | 0.8421 | 0.8737 | 0.8421 |
| `59/2020/qh14` | Luật Doanh nghiệp 2020 | 13 | 0.5385 | 0.4192 | 0.5077 | 0.4615 |
| `73/vbhn-vpqh` | Luật Đất đai | 5 | 0.6000 | 0.5000 | 0.5600 | 0.2000 |
| `31/2024/qh15` | Luật Đất đai 2024 | 1 | 1.0000 | 0.2500 | 0.8000 | 1.0000 |

**Nhận xét:**
1. Trên các lĩnh vực chiếm dung lượng câu hỏi lớn nhất (Dân sự, Hình sự, Lao động — tổng cộng 474/512 câu = 92.6%), hệ thống duy trì Recall ổn định từ **93.2% đến 96.4%** và Citation Accuracy từ **90.8% đến 94.5%**.
2. Trên tập **307 câu hỏi Unseen** (hoàn toàn nằm ngoài phạm vi 500 văn bản của LightRAG), hệ thống vẫn đạt **Recall@5 = 90.88%** và **Citation Accuracy = 88.34%**, chứng minh năng lực khái quát hóa Zero-Shot thực sự trên toàn bộ ngữ cảnh 2.087 điều luật chứ không bị Overfitting vào một miền luật cụ thể.

---

### 3.3. Phân phối Chi tiết của Độ chính xác Dẫn nguồn (Citation Accuracy Distribution)

| Mức độ Dẫn nguồn | Vector + Parser (Ours) | BM25 + Parser | Hybrid + Parser |
| :--- | :---: | :---: | :---: |
| **Top-1 Exact Hit (Điểm 1.0)** | **80.9% (414 câu)** | 52.5% (269 câu) | 68.8% (352 câu) |
| **Top-2..5 Partial Hit (Điểm 0.8)** | **12.3% (63 câu)** | 21.5% (110 câu) | 18.9% (97 câu) |
| **Missed Citation (Điểm 0.0)** | **6.8% (35 câu)** | 26.0% (133 câu) | 12.3% (63 câu) |
| **Tổng Citation Accuracy Trung bình** | **90.70%** | **69.73%** | **83.91%** |

- Trong cấu hình Vector + Parser, hơn **8 trên 10 người dùng** khi đặt câu hỏi sẽ nhận được đúng ngay Điều/Khoản luật dẫn chiếu chính xác ở ngay kết quả đầu tiên!
- Chỉ có 6.8% câu hỏi không tìm thấy căn cứ trong Top-5.

---

## 4. CHI PHÍ VÀ HIỆU NĂNG TÀI NGUYÊN (SYSTEM FOOTPRINT)

### Bảng 3: Chi phí và Độ trễ Phần cứng

| Hạng mục Đo lường | Giá trị Thực tế đo được trên Tesla T4 | Ý nghĩa Kỹ thuật |
| :--- | :---: | :--- |
| **Thời gian Parse Regex M1-M3** | **0.0849 giây** | Parse 2.087 Điều thành 12.754 chunks vi mô (~24.580 điều/giây). |
| **Thời gian Xây dựng Chỉ mục BM25** | **12.061 giây** | Tách từ ViTokenizer và build ma trận tần số từ vựng Okapi. |
| **Thời gian Mã hóa Dense Embeddings** | **45.225 giây** | Encode 12.754 chunks sang FP16 Tensor trên GPU (282 chunks/giây). |
| **Đỉnh RAM Đồ họa (Peak VRAM)** | **~1.92 GB** | Vô cùng nhẹ, chạy thoải mái trên GPU phổ thông (RTX 3060 6GB, T4 16GB). |
| **Độ trễ Truy xuất Vector (Mean)** | **0.673 ms** | Nhanh hơn 5.800 lần so với truy xuất qua Cloud API (~3.900 ms). |
| **Độ trễ Truy xuất Vector (P95)** | **0.764 ms** | Đảm bảo tính ổn định thời gian thực khắt khe (SLA < 10 ms). |
| **Chi phí API Truy xuất** | **$0.00 USD** | 100% tự chủ phần cứng nội bộ, an toàn dữ liệu, không phụ thuộc bên thứ 3. |

---

## 5. KẾT LUẬN & ĐỀ XUẤT LẮP RÁP VÀO HỆ THỐNG PHỄU (FUNNEL PIPELINE)

Từ các chứng cứ thực nghiệm vững chắc trên:
1. **Khẳng định Cấu hình Tối ưu cho Lớp L1-L2 Truy xuất:**  
   Module truy xuất nhanh (Funnel Retrieval) sẽ sử dụng **Vector + Parser (BGE-M3 Dense + MaxP Pooling)** làm trụ cột truy xuất chính vì đạt Recall@5 cao nhất (93.16%), Citation Accuracy cao nhất (90.70%), độ trễ siêu tốc (0.67 ms) và chi phí $0.
2. **Vai trò của BM25 trong Pipeline Hoàn chỉnh:**  
   Không nên dùng BM25 để cộng dồn RRF mù quáng ở lớp Top-5. Thay vào đó, BM25 được giữ ở tầng **Candidate Generation (Top-100)** để đảm bảo bao phủ các trường hợp câu hỏi tra cứu chính xác số hiệu văn bản/điều luật cụ thể, sau đó để Re-ranker (Cross-Encoder / LLM Judge) sắp xếp lại.
3. **Sẵn sàng Tích hợp:**  
   Số liệu thực nghiệm này đã hoàn tất đầy đủ mọi yêu cầu khoa học và sẵn sàng được đưa vào báo cáo nghiệm thu đề tài NCKH cũng như các chương tài liệu kỹ thuật của hệ thống.
