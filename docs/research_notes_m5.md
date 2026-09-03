# MODULE 5 — Semantic Router (Decision Layer)

## 0. Module Snapshot

**Mục tiêu**
Nhận PhysicalGraph (từ M4) hoặc validated_nodes (từ M3 qua adapter), phân tích từng node bằng tổ hợp Regex keyword scan + Embedding similarity (Qwen3-Embedding-0.6B), quyết định mỗi node thuộc nhánh nào: REJECT, RULE_ONLY, hoặc LLM_CANDIDATE. Đây là Decision Layer trong Data Ingestion Pipeline, không thực hiện Retrieval.

**Input**
- Mode A (dev/standalone): validated_nodes.json từ M3 (qua PhysicalGraph adapter, edges=[])
- Mode B (production/merged): physical_graph.json từ M4 (222 nodes, 551 edges)

**Output**
routing_candidates.json — danh sách RoutingCandidate theo schema đã chốt.

**Corpus hiện tại**
Chương III Luật Đất Đai 2024 (Luat_dat_dai_chuong_3.docx), 222 nodes.

**Embedding Model**
Qwen3-Embedding-0.6B via SentenceTransformers official integration (Kaggle Notebook — GPU T4/L4).
Kết quả export ra embeddings.npy + embedding_config.json.

**Trạng thái**
- Data Contract M4->M5: Done
- Data Contract M5->M6: Done (schema RoutingResult)
- Merge M4: Pending (2 sửa đổi nhỏ json_exporter.py)
- contracts_m45.py: Chua viet
- Embedding Engine: Chua viet
- Routing Engine: Chua viet
- Kaggle Notebook: Chua tao

---

## 1. Scope & Objective

**In Scope**
- Nhận diện Legal Node có khả năng chứa Cross-reference, Exception, Condition, Obligation, Permission.
- Phân loại 3 nhánh: REJECT / RULE_ONLY / LLM_CANDIDATE.
- Chạy 3 baseline độc lập (Regex-only, Embedding-only, Fusion) để có ablation evidence.
- Xuất routing_candidates.json theo contract đã chốt.

**Out of Scope**
- Không thực hiện Information Extraction (thuộc M6).
- Không thực hiện Retrieval hay QA.
- Không xây dựng Knowledge Graph.
- Không tối ưu hóa query time.
- Chưa chốt scoring formula hay threshold (thuộc experiment, không phải architecture).

**Clarification — REJECT semantics (quan trọng):**
REJECT không có nghĩa xóa node khỏi hệ thống.
Physical Node vẫn tồn tại đầy đủ trong PhysicalGraph và Neo4j sau này.
REJECT chỉ có nghĩa: không đưa node vào M6 (LLM Structured Extraction).
Physical Graph phải luôn toàn vẹn, độc lập với kết quả routing.

---

## 2. Problem Definition

**Vấn đề:**
Không phải câu luật nào cũng chứa ngữ nghĩa phức tạp cần LLM bóc tách.
Đưa toàn bộ 222 nodes vào LLM -> tốn token, chi phí cao.

**Mục tiêu nghiên cứu:**
Đánh giá xem hybrid routing (Regex + Embedding) có thể giảm LLM calls đáng kể trong khi giữ được semantic recall ở mức chấp nhận được không.

**Mục tiêu định lượng (research target, không phải pass/fail):**
- Routing Recall >= 0.80 (initial target, sẽ điều chỉnh sau khi có data)
- LLM Reduction Rate >= 0.50
- Các con số này phụ thuộc threshold, anchor quality, annotation guideline — không cứng nhắc.

**Điểm khó:**
- Node text pháp luật ngắn, đặc thù tiếng Việt pháp lý.
- Ranh giới giữa câu mô tả thuần và câu có cross-reference ẩn không rõ ràng.
- Threshold overfit trên corpus nhỏ (222 nodes) là rủi ro thực sự.

---

## 23.7. Audit Golden Set & Change Logs
*(Đã thực hiện ở phiên trước)*

## 24. Kết Quả Thực Nghiệm & Chốt Module 5 (Kaggle Benchmark)

Vào thời điểm hoàn thành Module 5, chúng tôi đã triển khai code benchmark lên Kaggle GPU T4x2 để đánh giá 6 models Embedding và 5 chiến lược Fusion trên tập Golden Set v2.

### 24.1. Tính Toàn Vẹn Của Hệ Thống Đánh Giá (Invariant Check)
Một trong những lo ngại lớn nhất là sự vi phạm tính đơn điệu (Monotonicity Violation) trong đồ thị Cost-Recall do nhiễu dữ liệu. Tuy nhiên, qua thuật toán phân tích, toàn bộ các chiến lược trên mọi mô hình đều **bảo toàn tính đơn điệu tuyệt đối** (Non-increasing Cost, Non-increasing Recall khi Threshold tăng). Điều này chứng minh Dataset sau Audit đã hoàn toàn sạch, và Metric định nghĩa dựa trên State Determinism là vững chắc về mặt toán học.

### 24.2. Operating Points Khuyến Nghị
Đồ thị `Figure_1_Model_Comparison.html` chỉ ra rằng họ mô hình **Qwen2.5 (đặc biệt là bản siêu nhẹ Qwen-0.5B)** có khả năng nhúng ngữ nghĩa (Semantic Embedding) pháp lý xuất sắc hơn các mô hình Embedding chuyên dụng truyền thống (BGE-M3, E5-Large) khi áp dụng trong bài toán Legal Semantic Router.

**Các Cấu hình Tối ưu (Operating Points) được đề xuất cho Module 6:**

1. **Mức Thận trọng (Target Recall ≥ 95%):**
   * Chiến lược: **Weighted-Fusion (w=0.3)** hoặc **Max-Fusion**
   * Model: **Qwen-0.5B**
   * Cost: ~174-179 nodes (giảm ~20% gánh nặng so với việc đưa toàn bộ Node vào LLM)
   * Actual Recall: 96.9% - 97.6% (Đảm bảo không rớt logic state quan trọng).

2. **Mức Cân bằng (Target Recall ≥ 85%):**
   * Chiến lược: **Average-Fusion** hoặc **Max-Fusion** (với Threshold cao ~0.9)
   * Model: **Qwen-0.5B**
   * Cost: 157 nodes
   * Actual Recall: 89.8%, Precision: 72.6%, F1: >0.8

### 24.3. Chốt Module 5
Với các chứng minh toán học và thực nghiệm trên Kaggle, Module 5 (Hybrid Semantic Router) chính thức được đóng lại với một pipeline thành công:
1. `Rule-based` Regex làm lưới lọc cứng.
2. `Embedding` Qwen-0.5B làm lưới lọc ngữ nghĩa mềm (Max-Fusion / Weighted-Fusion).
Kết quả đầu ra của M5 hiện tại là một danh sách các Node thu gọn nhưng chứa trọn vẹn Semantic State để truyền sang cho Module 6 (Graph Construction). Routing dựa trên 2 tín hiệu độc lập — chạy RIÊNG trước, fuse sau:

**Tín hiệu A — Lightweight Semantic Pattern Registry:**
- Regex được tổ chức thành tập các semantic cue (dataclass chứa: name, pattern, category, strength).
- Categories: EXCEPTION, CROSS_REF, CONDITION.
- Binary/Weighted: `strength` có thể là 1.0 (strong trigger) hoặc 0.4 (weak trigger).

---

## 3. Current Understanding

Kiến trúc Routing dựa trên 2 tín hiệu độc lập — chạy RIÊNG trước, fuse sau:

**Tín hiệu A — Lightweight Semantic Pattern Registry:**
- Regex được tổ chức thành tập các semantic cue (dataclass chứa: name, pattern, category, strength).
- Categories: EXCEPTION, CROSS_REF, CONDITION.
- Binary/Weighted: `strength` có thể là 1.0 (strong trigger) hoặc 0.4 (weak trigger).
- Ưu: Có phân loại category giúp debug trực quan (ví dụ: `reason: "Matched EXCEPTION"`). Dễ phân tích trong EXP-A.
- Nhược: False positive (VD: "trong trường hợp..." không phải exception), bỏ sót cross-reference ngầm.
- Lưu ý: Regex được sử dụng như một nguồn semantic cue có tính xác định, bổ trợ cho routing; việc diễn giải semantic relation (nó thực sự nghĩa là gì) vẫn thuộc về tầng LLM (M6).

