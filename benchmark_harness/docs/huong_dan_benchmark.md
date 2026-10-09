# SỔ TAY HƯỚNG DẪN CHẠY BENCHMARK TOÀN TẬP (KAGGLE EDITION)

Tài liệu này hướng dẫn chi tiết "cầm tay chỉ việc" cho 3 thành viên đội Dev để chạy chấm điểm (benchmark) 3 hệ thống Vector, Hybrid và LightRAG độc lập với nhau trên 3 máy tính (hoặc Kaggle) riêng biệt.

---

## BƯỚC 1: KHỞI TẠO MÔI TRƯỜNG KAGGLE
1. Mở Kaggle, tạo một Notebook mới.
2. Ở panel bên phải: **ACCELERATOR** -> Chọn **GPU T4 x2** (Bắt buộc, nếu không sẽ báo lỗi NO_GPU).
3. Mở Terminal dưới cùng của Kaggle và gõ lệnh tải code về:
   ```bash
   git clone https://github.com/luuthanhlam04-cloud/hybrid-parser-nckh.git
   cd hybrid-parser-nckh/Benchmark
   git checkout benchmark
   ```
   *(LƯU Ý QUAN TRỌNG: TUYỆT ĐỐI bám chặt vào nhánh `benchmark` này. Không dùng các nhánh cá nhân cũ (như `duong` hay `lam_m7`) vì chúng đã lỗi thời và không tương thích với siêu kiến trúc mới).*

4. Cài đặt các thư viện cần thiết. Gõ lệnh tương ứng với hệ thống bạn phụ trách:
   - **Vector RAG:** `pip install sentence-transformers faiss-gpu pandas requests`
   - **Hybrid RAG:** `pip install sentence-transformers faiss-gpu rank_bm25 FlagEmbedding torch pandas requests`
   - **LightRAG:** `pip install lightrag sentence-transformers pandas requests`

---

## BƯỚC 2: CÀI ĐẶT API KEY CHO GIÁM KHẢO
Hệ thống chấm điểm cần GPT-4o-mini thông qua OpenRouter. Bắt buộc phải truyền API Key vào biến môi trường:
```bash
export OPENROUTER_API_KEY="sk-or-v1-xxxxxxxxxxxxxxxxx"
```
*(Thay `sk-or-v1-xxxxxxxxxxxxxxxxx` bằng API Key thật của nhóm. Tuyệt đối không hardcode key vào source code).*

---

## BƯỚC 3: "MỞ KHOÁ" CODE LOGIC CỦA BẠN (WRAPPER)
Code tải về hiện đang dùng dữ liệu giả (fake data) để an toàn. 
Mỗi người cần mở file tương ứng của mình ra và nhúng code thuật toán RAG thật vào:
- **Người số 1:** Sửa file `benchmark_harness/systems/vector_rag/wrapper.py`
- **Người số 2:** Sửa file `benchmark_harness/systems/hybrid_rag/wrapper.py`
- **Người số 3:** Sửa file `benchmark_harness/systems/light_rag/wrapper.py`

**Lưu ý sinh tử (Quy tắc "Nhà ai nấy ở, Code ai nấy sửa"):**
- **CẤM ĐỤNG CHẠM** vào các file lõi như `run_harness.py`, `core/evaluator.py` hay `core/pydantic_schemas.py`. Kiến trúc này đã được thiết kế hoàn hảo với "Áo giáp chống sập (Anti-Crash OOM)", đếm tiền Token API và tự động Resume khi Kaggle sập. Mọi chỉnh sửa ngoài `wrapper.py` sẽ làm vỡ trận toàn hệ thống!
- Đọc kỹ các phần comment `""" """` tôi đã viết sẵn để biết chỗ nào cần bỏ comment (uncomment).
- Đảm bảo hàm `retrieve_and_answer` trả về đúng format `SystemResponse`.
- Chỗ sinh câu trả lời LLM **BẮT BUỘC BỌC `try-except`**. Tránh trường hợp LLM sập làm mất luôn kết quả tìm kiếm Vector (Đã ghi chú kỹ trong code).

---

## BƯỚC 4: CHẠY THỬ NGHIỆM ĐỂ XÁC NHẬN (5 CÂU)
Trước khi đốt tiền API và thời gian GPU cho 512 câu, phải chạy test để kiểm tra 100% không có lỗi ngớ ngẩn. 

Di chuyển vào thư mục harness:
```bash
cd benchmark_harness
```

Chạy script test tương ứng của bạn:
- **Người Vector:** `python test_vector_5cau.py`
- **Người Hybrid:** `python test_hybrid_5cau.py`
- **Người LightRAG:** `python test_lightrag_5cau.py`

**Đọc Log kết quả:**
- Nếu máy in ra `API_KEY_MISSING` -> Bạn quên bước 2.
- Nếu in ra `NO_GPU` -> Bạn quên bật GPU ở bước 1.
- Nếu in ra `[LỖI CỤ THỂ TẠI CÂU...]` -> Code Wrapper của bạn ở Bước 3 viết sai logic.
- Nếu máy chạy mượt mà, điểm số in ra màn hình và dòng cuối báo **`- Trạng thái: PASS`** -> CHÚC MỪNG, bạn đã sẵn sàng!

---

## BƯỚC 5: CHẠY BENCHMARK TOÀN DIỆN (512 CÂU)
Vẫn đứng tại thư mục `benchmark_harness`, chạy duy nhất lệnh này tuỳ theo hệ thống của bạn:
```bash
# Chọn 1 trong 3 lệnh sau:
python run_harness.py --system vector
python run_harness.py --system hybrid
python run_harness.py --system light
```

**Tính năng an toàn tự động (Đừng hoảng sợ nếu gặp):**
1. **Resume (Chống sập):** Kaggle giới hạn chạy liên tục vài tiếng. Nếu máy ảo bị sập giữa chừng, bạn bật máy lại và gõ lại y hệt lệnh trên. Hệ thống sẽ tự nạp file `checkpoint_results_XYZ.csv` và CHẠY TIẾP từ câu bị đứt, bỏ qua các câu đã chấm.
2. **API Quá Tải:** Nếu OpenRouter báo 429 Rate Limit, màn hình sẽ in "Đang đợi 2s, 4s...". Hãy cứ mặc kệ nó, nó sẽ tự động thử lại thành công.
3. **Cắt Cầu Dao:** Nếu script in ra "BÁO ĐỘNG: CHI PHÍ VƯỢT QUÁ $5", nó sẽ tự tắt để bảo vệ tiền của bạn.

---

## BƯỚC 6: THU HOẠCH KẾT QUẢ VÀ TẢI VỀ MÁY
Khi 512 câu chạy xong, báo cáo tóm tắt (Tổng số Token, Giá tiền, Điểm trung bình) sẽ hiện trên màn hình Kaggle.
Trong thư mục `benchmark_harness` sẽ xuất hiện file kết quả siêu quý giá:
- `final_benchmark_results_VECTOR.csv` (Hoặc HYBRID, LIGHT)
- `checkpoint_results_VECTOR.csv`

**Cách tải về:**
Trên giao diện Kaggle, ở cây thư mục bên phải, tìm đến 2 file `.csv` này, ấn vào dấu 3 chấm `...` cạnh file và chọn **Download**. Gửi file này về cho trưởng nhóm để gộp lại báo cáo chung. Đóng máy và ăn mừng! 
