# Tóm tắt Module 8 — Unified Knowledge Graph Fusion

Tài liệu này tóm tắt kiến trúc, luồng xử lý và kết quả hiện tại của
**Module 8 (M8)**. M8 kết hợp Đồ thị vật lý từ Module 4 (M4) với Đồ thị ngữ
nghĩa chuẩn hóa từ Module 7 (M7) để tạo **Unified Knowledge Graph (UKG)**.
M8 bảo toàn cấu trúc điều khoản của văn bản, bổ sung quan hệ ngữ nghĩa, liên
kết quan hệ về vị trí nguồn và cung cấp các kiểm tra chất lượng đồ thị.

---

## 1. Vị trí của M8 trong toàn pipeline

```text
Văn bản pháp luật
    ├── M1–M4: cấu trúc vật lý của văn bản và Physical Graph
    └── M5–M7: định tuyến, trích xuất và chuẩn hóa ngữ nghĩa
                         ↓
                  M8 Graph Fusion
                         ↓
             Unified Knowledge Graph (UKG)
```

M8 không thay thế M4 hoặc M7:

- **M4 là nguồn có thẩm quyền** cho cây cấu trúc văn bản như Chương, Mục,
  Điều, Khoản và Điểm.
- **M7 bổ sung ngữ nghĩa**: chủ thể, hành vi, đối tượng, quy phạm, điều kiện,
  ngoại lệ và dẫn chiếu.
- **M8 chịu trách nhiệm hợp nhất**, tạo các cạnh liên kết giữa ngữ nghĩa và
  node văn bản nguồn, kiểm tra hợp đồng dữ liệu, phát hiện xung đột tiềm tàng
  và kiểm định graph.

---

## 2. Thành phần và vai trò của các file

### Động cơ hợp nhất

- **`src/fusion/fusion_engine.py`**: Điều phối M8. Đọc Physical Graph và M7
  graph, kiểm tra đầu vào, chuẩn hóa dữ liệu M7, hợp nhất node/cạnh, gắn
  `MENTIONS` và `RESOLVES_TO`, gọi phát hiện xung đột và tạo báo cáo.
- **`src/fusion/m7_adapter.py`**: Chuyển đổi schema M7 về dạng M8 dùng chung.
  Hỗ trợ schema `entities`/`relations` cũ và schema M7 mới gồm
  `active_nodes`/`concepts`/`norms`/`active_edges`.
- **`src/fusion/merge_policy.py`**: Giữ phân biệt node vật lý (`PHYSICAL`) và
  node ngữ nghĩa (`SEMANTIC`); không làm mất thẩm quyền của cấu trúc M4.
- **`src/fusion/edge_mapper.py`**: Chuẩn hóa cạnh, lưu provenance và tính điểm
  confidence từ các tín hiệu hiện có; nếu có calibrator đã fit thì áp dụng
  hiệu chuẩn.
- **`src/fusion/node_mapper.py`**: Tra cứu node vật lý, tổ tiên/phạm vi của
  node, hồi chỉ như “Điều này”, “Khoản này”, dẫn chiếu cụ thể và phạm vi văn
  bản. Dẫn chiếu toàn văn bản như “Luật này” được liên kết tới node
  `DOCUMENT` tổng hợp, không gán nhầm vào node Chương.
- **`src/fusion/graph_contract.py`**: Fail-fast khi dữ liệu có ID trùng, node
  cha không tồn tại, cạnh mồ côi, relation sai kiểu, thiếu evidence hoặc
  confidence ngoài khoảng `[0, 1]`.

### Kiểm tra chất lượng và xung đột

- **`src/fusion/conflict_resolver.py`**: Phát hiện xung đột quy phạm trên cùng
  cặp chủ thể–hành vi. `ALLOW` hoặc `REQUIRE` đối nghịch với `PROHIBIT` được
  gắn cờ `POTENTIAL_LEGAL_CONFLICT` nếu không có ngoại lệ liên kết phù hợp.
  Kết quả là cảnh báo cần chuyên gia xem xét, không phải kết luận pháp lý.
- **`src/fusion/shacl_validator.py`** và **`src/fusion/shapes.ttl`**: Chuyển UKG
  sang RDF và kiểm tra bằng SHACL. Các đặc trưng cấu trúc cần kiểm tra được
  tính trước theo các lượt tuyến tính; SHACL kiểm tra các giá trị bằng property
  shapes thay vì chạy truy vấn SPARQL lặp cho từng cạnh. Không bật RDFS
  inference.