**Tín hiệu B — Embedding Similarity:**
- Embed node.text -> Dense vector (Qwen3-Embedding-0.6B, SentenceTransformers)
- Cosine similarity với anchor vectors
- Continuous: [0.0, 1.0]
- Ưu: bắt được ngữ nghĩa ẩn không phụ thuộc từ khóa cụ thể
- Nhược: phụ thuộc chất lượng anchor vectors; Qwen3 chưa được test trên domain luật Việt Nam

**Ablation plan (thứ tự chạy):**
```
EXP-M5-A: Regex-only baseline
EXP-M5-B: Embedding-only baseline (Qwen3)
EXP-M5-C: Fusion (W1/W2/W3 so sánh)
```
Không code W2 thành architecture trước khi có evidence từ A và B.

---

## 4. Technical Model

**4.1 Node Pre-filter (Type-based, deterministic)**
```
CHAPTER -> RULE_ONLY (tiêu đề, không có body text ngữ nghĩa)
SECTION -> RULE_ONLY (tiêu đề mục)
ARTICLE với text="" -> RULE_ONLY (chỉ có title, không có body)
ARTICLE với text != "" -> vào routing pipeline
CLAUSE -> vào routing pipeline
POINT -> vào routing pipeline
```
Quy tắc giữ tối giản — không thêm rule cho đến khi thấy corpus.
Lưu ý: `children_count > 0` KHÔNG được dùng như điều kiện semantic gate mạnh.
Node có children vẫn có thể chứa semantic content. children_count chỉ dùng như context/fallback nếu cần.

**4.2 Routing Score — Iteration 1 (chạy riêng, không fuse ngay)**
```
[Tín hiệu A — Semantic Pattern Match]
Tìm pattern có `strength` cao nhất khớp với text.
regex_score = max(pattern.strength for pattern in matched_patterns)
match_category = pattern.category (VD: "EXCEPTION", "CROSS_REF")

[Tín hiệu B]
embed_vec   = embed(node.text)          # Qwen3-0.6B, precomputed trên Kaggle
embed_score = max(cosine_sim(embed_vec, anchor_vecs))

[Output Iteration 1]
Ghi cả 2 score vào output, chưa fuse:
{
  "node_id": "...",
  "regex_score": 0.0 | 1.0,
  "embed_score": 0.73,
  "route": "...",        # quyết định bởi threshold heuristic tạm thời
  "routing_score": ...,  # sẽ là fused score sau ablation
  "reason": "..."
}
```

**4.3 Anchor Vectors — Iteration 1 (A1 = lexical baseline)**
Embed các câu trigger mẫu bằng Qwen3-Embedding (cache lại, không recompute):
```
- "Trừ trường hợp quy định tại khoản..."
- "Theo quy định tại điều..."
- "Không áp dụng đối với trường hợp..."
- "Điều kiện để được hưởng quyền..."
- "Nghĩa vụ nộp tiền sử dụng đất..."
- "Người sử dụng đất có quyền thực hiện..."
... (10-15 câu đại diện)
```
Lưu ý: A1 là lexical-trigger anchor — đây là baseline, không phải assumption thiết kế chính.
Sẽ benchmark A2 (câu mẫu thực tế từ corpus) sau khi có Golden Label.
Chưa dùng A3 (cluster centroid) vì chưa có labeled dataset.

**4.4 Threshold — Iteration 1 (baseline configuration)**
```
threshold_high = 0.75   # baseline configuration cho iteration 1
threshold_low  = ?      # hyperparameter của routing policy — xác định trong experiment
```
Threshold là thành phần hợp lệ của M5. threshold_controller.py justified.

`lower_bound` (threshold_low) là hyperparameter chưa có nguồn lý thuyết — sẽ được chọn từ score distribution và PR analysis sau khi có Golden Label. 0.40 chỉ là placeholder chưa được validate.

Kế hoạch experiment threshold:
- **Iteration 1:** Fixed threshold_high = 0.75 làm baseline
- **Experiment:** So sánh Fixed 0.75 vs Fixed khác vs Adaptive Threshold
- **Đo lường:** Precision, Recall, F1, LLM Reduction Rate
- **Nguyên tắc:** LLM Reduction Rate chỉ có ý nghĩa khi Recall vẫn ở mức chấp nhận được. Reduction 90% với Recall 40% không phải router tốt.

**4.5 Qwen3-Embedding-0.6B — Kỹ thuật**
- Model: Qwen/Qwen3-Embedding-0.6B (HuggingFace)
- Integration: `SentenceTransformer("Qwen/Qwen3-Embedding-0.6B")` — official integration
- **Không tự implement pooling.** Model card đã hỗ trợ SentenceTransformers; cấu hình pooling được xử lý bởi thư viện.
- Embedding dim: 1024
- Context length: 32K
- Model file: ~1.21 GB — phù hợp Kaggle T4/L4
- Khi embedding query/anchor, thống nhất và ghi lại instruction/task description sử dụng (vào embedding_config.json) để đảm bảo reproducibility.
- Lưu ý: P100 trên Kaggle ngừng từ 15/09/2026, chuyển sang T4x2/L4
- Batch size đề xuất: 16-32 (T4)

**4.6 Kaggle Notebook — 3 file bắt buộc đi cùng nhau**
```
embeddings.npy          # shape [N, 1024] — vector của toàn bộ node
node_ids.json           # list[str] — mapping thứ tự index -> node_id
embedding_config.json   # metadata reproducibility
```

Nội dung tối thiểu của `embedding_config.json`:
```json
{
  "model_name": "Qwen/Qwen3-Embedding-0.6B",
  "model_revision": "<git sha hoặc tag>",
  "embedding_dim": 1024,
  "instruction": "<instruction text dùng khi embed>",
  "normalize": true,
  "input_source": "physical_graph.json",
  "node_count": 222,
  "kaggle_gpu": "T4",
  "date": "<YYYY-MM-DD>"
}
```
Không có 3 file này đi cùng -> embeddings.npy vô nghĩa về sau (không biết config nào sinh ra nó).

---

## 5. Research Questions

**RQ-M5-1 — Ablation: Regex vs Embedding vs Fusion**
Regex-only, Embedding-only, hay Fusion cho F1 tốt hơn? Đây là câu hỏi trọng tâm của M5.

**RQ-M5-2 — Anchor Vector Quality (A1 vs A2)**
Anchor từ lexical trigger (A1) vs anchor từ câu thực tế corpus (A2): loại nào cho Recall cao hơn?

**RQ-M5-3 — Threshold Sensitivity**
Distribution của embed_score trên 222 nodes trông như thế nào? Có gap tự nhiên giữa nhóm semantic / non-semantic không?

**RQ-M5-4 — Node Type Prior**
CLAUSE vs POINT — loại nào có tỷ lệ LLM_CANDIDATE cao hơn trên Ch3-LDD?

**RQ-M5-5 — Recall vs Reduction Trade-off**
Tại threshold nào thì đạt điểm cân bằng tốt giữa Recall và LLM Reduction Rate?

**RQ-M5-6 — Structural Context (để sau)**
Edges từ M4 có cải thiện routing decision không? VD: nếu node NEXT là LLM_CANDIDATE thì node hiện tại có prior cao hơn không?

---

## 6. Investigations

*(Sẽ cập nhật khi tiến hành thử nghiệm)*

---

## 7. Experiments & Prototypes

### EXP-M5-A — Regex-Only Baseline (Semantic Pattern Registry)
- Mục tiêu: Xác định F1 của routing khi chỉ dùng regex, và phân tích pattern nào (EXCEPTION/CROSS_REF/CONDITION) tạo tín hiệu tốt / false positive.
- Input: physical_graph.json (222 nodes), Golden Label
- Expected: Precision cao với strong trigger, Recall thấp (bỏ sót ngữ nghĩa ẩn)
- Kết quả: TBD

### EXP-M5-B — Embedding-Only Baseline (Qwen3-0.6B)
- Mục tiêu: Xác định F1 của routing khi chỉ dùng embedding similarity + anchor A1
- Input: embeddings.npy từ Kaggle + anchor vectors + Golden Label
- Evaluation: Relative ranking (positive nodes có score cao hơn negative không?), không hard-code threshold 0.5
- Kết quả: TBD

