# MODULE 2 — Regex Parser (Phân rã Cấu trúc Vật lý)

## 0. Module Snapshot

**Mục tiêu**
Chuyển Clean Legal Text thành các Legal Node theo cấu trúc vật lý của văn bản pháp luật: Chương → Mục → Điều → Khoản → Điểm.

**Input**
Clean Legal Text (DOCX paragraphs hoặc plain text kèm metadata) từ Module 1.

**Output**
Legal Nodes JSON.

**Corpus hiện tại**
Chương III Luật Đất Đai 2024 (`Luat_dat_dai_chuong_3.docx`).

**Trạng thái**
- Pattern Registry & Regex Engine: Prototype verified
- Boundary Detector: đang verify
- Hierarchy Builder: verified trên Ch3-LDD
- Node Generator: verified prototype, interface pending
- M1→M2 contract: pending
- TXT fallback: open, chưa thuộc critical path hiện tại

---

## 1. Scope & Objective

**In Scope**
- Nhận diện cấu trúc vật lý của văn bản (Chương, Mục, Điều, Khoản, Điểm).
- Xác định điểm bắt đầu và kết thúc (boundary) của các node.
- Dựng cây cấu trúc (hierarchy) từ chuỗi văn bản tuyến tính.
- Tạo cấu trúc dữ liệu Legal Node chuẩn hóa.

**Out of Scope**
- Nhận diện các liên kết ngữ nghĩa (Semantic relation).
- Xây dựng Ontology pháp lý (thuộc Module 7).
- Hệ thống truy xuất (Retrieval) hay hỏi đáp (QA).
- Xử lý văn bản chứa bảng biểu, hình ảnh phức tạp hoặc phụ lục.

---

## 2. Problem Definition

**Vấn đề hiện tại:**
Văn bản pháp luật về bản chất là một chuỗi văn bản tuyến tính, nhưng cấu trúc thực tế lại có dạng cây phân cấp. Cần trích xuất cấu trúc này để làm nền tảng cho GraphRAG.

**Điểm khó:**
Cùng một loại cấu trúc có thể có nhiều biến thể định dạng (ví dụ: "Điều 26.", "ĐIỀU 26."). Hơn nữa, việc xác định ranh giới (boundary) của một node không đơn giản, vì nội dung có thể trải dài qua nhiều đoạn văn và chỉ thực sự kết thúc khi gặp một marker cùng cấp hoặc cấp cao hơn.

**Tại sao cách đơn giản không đủ:**
Regex thuần túy có thể nhận diện các marker rõ ràng ở đầu dòng, nhưng dễ tạo ra false positive với các chuỗi mơ hồ như "1.", "a)", "Điều X" nằm giữa nội dung câu. Ngoài ra, việc ngắt câu bằng Regex đơn thuần sẽ làm đứt gãy nội dung của các cấu trúc đa đoạn (multi-paragraph).

---

## 3. Current Understanding

Hiện tại nhóm hiểu luồng xử lý cấu trúc vật lý như sau:
`Clean Text` → `nhận diện marker / metadata` → `tạo candidate` → `xác định boundary` → `xây dựng hierarchy` → `sinh Legal Node`.

Hiện tại chưa coi Regex (trên văn bản thuần) là tín hiệu duy nhất. 
Trong DOCX, parser có thể dùng 4 tín hiệu: metadata numbering, Word Style, text pattern và context.
Trong plain text, Style và numbering có thể không tồn tại, khi đó parser chỉ dựa trên text pattern và context.

---

## 4. Technical Model

**4.1 Input representation**
Văn bản đã qua chuẩn hóa. Với DOCX, representation có thể kèm metadata định dạng; với plain text, các metadata này có thể không tồn tại.

**4.2 Pattern model (Pattern Taxonomy)**
Quản lý các mẫu regex theo mức độ tin cậy (HIGH, MEDIUM, LOW) và theo nguồn corpus. Confidence hiện là thuộc tính của pattern dùng để quản lý mức độ tin cậy và theo dõi nguồn evidence; chưa phải xác suất được calibration.

**4.3 Boundary model**
Prototype hiện tại dùng Stack-based boundary detection; còn cần verify các trường hợp multiline và boundary liên tiếp.

**4.4 Hierarchy model**
Sử dụng Stack để theo dõi cấp độ hiện tại (depth). Khi gặp node mới, so sánh với đỉnh stack để push hoặc pop, qua đó thiết lập quan hệ cha-con.

**4.5 Node schema**
Bao gồm các trường cốt lõi: `id`, `type`, `depth`, `title`, `text`, `parent_id`, `position`, `number`, `start_idx`, `end_idx`.

**4.6 Data flow**
Structured Paragraph → Candidate Detection → Boundary Detection → Hierarchy Builder → Node Generator.

---

## 5. Research Questions

**RQ1 — Structural Detection**
Làm sao nhận diện cùng một cấu trúc pháp luật dưới nhiều dạng trình bày (format variants) mà không làm phình to bộ luật Regex gây mất kiểm soát?

