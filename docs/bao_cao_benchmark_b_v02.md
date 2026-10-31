# Báo cáo triển khai Benchmark B v0.2

Ngày: 30/10/2026. Nhánh làm việc: benmark_b.

## Phạm vi đã triển khai

Giữ dataset v0.1, tạo dataset v0.2 draft và map ID riêng; bổ sung evidence alignment, evaluator cấu trúc, review workflow và per-request API ledger cho extraction indexing. Chi phí nghiên cứu là M6 vs mọi LLM callback indexing LightRAG; query/judge không được cộng vào so sánh extraction.

## Phase 0 — Contract

Thêm contracts.py với CanonicalLocator, EvidenceItem, ReferenceStep, AtomicFact. Locator dùng LD2024:A...:K...:D..., không phụ thuộc hậu tố ID M4. Giữ d/đ Unicode khác nhau. Bốn trạng thái alignment và ba trạng thái metric được định nghĩa riêng. Không đưa đáp án/gold annotation vào retrieval.

## Phase 1 — Mapping

prepare.py sinh benchmark_B_v02.json và benchmark_b_locator_map.json. Kết quả trên graph thực: 217 locator vật lý cho Điều/Khoản/Điểm; map đủ **148/148 gold occurrences**, tương ứng **105 locator gold duy nhất** trong 50 câu. Hash graph/text được kiểm tra lại trước chấm. Điều 47 có direct ARTICLE text, hai điểm d/đ Điều 45 khoản 6 có ID khác nhau. Map không phải bằng chứng parser đúng với DOCX; vẫn cần reviewer độc lập đối chiếu nguồn gốc.

## Phase 2 — Evidence

Corpus giữ 23 article documents, bổ sung source spans ký tự của node. Hybrid M10 xuất retrieval_records; adapter giữ retrieved evidence riêng với bounded generation context. LightRAG dùng aquery_llm để lấy câu trả lời và chunks trong cùng query; sử dụng source chunk IDs/file_path và text thay vì suy evidence từ answer. Text lặp nhiều nơi hoặc thiếu fragment cần thiết được để UNRESOLVED. Không chỉ nhìn ID rồi tự cấp toàn văn Điều cho metric. Source chunks có thể bị split nên recall có thể không đo đủ: cần pilot xác nhận mức alignment thực trước báo cáo so sánh.

## Phase 3 — Reference chain

Có **18/50 câu** chứa chain. Migration giữ nhiều nhánh bắt buộc cùng một nhóm; additional accepted_chain_sets biểu diễn alternative hợp lệ. Chuyển chain thành source/type/target. PARENT_CHILD_CONTEXT xác định theo cấu trúc; nhãn DIRECT_REFERENCE chỉ là mặc định draft, phải review nghĩa pháp lý. Mode B Neo4j trả directed relationship IDs; adapter có phép chuyển BELONG_TO sang parent-child và REFERS_TO/REFERENCE_TO sang direct reference. Mode A không có trace: not_measured. LightRAG chưa có trace pháp lý tương đương: not_measured. Không công bố chain superiority chỉ vì baseline thiếu trace.

## Phase 4 — Atomic annotations

Chuyển **129 facts** thành annotation có ID, text, evidence_any_of, weight, required và review status. Chuyển **13 exceptions** và **8 forbidden claims** thành annotation riêng. Role ngữ nghĩa ban đầu UNREVIEWED; supporting_locators exception/forbidden để trống, candidate_locators không được xem là gold đã chứng minh. review.py sinh template và nhập quyết định người chấm với reviewer identity bắt buộc. Không gọi LLM Judge hay gán điểm giả; hoàn thiện gold pháp lý là công việc reviewer còn cần thực hiện.

## Phase 5 — Evaluator

Thêm Exact Locator Recall@5; hierarchy parent/child completeness trên bounded context; Reference Target Recall, Chain Step P/R/F1, Chain Exact Match và Edge Label Accuracy khi có trace và nhãn gold đã duyệt. Citation explicit cấp Điều/Khoản/Điểm có precision/recall. Semantic metrics lấy review quyết định từng fact/exception/forbidden claim; Unsupported Claim Rate, Abstention Accuracy, Refusal Quality cũng có kênh review. Citation parser là kiểm tra locator, không xác minh áp dụng luật về ngữ nghĩa.