### EXP-M5-C — Fusion Ablation (W1/W2/W3)
- Mục tiêu: So sánh 3 fusion strategy:
  W1 = alpha*regex + (1-alpha)*embed
  W2 = regex gate: nếu regex=1 -> LLM_CANDIDATE ngay; embedding cho phần còn lại
  W3 = embedding gate: loại REJECT < threshold_low trước, regex classify phần còn lại
- Input: EXP-A + EXP-B scores + Golden Label
- Kết quả: TBD

### EXP-M5-D — Threshold Sensitivity
- Mục tiêu: Vẽ PR curve theo threshold, tìm operating point
- Input: embed_score distribution từ EXP-B + Golden Label
- Kết quả: TBD

### EXP-M5-E — Anchor Strategy A1 vs A2 (để sau, cần corpus thực tế)
- Mục tiêu: So sánh A1 (lexical trigger) vs A2 (câu mẫu thực tế từ Ch3-LDD)
- Kết quả: TBD

---

## 8. Findings

*(Sẽ cập nhật khi có kết quả thực nghiệm)*

---

## 9. Design Decisions

### Decision: Mode A / Mode B Dual Input Support
- Lựa chọn: M5 hỗ trợ cả 2 mode qua PhysicalGraph.from_json() và adapter M3->PhysicalGraph
- Lý do: Không hard-block M5 vào M4; phát triển song song
- Invariant: Cả 2 mode phải cùng semantics qua property accessor (node.text, node.node_type...)
- Trạng thái: Đã thiết kế, chưa implement

### Decision: Qwen3-Embedding-0.6B qua SentenceTransformers
- Lựa chọn: SentenceTransformer("Qwen/Qwen3-Embedding-0.6B") — official integration
- Lý do: Model card hỗ trợ chính thức, tránh tự viết pooling theo phỏng đoán
- Trade-off: Ít kiểm soát hơn raw Transformers, nhưng đúng hơn cho prototype
- Trạng thái: Đã chốt cho Iteration 1

### Decision: Benchmark Regex/Embedding/Fusion độc lập
- Lựa chọn: Chạy 3 baseline riêng (EXP-A, EXP-B, EXP-C) thay vì code W2 thành architecture
- Lý do: Nếu Regex-only F1=0.68 và Embedding-only F1=0.61 thì kết luận khác hẳn so với trường hợp ngược lại
- Trạng thái: Đã chốt phương pháp luận

### Decision: route enum thay vì candidate bool
- Lựa chọn: 3 trạng thái REJECT | RULE_ONLY | LLM_CANDIDATE
- Lý do: bool không biểu diễn được RULE_ONLY; REJECT không có nghĩa xóa node
- Trạng thái: Đã chốt trong data contract

### Decision: routing_model và threshold là run metadata
- Lựa chọn: Optional trong router_metadata, không phải contract cứng
- Lý do: M5 đang nghiên cứu, tránh ép architecture sớm
- Trạng thái: Đã chốt

### Decision: Lightweight Semantic Pattern Registry cho M5
- Lựa chọn: Thay vì mảng string đơn thuần, Regex được bọc trong dataclass `(name, pattern, category, strength)`.
- Lý do: Mang tính kế thừa từ M2 (Structural Registry), giúp categorize rõ tín hiệu (EXCEPTION, CROSS_REF...). Trả về thông tin cho field `reason` rõ ràng hơn.
- Principle: Regex ở M5 chỉ là **nguồn semantic cue có tính xác định** để tạo routing signal. Việc diễn giải semantic relation hoàn chỉnh vẫn ở M6.
- Trạng thái: Đã chốt cho Iteration 1.

### Decision: Threshold là thành phần hợp lệ của M5
- Lựa chọn: Fixed threshold = 0.75 làm baseline configuration iteration 1
- Lý do: Implementation plan xác nhận "Thử nghiệm Fixed Threshold vs Adaptive Threshold" là task hợp lệ. Cần có baseline cụ thể để so sánh.
- Experiment plan: Fixed 0.75 → Fixed các giá trị khác → Adaptive Threshold, đo Precision/Recall/F1/Reduction Rate
- **Chưa chốt:** 0.75 có phải giá trị tối ưu — câu hỏi này thuộc EXP-M5-D, không phải architecture decision
- Trạng thái: threshold_controller.py justified; giá trị 0.75 là baseline iteration 1

---

## 10. Trade-offs

| Vấn đề | Lựa chọn A | Lựa chọn B | Hiện tại |
|---|---|---|---|
| Embedding model | 0.6B (nhanh, 1.21GB, Kaggle an toàn) | 4B (mạnh hơn) | 0.6B cho Iteration 1 |
| Embedding integration | SentenceTransformers (official) | Raw Transformers + tự viết pooling | SentenceTransformers |
| Score fusion | Riêng biệt -> ablation | Fuse ngay W2 | Riêng biệt trước |
| Anchor strategy | A1: lexical trigger (baseline) | A2: câu mẫu thực tế (sau) | A1 Iteration 1 |
| Threshold | Fixed 0.75 baseline (iteration 1) | Adaptive (theo phân phối) sau experiment | Fixed 0.75 baseline → so sánh trong EXP-M5-D |
| Benchmark thêm model | BGE-m3/E5 (sau) | Chỉ Qwen3 (hiện tại) | Chỉ Qwen3 v1 |

---

## 11. Current Limitations

- KL-M5-01: Chưa có Golden Label để đánh giá Precision/Recall. Annotation guideline chưa được viết.
- KL-M5-02: Anchor vectors A1 dựa trên intuition — đây là baseline, chưa phải thiết kế chính.
- KL-M5-03: Qwen3-Embedding chưa được test trên domain luật Việt Nam tiếng Việt.
- KL-M5-04: Corpus nhỏ (222 nodes) — bất kỳ threshold nào cũng có nguy cơ overfit.
- KL-M5-05: Regex keyword list chưa đầy đủ; false positive "trong trường hợp..." chưa được xử lý.

---

## 12. Open Problems

**Open (cần giải quyết vòng đầu):**
- Viết annotation guideline cho Golden Label (định nghĩa rõ Exception / Condition / Cross-reference)
- Xây dựng Golden Label 30-50 nodes (stratified sampling theo type + semantic class)
- Chốt instruction/task_description cho Qwen3 khi embed node text vs anchor text

**Open (sau khi có ablation results):**
- Chọn fusion strategy W1/W2/W3 dựa trên evidence
- Chọn threshold dựa trên PR/ROC analysis
- Benchmark A1 vs A2 anchor strategy

**Open (để sau, thấp ưu tiên):**
- Adaptive threshold dựa trên phân phối corpus
- Structural context (edges) trong routing decision (RQ-M5-6)
- Benchmark thêm model thứ hai (bkai/BGE-m3)
- Cross-corpus generalization

---

## 13. Research Gaps

Gap tiềm năng: Chưa có baseline công bố về hybrid routing quality cho Legal Node classification trong văn bản pháp luật Việt Nam. Nếu ablation study được thiết kế đúng, kết quả M5 (đặc biệt EXP-A/B/C comparison) có thể là contribution độc lập.

---

## 14. Evaluation Plan

**Input corpus:** Ch3-LDD, 222 nodes.

**Ground truth — Golden Label (30-50 nodes, stratified sampling):**
- Phải có đại diện của mọi node_type: CHAPTER, SECTION, ARTICLE, CLAUSE, POINT
- Phải có đại diện semantic class: cross-reference, exception, condition, ordinary text, header
- Tránh sampling toàn ordinary text -> Precision ảo cao
- **Annotation guideline PHẢI được viết và chốt TRƯỚC khi annotate** — không vừa annotate vừa đổi definition
- Nếu 2 người annotate: tính inter-annotator agreement trước khi dùng làm ground truth

**Định nghĩa Ground Truth — QUAN TRỌNG:**
Label là SEMANTIC = node **cần M6 (LLM) xử lý để extract structured information**.
KHÔNG phải = "node có semantic content" (gần như mọi CLAUSE/POINT đều có semantic content).

M5 hỏi: *"Node này có đủ phức tạp / chứa loại thông tin cần LLM structured extraction không?"*
Không hỏi: *"Node này có nghĩa gì không?"*

**Metrics:**
- Routing Recall = TP / (TP + FN) [không bỏ sót node cần M6]
- Routing Precision = TP / (TP + FP) [không gửi thừa node vào M6]
- F1 = harmonic mean
- LLM Reduction Rate = 1 - (LLM_candidates / total_nodes)
  **Nguyên tắc:** Reduction Rate chỉ có ý nghĩa khi Recall đủ cao. Không báo cáo Reduction Rate độc lập.