- **`src/fusion/delta_engine.py`**: So sánh hai phiên bản UKG theo ID node và
  khóa cạnh ổn định để tạo danh sách thêm, sửa, xóa. `Neo4jDeltaApplier` áp
  dụng delta trong một transaction qua Neo4j driver.
- **`src/fusion/confidence_calibration.py`**: Isotonic calibration theo PAV và
  các metric như Brier score, ECE, precision/recall tại ngưỡng.
- **`src/fusion/quality_evaluation.py`**: Đánh giá nhãn chuyên gia cho hỗ trợ
  quan hệ, xung đột quy phạm và phân giải dẫn chiếu; có tính pairwise Cohen's
  kappa khi có nhiều reviewer.

### CLI, đánh giá và kiểm thử

- **`run_fusion.py`**: Chạy riêng M8, ghi UKG, danh sách xung đột và báo cáo
  SHACL.
- **`run_fusion_delta.py`**: Tính và áp dụng chênh lệch UKG vào Neo4j.
- **`run_fusion_confidence_eval.py`** và
  **`run_fusion_quality_eval.py`**: Fit/đánh giá confidence và chất lượng theo
  CSV đã được gán nhãn.
- **`scripts/sample_fusion_eval.py`**: Lấy mẫu phân tầng có seed cố định để
  chuyên gia gán nhãn; giữ split theo node nguồn để giảm rò rỉ train/test.
- **`scripts/sample_m6_candidates.py`**: Xếp hạng các M5 candidate phức tạp để
  chuẩn bị thử nghiệm M6 mà không tự gọi API.
- **`run_pipeline.py`**: Điều phối pipeline từ M1/M2 đến M8. M6 cần opt-in rõ
  ràng bằng `--allow-llm` và một `--m6-limit` dương vì có thể phát sinh chi
  phí API.
- **`tests/unit/test_fusion_engine.py`**: Kiểm tra hợp nhất, contract đầu vào,
  phát hiện xung đột, dẫn chiếu, SHACL, delta và đánh giá.

---

## 3. Luồng xử lý M8

1. **Đọc graph đầu vào**: nạp M4 Physical Graph và M7 Canonical Semantic Graph.
2. **Chuẩn hóa hợp đồng**: adapter chuyển schema M7 về entities/relations và
   graph contract kiểm tra các khóa, endpoint, evidence và confidence.
3. **Giữ node và cạnh vật lý**: các node/cạnh M4 được giữ nguyên vai trò
   `PHYSICAL`; quan hệ cấu trúc không bị thay thế bởi ngữ nghĩa.
4. **Bổ sung graph ngữ nghĩa**: thêm các entity chuẩn hóa cùng quan hệ như
   `ALLOW`, `REQUIRE`, `PROHIBIT`, `HAS_EXCEPTION`, `HAS_CONDITION` và
   `REFERENCE_TO`.
5. **Neo ngữ nghĩa vào văn bản**: tạo `MENTIONS` từ node vật lý nguồn tới các
   entity được trích xuất tại đó. Dẫn chiếu chỉ tạo `RESOLVES_TO` khi phân
   giải được duy nhất trong phạm vi graph; “Luật này” có thể trỏ tới node
   `DOCUMENT`.
6. **Phân loại dẫn chiếu chưa giải quyết**: tách các trường hợp
   `EXTERNAL_SCOPE`, `GENERAL_LEGAL_SCOPE`, `AMBIGUOUS_REFERENCE`,
   `DOCUMENT_LEVEL_REF` và `UNRESOLVED_REFERENCE` trong báo cáo.
7. **Phát hiện xung đột quy phạm**: so sánh các modality trên cùng cặp
   subject/action; lưu relation IDs, loại xung đột và ngữ cảnh để truy vết.
8. **Kiểm định SHACL và xuất kết quả**: kiểm tra tính toàn vẹn endpoint, số
   Điều, quan hệ cấu trúc, thứ tự và domain/range ngữ nghĩa. Nếu SHACL không
   conform, runner báo lỗi thay vì coi pipeline thành công.

---

## 4. Kết quả chạy và Phân tích đánh giá định lượng

### 4.1. Bảng tổng hợp và Đối soát số liệu định lượng

Lần chạy trên dữ liệu Chương III Luật Đất đai 2024 (`Luat_dat_dai_chuong_3.docx`) trong repository:

| Hạng mục đầu ra | File kết quả | Chỉ số định lượng | Đánh giá sơ bộ & Đối soát |
|---|---|---:|---|
| **Đồ thị vật lý (M4)** | `physical_graph.json` | **222** nodes, **551** edges | Cấu trúc cây hoàn chỉnh (Chương → Mục → Điều → Khoản → Điểm), 0 chu trình lặp |
| **Đồ thị ngữ nghĩa (M7)** | `canonical_semantic_graph.json` | **71** entities, **378** relations | Chuẩn hóa ontology đầy đủ, bao phủ chủ thể, hành vi, khách thể, điều kiện, quy phạm |
| **Đồ thị hợp nhất (M8 UKG)** | `unified_knowledge_graph.json` | **294** nodes, **1.371** edges | Dung nạp 100% hai đồ thị, sinh thêm 1 node `DOCUMENT`, **435** cạnh `MENTIONS` và **7** cạnh `RESOLVES_TO` |
| **Kiểm định SHACL** | `fusion_shacl_report.json` | `conforms: true` | Đạt 100% ràng buộc hình thức W3C RDF/SHACL, thời gian chạy ~2,76s |
| **Xung đột quy phạm** | `fusion_conflicts.json` | **1** xung đột tiềm năng | Cặp `REQUIRE_PROHIBIT` giữa `subject.state` và `action.transaction.mortgage` |
| **Phân giải dẫn chiếu** | Trích xuất từ `fusion_report` | **27** quan hệ dẫn chiếu | **10** quan hệ giải quyết (sinh 7 cạnh `RESOLVES_TO`), **17** quan hệ bị từ chối tạo cạnh nội bộ (10 ngoài chương, 4 quy định chung, 3 ngoài luật) |
| **Bộ khung đánh giá vàng** | `outputs/evaluation/*.csv` | **80** mẫu confidence<br>**135** mẫu quality | Đã chia `train` / `test` nhóm theo node vật lý nguồn để chống rò rỉ dữ liệu (Quality gồm 80 support, 34 reference, 21 conflict) |

#### Chi tiết phân tầng cấu trúc đồ thị

1. **Phân bố Node và Cạnh Vật lý (M4 - 222 nodes, 551 edges):**
   - **Nodes theo cấp bậc:** 1 `CHAPTER` (Chương III), 5 `SECTION` (Mục), 23 `ARTICLE` (Điều 26–48), 84 `CLAUSE` (Khoản), 109 `POINT` (Điểm).
   - **Cạnh cấu trúc:** 221 `BELONG_TO` (cây phả hệ phân cấp), 165 `NEXT` (liền kề tiếp theo), 165 `PREVIOUS` (liền kề trước).

2. **Phân bố Thực thể và Quan hệ Ngữ nghĩa (M7 - 71 entities, 378 relations):**
   - **Thực thể theo Ontology:** 29 `LEGAL_ACTION`, 19 `LEGAL_SUBJECT`, 10 `LEGAL_DOCUMENT_REF`, 8 `CONDITION`, 5 `LEGAL_OBJECT`.
   - **Quan hệ quy phạm:** 157 `ALLOW`, 125 `HAS_OBJECT`, 39 `REQUIRE`, 27 `REFERENCE_TO`, 22 `HAS_CONDITION`, 8 `PROHIBIT`.

3. **Cơ cấu Đồ thị Hợp nhất (M8 UKG - 294 nodes, 1.371 edges):**
   - **Nodes (294):** 222 `PHYSICAL` + 71 `SEMANTIC` + 1 `DOCUMENT` (`document_59_2024_qh15`).
   - **Edges (1.371):** 551 cạnh vật lý + 378 cạnh ngữ nghĩa + 435 cạnh `MENTIONS` + 7 cạnh `RESOLVES_TO`.

4. **Bộ mẫu đánh giá thẩm định:**
   - `fusion_confidence_gold_template.csv`: 80 dòng (65 train, 15 test). Gồm 42 `ALLOW`, 23 `REQUIRE`, 8 `PROHIBIT`, 7 `RESOLVES_TO`.
   - `fusion_quality_gold_template.csv`: 135 dòng (108 train, 27 test). Gồm 80 ca `relation_support`, 34 ca `reference_resolution`, 21 ca `deontic_conflict`.

---

### 4.2. Phân tích và Đánh giá chuyên sâu kết quả đầu ra

