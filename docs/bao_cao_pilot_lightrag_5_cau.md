# Pilot LightRAG: 5 câu đầu Benchmark B

Trạng thái: **hoàn tất 5/5 câu hỏi**, chạy API thật. Run ID: `pilot5_20261030_01`.

## Phạm vi

- Nhánh `benmark_b`, dataset `datasets/benchmarks/benchmark_B_v02.json`.
- Chỉ hỏi B001–B005; corpus indexing vẫn là toàn bộ 23 Điều (26–48) Chương III.
- Model LLM `openai/gpt-4o-mini` qua OpenRouter; embedding local BAAI/bge-m3 1024 chiều trên CPU.
- LightRAG SDK `lightrag-hku==1.5.7`; mode hybrid, graph top_k=5, chunk 1200 token, overlap 100. SDK mặc định chunk_top_k=20: số chunks vào context lần lượt 20, 20, 10, 20, 20. Đây chưa phải cấu hình giới hạn context bằng nhau với Hybrid.
- Indexing và query được ghi từng API call với phase riêng trong `api_events.jsonl`.
- Gold pháp lý vẫn là draft cần review; không tự sinh điểm human review.

## Chuẩn bị và sửa lỗi vận hành

- Cài LightRAG và các dependency vào `venv` hiện có; xác thực khóa OpenRouter thành công (không ghi khóa vào report).
- Tải model embedding lần đầu, khoảng 2.27 GB trọng số; cache Hugging Face nằm ngoài repo.
- Chốt trạng thái tất cả 23 document phải `processed` trước khi công nhận index thành công.
- Tắt cả cache LLM chung và cache extraction; embedding batch 8, timeout 300 giây phù hợp CPU.
- Sửa metadata báo cáo để trỏ dataset v0.2 thực dùng.
- Kiểm thử vòng 1: `tests/unit/test_benchmark_b.py` và `tests/unit/test_benchmark_b_v02.py`: **18 passed**. Giới hạn tối đa 3 vòng kiểm thử.
- Khi kết thúc index, phát hiện SDK còn worker chờ trong event loop. Đã bổ sung hủy và chờ worker trước khi đóng loop; thêm regression test tương ứng. Tiến trình pilot đã nạp code trước bản sửa nên console log gốc vẫn giữ cảnh báo shutdown; dữ liệu index và kết quả 5 câu đã lưu thành công, hai lệnh đều exit code 0. Không chạy lại API chỉ để xóa cảnh báo.
- Vòng kiểm thử 2: **18 passed**; vòng 3 sau khi thêm regression test: **19 passed**. Không chạy thêm vòng pytest. `git diff --check` đạt.

## Kết quả

Index hoàn tất **23/23 documents**, **26 chunks**, **91 entities**, **166 edges**. Thời gian index khoảng **427,25 giây**, bao gồm khởi tạo model ở lệnh index; thời gian tải trọng số lần đầu nằm ngoài số này. SHA256 trọng số đã đối chiếu khớp nguồn Hugging Face.

| Câu | Căn cứ gold | Vị trí Điều gold trong danh sách Điều top 5 | Quan sát sơ bộ câu trả lời (chưa phải điểm human review) |
|---|---|---:|---|
| B001 | Điều 26 khoản 5 | 2 | Có ý Nhà nước bảo hộ; thêm nhiều quyền khác ngoài trọng tâm câu hỏi. |
| B002 | Điều 27 khoản 3 điểm c | 1 | Có đáp án pháp luật về dân sự; phần giải thích sau trộn thêm quy định công chứng, chứng thực và chưa chỉ rõ khoản/điểm. |
| B003 | Điều 28 khoản 1 điểm c | 1 | Nêu đủ khu công nghiệp, cụm công nghiệp, khu công nghệ cao. |
| B004 | Điều 29 khoản 1 | 1 | Liệt kê các nhóm nhu cầu trong gold, kèm diễn giải. |
| B005 | Điều 30 khoản 3 | 2 | Nêu chuyển phần diện tích có nhu cầu sang thuê đất thu tiền hằng năm. |

Đây là nhận xét đối chiếu với dataset/corpus đóng băng của benchmark, không phải đánh giá hiệu lực pháp luật hiện hành.