**RQ2 — Ambiguous Markers**
Làm sao giảm false positive của các marker mơ hồ (ví dụ: "1.", "a)") khi chúng xuất hiện trong ngữ cảnh câu thông thường?

**RQ3 — Boundary**
Làm sao xác định boundary của một node khi nội dung của nó trải qua nhiều paragraph và không có dấu hiệu ngắt rõ ràng?

**RQ4 — Hierarchy**
Làm sao dựng lại cây phân cấp từ chuỗi tuyến tính và xử lý đúng khi cấu trúc bị khuyết (ví dụ: khuyết Khoản, từ Điều nhảy thẳng xuống Điểm)?

**RQ5 — Representation Robustness**
Parser phụ thuộc tới đâu vào metadata của nguồn? Làm sao duy trì độ chính xác khi nguồn mất định dạng (plain text)?

**RQ6 — Information Preservation**
Khi tài liệu được chuyển qua các bước tiền xử lý, những tín hiệu cấu trúc nào cần được giữ lại để Module 2 có thể khôi phục hierarchy mà không phải suy diễn lại thông tin đã bị mất?
*Hướng nghiên cứu tiếp theo (Ablation study theo Information Signal):*
- Full metadata → Baseline
- Remove style → Quality giảm?
- Remove numbering → Quality giảm?
- Remove both → Quality giảm?
- Text only → Quality giảm bao nhiêu?

---

## 6. Investigations

### Investigation: DOCX Numbering (Khoản/Điểm bị ẩn số)

**Vấn đề**
Regex `^\d+\.` không nhận diện được Khoản (CLAUSE) trong file DOCX. Số lượng Khoản nhận diện được là 0%.

**Cách tiếp cận hiện tại**
Ban đầu giả định số thứ tự của Khoản nằm trực tiếp trong `paragraph.text`.

**Thử nghiệm**
Inspect paragraph structure và file `numbering.xml` của file `Luat_dat_dai_chuong_3.docx`. Phát hiện các giá trị `ilvl`, `numFmt`, và `lvlText`.

**Quan sát**
`paragraph.text` không chứa số "1.", "2.", "3.". Số thứ tự do Word tự động sinh (Auto-numbering) từ metadata.

**Finding**
Khoản không phải bài toán Regex text thuần. Trên Chương III Luật Đất đai, cấu trúc danh sách trong Word dựa vào metadata: `ilvl=0` + `decimal` tương ứng với Khoản; `ilvl=1` + `lowerLetter` tương ứng với Điểm.

**Quyết định**
Ưu tiên sử dụng numbering metadata (`ilvl`, `numFmt`) khi có. (Lưu ý: Kết quả này mới được xác nhận trên Chương III Luật Đất đai 2024, chưa được xem là quy luật chung cho mọi văn bản DOCX). Sử dụng Regex text thuần như một fallback.

**Hệ quả**
Khôi phục thành công việc nhận diện 185 Khoản trong file DOCX. Yêu cầu M1 truyền metadata xuống M2.

**Còn bỏ ngỏ**
Xử lý Plain text khi export bị mất numbering metadata hoàn toàn.

### Investigation: Separator Paragraphs rỗng

**Vấn đề**
Có 20 paragraph có định dạng `List Paragraph` nhưng `numId=None`.

**Thử nghiệm & Quan sát**
Kiểm tra text của 20 paragraph này. Kết quả: tất cả đều rỗng (`text.strip() == ""`). Đây là các đoạn do người dùng nhấn Enter tạo khoảng trắng dư.

**Quyết định**
Bỏ qua (skip) các đoạn văn rỗng.

### Investigation: Điểm mồ côi (Orphan POINT)

**Vấn đề**
Trong bản plain text, do mất Khoản, 8 Điểm bị đẩy lên gắn trực tiếp vào Điều.

**Quan sát**
Hierarchy stack pop về Điều, tạo ra quan hệ trực tiếp Điều -> Điểm (depth 2 -> 4). Cờ `implicit_parent` lúc đầu bị gán sai do logic check chuỗi tĩnh.

**Quyết định**
Cập nhật logic cờ `implicit_parent` để đánh dấu các node bị khuyết cha trực tiếp.

**Hệ quả**
Fix thành công, 8/8 orphan POINTs được đánh dấu đúng trong TXT mode.

---

## 7. Experiments & Prototypes

### EXP-A — Regex Thuần (Prototype A)
- **Input:** `Luat_dat_dai_chuong_3.docx`
- **Thay đổi:** Áp dụng Pattern Registry cơ bản.
- **Kết quả:** CHAPTER(1), SECTION(5), ARTICLE(23), CLAUSE(0), POINT(0).
- **Failure:** Miss toàn bộ Khoản và Điểm.
- **Finding:** Không thể dùng text thuần trên DOCX có sử dụng list auto-numbering.