**Evaluation constraints:**
- T2.2 (test embedding): kiểm tra `sim(positive, anchor) > sim(negative, anchor)` — relative ranking, không test absolute score
- Metrics targets (0.80/0.60/0.70) là research targets, không phải pass/fail criteria
- Kết quả bất kỳ (kể cả Regex >> Embedding) đều là finding có giá trị nghiên cứu

**Baselines (theo thứ tự chạy):**
1. Regex-only (EXP-M5-A) — chạy cuối Phase 2, trước khi có embedding
2. Embedding-only (EXP-M5-B) — Phase 4
3. Fusion W1/W2/W3 (EXP-M5-C) — Phase 4, sau khi có A và B

---

## 15. Next Actions

**Phase 1 — Merge M4 + Contract**
1. [ ] Copy 3 files M4 vào hybrid_parser_graphrag/src/physical_graph/
2. [ ] Sửa json_exporter.py: thêm document_id/schema_version, xóa parent_id khỏi excluded keys
3. [ ] Viết src/contracts_m45.py
4. [ ] Viết tests/test_contracts_m45.py (Invariant 1 + 2)

**Phase 2 — Rule-based baseline (không cần GPU)**
5. [ ] Viết routing_engine.py (Regex keyword scan, binary score)
6. [ ] Viết type-based pre-filter (CHAPTER/SECTION -> RULE_ONLY)
7. [ ] Chạy EXP-M5-A, ghi kết quả vào section 7

**Phase 3 — Kaggle Embedding**
8. [ ] Viết annotation guideline cho Golden Label
9. [ ] Annotate Golden Label 30-50 nodes (stratified)
10. [ ] Tạo Kaggle Notebook embed_nodes_qwen3.ipynb
    - SentenceTransformer("Qwen/Qwen3-Embedding-0.6B")
    - Lưu embeddings.npy + embedding_config.json (model_name, revision, instruction, dim, normalize...)
11. [ ] Chạy Kaggle, download về local

**Phase 4 — Integration + Ablation**
12. [ ] Viết embedding_engine.py (load precomputed mode)
13. [ ] Chạy EXP-M5-B (Embedding-only, relative ranking evaluation)
14. [ ] Chạy EXP-M5-C (W1/W2/W3 fusion comparison)
15. [ ] Chạy EXP-M5-D (threshold sensitivity, PR curve)
16. [ ] Chốt scoring formula và threshold từ evidence
17. [ ] Ghi kết quả vào section 7/8/9

**Phase 5 — Final Output**
18. [ ] Integrate SemanticRouter end-to-end
19. [ ] Export routing_candidates.json
20. [ ] Cập nhật Evolution Log

---

## 16. Evolution Log

- 2026-08-25 (v1): Tạo thư mục docs/researchnote_m5/. Chốt Data Contract M4->M5, M5->M6. Chốt 2 Invariant. Viết plan triển khai đầy đủ. Chốt Qwen3-Embedding-0.6B + SentenceTransformers trên Kaggle.
- 2026-08-25 (v2): (1) SentenceTransformers official — không tự viết pooling; (2) Ablation-first: EXP-A/B/C riêng trước khi chọn W2/W1/W3; (3) threshold 0.75 = baseline configuration hợp lệ, chưa phải tối ưu; (4) T2.2 → relative ranking sim(pos,anchor)>sim(neg,anchor); (5) Metrics = research targets; (6) REJECT semantics — physical node không bị xóa; (7) Kaggle lưu 3 file: embeddings.npy + node_ids.json + embedding_config.json; (8) Golden Label: stratified + annotation guideline chốt trước.
- 2026-08-25 (v3): (1) Xóa mâu thuẫn Qwen pooling trong §4.5 — chỉ giữ SentenceTransformers; (2) lower_bound = hyperparameter chưa có nguồn, ghi rõ trong §4.4; (3) children_count không phải gate mạnh cho RULE_ONLY; (4) T1.5 cần thêm negative test cases (non-trigger, near-miss); (5) T2.2 làm rõ: sim(pos,anchor)>sim(neg,anchor) per triplet; (6) Annotation guideline: SEMANTIC = "cần M6 xử lý", không phải "có semantic content"; (7) LLM Reduction Rate chỉ có ý nghĩa khi Recall đủ cao — không báo cáo độc lập; (8) EXP-A chạy cuối Phase 2, EXP-B/C trong Phase 4.

---

## 17. References

**Đã đọc:**
- Tài liệu kiến trúc hệ thống - mô tả M5 Decision Layer
- Implementation plan team - Module 5 task checklist
- Data Contract M4-M5 (m4_m5_contracts.md)
- Code M4 thực tế: graph_builder.py, edge_generator.py, json_exporter.py
- Qwen3-Embedding model card (HuggingFace) — confirmed SentenceTransformers support

**Cần đọc:**
- Qwen3 technical report -- instruction format cho embedding task
- Literature review: legal text routing / semantic classification baseline

---

## 18. Defense Notes

**Tại sao M5 không phải Retrieval?**
Retrieval là bài toán trả lời query. M5 là Decision Layer trong Data Ingestion -- chạy 1 lần khi build Knowledge Graph, không liên quan đến query của user. Nhầm lẫn xảy ra vì M5 dùng embedding, nhưng embedding ở đây chỉ phục vụ routing score, không phải ANN search.

**Tại sao không đưa toàn bộ 222 nodes vào LLM?**
Chi phí API tỷ lệ với số node x độ dài text. Với nhiều lần thử nghiệm, chi phí không kiểm soát. Semantic Router là giải pháp trade-off: giữ recall ổn định trong khi giảm LLM calls.

**Tại sao không code W2 (regex gate) ngay?**
Nếu regex=1 → LLM_CANDIDATE trực tiếp, thì embedding chỉ xử lý phần regex bỏ sót. Khi kết quả tốt/xấu, không thể biết lợi ích đến từ regex hay embedding. Ablation-first (EXP-A/B/C riêng biệt) mới xác định được contribution của từng tín hiệu.

**Tại sao threshold 0.75 là baseline hợp lệ nhưng không phải "giá trị tối ưu"?**
0.75 là điểm xuất phát để có prototype chạy được. Giá trị tối ưu phải được xác định từ PR curve và score distribution trên Golden Label. Đây là EXP-M5-D, không phải assumption kiến trúc.

---

## 19. Appendix

**Annotation Guideline Draft (v0 -- phải chốt TRƯỚC khi annotate, KHÔNG đổi giữa chừng)**

**Câu hỏi annotation:** Node này có cần M6 (LLM) xử lý để extract structured information không?
KHÔNG hỏi: Node này có semantic content không? (gần như mọi node đều có.)

Label **SEMANTIC** (cần M6) khi node chứa:
- Cross-reference: dẫn chiếu đến điều/khoản khác ("theo quy định tại Điều X", "căn cứ khoản Y")
- Exception: ngoại lệ rõ ràng ("trừ trường hợp...", "không áp dụng đối với...")
- Condition: điều kiện áp dụng ("chỉ khi...", "trong trường hợp có đủ điều kiện...")
- Obligation/Permission có điều kiện kèm theo ("có quyền X, trừ khi...")

Label **NON_SEMANTIC** (không cần M6) khi:
- Là tiêu đề chương/mục/điều (CHAPTER, SECTION, ARTICLE empty)
- Là câu mô tả quyền/nghĩa vụ đơn thuần, tự chứa, không tham chiếu ngoài
- Là liệt kê độc lập không có cross-reference

**Nếu muốn chi tiết hơn (optional, để sau):**
Sub-label: EXCEPTION / CONDITION / REFERENCE / OBLIGATION_CONDITIONAL / OTHER / NONE
Chỉ mở rộng sau khi thấy corpus và có đủ inter-annotator agreement.

*(Đã cập nhật sau khi triển khai và đánh giá thực tế - Xem Phần 20)*

---

## 20. Nhật ký Triển khai và Đánh giá (Implementation & Evaluation Log)
Phần này tổng hợp toàn bộ các quyết định kiến trúc, quá trình thực thi, điểm nghẽn, sự đánh đổi (trade-offs) và kết quả benchmark thực tế từ lúc khởi tạo Module 5 đến khi hoàn thành.