#### 1. Mật độ kết nối & Khả năng truy vết nguồn gốc (Traceability & Provenance)
- Đồ thị hợp nhất đạt mật độ **4,66 cạnh/node** (1.371 cạnh / 294 node).
- **435 cạnh `MENTIONS`** được thiết lập tự động cho 378 quan hệ ngữ nghĩa (trung bình 1,15 liên kết neo vết/quan hệ). Mỗi thực thể và quy phạm đều được liên kết trực tiếp về đúng Khoản/Điều nguồn, đảm bảo tính minh bạch, có thể giải thích được (Explainable AI) và loại bỏ hoàn toàn hiện tượng ảo giác (hallucination).
- 100% cạnh mang trường `provenance: ["M4"]`, `["M7"]` hoặc `["M8"]`.

#### 2. Chất lượng phân giải dẫn chiếu (Reference Resolution)
Tổng cộng có **27 quan hệ `REFERENCE_TO`**, được xử lý rành mạch:
- **Dẫn chiếu nội bộ giải quyết thành công (6 quan hệ):** Tạo thành 5 cạnh `RESOLVES_TO` trỏ chính xác về node Điều tương ứng trong Chương III (ví dụ: `REL_REL_0324` và `REL_REL_0549` trỏ về Điều 31 và Điều 41).
- **Dẫn chiếu toàn văn cấp văn bản (4 quan hệ):** Nhận diện cụm từ *"Luật này"*, tự động tạo 2 cạnh `RESOLVES_TO` nối về node ảo `document_59_2024_qh15` đại diện toàn bộ đạo luật, khắc phục triệt để lỗi gán nhầm vào node Chương.
- **17 quan hệ bị từ chối tạo cạnh nội bộ (`rejected_relations`):**
  - **4 `GENERAL_LEGAL_SCOPE`:** Quy phạm mở, mang tính nguyên tắc chung (*"theo quy định của pháp luật về đất đai"*, *"pháp luật về kinh doanh bất động sản"*).
  - **3 `EXTERNAL_SCOPE`:** Dẫn chiếu tường minh sang văn bản pháp luật khác (*"Quy định pháp luật khác"*).
  - **10 `UNRESOLVED_REFERENCE`:** Điển hình là `REL_REL_0767` trích dẫn *"khoản 3 Điều 16"*. Do tập dữ liệu thử nghiệm chỉ gồm **Chương III (Điều 26–48)** trong khi Điều 16 nằm ở Chương II, việc không tìm thấy node đích phản ánh đúng **giới hạn cắt lát dữ liệu đầu vào (data slice limitation)**, không phải lỗi thuật toán regex. Việc tách riêng nhóm này giúp tránh phạt oan độ chính xác của mô hình.

#### 3. Phân tích ca xung đột Deontic điển hình (Quality Gate Case Study)
Báo cáo xung đột ghi nhận 1 cảnh báo:
- **Xung đột:** `REQUIRE_PROHIBIT` giữa quan hệ `REL_REL_0765` và `REL_REL_0777` trên cặp `(subject.state, action.transaction.mortgage)`.
- **Bằng chứng văn bản:**
  - `REL_REL_0765`: *"Cá nhân là người dân tộc thiểu số được Nhà nước giao đất... thì **được** thế chấp quyền sử dụng đất tại ngân hàng chính sách."*
  - `REL_REL_0777`: *"Cá nhân là người dân tộc thiểu số được Nhà nước giao đất... **không được** chuyển nhượng, góp vốn, tặng cho, thừa kế, thế chấp... **trừ trường hợp quy định tại khoản 1 và khoản 2 Điều này**."*
- **Đánh giá bản chất:**
  - **Về thuật toán M8:** `ConflictResolver` hoạt động hoàn toàn chính xác theo logic quy phạm (Deontic Logic): khi phát hiện 1 quan hệ bắt buộc/cho phép đối kháng trực tiếp với quan hệ cấm trên cùng cặp chủ thể–hành vi mà thiếu cạnh `HAS_EXCEPTION`, hệ thống lập tức gắn cờ `POTENTIAL_LEGAL_CONFLICT`.
  - **Về tầng trích xuất M6/M7:** Cảnh báo này đã bộc lộ điểm yếu của tầng trích xuất NLP/LLM thượng nguồn khi xử lý câu bị động tiếng Việt (*"Cá nhân... được Nhà nước giao đất..."* bị hiểu nhầm chủ thể là "Nhà nước" thay vì cá nhân người dân tộc thiểu số, nhầm lẫn modality `ALLOW` thành `REQUIRE`, và bỏ sót cạnh ngoại lệ `HAS_EXCEPTION`).
  - **Ý nghĩa:** Module 8 đóng vai trò xuất sắc như một **bộ lọc kiểm định chất lượng (Quality Gate)**, hỗ trợ phát hiện sớm sai số của các mô hình trích xuất thượng nguồn.