### EXP-B — DOCX Metadata & Scope (Prototype B)
- **Input:** `Luat_dat_dai_chuong_3.docx`
- **Thay đổi:** Bổ sung điều kiện `required_style = List Paragraph`, stateful tracking cho scope, fix mapping `đ` -> `d`.
- **Kết quả:** CHAPTER(1), SECTION(5), ARTICLE(23), CLAUSE(185), POINT(8). (Tổng 222 nodes). Nhưng chưa xác minh taxonomy.
- **Failure (Phát hiện sau):** Dù tổng số node bằng 222 (đủ số lượng), nhưng Taxonomy bị sai lệch nặng. Do phụ thuộc vào fallback Word Style (`List Paragraph` → CLAUSE), 101 Điểm (có cùng style) đã bị phân loại nhầm thành Khoản.
- **Finding:** Style-based fallback rất rủi ro. Tổng số node count không đủ để khẳng định sự chính xác của parsing. Đây là bài học benchmark cực kỳ đáng giữ: Số lượng đúng chưa chắc phân loại đúng.

### EXP-B2 — M1-M2 Integration (Structured Metadata)
- **Input:** `StructuredParagraph` contract từ Module 1 (giữ nguyên numbering metadata).
- **Thay đổi:** Phân tách `number` và `marker` ở schema; Regex Engine sử dụng `numbering_hint` (ilvl, num_fmt) như tín hiệu cấu trúc ưu tiên cao nhất, bỏ qua check `required_style` khi hint khớp.
- **Kết quả:** CHAPTER(1), SECTION(5), ARTICLE(23), CLAUSE(84), POINT(109). (Tổng 222 nodes).
- **Delta so với Prototype B:** -101 CLAUSE, +101 POINT.
- **Finding:** Việc giữ lại metadata chính xác (`ilvl=0` + `decimal` → CLAUSE; `ilvl=1` + `lowerLetter` → POINT) đã giúp khôi phục đúng taxonomy của 101 node bị phân loại nhầm trước đó. Tuy nhiên, để khẳng định tỷ lệ 84/109 là 100% đúng thực tế (ground truth), cần một bước kiểm tra chéo (cross-check) trên file DOCX gốc.

### EXP-C — Plain Text Fallback (Prototype C)
- **Input:** `luat_ch3_output.txt`
- **Mục đích:** Test mức độ phụ thuộc vào metadata.
- **Kết quả:** CLAUSE = 0% (Miss hoàn toàn), POINT = 100%. Nhận diện 37 node.
- **Failure:** CLAUSE mất numbering; phát sinh lỗi trùng lặp ID (ID Collision) do mất tầng Khoản (7/8 POINT trùng ID).
- **Finding:** Parser hiện tại phụ thuộc nặng vào DOCX metadata đối với cấu trúc Khoản.

---

## 8. Findings

**Đã xác nhận trên corpus hiện tại (Ch3-LDD)**
- Word Style là một tín hiệu cấu trúc mạnh: `List Paragraph` thường xuất hiện ở Khoản.
- Trên Chương III Luật Đất đai, numbering metadata định hình cấu trúc: `ilvl=0` + `decimal` tương ứng Clause, `ilvl=1` + `lowerLetter` tương ứng Point.
- Hierarchy builder dạng Stack hoạt động hiệu quả với thứ tự tuyến tính của văn bản pháp luật.
- Tín hiệu `Context` (giới hạn tìm Điểm bên trong Khoản) giúp loại bỏ False Positive hiệu quả so với code dùng regex thuần.

**Chưa đủ dữ liệu**
- Word Style có nhất quán giữa các tài liệu DOCX từ các nguồn khác nhau hay không.
- Mục có thể dùng số La Mã không (corpus hiện tại chỉ có số Ả Rập).
- Với file TXT mất numbering hoàn toàn, khôi phục cấu trúc Khoản dựa vào vị trí như thế nào.

---

## 9. Design Decisions

### Decision: Cấu trúc mô hình tín hiệu 4 lớp
- **Lựa chọn:** Dùng kết hợp Word Style, Numbering, Text Pattern, và Context.
- **Lý do:** Regex thuần túy không đọc được số tự động sinh của DOCX và dễ sinh False Positive.
- **Ưu:** Tận dụng được nhiều tín hiệu hơn khi metadata tồn tại, giảm phụ thuộc vào một regex đơn.
- **Nhược:** Tăng độ phức tạp của module, giảm hiệu năng phân giải trên Plain text.
- **Trạng thái:** Đang dùng.

### Decision: Hierarchy Builder dùng Stack
- **Lựa chọn:** Stack-based traversal.
- **Lý do:** Cấu trúc node xuất hiện theo thứ tự tuyến tính, parent luôn nằm trước child. Duyệt preorder tuyến tính phù hợp.
- **Ưu:** O(n), đơn giản, dễ trace và debug.
- **Nhược:** Phụ thuộc hoàn toàn vào việc depth của candidate đã được nhận diện đúng.
- **Trạng thái:** Đã verify trên Ch3-LDD.