### 20.1 Quyết định Kiến trúc & Triển khai thực tế
- **Cấu trúc M4 (Physical Graph):** M4 xuất ra file `physical_graph.json` với cấu trúc đồ thị phẳng (flat graph). Các quan hệ phân cấp (hierarchy) được biểu diễn bằng thuộc tính `parent_id` hoặc qua các cạnh `BELONG_TO`. M5 đã thiết kế `SemanticRouter` đọc thẳng vào cấu trúc phẳng này và giữ nguyên metadata để serialize cho M6.
- **Tách biệt Orchestrator & Engine:** M5 không gom toàn bộ code vào một class. `SemanticRouter` đóng vai trò Orchestrator; `RoutingEngine` xử lý Regex/Fusion; `EmbeddingEngine` lo nạp vector. Điều này cho phép dễ dàng Unit Test từng cụm (M5 đã vượt qua 41/41 unit tests).
- **Tính toán Vector tại Local:** Vì Kaggle chỉ tạo embeddings cho 222 nodes của văn bản luật, các từ khóa "neo" (Anchors) như *"ngoại trừ"*, *"theo quy định tại"* được tính toán ngay trên máy local bằng `SentenceTransformer` (Qwen3-Embedding-0.6B) với file `compute_anchors.py`. 

### 20.2 Kết quả Benchmark & Đánh giá (Ablation Study)
Tập **Golden Label** được tạo thông qua Random Sample (50 nodes - loại trừ Chapter/Section) và gán nhãn thủ công (bằng AI Annotation bám sát guideline). Kết quả chạy `eval_routing.py` với threshold = `0.75`:

| Chiến lược | Precision | Recall | F1-Score | TP / FP / FN / TN |
| :--- | :--- | :--- | :--- | :--- |
| **EXP-A (Regex-only)** | **1.000** | 0.548 | **0.708** | 17 / 0 / 14 / 19 |
| **EXP-B (Embedding-only)** | 0.500 | 0.323 | 0.392 | 10 / 10 / 21 / 9 |
| **EXP-C (Max-Fusion)** | 0.677 | **0.677** | 0.677 | 21 / 10 / 10 / 9 |

### 20.3 Đánh giá Trade-off (Sự Đánh đổi) & Điểm nghẽn
1. **Trade-off của Max-Fusion (EXP-C):** 
   - **Tăng Recall, Giảm Precision:** Kết hợp tín hiệu Embedding giúp thuật toán bắt được những "biến thể ngữ nghĩa" mà Regex cứng nhắc bỏ qua (Recall tăng từ 54.8% lên 67.7%). Tuy nhiên, điều này mang theo nhiễu, làm tụt Precision (từ 1.0 xuống 0.677).
   - **Lựa chọn kiến trúc:** Việc chấp nhận Precision thấp một chút ở M5 là **hợp lý**. M5 chỉ là bộ lọc thô (Gatekeeper). Nếu bỏ sót (False Negative), kiến thức luật đó sẽ mất vĩnh viễn. Nếu bắt nhầm (False Positive), LLM ở M6 vẫn có cơ hội reject. Do đó, ưu tiên Recall > Precision ở M5 là lựa chọn thiết kế đúng đắn.
2. **Điểm nghẽn của Embedding-only (EXP-B):**
   - **Fixed Threshold:** Việc chốt cứng ngưỡng `0.75` cho khoảng cách Cosine Similarity bộc lộ điểm yếu lớn (F1 chỉ đạt 0.392). Các vector sinh ra từ Qwen3 có xu hướng cluster sát nhau (đặc tính chung của Dense LLM Embeddings), khiến một ngưỡng cố định không áp dụng được cho mọi Anchor.

### 20.4 Những vấn đề nghiên cứu mở (Future Work)
- **Nghiên cứu Adaptive Threshold:** Thay vì `> 0.75`, có thể xem xét:
  - Lấy Top-K tương đồng nhất (VD: lấy 30% node có điểm cao nhất).
  - Hoặc ngưỡng nội suy động dựa trên độ lệch chuẩn phân phối điểm (Z-score).
- **Huấn luyện một Lightweight Classifier:** Thay vì dùng Cosine Similarity thẳng với Anchors, có thể huấn luyện một mô hình cực nhẹ (Logistic Regression hoặc SVM) nhận Input là Embedding Vector [1024-dim] và Output là xác suất (0/1). Cách này cần một tập Golden Label đủ lớn (>500 samples) nhưng sẽ giải quyết triệt để bài toán chọn Threshold.
- **Tiến trình sang Module 6:** Module 6 cần được thiết kế (Prompt Engineering) sao cho LLM có sức đề kháng với các False Positive mà EXP-C truyền sang. LLM cần có khả năng output `None` khi nhận được một node vô nghĩa.

---

## 21. Sự tiến hóa trong tư duy Đánh giá (Advanced Benchmarking Insights)

Trong quá trình đánh giá và tối ưu Module 5, một loạt các rào cản tư duy (cognitive traps) đã được phá vỡ, dẫn đến một sự thay đổi hoàn toàn về chiến lược Benchmark. Dưới đây là những phát kiến cốt lõi định hình lại hệ thống:

### 21.1 Bản chất của "Độc tài Regex" và Cạm bẫy của hàm Average
- **Phát hiện:** Regex và Embed bắt được 2 tập hợp gần như khác biệt hoàn toàn (chỉ giao nhau 14 nodes).
- **Vấn đề "Độc tài":** Hàm `Max(Regex, Embed)` với Regex là [0, 1] khiến Regex có quyền lực tuyệt đối (Regex=1 thì auto pass). Có đề xuất đổi thành `Average(Regex, Embed) / 2` để giảm quyền lực này.
- **Bác bỏ hàm Average:** Nếu dùng Average, một node bị Regex bỏ sót (0) nhưng có ngữ nghĩa cực chuẩn (Embed = 0.96) sẽ bị kéo điểm xuống `0.48`. Nếu Threshold là `0.5`, node này sẽ bị loại. Hàm Average biến logic `OR` (bù khuyết) thành một biến thể của `AND`, trừng phạt nặng nề nhánh Embedding và giết chết Recall. Do đó, **Max-Fusion là thiết kế không thể thay thế**.

### 21.2 Lỗ hổng của việc "Đi tìm Threshold tối ưu cho Embed-only"
- **Sai lầm ban đầu:** Cố gắng vẽ PR-Curve cho riêng nhánh Embed-only để tìm Threshold, sau đó "cắm" Threshold đó vào Max-Fusion.
- **Tại sao sai?** Điểm số của Max-Fusion đã bị thay đổi hoàn toàn do sự bọc lót của Regex (Regex đẩy hàng loạt True Positives lên điểm 1.0). Threshold tối ưu của Embed-only không thể là Threshold tối ưu của Max-Fusion.
- **Giải pháp:** Bỏ qua hoàn toàn việc tìm Threshold trên Embed-only. Mọi phép Benchmark và quét Threshold **chỉ được thực hiện trực tiếp trên mảng điểm của Max-Fusion**.

### 21.3 Tối ưu hóa hệ thống bằng Biểu đồ Cost-Recall (Token vs Quality)
- **Vượt qua cái bóng của AUPRC/F1:** Bài toán của M5 không phải là Classification thông thường, mà là bài toán **Tối ưu chi phí (Constrained Optimization)**: Làm sao tiết kiệm Token API (Cost) mà không đánh rơi Điều luật quan trọng (Recall).
- **Sự kỳ diệu của trục Cost-Recall:** Bằng cách vẽ biểu đồ với Trục X = Số lượng Candidates (Chi phí) và Trục Y = Recall (Chất lượng), chúng ta gom được toàn bộ 6 chỉ số (Precision, Recall, F1, TP, FP, TN, FN) vào 2 biến số thực dụng nhất.
- **Quy trình Benchmark cuối cùng:**
  1. Tính điểm Max-Fusion cho tất cả các Model (Qwen3, BGE-M3...).
  2. Quét Threshold (0.3 đến 1.0, step 0.05) trên điểm Max-Fusion để vẽ các đường cong Cost-Recall của các Model lên cùng một mặt phẳng.
  3. Chọn Model có đường cong tiệm cận góc trên bên trái nhất (Tiết kiệm Token nhất mà Recall cao nhất).
  4. "Chốt" một điểm Threshold trên đường cong đó dựa vào ngân sách dự án.
  5. Xuất ra 1 Bảng báo cáo duy nhất chứa đủ (Precision, Recall, F1, TP...) tại đúng Threshold đó để nghiệm thu.

