# Benchmark B v0.2 — contract và vận hành

## Dữ liệu và đánh giá

`python -m benchmark_b.runner prepare-v02` sinh bản v0.2 riêng và locator map; v0.1 giữ nguyên. Map lấy cấu trúc parent của graph, bảo toàn d/đ và ARTICLE chứa text trực tiếp. Không dùng ID M4 làm canonical gold. Mỗi lần chấm sẽ kiểm tra hash graph và toàn bộ map/text, chặn map sai hoặc stale. Đây là kiểm tra tính nhất quán; gold vẫn phải đối chiếu tài liệu gốc độc lập để tránh kế thừa lỗi parser.

Evidence giữ ID chunk/node, rank, text, alignment status và các locator nhận diện được. Corpus có source spans ký tự cho từng node và giữ nguyên text pháp luật; không thêm header mang đáp án/chain gold vào prompt extraction. Mỗi chunk chỉ được khớp với text thực nằm trong chunk, có filter article nếu SDK trả file_path. Đoạn trùng nhiều nơi không tự gán vị trí. Đoạn bị cắt không đủ nhận diện được ghi UNRESOLVED.

Hybrid xuất raw retrieval records, evidence retrieval và bounded generation context riêng. LightRAG dùng aquery_llm một lần để lấy cả source chunks và answer, tránh hai lần retrieval trả context khác nhau. M10 Mode B có directed source/target trong mỗi cạnh; Mode A hiện chỉ xuất norm records nên chain trace ở Mode A là not_measured. LightRAG cũng chưa có legal typed traversal trace: Chain metrics của baseline là not_measured, target/content recall vẫn có thể chấm từ evidence sau khi annotation hoàn thiện. Không so hai hệ bằng trung bình chain trên hai tập quan sát khác nhau.

Reference paths cũ giữ tất cả nhánh trong required_paths; các nhóm accepted_chain_sets khác nhau biểu diễn các cách giải hợp lệ. Quan hệ parent-child được suy ra từ cấu trúc. Các nhãn nghĩa pháp lý DIRECT_REFERENCE cần reviewer sửa thành REQUIRES_CONDITION_FROM / EXCEPTION_REFERENCE / INHERITS_RIGHTS_OBLIGATIONS khi cần và đánh dấu REVIEWED. Không tự coi đây là gold đã duyệt. Chain scoring chờ nhãn được duyệt, tôn trọng thứ tự, tất cả nhánh và alternative sets.

129 atomic facts đã có ID/text/evidence; role ban đầu UNREVIEWED. Reviewer gán role REQUIRED_CONDITION, SUBJECT_SCOPE, RIGHT_OR_OBLIGATION, EXCEPTION, PROHIBITION, CONSEQUENCE hoặc PROCEDURAL_REQUIREMENT. Ngoại lệ/forbidden claims chuyển thành annotation riêng, supporting_locators để trống đến khi review, candidate_locators chỉ là gợi ý nguồn chứ chưa được dùng làm chứng cứ.

## Lệnh chạy

Chạy tại root repo, kích hoạt môi trường có requirements.txt. LightRAG SDK phải hỗ trợ initialize_storages, ainsert, aquery_llm, finalize_storages. Chưa cài SDK thì dừng rõ lỗi. Ghi version package thực cài trong báo cáo run.

```powershell
python -m benchmark_b.runner prepare-v02
python -m benchmark_b.runner prepare-corpus

# Chỉ đo M6, tạo output riêng, không ghi đè output M6 đã curate.
python -m benchmark_b.runner extract-m6 --run-id m6_fresh_01

# Chỉ indexing LightRAG; dùng run-id mới để có workspace mới.
python -m benchmark_b.runner index --system lightrag --fresh --run-id light_fresh_01

# QA evaluation là thí nghiệm riêng. Cùng run-id LightRAG để dùng index vừa tạo.
python -m benchmark_b.runner run --system hybrid --run-id qa_hybrid_01 --mode AUTO
python -m benchmark_b.runner run --system lightrag --run-id light_fresh_01

# Sau human review: chấm lại từ answers + reviewer decisions, không gọi API.
python -m benchmark_b.runner score-v02 --answers outputs/benchmark_b/hybrid/qa_hybrid_01/answers.jsonl --reviews outputs/benchmark_b/hybrid/qa_hybrid_01/review_decisions.json
python -m benchmark_b.compare_costs --hybrid outputs/benchmark_b/hybrid/m6_fresh_01/api_events.jsonl --lightrag outputs/benchmark_b/lightrag/light_fresh_01/api_events.jsonl
```

