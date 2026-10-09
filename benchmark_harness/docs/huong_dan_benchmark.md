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
   - **Vector RAG:** `pip install -q sentence-transformers faiss-gpu pandas requests`
   - **Hybrid RAG:** `pip install -q sentence-transformers faiss-gpu rank_bm25 FlagEmbedding torch pandas requests`
   - **LightRAG:** Bắt buộc cài cẩn thận theo trình tự sau để không lỗi `tiktoken`:
     ```bash
     !pip install -q --upgrade setuptools-rust tiktoken
     !pip install -q lightrag-hku --no-deps
     !pip install -q backoff jsonlines nest-asyncio python-dotenv pyyaml numpy
     !pip install -q sentence-transformers pandas requests
     ```

---

## BƯỚC 2: CÀI ĐẶT API KEY CHO GIÁM KHẢO
Hệ thống chấm điểm cần GPT-4o-mini thông qua OpenRouter. Bắt buộc phải truyền API Key vào biến môi trường:
```bash
export OPENROUTER_API_KEY="sk-or-v1-xxxxxxxxxxxxxxxxx"
```
*(Thay `sk-or-v1-xxxxxxxxxxxxxxxxx` bằng API Key thật của nhóm. Tuyệt đối không hardcode key vào source code).*

---

## BƯỚC 3: "MỞ KHOÁ" CODE LOGIC CỦA BẠN (WRAPPER)
Code tải về ĐÃ ĐƯỢC CHUẨN HOÁ. Các thành viên chỉ việc kiểm tra sơ bộ:
- **Người số 1:** Sửa file `benchmark_harness/systems/vector_rag/wrapper.py`
- **Người số 2:** Sửa file `benchmark_harness/systems/hybrid_rag/wrapper.py`
- **Người số 3:** Sửa file `benchmark_harness/systems/light_rag/wrapper.py` (Đã được vá lỗi Numpy và tương thích hoàn toàn `lightrag-hku`)

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
Vẫn đứng tại thư mục `benchmark_harness`, chạy lệnh tuỳ theo hệ thống của bạn. 

### Đối với Vector và Hybrid (Nhanh & Xoá sạch làm lại):
```bash
python run_harness.py --system vector
python run_harness.py --system hybrid
```

### Đối với LightRAG (Quy trình Sinh tồn - KHÔNG BAO GIỜ CHẠY 500 VĂN BẢN MỘT LẦN):
Do LightRAG tốn hàng tiếng đồng hồ để Index, nếu Kaggle sập sẽ mất toàn bộ đồ thị. Bạn **BẮT BUỘC** phải chia nhỏ quá trình Index:
1. Chạy 50 văn bản đầu tiên: `python run_harness.py --system lightrag --n_docs 50`
2. Đợi máy chạy xong, hệ thống sẽ tự động sao lưu vào thư mục `lightrag_backup_batch_...`.
3. Tải ngay thư mục backup này về máy tính hoặc đẩy lên Kaggle Dataset để cất giữ.
4. Ở lần chạy sau, giải nén thư mục đó vào lại `/kaggle/working/lightrag_workspace`. Khi bạn nới rộng số lượng lên (ví dụ: `--n_docs 100`), LightRAG sẽ **Resume (bỏ qua 50 bài cũ)** và chạy tiếp 50 bài mới mà không tốn tiền API hay thời gian lại từ đầu.
5. Lặp lại quá trình tới khi hết 500 documents. Sau đó hãy bỏ lệnh `--n_docs` để chạy chấm điểm 512 câu hỏi.

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

**Lưu ý đặc biệt cho báo cáo:**
- LightRAG không hỗ trợ trích xuất chunk ID do cấu trúc đồ thị. 
- Do đó, Recall@5 và MRR@5 không được báo cáo cho LightRAG.
- Chỉ so sánh chất lượng câu trả lời (Faithfulness, Answer Correctness) cho LightRAG.

**Cách tải về (Đặc biệt quan trọng):**
Trên giao diện Kaggle, ở cây thư mục bên phải, tìm đến 2 file `.csv` kết quả. Ấn vào dấu 3 chấm `...` cạnh file và chọn **Download**. Gửi file này về cho trưởng nhóm.

**🌟 SAO LƯU DỮ LIỆU INDEXING (Để chạy lại không tốn tiền):**
Khi chạy xong, để tải thành quả Index (đồ thị LightRAG hoặc File FAISS) về máy tính, bạn gõ lệnh sau để tạo file ZIP:
```bash
# Bứng nguyên Đồ thị của LightRAG (nếu bạn chạy LightRAG)
!zip -r /kaggle/working/lightrag_backup.zip lightrag_workspace/

# Bứng CSDL FAISS của Vector/Hybrid (nếu bạn chạy 2 cái kia)
!zip -r /kaggle/working/vector_hybrid_backup.zip data/index_*
```
Sau đó Download file `.zip` ở panel bên phải về cất vào máy. **TUYỆT ĐỐI KHÔNG PUSH CÁC THƯ MỤC NÀY LÊN GITHUB BẰNG KAGGLE** để tránh phình kho code.

Đóng máy và ăn mừng!
