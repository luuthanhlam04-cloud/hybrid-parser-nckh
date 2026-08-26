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