## Phase 6 — Eligibility

Metric ghi value và status scored/not_measured/not_applicable. Negative corpus scope loại khỏi locator/chain/fact/citation; câu không chain không được điểm mặc định 1; exception rỗng không được cộng đủ. Summary xuất n_eligible, n_scored, n_not_measured, n_not_applicable và eligible IDs. Chưa có overall score. Top-5 evidence có giới hạn với câu cần hơn năm căn cứ; full context hierarchy báo riêng. Giữ checkpoint answers sau từng câu để không mất toàn bộ kết quả khi API lỗi.

## Phase 7 — Extraction cost

EventLog lưu run/system/phase/operation, generation ID, model/provider nếu có, attempt, node, tokens, usage.cost, provider cached tokens và latency. Không ghi key/prompt. MeteredTransport ghi từng HTTP attempt trước Instructor parsing nên không bỏ qua usage của response bị validation retry. M6 output benchmark nằm trong run directory mới, không ghi đè semantic_extraction.json curated.

LightRAG callback ghi usage mọi request và failure event, SDK retry tắt để giới hạn retry callback tối đa ba lần; local LLM cache tắt; storage dùng một event loop và initialize/finalize đúng SDK. Workspaces mới theo --run-id, không xóa workspace cũ. Hai key riêng có thể cấu hình, key chung là fallback. Tổng extraction LightRAG gồm tất cả call callback khi indexing. Breakdown operation cụ thể hiện graph_index_llm_unclassified vì chưa có role hook xác nhận từ SDK thực cài; không đoán nhãn extraction/gleaning/merge rồi trình bày như số liệu thật.

compare_costs.py đọc duy nhất phase=index và chỉ công bố phần trăm giảm khi có tokens/cost đầy đủ và cùng model. Manifest nguồn và provider/cache policy vẫn phải được kiểm tra trước diễn giải nghiên cứu. known_provider_cost_usd là tổng phần quan sát được, không phải total billed cost nếu complete=false. Bảng giá trong CostLedger cũ chỉ là tariff estimate; provider usage.cost là nguồn billed cost. OpenRouter usage hiện được trả tự động theo tài liệu chính thức: https://openrouter.ai/docs/cookbook/administration/usage-accounting .

## Phase 8 — Kiểm thử và điều kiện chạy thật

Vòng 1: **20 passed, 1 failed**. Lỗi tie-break giữa các alternative chain cùng Step F1 nhưng một chain khớp đúng thứ tự. Đã sửa để ưu tiên exact match khi Step F1 bằng nhau.

Vòng 2: **25 passed**. Bổ sung HTTP retry/cost, missing usage, alternative chain/order, negative eligibility, duplicate mapping, d/đ, Điều 47, explicit citation, review identity, Hybrid/LightRAG evidence contract và không trộn query cost.

Đã kiểm tra compileall cho benchmark_b, llm_extraction, retrieval; diff --check đạt. Vòng 3: **25 passed**, một cảnh báo deprecation từ plugin anyio/pytest. Đây là verification cuối sau bổ sung eligible IDs và endpoint-conditioned edge label accuracy. Tổng cộng đúng ba vòng pytest, đã dừng theo giới hạn.

Chưa chạy OpenRouter/Neo4j/LightRAG thật; Python đang dùng chưa có instructor và lightrag. Test HTTP và SDK dùng stubs không tạo số liệu nghiên cứu. Chưa có kết luận giảm token/USD hoặc QA quality. Cần môi trường dependency đầy đủ, legal gold review và pilot sáu nhóm câu trước chạy 50 câu chính thức. Bản v0.2 vẫn REQUIRES_HUMAN_LEGAL_REVIEW.

Hướng dẫn lệnh và rubric: docs/benchmark_b_v02.md. Thay đổi xóa file khóa DOCX ~$at_dat_dai_chuong_3.docx đã tồn tại trước tác vụ, được giữ nguyên theo trạng thái của người dùng.