Không chạy lại prepare-v02 sau khi đã review thủ công mà chưa lưu/commit các annotation; nó là phép migration tái lập từ v0.1 và sẽ tái sinh bản draft. Freeze phiên bản, hash và commit sau review. Không tự dùng bộ test 50 câu để tối ưu pipeline; dành câu development riêng.

## Người chấm và quy tắc metric

Locator recall và hierarchy completeness chấm bằng code trên evidence; chain chấm tuples source/type/target theo thứ tự. Citation chấm explicit Điều–Khoản–Điểm theo precision và recall, chưa phải chứng minh logic viện dẫn đúng. Câu insufficient-corpus loại khỏi các metric nội dung/evidence/citation. Câu không chain hoặc không exception là not_applicable. Câu có metric nhưng chưa có trace/annotation/review là not_measured. Hai loại thiếu này có mẫu số riêng; score không quan sát được luôn null.

`review_decisions.json` để người review chấm từng fact 0 (sai/thiếu), 0.5 (một phần), 1 (đủ); exception tương tự; forbidden claim 1 nghĩa claim sai có xuất hiện. Thêm reviewer và REVIEWED mới nhập điểm. Unsupported claim rate, abstention accuracy và refusal quality cần reviewer cho số [0,1]. Không dùng từ khóa từ chối làm điểm pháp lý cuối. Template đi cùng human_review.csv và answers.jsonl; reviewer phải xem evidence/gold, không chỉ câu trả lời. LLM Judge chưa được bật: các điểm ngữ nghĩa chờ người review thay vì dùng mock.

`structural_summary.json` có mean, n_eligible, n_scored, n_not_measured, n_not_applicable và eligible_question_ids. Không có overall score. Exact Recall@5 có giới hạn 5 evidence units: câu có 6 căn cứ có thể không đạt 1. Cần báo thêm context completeness toàn context để thể hiện đủ điều kiện, cố định budget text và K giữa các hệ trước khi chạy chính thức.

## Chi phí indexing extraction

M6 bắt HTTP response trước Instructor parsing nên giữ usage mọi SDK/Instructor retry. Log không chứa key, prompt hay exception message. LightRAG ghi mọi call callback indexing, tắt local LLM cache, giữ cùng event loop cho storage; query log có phase riêng. Operation hiện graph_index_llm_unclassified vì SDK chưa truyền nhãn extraction/gleaning/merge đáng tin cậy: tổng chi phí indexing LLM có thể cộng đầy đủ, breakdown từng operation cần hook role của phiên bản SDK thực cài. Không phân loại bằng đoán prompt rồi công bố là chính xác.

Event giữ generation ID, model/provider nếu có, tokens, provider_cost_usd từ usage.cost, cached_tokens, attempt và latency. OpenRouter hiện trả usage tự động; không dùng tham số include deprecated. Nguồn: https://openrouter.ai/docs/cookbook/administration/usage-accounting . CostLedger cũ giữ để tương thích, số tính từ bảng giá chỉ là estimated_tariff_cost_usd; nguồn đối soát billed cost là api_events.jsonl. Thiếu usage hoặc cost thì báo chưa hoàn chỉnh, không thay bằng 0. Không tự nhận fresh local cache đồng nghĩa provider prompt cache MISS; provider cache được log riêng.

M6 và LightRAG lấy cùng file clean TXT làm nguồn; manifest hash giữ đầu vào. M6 gửi candidates kèm parent context; LightRAG index trực tiếp toàn bộ TXT thành một document nguồn và tự chunk. Physical graph chỉ dùng cho locator mapping/evaluation, không dùng làm input index LightRAG. Chênh lệch token gồm prompt/schema/history lặp và gleaning/merge; không chỉ token text corpus. Khi diễn giải so sánh phải kiểm tra manifest, model/provider, trạng thái cache và thành công extraction. Hai key riêng tùy chọn trong .env.example; fallback key chung vẫn chạy. Phí query, judge và local compute không vào extraction comparison.

LightRAG query contract cố định: graph `top_k=5`, `chunk_top_k=5`, `max_total_tokens=10000`, entity budget 2000, relation budget 2000, rerank tắt. Năm chunks 1200 token dùng tối đa khoảng 6000 token; phần còn lại dành cho graph context. Runner từ chối top_k khác 5 để tránh thay đổi cấu hình giữa các run.

## Kiểm tra trước chạy thật

Chọn sáu câu đại diện dựa trên category (direct, multi-condition, one-hop, multi-hop, subject, insufficient); kiểm tra source chunks thật, text alignment và draft annotation trước chạy 50. Chưa chạy pilot thật trong thay đổi này do môi trường hiện thiếu instructor và lightrag; unit tests dùng HTTP/SDK stubs. Không suy ra số liệu QA hoặc chi phí nghiên cứu từ unit tests.
