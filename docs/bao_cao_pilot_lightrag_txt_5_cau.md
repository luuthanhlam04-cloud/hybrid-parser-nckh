# Báo cáo pilot LightRAG trên file TXT sạch

Run ID: `txt_pilot5_20261030_01`  
Nhánh: `benmark_b`  
Trạng thái: hoàn tất indexing và hỏi 5 câu đầu.

## Thay đổi pipeline

LightRAG đã được chuyển sang nhận trực tiếp file:

`outputs/clean_texts/clean_Luat_dat_dai_chuong_3.txt`

Pipeline mới gửi toàn bộ file này cho LightRAG như **một document nguồn**. LightRAG tự chia chunk và tự trích xuất entity/relation. `physical_graph.json` không còn là input indexing của LightRAG; file đó chỉ được dùng sau truy xuất để đối chiếu evidence với locator pháp lý của Benchmark B.

Metadata của run ghi:

- input source: `outputs/clean_texts/clean_Luat_dat_dai_chuong_3.txt`
- input SHA256: `ce3297fe2c7ae44a59dee6d19d4cceb7f768104a491f30d780898f889b39412a`
- document count: 1
- chunk size: 1200 token
- overlap: 100 token
- model: `openai/gpt-4o-mini`
- embedding: `BAAI/bge-m3`, local, 1024 chiều

## Kết quả indexing

- Documents: **1/1 processed**
- Chunks: **12**
- Entities: **83**
- Relations: **119**
- Thời gian index: khoảng **215,37 giây**, gồm thời gian nạp model và embedding trên CPU.
- API indexing calls: **25**, đều thành công.
- Input tokens: **88.304**
- Output tokens: **15.924**
- Chi phí provider xác nhận: **0,0202752 USD**
- Chi phí embedding API: **0 USD** vì BGE-M3 chạy local.

## Kết quả B001–B005

- Số câu trả lời: **5/5**
- Article Recall@5: **1,0**
- Article MRR@5: **0,6167**
- Exact Locator Recall@5: **0,8**
- Chi phí query: **0,01399245 USD**
- Query calls: **10** cho 5 câu; gồm keyword extraction và answer generation.
- Citation Article Precision/Recall: **0,2** theo scorer hiện tại.
- Fact coverage và legal correctness: **chưa chấm**, cần human review.
- Reference-chain metrics: **N/A** vì 5 câu đầu không có reference chain.

Quan sát câu trả lời: B001, B003, B004 và B005 trả lời đúng trọng tâm chính; B002 nêu đúng pháp luật về dân sự nhưng câu trả lời chưa trích rõ `Điều 27 khoản 3 điểm c`. LightRAG reference chỉ ghi tên file TXT nên citation parser chưa lấy được locator cấp Điều/khoản/điểm đầy đủ.

## Lưu ý về điểm locator

Evidence alignment hiện tìm các node có text nằm trong chunk trả về. Vì một chunk 1200 token chứa nhiều điều khoản, một evidence chunk có thể map vào nhiều locator cùng lúc. Do đó Exact Locator Recall@5 trong pilot này là tín hiệu truy hồi, chưa phải bằng chứng rằng LightRAG trả đúng một điểm pháp lý duy nhất. Trước benchmark chính thức cần bổ sung offset hoặc article/section segmentation cho chunk TXT để tránh over-alignment.

## File kết quả

Thư mục run: `outputs/benchmark_b/lightrag/txt_pilot5_20261030_01/`

- `index_metadata.json`: input, hash, số document/chunk/entity/relation và chi phí indexing.
- `answers.jsonl`: 5 câu trả lời, evidence và raw retrieval.
- `metrics.json`: metric tổng hợp.
- `structural_metrics.jsonl`: metric theo từng câu.
- `api_events.jsonl`: token, chi phí và trạng thái từng lượt API, tách index/query.
- `workspace/`: graph, vector store và document store của LightRAG.

Run cũ `pilot5_20261030_01` index theo 23 document dựng từ physical graph nên không dùng làm kết quả chính thức. Run `txt_pilot5_20261030_01` mới là run đúng với thiết kế input TXT.

Đã kiểm tra cú pháp các file pipeline và `git diff --check`. Không chạy thêm pytest trong lượt này để giữ giới hạn vòng kiểm thử đã chốt trước đó.