### Decision: Tách riêng `position` và `number`
- **Lựa chọn:** Lưu `position` (thứ tự tương đối 1,2,3...) và `number` (số gốc trên văn bản) thành 2 trường riêng.
- **Lý do:** Tài liệu có thể bị khuyết số (thiếu Khoản 2). Nếu dùng position làm number thì Module Validation không thể phát hiện lỗi ngắt quãng.
- **Trạng thái:** Đang dùng.

### Decision: Cờ `implicit_parent` thay vì Virtual Node
- **Lựa chọn:** Đánh dấu `implicit_parent=True` cho các node khuyết cha.
- **Lý do:** Parser chỉ làm nhiệm vụ quan sát và phản ánh thực tế cấu trúc, không tự nội suy cấu trúc giả.
- **Trạng thái:** Đã verify.

---

## 10. Trade-offs

| Vấn đề | Lựa chọn A | Lựa chọn B | Hiện tại |
|---|---|---|---|
| **Tín hiệu đầu vào** | Chỉ dùng Text (đơn giản, đồng nhất) | Dùng cả Metadata (chính xác hơn cho DOCX) | Dùng cả Metadata khi có |
| **Suy luận cấu trúc khi thiếu metadata** | Khôi phục nhiều node hơn (nguy cơ tạo cấu trúc sai) | Không suy luận, giữ tính bảo toàn (nguy cơ bỏ sót cấu trúc) | Đang ưu tiên an toàn |
| **Position vs Number** | Dùng chung 1 trường (đơn giản) | Tách riêng (phát hiện gap) | Tách riêng |
| **Định danh ID** | Hierarchical ID (dễ truy vết) | UUID (Đảm bảo unique tuyệt đối) | Hierarchical (current prototype; final strategy chưa chốt) |

---

## 11. Current Limitations

- **KL-01:** Plain text mất numbering metadata. Khi mất số tự động → CLAUSE không nhận diện được (0%).
- **KL-02:** Trong Prototype C, khi mất tầng Khoản, Hierarchical ID có thể collision do path bị rút ngắn.
- **KL-03:** Boundary đa đoạn (multiline) chưa được benchmark đầy đủ do thiếu mẫu trong corpus hiện tại.

---

## 12. Open Problems

**Open (cần giải quyết trong phiên bản hiện tại)**
- Boundary nhiều đoạn văn: Xử lý cơ chế pending chunks ổn định.

**Open (để phiên bản sau / chưa thuộc critical path hiện tại)**
- TXT mất numbering: Cần có fallback heuristic để nhận diện Khoản khi không có metadata.
- Chiến lược ID: Đánh giá lại việc dùng Hybrid ID (kết hợp Hierarchy + Hash) để khắc phục KL-02.
- Pattern mở rộng: Các dạng ký tự điểm khác (`a.`, `(a)`).

**Out of current scope**
- Lỗi chính tả OCR (Đ -> D, ọ -> o).
- Xử lý cấu trúc Phụ lục.

---

## 13. Research Gaps

*(Tạm thời chưa đưa thành Gap cho đến khi survey xong literature).*

Gap tiềm năng: Xử lý cấu trúc pháp luật tiếng Việt trong điều kiện biểu diễn đầu vào (input representation) không đồng nhất.

---

## 14. Evaluation Plan

- **Input corpus:** Tập văn bản pháp luật chuẩn hóa (DOCX và TXT).
- **Ground truth:** JSON Node Tree được gán nhãn thủ công.
- **Metrics:** Node Precision / Recall / F1, Parent Accuracy, Boundary Accuracy, ID Collision Rate.
- **Baseline:** Regex thuần túy.

---

## 15. Next Actions

1. Chốt Data Contract M1→M2.
2. Merge M1 + M2.
3. Verify Boundary Detector.
4. Re-run Ch3-LDD.
5. Benchmark v0.

---

## 16. Evolution Log

- **Prototype A**: Regex Thuần (DOCX) → Thất bại với Khoản/Điểm (0 nodes).
- **DOCX Inspection**: Tìm thấy numbering.xml. Phát hiện Word Style và `ilvl`.
- **Prototype B**: Bổ sung `required_style` và logic metadata → Thành công (222 nodes). [Retained]
- **Prototype C**: Plain Text Fallback → Phát hiện lỗ hổng CLAUSE=0% và ID Collision.
- **M1–M2 Contract**: Đề xuất M1 truyền metadata định dạng xuống cho M2.

---

## 17. References

**Đã kiểm tra và dùng**
- `python-docx` paragraph model documentation — phục vụ phân tích numbering XML.

**Cần đọc**
- Nghị định 34/2016/NĐ-CP — Quy định định dạng văn bản QPPL VN.
- TCVN 9245 — Tiêu chuẩn soạn thảo văn bản hành chính.

---

## 18. Defense Notes