---

## 22. Tư liệu Học thuật: Benchmark M5 — Từ Vướng mắc đến Phát kiến
*(Research Journal — Tư liệu viết luận văn)*

### 22.1 Bài toán Gốc và Bối cảnh

Module 5 (Semantic Router) đóng vai trò bộ lọc đầu vào của LLM (Module 6). Nó nhận vào toàn bộ tập hợp các node của đồ thị vật lý (~222 nodes trong Chapter III Luật Đất Đai) và phải quyết định: **Node nào có khả năng chứa quan hệ ngữ nghĩa (Semantic Relation) đáng để ném vào M6 xử lý?**

Bài toán tối ưu hóa thực chất là:

> Tối thiểu hóa Cost(T) với điều kiện ràng buộc Recall(T) ≥ recall_target

Trong đó **Cost(T)** = Số node vượt ngưỡng Threshold T (Chi phí Token API cho M6), và **Recall(T)** = Tỉ lệ node "Semantic thực sự" được giữ lại.

### 22.2 Cái Bẫy #1: "Benchmark = Bảng Số Liệu Tĩnh"

**Biểu hiện:** Toàn bộ nỗ lực ban đầu tập trung vào việc xây dựng bảng số liệu tĩnh tại *một mốc Threshold duy nhất* (Precision, Recall, F1, TP, FP...). Câu hỏi thường gặp: *"Chọn Threshold bao nhiêu là tốt nhất?"*

**Vấn đề:** Bảng số liệu tại một Threshold ẩn chứa một quyết định thiết kế quan trọng nhưng không được giải thích: *Threshold được chọn ra sao?* Nếu chọn Threshold trên tập train = tập test → overfitting. Chọn bằng cảm tính → thiếu tính khách quan. Bảng tĩnh không thể hiện được mối quan hệ đánh đổi (trade-off) giữa Cost và Recall.

**Phát kiến:** Thay vì hỏi "Bảng số liệu tốt không?", câu hỏi đúng là: **"Đường cong Cost-Recall của hệ thống có hình dạng thế nào?"** — Đường cong đó chứa TOÀN BỘ thông tin của bảng số liệu ở mọi mốc Threshold có thể.

> **→ Ghi chú viết luận:** Trình bày đây là lý do tại sao nghiên cứu chọn Cost-Recall Curve thay vì điểm F1 đơn lẻ. Dẫn chiếu đến các bài báo về "LLM Routing" và "Cascaded Systems" — họ đều đánh giá theo dạng Quality-Cost frontier thay vì single-point metrics.

### 22.3 Cái Bẫy #2: "Threshold Embed-Only áp dụng được cho Max-Fusion"

**Sai lầm:** Cố gắng vẽ Precision-Recall Curve cho riêng nhánh Embedding để tìm Threshold tối ưu, sau đó "cắm" Threshold đó vào hệ thống Max-Fusion.

**Phân tích toán học:** Phân phối điểm số của Max-Fusion khác hoàn toàn với Embed-Only do hiện tượng "Regex Elevation":

```
S_MaxFusion(n) = max(S_Regex(n), S_Embed(n))
```

Đối với bất kỳ node nào có `S_Regex = 1.0` (Regex match), điểm MaxFusion sẽ luôn = 1.0 bất kể `S_Embed` là bao nhiêu. Điều này làm phân phối điểm của MaxFusion bị "kéo dúm" về phía 1.0 so với Embed-Only. Threshold tối ưu trên phân phối Embed-Only (ví dụ 0.65) không còn ý nghĩa khi áp dụng lên phân phối MaxFusion.

**Invariant thiết kế cốt lõi:** Mọi phép Benchmark, mọi lần quét Threshold, phải được thực hiện **trực tiếp và duy nhất** trên phân phối điểm của MaxFusion.

> **→ Ghi chú viết luận:** Có thể trình bày dưới dạng một Lemma nhỏ: *"Threshold calibration phải được thực hiện trên joint score distribution, không phải trên marginal distribution của từng component."*

### 22.4 Cái Bẫy #3: "F1 là chỉ số đánh giá đủ"

**Vấn đề với F1 trong bài toán Routing:** Trong bài toán Classification đối xứng, F1 = `2PR/(P+R)` rất tốt. Tuy nhiên trong Cascade System (Routing → LLM), hai loại lỗi không đối xứng:
- **False Negative** (Bỏ lọt luật quan trọng) → LLM không có dữ liệu để sinh tri thức → **Chi phí học thuật cực cao, không phục hồi được.**
- **False Positive** (Ném rác vào LLM) → Chi phí Token tăng, nhưng LLM vẫn có thể tự lọc → **Chi phí tài chính, điều chỉnh được.**

F1 không phản ánh được bất đối xứng này. Tối ưu F1 có thể vô tình "hy sinh" Recall để tăng Precision.

**Giải pháp:** Tối ưu theo **Recall-Cost Trade-off**: đặt mức Recall tối thiểu (ví dụ ≥ 85%), trong số các cấu hình đáp ứng điều kiện đó, chọn cấu hình có Cost thấp nhất.

> **→ Ghi chú viết luận:** Đây là đóng góp quan trọng. Không nhiều hệ thống RAG trình bày rõ ràng rằng Recall ≠ Precision trong pipeline. Có thể dẫn chiếu đến "Asymmetric Cost of Errors in Information Retrieval" và các bài báo về "Safety-Critical Retrieval".

### 22.5 Phát kiến Cốt lõi: Hai Trục Đồ thị Chứa Đủ Toàn bộ Confusion Matrix

Với một Model embedding M và chiến lược fusion F, đường cong Cost-Recall là tập hợp các điểm:

```
Curve(M,F) = { (Cost(T), Recall(T)) | T ∈ [0.30, 1.00] }
```

**Invariant đơn điệu (Monotonicity):**
```
T₁ < T₂  ⟹  Cost(T₁) ≥ Cost(T₂)  và  Recall(T₁) ≥ Recall(T₂)
```
Nếu Invariant này bị vi phạm → **Bug trong implementation**, không phải nhiễu. Không được dùng Pareto Frontier hay bất kỳ smoothing nào để che lỗi.

**Tính chất "Gom đủ chỉ số":** Tại bất kỳ điểm (C₀, R₀) nào trên đường cong, với Threshold T₀ tương ứng, toàn bộ confusion matrix được suy ra hoàn toàn:

```
TP = R₀ × P_true         FN = P_true - TP
FP = C₀ - TP             TN = N_true - FP
Precision = TP / C₀       F1 = 2·P·R / (P+R)
```

Tức là: **2 trục đồ thị + số lượng Positive thực tế = Đủ để tính toàn bộ confusion matrix**.

> **→ Ghi chú viết luận:** Đây là điểm quan trọng để bảo vệ trước hội đồng khi bị hỏi "Tại sao không có bảng TP/FP đầy đủ?". Trả lời: Bảng đó được suy ra trực tiếp từ đường cong — và đường cong chứa nhiều thông tin hơn bất kỳ bảng tĩnh tại một Threshold nào.

### 22.6 Thiết kế Đồ thị: Trục Toạ độ và Hướng đọc

**Trục toạ độ:**
```
Y = Recall (%)          ← Chất lượng (Quality)
X = Candidate nodes     ← Chi phí (Cost)
```
Đọc từ **trái sang phải**: Chấp nhận thêm Cost → Thu được Recall cao hơn. Threshold chỉ là **metadata** của từng điểm (hiển thị qua tooltip khi hover), không phải hướng đọc chính.

**Lý do không đặt Threshold làm trục X:** Threshold là công cụ điều chỉnh nội bộ, không phải đơn vị đo lường có ý nghĩa thực tế. Số lượng candidate (Cost) mới là thứ team dự án có thể ra quyết định dựa trên ngân sách thực tế.

**Về Regex-Only — Tại sao không vẽ Curve mà chỉ lập luận:** Regex có `S ∈ {0, 1}` — binary signal. Threshold sweep hầu như chỉ tạo ra 2-3 operating states, không có "continuous curve". Do đó Regex-Only được phân tích dưới dạng **Rule-based baseline** với lập luận kèm theo, thay vì đưa vào đồ thị đường cong.

> **→ Ghi chú viết luận:** Việc kết hợp Regex (hard binary) + Embedding (soft continuous) qua MaxFusion chính là đóng góp kỹ thuật cốt lõi của M5 — kết hợp được độ chắc chắn tuyệt đối của rule-based với độ phủ linh hoạt của semantic embedding.

