# 3.4.3. Cấu hình và điều kiện đối sánh Benchmark B

## 1. Mục tiêu

Benchmark B so sánh LightRAG và Hybrid Parser/UKG trên cùng bộ 50 câu hỏi pháp luật thuộc Chương III Luật Đất đai. Mục tiêu của cấu hình đối sánh là giữ những điều kiện chung ở mức có thể so sánh, đồng thời công bố rõ khác biệt kiến trúc indexing của hai hệ thống.

Không coi hai hệ thống là có cùng biểu diễn nội bộ: LightRAG sử dụng chunk và graph do LightRAG xây dựng từ văn bản, còn Hybrid Parser sử dụng các node pháp lý được tách theo cấu trúc Điều–Khoản–Điểm và UKG đã xây dựng trước. Vì vậy, việc so sánh tập trung vào đầu ra truy hồi, câu trả lời, căn cứ pháp lý và chi phí được ghi nhận trong cùng giao thức benchmark.

## 2. Corpus dùng chung

Hai hệ thống cùng sử dụng nội dung Chương III của Luật Đất đai từ:

`outputs/clean_texts/clean_Luat_dat_dai_chuong_3.txt`

Corpus được cố định trước khi chạy benchmark. Bộ câu hỏi và nhãn vàng được lưu độc lập tại:

`datasets/benchmarks/benchmark_B_v03.json`

Phiên bản gold v0.3 đã được human review và dùng chung cho cả hai adapter. Locator chuẩn của benchmark không phụ thuộc vào chunk ID của LightRAG hoặc node ID của Hybrid Parser. Việc đối chiếu được thực hiện thông qua canonical locator Điều–Khoản–Điểm.

Mỗi run cần lưu manifest gồm đường dẫn corpus, checksum corpus, phiên bản gold, thời điểm chạy và cấu hình hệ thống. Không dùng output của một hệ thống làm input indexing cho hệ thống còn lại.

## 3. Cấu hình LightRAG

LightRAG indexing trực tiếp file text Chương III. Hệ thống thực hiện token-based chunking và xây dựng biểu diễn graph/chunk riêng của LightRAG. Các chunk không được tạo theo ranh giới pháp lý Điều–Khoản–Điểm một cách bắt buộc.

Cấu hình của lượt chạy LightRAG full v03:

| Thành phần | Cấu hình |
|---|---|
| Input indexing | File clean text Chương III |
| Graph retrieval top-k | 5 |
| Chunk retrieval top-k | 5 |
| Tổng context budget | 10.000 token |
| Entity context budget | 2.000 token |
| Relation context budget | 2.000 token |
| Model indexing/query | `openai/gpt-4o-mini` qua OpenRouter |
| Judge | `openai/gpt-4o-mini` |
| Chế độ đánh giá | 50 câu hỏi, cùng gold v0.3 |

LightRAG không xuất `reference_paths` có source, relation type và target theo contract chain của Benchmark B. Vì vậy các metric chain-level của LightRAG được ghi nhận là `N/A`, không quy đổi thành 0.

## 4. Cấu hình Hybrid Parser/UKG

Hybrid Parser indexing theo legal structure. Pipeline M1–M9 đã được chạy trước để tạo physical graph, semantic graph, canonical graph và unified knowledge graph. M5 sử dụng embedding local nên không tính là chi phí API LLM. M6 dùng LLM để trích xuất thực thể/quan hệ; M7–M9 chuẩn hóa, kiểm tra và hợp nhất graph.

Trong lượt benchmark Hybrid Parser, UKG được cố định trước khi chạy query, không indexing lại trong từng câu hỏi. M10 sử dụng `AUTO_FUSION`, kết hợp anchor search, truy hồi quan hệ dẫn chiếu, mở rộng node cha/con và lựa chọn evidence theo provenance.

Cấu hình chính của lượt chạy Hybrid Parser full v04:

| Thành phần | Cấu hình |
|---|---|
| Input query corpus | UKG M1–M9 đã chuẩn bị trước |
| Anchor top-k | 5 |
| Retrieval mode | `AUTO_FUSION` |
| Embedding | M5 local embedding |
| Answer model | `openai/gpt-4o-mini` qua OpenRouter |
| Judge model | `openai/gpt-4o-mini` |
| Judge retry | Tối đa 3 lần khi output không hợp lệ |
| Gold/evaluator | Gold v0.3 và evaluator chung Benchmark B |

Khác với LightRAG, Hybrid Parser có locator và cấu trúc pháp lý tường minh hơn, đồng thời có thể xuất evidence provenance, explicit reference edges, hierarchy steps và answer paths. Tuy nhiên, các trường này chỉ được chấm khi adapter xuất đúng contract; việc có UKG không tự động đồng nghĩa chain được xem là đúng.

## 5. Khác biệt indexing cần công bố