**Tại sao không dùng LLM cho structural parsing?**
Bài toán khôi phục cấu trúc vật lý là bài toán có quy luật. Rule-based parsing có tính tái lập cao vì cùng input và cùng rule sẽ cho cùng kết quả, chi phí thấp, và kiểm soát lỗi dễ dàng hơn.

**Tại sao parser lại phụ thuộc vào DOCX metadata?**
Đó là chiến lược hiệu quả hơn trên DOCX có metadata trong corpus hiện tại để giảm false positive và khôi phục số thứ tự ẩn (thứ bị mất trong TXT).

---

## 19. Appendix

Appendix A — Prototype statistics
Appendix B — Numbering metadata
Appendix C — Failure cases
Appendix D — Sample JSON

---

## 19. Session Summary (M1-M2 Integration & DOCX Baseline)

*(Tổng kết phiên làm việc: Hợp nhất Module 1 và Module 2)*

**1. Architecture & Data Contract**
- **Quyết định:** Định nghĩa `StructuredParagraph` là contract chính.
- **Schema:** Tách bạch `number` (Khoản, Điều) và `marker` (Điểm). Không dùng chung một trường.
- **Giá trị:** Đẩy metadata (ilvl, num_fmt) đi xuyên suốt, không bắt Regex phải đoán lại thông tin mà XML cấp thấp đã biết.

**2. Major Findings (Sự khôi phục taxonomy)**
- **Trước khi merge (Prototype B):** 222 nodes (185 CLAUSE / 8 POINT).
- **Sau khi merge (M1+M2):** 222 nodes (84 CLAUSE / 109 POINT).
- **Phân tích:** Prototype B có taxonomy sai lệch lớn: 101 node thực chất là POINT nhưng bị phân loại thành CLAUSE (do dùng fallback style "List Paragraph" khi bị mất marker). Việc giữ lại metadata chính xác từ M1 đã giúp khôi phục đúng taxonomy của 101 node này.

**3. Tree-building / ID failure**
- **Vấn đề:** Lỗi ID Collision khi dùng `temp_id` chuỗi để dò ngược tìm cha (ví dụ "khoan_pos5" đụng độ nhau).
- **Giải quyết:** Lưu trực tiếp `parent_node` object reference trong `HierarchyNode`, sau đó dùng object identity (`id(node)`) để ánh xạ sang final ID. Đã xác minh bằng code trace và fix dứt điểm.

**4. Pattern Registry evolution**
- **Quyết định:** Sinh ra `DOCX_NUMBERING_HINTS` thay vì hard-code `ilvl=0` luôn là CLAUSE.
- **Đánh giá:** Cấu hình phức tạp hơn, nhưng dễ mở rộng khi xuất hiện format mới ở các corpus khác.

**5. Ground Truth Cross-check & Test Validation**
- **Trạng thái M2 (DOCX Baseline):**
  - *Taxonomy:* verified on representative ground-truth samples (Đã có một tập cross-check đại diện xác nhận bước đầu phù hợp với DOCX gốc).
  - *Hierarchy:* verified (ARTICLE → CLAUSE → POINT đang đúng).
  - *Parent-child:* verified.
  - *Numbering:* verified (Lấy được từ M1 và khớp với thứ tự thực tế của DOCX).
  - *Multiline boundary:* verified on representative case (VD: Điểm l trải qua 2 paragraph nhưng vẫn được gom thành một node, chứng minh Boundary Detector không bị ép cứng "mỗi paragraph = một node").
  - *Full-corpus manual ground truth:* chưa có.
- **Phát hiện về Auto-numbering:** 109/109 Point trong DOCX này đều đến từ Word Auto-numbering. Không có Point nào viết cứng `a), b)` trong văn bản. Điều này làm câu chuyện Prototype B → M1+M2 cực kỳ "sạch": DOCX XML → numbering metadata → 109 POINT, thay vì dùng Word Style để "đoán".
- **Bài học về Testing:** Verification script cũng có thể tạo false evidence. Một đoạn script ban đầu đếm được 84 Khoản có `position != number`, nhưng kiểm tra lại thì do lỗi so sánh kiểu dữ liệu (position là `int`, number là `str`). Thực tế `position` và `number` khớp nhau 100% trên toàn bộ corpus hiện tại. **Bài học:** Parser cần validation, và evaluation code cũng cần validation. (Dù vậy, design decision tách riêng position và number vẫn đúng để dự phòng cho corpus bị bãi bỏ/nhảy số sau này).

**6. Evaluation insight: node count ≠ taxonomy correctness**
- **Bài học đánh giá:** Node count là metric không đủ để đánh giá parser. Tổng số node giống nhau (222 nodes) không đồng nghĩa taxonomy đúng. Parser cần được đánh giá theo loại node và quan hệ cha–con, không chỉ theo node count.

**7. RQ6 Status & Next Step (Prototype C2)**
- RQ6: Evidence strong trên Ch3-LDD → structured metadata giúp tránh misclassification do information loss. Tuy nhiên chưa chứng minh cross-corpus và cần ablation trên TXT.
- **Next step (C2):** TXT baseline được dùng để đo mức suy giảm khi các tín hiệu cấu trúc của DOCX bị loại bỏ. Sau khi có số liệu suy giảm, ta mới xem xét các giải pháp phục hồi (C2-Recovery) bằng Hypothesis testing.