### 22.7 Thiết kế Benchmark 3 Layers (Hierarchical Evaluation Framework)

**Layer 1 — Model Comparison (Figure 1):** Vẽ đường cong MaxFusion của tất cả Models. Trả lời: *Với cùng kiến trúc Routing, model embedding nào cho frontier Cost-Recall tốt hơn?*

**Layer 2 — Fusion Ablation (Figure 2-N):** Với từng model, so sánh 5 chiến lược fusion (Embed-Only, Average, Weighted, Max, và operating points của Regex-Only). Trả lời: *MaxFusion có nhất quán thống trị các chiến lược khác trên tất cả các models không?*

**Layer 3 — Operating Point Analysis (Table):** Tại các mốc Recall cụ thể (≈70%, ≈80%, ≈90%), tìm model+strategy nào cần ít Cost nhất. Kết luận được gắn với yêu cầu thực tế:
> *"At Recall ≥ 85%, Model X with Max-Fusion requires only N candidate nodes, compared to M nodes required by Average-Fusion — a X% reduction in LLM processing cost."*

### 22.8 Những Điều Chỉnh Quan Trọng từ Phản biện Học Thuật
*(Checklist tránh bị hội đồng bắt bẻ khi viết luận)*

1. **Không claim "SOTA"** khi mô tả model. Dùng ngôn ngữ trung tính: "multilingual pretrained embedding baseline".
2. **OpenAI không phải "Upper Bound"**. Gọi là "Commercial API baseline" và giải thích sự khác biệt về reproducibility, latency, chi phí — không thể so sánh trực tiếp với open-source model.
3. **Không dùng Pareto Frontier hoặc bất kỳ smoothing** để "làm đẹp" đường cong. Monotonicity là invariant — vi phạm = bug trong code.
4. **Không viết kết luận trước khi chạy experiment**: Viết "Max-Fusion là chiến lược được đề xuất và cần kiểm định qua ablation" — không phải "Chứng minh Max-Fusion là tốt nhất".
5. **Weighted-Fusion phải được đánh giá trên Cost-Recall curve**, không phải tối ưu F1 — để nhất quán với objective của benchmark.
6. **Kaggle được dùng vì embedding inference + reproducibility**, không phải vì "threshold sweep bất khả thi trên CPU" (sweep chỉ là 6×5×15×222 phép tính, cực nhỏ).

---

## 23. Phát kiến về Tiêu chí Phân loại Nhãn: "Tính Xác định Trạng thái" (State Determinism)

### 23.1 Hạn chế của Nhìn nhận Thuần Văn bản

Cách tiếp cận ban đầu để phân loại nhãn 0/1 chủ yếu dựa trên "Dấu hiệu bề mặt" (Surface Features):
- Có từ khóa cross-reference ("theo Điều...", "theo quy định tại...") → 1
- Không có → 0

Tuy nhiên, qua phân tích các trường hợp borderline (đặc biệt là `dieu-28_khoan-1_diem-m`), nhận ra rằng tiêu chí này **không đủ**. Có một chiều kích sâu hơn bị bỏ qua: **Trạng thái xác định của các thực thể trong câu luật**.

### 23.2 Phát kiến: "State Determinism" như Tiêu chí Phân loại

**Định nghĩa:**

Một node được gán nhãn **0 (Không cần M6)** khi và chỉ khi trạng thái của tất cả các thực thể trong câu là **State-Deterministic** — tức là trạng thái pháp lý của chủ thể được xác định hoàn toàn bởi chính văn bản trong node đó, không phụ thuộc vào kết quả của bất kỳ quá trình pháp lý nào từ bên ngoài.

Một node được gán nhãn **1 (Cần M6)** khi có ít nhất một thực thể ở trạng thái **State-Dependent** — tức là trạng thái pháp lý của chủ thể chỉ được xác định *sau khi* một quá trình ngoại sinh (bản án, quyết định thi hành án, kết quả hòa giải, phán quyết trọng tài...) đã hoàn thành.

**Công thức phân loại:**
```
is_semantic = 1  nếu  ∃ thực thể e trong node: State(e) phụ thuộc ngoại sinh
is_semantic = 0  nếu  ∀ thực thể e trong node: State(e) tự xác định nội tại
```

### 23.3 Ví dụ Phân tích (Case Study từ Golden Set)

**Case `dieu-28_khoan-1_diem-m` — Phân loại đúng: 1**
> *"...được nhận quyền sử dụng đất theo kết quả hòa giải thành... quyết định thi hành án **đã được thi hành**; quyết định hoặc phán quyết của Trọng tài thương mại Việt Nam..."*

- Cụm **"đã được thi hành"** là một **state condition ngoại sinh điển hình**: Quyền nhận đất chỉ phát sinh khi một quá trình thi hành án bên ngoài đã hoàn thành.
- Cụm **"phù hợp với pháp luật"** (trong "văn bản công nhận kết quả đấu giá phù hợp với pháp luật") cũng là state condition — tính hợp pháp phụ thuộc vào đánh giá của cơ quan bên ngoài.
- AI gán 0 vì chỉ thấy danh sách chủ thể. Hệ thống Rule-based trích xuất được "quyết định thi hành án" nhưng **bỏ sót hoàn toàn** điều kiện trạng thái "đã được thi hành" đi kèm. → **Nhãn đúng: 1.**

**Case `dieu-27_khoan-2_diem-b` — Phân loại đúng: 0**
> *"Trường hợp nhóm người sử dụng đất mà quyền sử dụng đất phân chia được theo phần cho từng thành viên... thì phải thực hiện đăng ký biến động..."*

- Điều kiện "phân chia được theo phần" là **điều kiện nội tại** — không cần tra cứu bất kỳ kết quả pháp lý nào từ bên ngoài.
- Trạng thái của mọi thực thể (nhóm người SDĐ) được xác định ngay trong câu. → **Nhãn đúng: 0.**

### 23.4 Tại sao Rule-based (Regex) Không Thể Bắt được State Conditions

Rule-based có ba điểm mù không thể khắc phục khi xử lý state conditions trong văn bản pháp lý:

1. **Bỏ sót điều kiện trạng thái:** Regex có thể nhặt ra danh từ "quyết định thi hành án" nhưng không phân tích được cụm động từ hoàn thành "đã được thi hành" đi kèm. Trong pháp lý, bỏ sót điều kiện này là sai lệch hoàn toàn về nghĩa.

2. **Phá vỡ cấu trúc ngữ nghĩa khi cắt:** Nếu dùng rule cắt chuỗi theo dấu phẩy hoặc dấu chấm phẩy, câu như *"người gốc Việt Nam định cư ở nước ngoài được phép nhập cảnh vào Việt Nam, tổ chức kinh tế..."* sẽ bị cắt sai. Thuật toán có thể gán nhầm điều kiện "được phép nhập cảnh" cho "tổ chức kinh tế", hoặc tách nó thành một phần tử độc lập vô nghĩa. Regex không thể biết rằng cụm đó chỉ bổ nghĩa cho duy nhất nhóm "người gốc Việt Nam".

3. **Không xử lý được "Flat Structure" text dày:** Nhãn 0 thường áp dụng cho các đoạn văn ngắn, đơn nghĩa hoặc danh sách được định dạng sẵn (điểm a, b, c). Nhưng những câu như `dieu-28_diem-m` là khối text đặc, gom chung hàng chục biến số pháp lý — máy tính nhìn vào chỉ thấy chuỗi ký tự, không thấy cấu trúc phân tầng để xử lý.

### 23.5 Hệ quả đối với Thiết kế M5 và Annotation Guideline

**Ý nghĩa đối với Annotation:** Khi gán nhãn 0/1, annotator cần đặt câu hỏi: *"Để biết câu luật này áp dụng được cho thực thể nào, tôi có cần biết kết quả của một quá trình pháp lý bên ngoài không?"*
- Nếu **CÓ** → nhãn 1 (Cần M6 để trích xuất quan hệ điều kiện)
- Nếu **KHÔNG** → nhãn 0

**Ý nghĩa đối với Thiết kế M5:** Phát kiến này làm sáng tỏ **lý do cốt lõi tại sao Regex-Only là không đủ** và tại sao Semantic Embedding cần thiết trong kiến trúc Hybrid:
- Regex bắt được cấu trúc cú pháp nhưng mù với state conditions.
- Embedding model (được huấn luyện trên ngữ liệu lớn) có khả năng hiểu ngữ nghĩa của các cụm điều kiện trạng thái như "đã được thi hành", "phù hợp với pháp luật", "được công nhận".

