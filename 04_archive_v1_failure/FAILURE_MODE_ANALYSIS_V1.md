# BÁO CÁO PHÂN TÍCH CHẾ ĐỘ LỖI (FAILURE MODE ANALYSIS — V1 BENCHMARK)
## Nghiên cứu thực nghiệm về Hiện tượng "Mồ côi Ngữ cảnh" (Context Orphanage Effect) khi Phân mảnh Vi mô

> **Ngày thực hiện:** 02/11/2026  
> **Môi trường đo kiểm:** Kaggle Cloud GPU (Tesla T4, 16GB VRAM, CUDA 12.x)  
> **Bộ dữ liệu:** Benchmark A (512 câu hỏi pháp lý / 2.087 điều luật)  
> **Mục đích tài liệu:** Lưu trữ hồ sơ đối chứng thực nghiệm (Empirical Ablation Baseline) để đưa vào Luận văn phục vụ mục phân tích chuyên sâu về quy trình phát triển và kiểm định hệ thống.

---

### 1. BẢNG SỐ LIỆU ĐỐI CHỨNG V1 (TRƯỚC KHI TỐI ƯU HÓA TIỀN TỐ)

| Hệ thống | Phạm vi | Recall@5 | MRR@5 | Citation Accuracy | Độ trễ P95 (Phần cứng) | Chi phí API |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Naive Vector (Baseline)** | 512 câu | **0.9141** | **0.8129** | 0.4000 (Trần) | 3.968,3 ms (API) | $0.2255 USD |
| **2. Naive Hybrid (Baseline)** | 512 câu | **0.9316** | **0.8796** | 0.3986 (Trần) | 3.693,2 ms (API) | $0.2108 USD |
| **3. Vector + Parser (V1)** | 512 câu | **0.8906** | **0.8077** | Preserved (Hierarchical ID) | **0.783 ms** (Tesla T4) | **$0.00** |
| **4. Hybrid + Parser (V1)** | 512 câu | **0.8652** | **0.7260** | Preserved (Hierarchical ID) | **61.878 ms** (CPU loop) | **$0.00** |
| **5. LightRAG (Approx)** | 512 câu (24% docs) | **0.3867** | **0.3478** | 0.1129 (Verified 512) | 0.104 ms | $0.1130 USD |

---

### 2. PHÂN TÍCH NGUYÊN NHÂN KỸ THUẬT (THE "SMOKING GUN")

Qua kiểm toán chuyên sâu mã nguồn và dữ liệu, nhóm phát hiện 3 nguyên nhân cốt lõi dẫn đến việc V1 có Recall thấp hơn 0.023 so với Naive Vector:

#### 2.1. Hiện tượng "Mồ côi Ngữ cảnh" (Context Orphanage) do Đặc thù Dữ liệu Nguồn ngoài
- Kiểm tra toàn bộ 2.087 điều luật trong `corpus_final.json` (bắt nguồn từ bộ benchmark chuẩn quốc gia VMTEB trên HuggingFace): Có tới **1.869 / 2.087 điều luật (89.56%)** có trường metadata `title` chỉ lưu số hiệu đơn thuần (`'Điều 1'`, `'Điều 2'`, `'Điều 357'`), trong khi tiêu đề thực sự của điều luật (như *"Tội lạm quyền trong khi thi hành công vụ"*) lại bị đẩy xuống dòng 1 của trường `text`.
- Ở Parser V1: Tiêu đề thật sự ở dòng 1 bị biến thành `Chunk 0`. Các `Khoản 1 đến Khoản 5` (các chunk tiếp theo) chỉ nhận tiền tố là `[Điều 357: Điều 357] > [Khoản 5] Người phạm tội còn bị cấm đảm nhiệm chức vụ...`.
- Hậu quả: Khoản 5 bị **cắt đứt hoàn toàn mối liên hệ với Tên tội danh ("Tội lạm quyền")**. Khi người dùng hỏi về mức phạt tội lạm quyền, mô hình BGE-M3 Dense không tìm thấy từ khóa tội danh trong Khoản 5, dẫn đến điểm tương đồng bị tụt so với Naive Vector (vốn ôm cả bài 1.000 từ có sẵn cả tên tội danh lẫn mức phạt).

#### 2.2. Hiện tượng "Trôi dạt từ vựng" (Lexical Drift) của BM25 trên Văn bản Vi mô
- Khi văn bản bị cắt vụn thành 14.155 mẩu vi mô (Khoản/Điểm có độ dài 20–50 từ), các thuật ngữ pháp lý chung (*"hành vi", "xử lý", "tài sản", "trường hợp"*) xuất hiện dày đặc.
- BM25 bị hiệu ứng bão hòa tần số từ (*TF saturation penalty*) trên văn bản ngắn, dẫn đến việc đẩy các khoản rác chứa từ khóa chung lên vị trí Top đầu.
- Khi dung hợp RRF tỷ lệ 50-50 giữa BM25 và Dense, BM25 bị nhiễu đã vô tình kéo tụt thứ hạng của mô hình ngữ nghĩa sâu BGE-M3.

#### 2.3. Nghẽn cổ chai CPU của Thư viện Python `rank-bm25`
- Trong khi Vector + Parser chạy bằng phép nhân ma trận song song `torch.matmul` trên 2.560 nhân CUDA của Tesla T4 chỉ tốn **0.75 ms/query**, BM25 phải chạy bằng vòng lặp Python thuần đơn luồng trên CPU qua 14.155 văn bản, làm độ trễ tăng vọt lên **43.46 ms (P95: 61.88 ms)**.

---

### 3. ĐÓNG GÓP HỌC THUẬT RÚT RA TỪ BẢN V1
1. Khẳng định rằng trong RAG pháp lý, việc cắt nhỏ văn bản (Micro-chunking) **bắt buộc phải đi kèm cơ chế kế thừa tiêu đề điều luật (Title & Context Inheritance)**, nếu không sẽ làm đứt gãy ngữ cảnh.
2. Chứng minh thực nghiệm rằng trên các đoạn văn bản vi mô, mô hình biểu diễn ngữ nghĩa sâu (Dense Retrieval) có độ tin cậy vượt trội so với tìm kiếm từ khóa thuần túy (Lexical BM25).
3. Cung cấp bộ dữ liệu đối chứng minh bạch để chứng minh bước tiến của phiên bản V2 (Sau khi bổ sung Fallback Title Extraction và Document Score Aggregation).