---

## 20. Session Summary (Prototype C2 - Ablation Baseline)

*(Tổng kết phiên làm việc: Đo lường sự suy giảm cấu trúc trên TXT)*

**1. Input C2 (Ablation Baseline)**
- Sử dụng M1 (DocxLoader) trích xuất lại văn bản từ DOCX, chỉ lấy text thuần UTF-8 sạch, **cố ý không serialize metadata** vào văn bản.
- Biến độc lập chính của thử nghiệm là **tín hiệu cấu trúc (structural signals)**, loại bỏ hoàn toàn nhiễu do lỗi OCR hay lỗi encoding.

**2. Kết quả Đo lường (Degradation Baseline)**
Với cùng corpus Ch3-LDD:

| Metric | DOCX | TXT | Mức suy giảm |
| :--- | :--- | :--- | :--- |
| CHAPTER | 1 | 1 | 0% |
| SECTION | 5 | 5 | 0% |
| ARTICLE | 23 | 23 | 0% |
| **CLAUSE** | 84 | 0 | **-100%** |
| **POINT** | 109 | 8 | **-92.7%** |
| Total | 222 | 37 | -83.3% |

**3. Major Findings**
- **Structural Selectivity của Information Loss:** Sự suy giảm thông tin không tác động đồng đều lên mọi cấp. Các cấp có text marker rõ (Chương, Mục, Điều) vẫn sống sót 100%, trong khi các cấp phụ thuộc vào Word Numbering (Khoản, Điểm) sụp đổ gần như hoàn toàn. Đây là một finding rất đẹp và mạnh mẽ cho RQ5/RQ6 thay vì chỉ nói chung chung là "TXT kém hơn DOCX".
- **Sự đứt gãy Hierarchy:** Hierarchy bị suy giảm nghiêm trọng tại tầng Khoản; các node Point còn nhận diện được (8 node gõ cứng text marker `d)` có trong text) trở thành orphan và không thể tái hiện đầy đủ cấu trúc Article → Clause → Point (Trong khi Chapter → Section → Article vẫn đúng).

**4. Phương pháp luận C2-Recovery (Next Phase)**
Mục tiêu tiếp theo là trả lời câu hỏi: *Sau khi suy giảm, có thể phục hồi bao nhiêu cấu trúc từ tín hiệu còn lại (text + context)?*

Cách làm không phải là code thẳng thành Rule cứng để "fix TXT", mà là một **Experiment** đo lường Precision/Recall/FP/FN cho từng giả thuyết (Hypothesis) theo thứ tự:

- **TXT Baseline** (Đã có: Clause 0%)
- ↓
- **H1 (Hypothesis 1):** Paragraph đầu tiên sau Article không có marker → Clause vô danh. *(Lưu ý nguy cơ False Positive rất lớn vì paragraph đó có thể là body trực tiếp của Article. Chỉ dùng làm candidate detector, đo FP/FN).*
- ↓
- **H2 (Hypothesis 2):** Chuỗi paragraph có cùng pattern/context/layout cue → Nhóm Clause. *(Đo lường incremental gain).*
- ↓
- **H3 (Hypothesis 3):** Sequence logic giữa các đoạn (ví dụ có Point a theo sau) cho phép suy ngược ra Clause. *(Đo lường incremental gain).*

**Kết quả kỳ vọng:** Bảng so sánh Ablation toàn diện (DOCX vs TXT Baseline vs TXT+H1 vs TXT+H1+H2...). Bất kể mức độ phục hồi là 0 → 70% hay không vượt quá baseline, đó đều là Finding có giá trị nghiên cứu cao.

---

## 21. Session Summary (Prototype C2 — Ablation Study: TXT Information Loss)

*(Tổng kết phiên làm việc: Ablation Study đo lường suy giảm và phục hồi cấu trúc trên TXT)*

---

### 21.1 Mục tiêu và bối cảnh

C2 không phải là "cố làm cho TXT parser tốt hơn". Mục tiêu đúng:
> *Đo lường sự suy giảm cấu trúc khi loại bỏ metadata DOCX, và đánh giá khả năng phục hồi một phần từ các tín hiệu bối cảnh (context-only) — để trả lời RQ6.*

**Biến độc lập:** Sự hiện diện của structural signals (Word Style, Numbering XML).
**Biến phụ thuộc:** Số lượng và chất lượng CLAUSE/POINT được nhận diện đúng.
**Reference:** `output_module2_merged.json` — cross-checked đại diện, không phải full manual Ground Truth.

---

### 21.2 Methodology (Các quyết định quan trọng & lý do)