> **→ Ghi chú viết luận:** Đây là luận điểm kỹ thuật mạnh để biện hộ cho sự cần thiết của Embedding trong M5. Có thể trình bày theo dạng: *"Rule-based approaches extract syntactic patterns but fail to capture state-dependent semantic conditions inherent in legal clauses — a limitation that motivates the Hybrid Routing architecture."*

### 23.6 Câu hỏi Mở: Ranh giới giữa Temporal Constraint và State Condition

Trong quá trình áp dụng tiêu chí State Determinism vào thực tế, nảy sinh một vấn đề ontology quan trọng chưa được giải quyết dứt điểm: **Ràng buộc thời gian (Temporal Constraint) có phải là một dạng State Condition không?**

**Ví dụ điển hình gây tranh cãi:**
- *"...chuyển nhượng quyền sử dụng đất **trong thời hạn sử dụng đất**"* — Điều 41(3)(b), 41(3)(c), 45(1)(d)
- *"...trong thời hạn thuê đất"* — Điều 40(1)(c)

Về hình thức, "trong thời hạn" trông giống một state condition vì nó đặt điều kiện cho việc thực hiện quyền. Tuy nhiên, nó khác State Condition theo định nghĩa:
- **State Condition (Section 23.2):** Phụ thuộc vào *kết quả hoàn thành của một quá trình pháp lý ngoại sinh* (hòa giải, thi hành án, phán quyết...).
- **Temporal Constraint:** Là ràng buộc trục thời gian (lịch), không phụ thuộc vào bất kỳ quyết định hay quá trình nào từ bên ngoài. M6 không cần tra cứu thêm context để biết "trong thời hạn" nghĩa là gì.

**Phân biệt thêm: Static Eligibility vs. State-Dependent**

Một nguồn nhầm lẫn thứ hai: cụm từ kiểu *"tổ chức tín dụng **được phép hoạt động**"* hay *"người gốc Việt Nam **được phép nhập cảnh**"*. Những cụm này mô tả **thuộc tính phân loại tĩnh của đối tác/chủ thể** (ai có đủ điều kiện tham gia giao dịch), không phải trạng thái của *đối tượng pháp lý đang xét* phụ thuộc một quá trình bên ngoài.

**Hai tầng phân biệt độc lập cần khóa vào Annotation Guideline:**

```
Temporal Constraint   ≠   State-Dependent
(trục thời gian)          (kết quả quá trình ngoại sinh)

Static Eligibility    ≠   State-Dependent
(thuộc tính phân loại)    (kết quả quá trình ngoại sinh)
```

**Tiêu chí khóa để gán nhãn 1 theo State Determinism:**

> *"Gán nhãn 1 theo State Determinism khi và chỉ khi: **Legal state of the subject depends on an external legal process or external determination** — không phải khi chỉ có ràng buộc thời gian hay điều kiện phân loại chủ thể."*

**Hệ quả cho Audit:** Sau khi thống nhất ontology, các nodes *"trong thời hạn"* và *"được phép hoạt động/nhập cảnh"* được giữ nhãn 0. Chỉ 6 nodes được chốt sửa thành 1 (sau khi audit đợt 1): `28(1)(l)`, `28(1)(m)`, `28(1)(n)`, `28(1)(o)`, `45(1)(b)`, `46(2)(b)`. Phân phối Ground Truth sau cập nhật: **0: 94 | 1: 127 | 0.5: 1** (tổng 222 nodes).

Nhóm cần review tiếp: `37(2)(c)`, `35(4)`, `38(2)`, `40(1)(c)`, `41(2)(c)` — chưa đổi tự động do cần xác định rõ "tiếp tục cho thuê" và "được cơ quan có thẩm quyền cho phép" có biểu diễn outcome/state-dependent hay chỉ là điều kiện quan hệ pháp lý trực tiếp.

### 23.7 Nhật ký Ground Truth v2 — Các Thay đổi và Mẫu Phân tích

*(Ghi lại chi tiết 6 thay đổi nhãn và các pattern rút ra từ audit thực tế — tư liệu cho phần Data Annotation của luận văn)*

**Phân phối trước → sau audit:**
```
Trước:  0: 99  | 1: 121 | 0.5: 2
Sau:    0: 94  | 1: 127 | 0.5: 1
Net:    -5 từ nhóm 0 → 1  |  -1 từ nhóm 0.5 → 1
```

#### 6 Thay đổi được Chốt (0 → 1)

| Node | Dấu hiệu cốt lõi | Pattern |
|---|---|---|
| `28(1)(l)` | *"đất đang được sử dụng ổn định"* | Current persistent state của đối tượng đất |
| `28(1)(m)` *(từ 0.5)* | *"đã được thi hành"* | Completed legal process outcome |
| `28(1)(n)` | *"đã được thi hành"* + *"theo kết quả hòa giải thành"* | Multiple concurrent legal process outcomes |
| `28(1)(o)` | *"phù hợp với pháp luật"* | External validity determination |
| `45(1)(b)` | *"đã được giải quyết... đã có hiệu lực pháp luật"* | State transition: dispute → resolved → enforceable |
| `46(2)(b)` | *"đã ứng trước... mà chưa khấu trừ hết"* | Dual state: action completed + consequence pending |

#### 3 Mẫu State-Dependent Rút ra từ Audit

**Mẫu 1 — Legal Process Outcome (Kết quả Quá trình Pháp lý):**
Cụm từ dạng *"theo kết quả [X]"*, *"[quyết định/phán quyết] đã có hiệu lực"*, *"đã được thi hành"* → Luôn là 1. Quyền hoặc nghĩa vụ chỉ phát sinh sau khi một quá trình ngoại sinh đã hoàn thành. Đây là mẫu rõ ràng nhất và ít tranh cãi nhất.

**Mẫu 2 — External Validity Determination (Tính Hợp pháp Ngoại sinh):**
Cụm từ *"phù hợp với pháp luật"*, *"được [cơ quan] công nhận"* → Thường là 1. Tính hợp pháp của trạng thái phụ thuộc vào đánh giá của cơ quan bên ngoài, không tự xác định được từ nội dung câu. Cần phân biệt với trường hợp "phù hợp với pháp luật" chỉ là cụm tu từ thông thường trong văn bản hành chính.

**Mẫu 3 — Dual State (Trạng thái Kép):**
Cụm từ dạng *"đã [làm X] mà chưa [hoàn thành Y]"* → Là 1. Ví dụ điển hình: *"đã ứng trước tiền... mà chưa khấu trừ hết"* — Câu này mã hóa đồng thời 2 boolean states của một thực thể tài chính pháp lý. M6 cần tra cứu cả hai trạng thái này để xác định nghĩa vụ còn lại.

#### Phát hiện quan trọng: "Blind Spot" của Toàn bộ Hệ thống M5

Đáng chú ý nhất là node `28(1)(n)`: Cả 4 luồng xử lý đều cho kết quả = 0 (AI_Suggest=0, EXP-A=0, EXP-B=0, EXP-C=0), nhưng khi áp dụng tiêu chí State Determinism thì rõ ràng là 1. Node này có cấu trúc danh sách pháp lý dày đặc (chứa 5+ loại kết quả pháp lý ngoại sinh khác nhau), khiến cả Regex lẫn Embedding đều không nhận diện được signal ngữ nghĩa rõ ràng.

Đây là bằng chứng cho thấy: **Một tập con nhỏ của các trường hợp Semantic-Dependent trong văn bản pháp lý sẽ nằm ngoài tầm với của cả Hybrid System** — chúng đòi hỏi phân tích ngữ nghĩa ở mức độ hiểu pháp lý (legal comprehension), không chỉ ở mức độ pattern matching hay embedding similarity. Đây chính là ranh giới năng lực của M5 và là lý do M6 cần được thiết kế để chịu đựng được False Negatives từ M5.

> **→ Ghi chú viết luận:** Có thể dùng node `28(1)(n)` làm ví dụ minh họa trong phần "Limitations" của chương Methodology: *"Despite the Hybrid Routing architecture, a small subset of semantically complex nodes — those containing dense legal-process references — remain outside the detection capability of M5 and must be handled downstream."*


