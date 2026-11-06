# Báo cáo bộ dữ liệu 50 câu hỏi — Benchmark B

## 1. Mục đích

Benchmark B là bộ dữ liệu hỏi–đáp pháp luật để đánh giá truy hồi, tổng hợp căn cứ và trả lời trên **Chương III, Luật Đất đai năm 2024, Luật số 31/2024/QH15** (Điều 26–48). Bộ dữ liệu được lập cho phép so sánh LightRAG với Hybrid Parser/UKG trên cùng một phạm vi luật, đặc biệt ở các tình huống điều kiện, ngoại lệ, phân biệt chủ thể và dẫn chiếu chéo.

Đây là benchmark độc lập với Benchmark A (ba pipeline Naive/Hybrid/LightRAG cũ). Không gộp kết quả hai benchmark thành một điểm chung vì corpus, mục tiêu và contract đánh giá khác nhau.

## 2. Phiên bản được dùng khi chạy chính thức

| Thành phần | Giá trị |
|---|---|
| File gold chính thức | `datasets/benchmarks/benchmark_B_v03.json` |
| Phiên bản | `0.3` |
| Trạng thái | `HUMAN_REVIEWED` |
| Số câu | 50 |
| Phạm vi corpus | Chương III, Điều 26–48 |
| Bản đồ locator–node | `datasets/benchmarks/benchmark_b_locator_map.json` |
| File sign-off | `datasets/benchmarks/benchmark_B_v03_human_signoff.csv` |
| Kết quả sign-off | 50/50 câu `APPROVED` |

Metadata của bản v0.3 lưu dấu vết SHA-256 của DOCX nguồn, physical graph và sign-off CSV. Runner chỉ chấp nhận dataset mang trạng thái `HUMAN_REVIEWED`; các bản draft/AI-review-candidate không phải đầu vào chạy chính thức.

## 3. Thành phần và phân bố câu hỏi

### 3.1 Khả năng trả lời

| Nhóm | Số câu | Ý nghĩa đánh giá |
|---|---:|---|
| `ANSWERABLE_IN_CHAPTER_III` | 47 | Có đủ căn cứ để trả lời trong corpus Chương III. |
| `INSUFFICIENT_CORPUS` | 3 | Không có đủ căn cứ trong corpus; hệ thống phải từ chối/thừa nhận giới hạn. |

Ba câu insufficient-corpus không có positive retrieval gold. Vì thế không chấm Recall@k, chain metric hoặc citation-content metric như câu trả lời được; thay vào đó chấm hành vi abstention/refusal khi có review.

### 3.2 Nhóm năng lực pháp lý

| `benchmark_b_category` | Số câu | Năng lực chính |
|---|---:|---|
| `DIRECT_RIGHT_OBLIGATION` | 8 | Truy hồi trực tiếp quyền, nghĩa vụ. |
| `MULTI_CONDITION` | 10 | Liệt kê/tổng hợp nhiều điều kiện. |
| `CROSS_REF_ONE_HOP` | 6 | Theo một dẫn chiếu explicit. |
| `CROSS_REF_MULTI_HOP` | 4 | Theo chuỗi dẫn chiếu nhiều bước. |
| `PARENT_CHILD_SYNTHESIS` | 4 | Kết hợp Điều–Khoản–Điểm. |
| `SUBJECT_DISAMBIGUATION` | 5 | Phân biệt chủ thể và chế độ sử dụng đất. |
| `EXCEPTION_PROHIBITION` | 7 | Ngoại lệ, hạn chế hoặc cấm. |
| `LEGAL_SCENARIO` | 3 | Áp dụng quy định vào tình huống. |
| `INSUFFICIENT_CORPUS` | 3 | Nhận biết không đủ căn cứ. |

Phân bố độ khó: 15 câu mức 1, 20 câu mức 2, 15 câu mức 3. Toàn bộ câu hỏi ở dạng paraphrase, hạn chế việc chỉ khớp nguyên văn điều luật.

## 4. Ground truth và đơn vị annotation

Mỗi câu hỏi không chỉ có đáp án tham chiếu mà còn có các lớp ground truth độc lập với từng hệ thống:

| Trường | Vai trò |
|---|---|
| `gold_locations` | Locator pháp lý chuẩn ở cấp Điều/Khoản/Điểm. |
| `relevant_articles` | Projection cấp Điều phục vụ Recall@5 và MRR@5. |
| `acceptable_evidence_sets` | Tập locator bằng chứng có thể chấp nhận. |
| `reference_chain`, `accepted_chain_sets` | Đường dẫn dẫn chiếu với node và nhãn cạnh. |
| `hierarchy_requirements` | Parent context và child evidence cần có. |
| `required_atomic_facts` | Các mệnh đề bắt buộc của câu trả lời. |
| `required_exceptions` | Ngoại lệ bắt buộc phải nêu khi áp dụng. |
| `forbidden_claims` | Khẳng định không được đưa ra. |
| `reference_answer` | Đáp án tham chiếu để reviewer/judge đối chiếu. |
| `answerability`, `expected_behavior` | Quy tắc trả lời hoặc abstention. |

Tổng annotation của v0.3 gồm **143 gold locators**, **131 atomic facts**, **18 câu có accepted chain set**, **14 câu có ngoại lệ bắt buộc** và **10 câu có forbidden claims**.

Canonical locator dùng dạng:

```text
LD2024:A<Điều>[:K<Khoản>][:D<Điểm>]
```

Ví dụ: `LD2024:A46:K1:Da` là điểm a khoản 1 Điều 46. Locator map ràng buộc locator với physical node ID, text và span nguồn; không được tự tạo ID node mới khi đánh giá.

## 5. Quy trình xây dựng và kiểm duyệt

```text
DOCX Luật Đất đai, Chương III
        ↓ M1–M4 / clean-text / physical graph
Locator map chuẩn Điều–Khoản–Điểm
        ↓
Soạn 50 câu + đáp án + ground truth nhiều lớp
        ↓
AI-assisted review candidate v0.3
        ↓
Human sign-off từng câu
        ↓
benchmark_B_v03.json (HUMAN_REVIEWED)
```

Human sign-off lưu quyết định, reviewer, ngày review và ghi chú cho từng câu. Việc ký duyệt xác nhận chất lượng bộ gold; không biến LLM judge thành human review cho từng kết quả trả lời của hệ thống.

## 6. Cách dùng để chấm

1. Chạy retrieval/generation mà không truyền bất kỳ trường gold nào vào hệ thống.
2. Chuẩn hóa evidence hai hệ thống về `EvidenceItem` có locator và `alignment_status`.
3. Chấm deterministic retrieval/structure từ output và gold.
4. Chấm nội dung pháp lý bằng LLM judge có provenance hoặc human review theo contract.
5. Báo cáo mẫu số metric: `scored`, `not_measured`, `not_applicable`; không quy đổi `N/A` thành 0.

## 7. Giá trị nghiên cứu và giới hạn

Bộ dữ liệu cho phép tách bốn câu hỏi nghiên cứu:

- Hệ thống có tìm được Điều liên quan không?
- Có đưa đúng bằng chứng Điều–Khoản–Điểm vào context không?
- Có tái dựng được chuỗi dẫn chiếu đã định nghĩa không?
- Câu trả lời có đủ điều kiện/ngoại lệ và tránh khẳng định bị cấm không?

Tuy nhiên, 50 câu chỉ nằm trong một chương của một luật. Kết quả phản ánh năng lực trong phạm vi này, không đủ để khẳng định khả năng tổng quát cho toàn bộ pháp luật Việt Nam. Citation metric cũng phải được diễn giải thận trọng: citation parser không nhận ra mọi biến thể trình bày trích dẫn; mismatch không tự động đồng nghĩa câu trả lời sai về pháp lý.

## 8. Câu văn gợi ý cho báo cáo nghiên cứu

> Nhóm xây dựng Benchmark B gồm 50 câu hỏi pháp lý trên Chương III Luật Đất đai 2024. Mỗi câu được gắn locator chuẩn Điều–Khoản–Điểm, atomic facts, ngoại lệ, forbidden claims và, khi cần, chuỗi dẫn chiếu được chấp nhận. Bộ gold v0.3 đã được human sign-off cho toàn bộ 50 câu. Thiết kế này cho phép đánh giá tách biệt retrieval, evidence grounding, tái dựng dẫn chiếu và chất lượng câu trả lời; đồng thời bảo đảm các câu ngoài phạm vi corpus chỉ được chấm theo hành vi abstention phù hợp.