### 5.1. Token-based chunking của LightRAG

LightRAG chia văn bản thành các đoạn theo cơ chế chunking của hệ thống, sau đó dùng các đoạn và thực thể/quan hệ được sinh ra để phục vụ truy hồi. Ranh giới chunk có thể cắt qua hoặc gộp nhiều đơn vị pháp lý. Vì vậy:

- một chunk có thể chứa nhiều khoản hoặc điểm;
- locator chi tiết có thể không được giữ trong output câu trả lời;
- việc tính citation phải ánh xạ từ văn bản/chunk về canonical locator;
- chain dẫn chiếu không được suy ra chỉ từ việc chunk xuất hiện trong context.

### 5.2. Legal-structure-based indexing của Hybrid Parser

Hybrid Parser tách và lưu các đơn vị pháp lý theo cây Chương–Mục–Điều–Khoản–Điểm, sau đó bổ sung thực thể, quan hệ và dẫn chiếu vào UKG. Cách indexing này tạo thuận lợi cho:

- truy hồi đúng cấp Điều–Khoản–Điểm;
- lấy parent context và child evidence;
- biểu diễn explicit reference edge;
- truy nguyên nguồn của evidence;
- xây dựng và đánh giá answer path.

Đây là lợi thế thiết kế có chủ đích của Hybrid Parser, không phải một điều kiện cần phải loại bỏ. Tuy nhiên, báo cáo phải phân biệt lợi thế về biểu diễn cấu trúc với chất lượng câu trả lời cuối cùng.

## 6. Điều kiện so sánh công bằng

Các điều kiện sau được giữ chung:

1. Cùng corpus Chương III.
2. Cùng 50 câu hỏi và cùng thứ tự/`question_id`.
3. Cùng phiên bản gold locator, atomic facts, exceptions và forbidden claims.
4. Cùng quy tắc tính metric và cùng evaluator Benchmark B.
5. Cùng Judge model `openai/gpt-4o-mini`, prompt contract và JSON schema.
6. Chi phí indexing, query và Judge được tách riêng.
7. Các trường hợp không áp dụng ghi `N/A`, không ghi 0.
8. Không dùng gold locator để thay thế evidence trong quá trình trả lời.

Các điều kiện không đồng nhất cần công bố thay vì che giấu:

- biểu diễn indexing và granularity của chunk/node;
- cơ chế xây dựng graph;
- khả năng xuất provenance và reference path;
- cách hệ thống lập chỉ mục trước khi query;
- khả năng truy hồi nội bộ của từng kiến trúc.

## 7. Locator mapping và evaluator

Benchmark không so sánh trực tiếp node ID hoặc chunk ID. Adapter của từng hệ thống phải chuyển output về canonical locator. Một evidence được xem là ánh xạ được khi locator sau chuẩn hóa khớp với locator trong corpus/gold. Evidence không ánh xạ được phải giữ trạng thái `UNRESOLVED`, không được tự động gán vào gold.

Recall@5 và MRR@5 được tính ở cấp Điều theo `relevant_articles`. Các metric chi tiết hơn dùng locator cấp Khoản/Điểm. Citation được tách khỏi legal correctness: nêu đúng Điều không nhất thiết đồng nghĩa đã nêu đúng Khoản/Điểm hoặc giải thích đúng nội dung.

## 8. Judge và giới hạn diễn giải

Judge GPT-4o-mini đánh giá Legal Correctness, Atomic Fact Coverage, Condition Coverage, Exception Coverage, Subject-Scope Accuracy và các chỉ số an toàn. Các metric retrieval, locator, hierarchy và chain được tính bằng rule-based evaluator.

Do answer model và Judge dùng cùng model, Judge không độc lập tuyệt đối với generator. Vì vậy kết quả Judge phải được mô tả là đánh giá tự động theo rubric và gold annotation, không phải thẩm định pháp lý độc lập.

## 9. Kết luận

Thiết kế đối sánh của Benchmark B là hợp lệ nếu báo cáo đồng thời nêu hai mặt: cùng dữ liệu, câu hỏi, gold và evaluator; nhưng khác cách indexing và khả năng biểu diễn cấu trúc pháp luật. LightRAG được đánh giá trên chunk/graph do chính hệ thống tạo ra, còn Hybrid Parser được đánh giá trên legal-structure-based UKG. Các metric chung cho phép so sánh hiệu quả thực nghiệm, trong khi các metric chain chỉ được báo cáo khi hệ thống cung cấp đủ dữ liệu theo contract.

Do đó, không nên tuyên bố hai hệ thống có cùng pipeline nội bộ. Kết luận phù hợp là Benchmark B so sánh hai kiến trúc dưới cùng một bộ câu hỏi và giao thức đánh giá, đồng thời đo riêng tác động của cách indexing đối với truy hồi, căn cứ pháp lý và chất lượng câu trả lời.