| Quyết định | Lựa chọn | Lý do | Trade-off |
| :--- | :--- | :--- | :--- |
| Input TXT | M1 tạo lại từ DOCX (chỉ lấy text, bỏ metadata) | Loại nhiễu encoding (file cũ bị lỗi font) | TXT mất cả "1.", "a)" — đây là feature, không phải bug |
| Reference | "Reference Annotation", không phải "Gold Standard" | Chưa manual-annotate toàn bộ 222 node | Tăng độ cẩn trọng về claim; cần ghi rõ limitation |
| Evaluation | Text-based matching (normalize + substring) | DOCX index ≠ TXT index do dòng trống bị bỏ | Matching không hoàn hảo; false negative có thể xảy ra nếu text bị cắt ngắn |
| H1/H2/H3 | Candidate Detector, không phải Rule | Tránh bias khi design sau khi biết kết quả | Output là `ClauseCandidate`, không commit vào parser core |
| Testing | Isolated + Cumulative (7 config) | Đo contribution riêng của từng H | H2 saturate → H1+H2 = H2; cần corpus lớn hơn để phân biệt |

---

### 21.3 Kết quả Degradation Baseline

| Metric | DOCX Reference | TXT Baseline | Mức suy giảm |
| :--- | :---: | :---: | :---: |
| CHAPTER | 1 | 1 | 0% |
| SECTION | 5 | 5 | 0% |
| ARTICLE | 23 | 23 | 0% |
| **CLAUSE** | **84** | **0** | **−100%** |
| **POINT** | **109** | **8** | **−92.7%** |
| Total | 222 | 37 | −83.3% |

**Finding chính (Structural Selectivity):** Suy giảm thông tin không đồng đều. Cấp có text marker rõ (Chương/Mục/Điều) sống sót 100%. Cấp phụ thuộc Word Auto-numbering (Khoản/Điểm) sụp đổ gần hoàn toàn. Đây là đóng góp thực nghiệm cho RQ6.

---

### 21.4 Kết quả Recovery Experiment (với TXT Baseline làm mốc)

| Config | Cands | TP | FP | FN | Prec. | Recall | F1 | ΔF1 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **TXT Baseline** | 0 | 0 | 0 | 84 | 0.000 | 0.000 | 0.000 | — |
| H1 | 23 | 22 | 1 | 62 | 0.957 | 0.262 | 0.411 | +0.411 |
| H2 | 135 | 60 | 75 | 24 | 0.444 | 0.714 | 0.548 | +0.548 |
| H3 | 6 | 0 | 6 | 84 | 0.000 | 0.000 | 0.000 | +0.000 |
| H1+H2 | 135 | 60 | 75 | 24 | 0.444 | 0.714 | 0.548 | +0.548 |
| H1+H3 | 29 | 22 | 7 | 62 | 0.759 | 0.262 | 0.389 | +0.389 |
| H2+H3 | 135 | 60 | 75 | 24 | 0.444 | 0.714 | 0.548 | +0.548 |
| H1+H2+H3 | 135 | 60 | 75 | 24 | 0.444 | 0.714 | 0.548 | +0.548 |

*Matching: text-based similarity (NFC normalize + substring). Reference CLAUSE count: 84.*

---

### 21.5 Phân tích từng Hypothesis

**H1 — Clause-Start Inference (paragraph đầu tiên của ARTICLE)**
- Precision=0.957 (22/23 đúng): paragraph đầu trong một Điều thực sự thường là bắt đầu Khoản. Finding phụ: 1 FP là Điều không có Khoản con (body text trực tiếp của Điều).
- Recall=0.262 (22/84): H1 chỉ nhận diện được đúng 1 Khoản/Điều. 62 Khoản tiếp theo hoàn toàn bỏ qua.
- **Đây là heuristic an toàn nhất nhưng coverage quá thấp để dùng độc lập.**

**H2 — All-Paragraph Heuristic (mỗi paragraph = 1 Khoản)**
- Recall=0.714 (60/84): Phục hồi được 71.4% Khoản — mức cao nhất trong tất cả config, kể cả cumulative.
- FP=75/135 (55.6%): Hơn một nửa ứng cử viên là FP. Lý do: paragraph continuation (tiếp nối ý của Khoản đã match) bị tính thêm là Khoản mới.
- F1=0.548 (ΔF1=+0.548 so với baseline): Recovery gain tốt nhất, nhưng đi kèm FP không thể bỏ qua.
- **H2 là candidate phục hồi mạnh nhất nhưng phải giải quyết vấn đề continuation để dùng thực tế.**

**H3 — Point-Anchor Inference (suy ngược từ POINT marker)**
- Precision=0.000, Recall=0.000, FP=6/6: Toàn bộ 6 ứng cử viên đều là FP.
- Lý do thất bại: 6 paragraph được H3 đề xuất là "ngay trước POINT marker trong text" → sau text matching, đây là body continuation của Khoản (nằm giữa), không phải điểm bắt đầu Khoản. Reference Annotation không có CLAUSE nào start ở đó.
- **H3 fail hoàn toàn trên Ch3-LDD. Coverage quá thấp (chỉ 6 POINT có text marker) và logic suy ngược không đúng với cấu trúc thực tế.**

