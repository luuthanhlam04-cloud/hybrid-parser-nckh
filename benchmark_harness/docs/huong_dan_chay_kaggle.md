# BÍ KÍP CHẠY BENCHMARK TRÊN KAGGLE (QUICK GUIDE)

Tài liệu này là quy trình rút gọn dành riêng cho đội Dev khi bắt đầu thực thi code trên Kaggle.

## BƯỚC 1: KHỞI TẠO MÁY & CÀI ĐẶT
1. Bật máy ảo Kaggle, chọn cấu hình **GPU (T4 x2 hoặc P100)**.
2. Clone code và chuyển sang nhánh `benchmark`:
   ```bash
   git clone https://github.com/luuthanhlam04-cloud/hybrid-parser-nckh.git
   cd hybrid-parser-nckh/Benchmark
   git checkout benchmark
   ```
3. Cài đặt các thư viện lõi:
   ```bash
   pip install sentence-transformers faiss-gpu rank_bm25 FlagEmbedding torch pandas requests lightrag
   ```
4. Nạp biến môi trường API Key (Thay bằng Key thật của đội):
   ```bash
   export OPENROUTER_API_KEY="sk-or-v1-xxxxxxxxxxxxxxxx"
   ```

## BƯỚC 2: CHẠY THỬ KIỂM TRA (5 CÂU)
Chạy lần lượt 3 lệnh sau để kiểm thử từng hệ thống:
```bash
cd benchmark_harness
python test_vector_5cau.py
python test_hybrid_5cau.py
python test_lightrag_5cau.py
```

**Cách đọc Log để đánh giá PASS/FAIL:**
- **Thiếu GPU/Thư viện:** Nếu log in ra `"Mock mode"`, chứng tỏ Kaggle chưa nhận GPU hoặc bạn chưa `pip install` đủ. Lập tức **FAIL**, cài lại.
- **Thành công (Real model):** Log bắt buộc phải in `"Loading BGE-M3..."`.
- **Gọi API:** Log phải in `"Calling OpenRouter..."`.
- **Kết quả:** Cuối file sẽ in 5 dòng báo cáo (Hệ thống, Số câu, Recall, MRR, Trạng thái).
  - *Lưu ý riêng cho LightRAG:* LightRAG không hỗ trợ trích xuất Chunk ID do kiến trúc Đồ thị tri thức, nên Recall@5 và MRR@5 sẽ hiển thị là `N/A`. Chúng ta chỉ đánh giá LightRAG dựa trên chất lượng sinh câu trả lời (Faithfulness).

## BƯỚC 3: CHẠY TOÀN BỘ (512 CÂU)
Khi cả 3 file test đều PASS, tiến hành chạy lệnh chính thức:
```bash
python run_harness.py --system vector
python run_harness.py --system hybrid
python run_harness.py --system light
```
Tải các file `final_benchmark_results_*.csv` về máy để tổng hợp báo cáo.