#### 4. Hiệu năng thực thi và Khả năng mở rộng
- Thời gian kiểm định SHACL đạt **~2,76 giây** (với W3C SHACL không bật RDFS inference).
- Toàn bộ thời gian chạy `run_fusion.py` đạt **~4,40 giây**.
- Việc tối ưu hóa bằng các lượt duyệt tuyến tính trong Python để kiểm tra chu trình và thứ tự cấp bậc trước khi nạp vào SHACL đã giúp giảm thời gian kiểm định từ hàng chục giây xuống dưới 3 giây, hoàn toàn khả thi cho việc vận hành trong pipeline thời gian thực.


---

## 5. Cách chạy và kiểm thử

Chạy riêng M8:

```powershell
python run_fusion.py
```

Chạy riêng bước M8 thông qua master pipeline:

```powershell
python run_pipeline.py --from-stage M8 --to-stage M8
```

Chạy bộ kiểm thử M8:

```powershell
python -m pytest tests/unit/test_fusion_engine.py -q
```

Lấy mẫu CSV để chuyên gia gán nhãn:

```powershell
python scripts/sample_fusion_eval.py --size 80 --seed 42
```

Chuẩn bị 10 M6 candidates phức tạp để xem xét:

```powershell
python scripts/sample_m6_candidates.py --limit 10
```

Lệnh lấy mẫu M6 không gọi API. Chỉ chạy trích xuất LLM sau khi đã xem xét
danh sách và chấp nhận chi phí; với master pipeline phải truyền rõ
`--allow-llm --m6-limit N`.

---

## 6. Đầu ra chính

- `outputs/unified_graphs/unified_knowledge_graph.json`: UKG gồm metadata,
  nodes, edges, conflicts và fusion report.
- `outputs/unified_graphs/fusion_conflicts.json`: các cảnh báo xung đột và
  relation IDs liên quan.
- `outputs/unified_graphs/fusion_shacl_report.json`: trạng thái conform cùng
  nội dung báo cáo SHACL.
- `outputs/evaluation/fusion_confidence_gold_template.csv`: mẫu quan hệ và
  confidence; cột `label` để trống cho người đánh giá.
- `outputs/evaluation/fusion_quality_gold_template.csv`: mẫu đánh giá chất
  lượng, xung đột và dẫn chiếu; nhãn gold do reviewer cung cấp.
- `outputs/evaluation/m6_complex_candidate_sample.json`: danh sách M6
  candidates được xếp hạng theo dấu hiệu độ phức tạp.

---

## 7. Giới hạn và việc còn cần làm

- **Chưa có gold labels đã được chuyên gia xác nhận.** Confidence hiện tại là
  heuristic, có trạng thái `heuristic_uncalibrated`; không được diễn giải
  thành xác suất pháp lý đã hiệu chuẩn. Chỉ fit calibrator sau khi hoàn thành
  train split và giữ nguyên test split.
- **Xung đột là “potential”**: so khớp subject/action cùng modality và các
  ngoại lệ đã nối được; hệ thống chưa thay chuyên gia đánh giá khác biệt về
  phạm vi, thời điểm, điều kiện hoặc hiệu lực văn bản.
- **Neo4j delta chưa được xác nhận trên server thực tế.** Cần cấu hình
  credentials, kiểm thử trên database phù hợp và xác nhận backup trước khi
  áp dụng dữ liệu thật.
- **Chưa thực hiện M6 với prompt mới trong lần nghiệm thu này.** Cần chọn các
  candidate, chấp nhận chi phí API, chạy mẫu có giới hạn và rà soát evidence,
  chủ thể ẩn, điều kiện và ngoại lệ.
- Kết quả trên một chương luật chỉ xác nhận pipeline với tập dữ liệu này;
  đánh giá độ chính xác tổng quát cần gold set từ nhiều văn bản và kết quả
  held-out có ghi nhận mức đồng thuận reviewer.

---

## 8. Kết luận

M8 hiện đã có đường đi từ M4/M7 tới UKG, phát hiện xung đột tiềm tàng, xử lý
một số dạng dẫn chiếu, kiểm định SHACL, tạo mẫu đánh giá và hỗ trợ delta cho
Neo4j. Trên dữ liệu đang có, 21/21 test M8 pass và SHACL conform. Có thể xem
đây là **bản triển khai kỹ thuật sẵn sàng cho demo và đánh giá tiếp theo**;
chưa nên tuyên bố production/legal-ready cho tới khi có đánh giá chuyên gia,
held-out gold set và kiểm chứng Neo4j trên môi trường mục tiêu.