**Cumulative — Không có incremental gain đáng kể**
- H1+H2 = H2 = H2+H3 = H1+H2+H3 (mọi config chứa H2 đều cho cùng kết quả).
- H2 đã **saturate** không gian ứng cử viên — ôm toàn bộ paragraph trong mỗi Điều.
- H1+H3 (29 cands, F1=0.389) thấp hơn H1 đơn lẻ (F1=0.411) vì H3 thêm FP mà không thêm TP.
- **Kết luận cumulative:** Trong corpus hiện tại, "nhiều hypothesis" không cho thêm gain so với H2 đơn lẻ.

---

### 21.6 Trade-offs và Lựa chọn Design

| Trade-off | Lựa chọn A | Lựa chọn B | Hiện tại |
| :--- | :--- | :--- | :--- |
| Precision vs Recall | H1 (Prec=0.957, Rec=0.262) | H2 (Prec=0.444, Rec=0.714) | Chưa chọn — đo cả hai |
| Coverage vs Accuracy | Nhiều candidates (FP cao) | Ít candidates (FP thấp) | Chưa có bộ lọc continuation |
| Evaluation strictness | Node count (lạc quan hơn) | Text matching (nghiêm ngặt hơn) | Text matching |
| Claim về kết quả | "Parser phục hồi được" | "Evidence phục hồi một phần" | Evidence-based, thận trọng |

---

### 21.7 Phát hiện trong khi Build (Engineering Insights)

1. **Index mismatch:** DOCX dùng paragraph index gốc (kể cả dòng trống), TXT bỏ dòng trống nên index lệch. → Phải dùng text-based matching thay vì index-based alignment.

2. **H1/H2 logic bug đầu tiên:** Tìm paragraph ở `idx >= art_end` (sau boundary ARTICLE) thay vì `[art_start+1, art_end)` (trong nội dung ARTICLE). Lỗi vì trong TXT baseline, ARTICLE ôm toàn bộ content vào text và `end_idx` là exclusive — khác DOCX. → Bài học: cần test với data thực, không chỉ đọc schema.

3. **Evaluation version 1 (node count) lạc quan hơn thực tế:** H2 từ F1=0.740 → F1=0.548 sau khi đổi sang text matching. Lý do: node count không phạt FP từ paragraph continuation (nhiều paragraph cùng match một CLAUSE). → Xác nhận yêu cầu của bạn: FP/FN phải được đánh giá bằng boundary/text, không bằng số lượng.

4. **H3 fail hoàn toàn:** Không phải vì H3 sai về logic (suy ngược từ POINT là hợp lý về nguyên tắc), mà vì trong Ch3-LDD, paragraph TRƯỚC POINT là body continuation của Khoản, không phải điểm bắt đầu Khoản. Cấu trúc thực tế: `Khoản mở đầu → a) → b) → c)`. Paragraph dẫn nhập của Khoản không đứng liền POINT.

---

### 21.8 Vấn đề Còn Bỏ Ngỏ

| Vấn đề | Mức độ quan trọng | Hướng xử lý |
| :--- | :--- | :--- |
| 75 FP của H2: loại paragraph nào bị nhầm nhiều nhất? | Cao | Phân tích manual 75 FP cases |
| Bộ lọc continuation: có thể phân biệt "Khoản mới" và "tiếp nối Khoản cũ" không? | Cao | Length heuristic, dấu chấm cuối câu, indent cues |
| Cross-corpus: tỷ lệ H2 Recall=71% có giữ vững không? | Trung bình | Thử trên Chương IV hoặc văn bản khác |
| Full manual Ground Truth: 222 node chưa được annotate tay | Trung bình | Cần annotation tool hoặc quy trình bán tự động |
| H3 trên corpus có nhiều POINT text marker: sẽ hoạt động không? | Thấp (Ch3-LDD không có) | Thử trên corpus có điểm gõ cứng |

---

### 21.9 Kết luận cho RQ6 (Thận trọng)

> **"Khi loại bỏ Style + Numbering metadata khỏi representation của Ch3-LDD, structural parser mất toàn bộ tầng Khoản (−100%) và phần lớn tầng Điểm (−92.7%), trong khi tầng Chương/Mục/Điều vẫn giữ nguyên (0%). Điều này cho thấy metadata loss có tính chọn lọc theo cấu trúc (structural selectivity), không đồng đều."**

> **"Context-only heuristic (H2) có thể phục hồi 71.4% Khoản (Recall=0.714, F1=0.548) với FP rate 55.6% — cho thấy phục hồi một phần là khả thi nhưng đòi hỏi thêm cơ chế lọc để sử dụng thực tế."**

> **Lưu ý phạm vi:** Evidence này chỉ được đo trên Ch3-LDD (84 CLAUSE, 23 ARTICLE). Cần cross-corpus validation trước khi generalize.