- Article Recall@5: **1,0**; Article MRR@5: **0,8**, 5 câu đều đo được. Top 5 Điều được suy ra từ locator đã align trên evidence, không phải top 5 entity của SDK.
- Exact Locator Recall@5: **1,0 trên 2/5 câu đo được** (B003, B004). B001/B002/B005 là `not_measured` do còn evidence chưa align EXACT; không được công bố 100% cho cả 5 câu.
- Citation Article Precision/Recall theo parser hiện tại: **0,4**. Clause: **0,0**; Point: **0,0** trên 2 câu có yêu cầu điểm. Parser hiện chủ yếu nhận `Điều ...`; LightRAG dùng reference dạng `[n] qh15#26`, nên điểm citation còn bị ảnh hưởng bởi định dạng, chưa phản ánh đầy đủ nguồn được dẫn. Cần bổ sung chuẩn hóa citation trước benchmark chính thức.
- Cả 5 câu đều là `DIRECT_RIGHT_OBLIGATION`: chain metrics là **N/A**, lượt này không kiểm tra khả năng dẫn chiếu chéo.
- Fact coverage, subject scope, unsupported claims: **chờ human review**. Hierarchy context chưa đo được vì adapter chưa xuất context_evidence.
- Lệnh run mất **63,54 giây**, gồm khởi tạo model và ghi/chấm artifact. Latency từng câu sau khởi tạo khoảng 6,83–11,59 giây.

## Token và chi phí API

Nguồn số liệu thực: `api_events.jsonl`; chi phí lấy `usage.cost` của OpenRouter. Không trộn phí query vào indexing.

| Phase | API attempts | Thành công | Input token đã biết | Output token đã biết | USD được provider xác nhận | Thiếu usage/cost |
|---|---:|---:|---:|---:|---:|---:|
| Index | 64 | 59 | 152.647 | 25.149 | 0,03136245 | 5 |
| Query 5 câu | 10 | 10 | 73.748 | 1.241 | 0,01180680 | 0 |

Index có **5 APITimeoutError**, được retry. Vì không có response usage của các lần timeout, **0,03136245 USD chỉ là phần chi phí được xác nhận**, chưa thể công bố là tổng đối soát đầy đủ. Không gán chi phí timeout bằng 0. Query có 10 call cho 5 câu do gồm trích xuất keywords và sinh câu trả lời; không truy vấn lặp riêng để lấy evidence.

`cost_ledger` cũ còn trường `observed_cost_usd` nhưng thực chất là ước tính bảng giá: index 0,03798645 USD. Khi báo cáo tiền thực, dùng event log thay vì trường legacy này. Cached token ở provider có thể làm tiền thực khác ước tính; đã tắt local LLM cache nhưng không coi đó là bằng chứng provider cache MISS.

Embedding chạy local, không có phí embedding API; thời gian CPU và tải model không được quy thành tiền API.

## Các phát hiện cần lưu ý trước chạy chính thức

- Có warning sai số trường ở một số relation LLM trả về (Điều 28 và có thể các đoạn khác); giữ log gốc để kiểm tra chất lượng graph. `processed` xác nhận vận hành hoàn tất, không chứng minh extraction đầy đủ/chính xác.
- SDK báo rerank được bật mặc định nhưng không có rerank model; lượt này không có reranking thực.
- Cần chốt graph top_k, chunk_top_k và context token budget công bằng cho hai hệ trước khi so sánh chính thức.
- Cần hỗ trợ reference `[n] -> file_path -> locator` trong citation scorer và cải thiện alignment cho evidence bị cắt/chồng lấn. Chưa sửa scorer rồi áp điểm mới trong lượt này.
- Cần pilot thêm câu một hop, nhiều hop, ngoại lệ và thiếu corpus; B001–B005 chưa bao phủ các năng lực đó.

## File đầu ra

Thư mục: `outputs/benchmark_b/lightrag/pilot5_20261030_01/`.

- `answers.jsonl`: 5 câu trả lời nguyên bản, evidence alignment, raw retrieval, latency.
- `metrics.json`, `per_question_metrics.jsonl`, `structural_metrics.jsonl`: kết quả chấm tự động và mẫu số.
- `human_review.csv`, `review_decisions.json`: mẫu review còn pending.
- `index_metadata.json`: thông số index, trạng thái tài liệu, số liệu chi phí indexing.
- `api_events.jsonl`: log cả index và query, đủ phân tách phase.
- `index_console.log`, `query_console.log`: log vận hành gốc, bao gồm cảnh báo.
- `workspace/`: graph, vector stores, full docs, chunks và trạng thái document.

Lệnh đã chạy (dùng Python của venv):

```powershell
python -m benchmark_b.runner index --system lightrag --fresh --run-id pilot5_20261030_01
python -m benchmark_b.runner run --system lightrag --limit 5 --top-k 5 --run-id pilot5_20261030_01
```

Không chạy M6/Hybrid trong pilot này, nên chưa có kết luận giảm token/chi phí so với Hybrid.
