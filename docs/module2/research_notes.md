# MODULE 2: Regex Parser (Phân rã Cấu trúc Vật lý)
### Hybrid Parser · GraphRAG Văn bản Pháp luật Việt Nam

> **Phạm vi**: Module 2 — Regex Parser (Static Structural Pipeline)  
> **Corpus chính**: Chương III Luật Đất Đai 2024 (`Luat_dat_dai_chuong_3.docx`)  
> **Cập nhật**: 2026-08-14 — sau Prototype C  
> **Trạng thái**: Prototype B ✅ DONE · 2.2/2.3/2.4 🔄 IN PROGRESS · Prototype C2 🧊 FROZEN

---

## TRỤC CỐT LÕI CỦA RESEARCH NOTE NÀY

> **Không nghiên cứu "một bộ Regex chạy được trên Chương III".**  
> **Nghiên cứu cách xây dựng một bộ pattern có thể mở rộng dần theo các biến thể cấu trúc của văn bản pháp luật.**

Quy trình phát triển của Module 2 là:

```
Corpus
  ↓
Quan sát format
  ↓
Pattern Taxonomy
  ↓
Prototype
  ↓
Failure Cases
  ↓
Bổ sung / sửa pattern
  ↓
Test lại
  ↓
Corpus mới
  ↓
Khái quát hóa
```

Scope tag convention dùng xuyên suốt notes này:

| Tag | Ý nghĩa |
|---|---|
| `[CORPUS: Ch3-LDD]` | Quan sát từ Chương III Luật Đất Đai 2024 |
| `[HYPOTHESIS]` | Giả thuyết chưa có benchmark |
| `[GENERAL]` | Đã kiểm chứng trên nhiều corpus |

---

## MODULE STATUS BOARD

| Sub-module | Trạng thái | Kết quả | Ghi chú |
|---|---|---|---|
| **2.1 Regex Engine** | ✅ Baseline DONE (Prototype B) / 🔄 Generalization IN PROGRESS | DOCX: CHAPTER/SECTION/ARTICLE/POINT = 100% | CLAUSE TXT = 0% — frozen. Chưa tổng quát |
| **2.2 Boundary Detector** | 🔄 IN PROGRESS | Cần verify multiline / start\|end idx | Trọng tâm hiện tại |
| **2.3 Hierarchy Builder** | ✅ DONE — verified 12/12 checks | Stack, position, edge cases | EC-1/EC-3 đúng. Children IDs có artifact nhỏ |
| **2.4 Node Creator** | ✅ DONE — ID 222/222 unique, schema v1.1 | implicit_parent TXT fix ✅ | POINT ID prefix artifact — cosmetic, ghi chú ở dưới |
| **Pipeline tổng thể** | ⏳ PENDING | — | Chỉ review sau khi 2.2–2.4 ổn |
| **Prototype C2 (TXT+CLAUSE)** | 🧊 FROZEN | CLAUSE TXT = 0% | Xem Mục 7 |

> **Nguyên tắc tiến trình**: 2.2 → 2.3 → 2.4 → Pipeline review → Prototype C2 (plain text)

---

## 1. Overview (Tổng quan & Vai trò)

Module 2 là **lõi của tuyến tĩnh (Static Structural Pipeline)**. Mục tiêu là chuyển Clean Legal Text thành các Legal Node theo cấu trúc vật lý của văn bản pháp luật:

```
Chương  (depth=0)
  ↓
Mục     (depth=1)
  ↓
Điều    (depth=2)
  ↓
Khoản   (depth=3)
  ↓
Điểm    (depth=4)
```

**Input**: Clean Legal Text (DOCX paragraphs hoặc plain text)  
**Output**: Legal Nodes JSON

```json
{
  "id":             "ldd-2024_chuong-iii_muc-1_dieu-26_khoan-1",
  "type":           "CLAUSE",
  "depth":          3,
  "title":          null,
  "text":           "Được cấp Giấy chứng nhận quyền sử dụng đất...",
  "parent_id":      "ldd-2024_chuong-iii_muc-1_dieu-26",
  "children_count": 0,
  "position":       1,
  "number":         "1",
  "law_prefix":     "ldd-2024",
  "law_code":       "59/2024/QH15",
  "source_doc":     "Luat_dat_dai_chuong_3.docx",
  "word_style":     "List Paragraph",
  "implicit_parent": false
}
```

**Vị trí trong pipeline tổng thể**:

```
Raw Document
     ↓ (Module 1 — chuẩn hóa)
Clean Text / DOCX Paragraphs
     ↓ [MODULE 2 — ĐIỂM PHÂN NHÁNH]
Legal Nodes JSON
     ↓
Module 3 (Validation) → Module 4 (Physical Graph)
→ Module 5 (Semantic Router) → Module 6 (LLM Extraction)
→ Module 7 (Ontology Builder) → Module 8 (Fusion) → Neo4j
```

> **Parser sai → Toàn bộ pipeline sai.** Module 3 chỉ phát hiện lỗi, không tự sửa.

**Lưu ý về phạm vi mục tiêu**: Module 2 không nhận diện riêng một format của Chương III Luật Đất đai, mà nhận diện **nhiều biến thể định dạng (format variants)** của cùng một cấu trúc pháp luật.

Ví dụ — tất cả đều hướng tới `ARTICLE number=26`:
```
Điều 26.
Điều 26
ĐIỀU 26.
Điều 26. Quyền chung của người sử dụng đất
```

Nhưng một biến thể chỉ được nâng từ `[HYPOTHESIS]` thành `[GENERAL]` sau khi kiểm chứng trên nhiều corpus.

---

## 2. Background (Kiến thức nền & Khái niệm cốt lõi)

### 2.1 Regular Expression

Cần hiểu cú pháp: `^`, `$`, `\s`, `\d`, nhóm `(...)`, nhóm không bắt `(?:...)`, `+`, `*`, `?`, `{m,n}`, `|`, `re.MULTILINE`, `re.IGNORECASE`, `finditer()`, `group()`, `start()`, `end()`.

**Điểm quan trọng hơn cú pháp**: Mỗi pattern đang đưa ra **assumption** gì về hình thức văn bản?

Ví dụ:
```python
r"^\s*Điều\s+\d+"
```
Không chỉ là "tìm Điều + số", mà còn giả định:
- Marker nằm ở **đầu dòng** (hoặc đầu paragraph)
- Giữa "Điều" và số chỉ có khoảng trắng

Mỗi assumption là một rủi ro khi gặp corpus mới.

### 2.2 Hierarchical Structure

Văn bản là chuỗi tuyến tính nhưng cần chuyển thành cây:

```
ARTICLE
├── CLAUSE 1
│   ├── POINT a
│   └── POINT b
└── CLAUSE 2
    └── POINT a
```

Cần phân biệt rõ:
- **Thứ tự xuất hiện** (linear index trong văn bản)
- **Cấp cấu trúc** (depth: 0→4)
- **Quan hệ Parent–Child** (ai là cha của ai)
- **Position** (thứ tự trong cùng một parent)

### 2.3 Boundary Detection

**Marker detection ≠ Boundary detection** — đây là hai bài toán khác nhau:
- Regex → tìm điểm **bắt đầu** của node
- Boundary Detector → tìm điểm **kết thúc** của node

Ví dụ thực tế `[CORPUS: Ch3-LDD]`:
```
a) Cá nhân được nhận chuyển đổi...      ← bắt đầu Điểm a
   ...tiếp tục sang dòng tiếp theo...   ← vẫn thuộc Điểm a
b) Tổ chức kinh tế...                   ← bắt đầu node mới → Điểm a kết thúc
```

Nội dung Điểm **không kết thúc ở cuối dòng** — nó kéo dài đến khi gặp marker kế tiếp.

### 2.4 Document Metadata

Từ Chương III Luật Đất Đai DOCX, phát hiện thêm tín hiệu định dạng:

| Level | Word Style `[CORPUS: Ch3-LDD]` | Số lượng |
|---|---|---|
| CHAPTER / SECTION | Normal | 6 |
| ARTICLE | **Heading 2** | 23 |
| CLAUSE | **List Paragraph** | 185 |
| POINT | **Body Text** | 21 paragraphs Body Text, trong đó **8 được nhận diện là POINT** (còn lại là continuation text) |

**Nguyên tắc**: Đây chỉ là tín hiệu **bổ sung**. Không được phụ thuộc vào chúng vì PDF/TXT không có metadata, và DOCX từ nguồn khác có thể dùng Style khác.

---

## 3. Technical Design (Thiết kế Kỹ thuật & Luồng Dữ liệu)

### 3.1 Pipeline

```
Clean Legal Text
      ↓
2.1 Regex Engine / Structural Detection
      ↓
2.2 Boundary Detector
      ↓
2.3 Hierarchy Builder
      ↓
2.4 Node Generator
      ↓
Legal Nodes JSON
```

**Files đã implement**:

| File | Chức năng | Trạng thái |
|---|---|---|
| `regex_engine.py` | Pattern Registry + match functions | ✅ Prototype B |
| `boundary_detector.py` | Stack-based boundary detection | 🔄 Cần verify |
| `hierarchy_builder.py` | Parent-child tree builder | 🔄 Cần verify edge cases |
| `node_generator.py` | Legal Node JSON generator | 🔄 Cần chốt schema |
| `parser.py` | Orchestrator (DOCX + TXT mode) | ✅ Chạy được |

### 3.2 Pattern Taxonomy

Không tổ chức theo kiểu `ARTICLE = 1 regex`. Thay vào đó:

```
ARTICLE
├── Pattern A: "Điều \d+."   [CORPUS: Ch3-LDD, HIGH]
├── Pattern B: "ĐIỀU \d+."   [HYPOTHESIS]
└── Pattern C: "Điều \d+"    [HYPOTHESIS]
```

Mỗi PatternEntry có metadata:

```python
PatternEntry(
    pattern=r"^\s*(?:Đ|Ð)i[eề]u\s+(?P<number>\d+)\.?\s*(?P<title>.*)$",
    source_corpus="Ch3-LDD-2024",
    confidence="HIGH",
    example="Điều 26. Quyền chung của người sử dụng đất",
    known_fp="'Điều X' trong cross-reference",
    scope=None,
    required_style=None,
    anchor="start_of_line",
    note="[CORPUS: Ch3-LDD]"
)
```

### 3.3 Mô hình 3 lớp tín hiệu `[HYPOTHESIS]`

```
              Legal Document
                   │
      ┌────────────┴────────────┐
      │                         │
 Document Metadata          Text Content
 (nếu có)
      │                         │
  Style Signal             Text Pattern
  (Heading 2, Body Text)   (Điều \d+, ^[a-zđ]\))
      │                         │
      └────────────┬────────────┘
                   ↓
          Candidate Detection
                   ↓
          Context Analysis
          (parent / sequence / depth)
                   ↓
          Boundary Detection
                   ↓
          Hierarchy Builder
                   ↓
              Legal Node
```

Lớp 1 (Style) chỉ có khi DOCX. Lớp 2 (Text Pattern) luôn có. Lớp 3 (Context) là điều kiện giúp giảm FP.

### 3.4 Pattern Taxonomy v1 `[CORPUS: Ch3-LDD]`

**CHAPTER**:
- `Chương [La Mã]` → HIGH · Example: `Chương III`
- `Chương [Ả Rập]` → HYPOTHESIS
- `CHƯƠNG [...]` → HYPOTHESIS

**SECTION**:
- `Mục [Ả Rập]` → HIGH · Example: `Mục 1`, `Mục 2`

**ARTICLE**:
- `Điều \d+. [Tiêu đề]` → HIGH · Known FP: "Điều X" trong cross-ref
- `ĐIỀU \d+.` → HYPOTHESIS

**CLAUSE**:
- `^\d+\.\s+` (DOCX: List Paragraph) → HIGH `[CORPUS: Ch3-LDD]`
- `required_style="List Paragraph"` (fallback khi mất số) → HIGH `[CORPUS: Ch3-LDD]`
- `Khoản \d+.` → HYPOTHESIS
- Không dùng: `^\d+\.\s+[A-ZĐÁÀẢÃẠ]` — Khoản không bắt buộc bắt đầu bằng chữ hoa

**POINT**:
- `[a-zđ]\)\s+` → HIGH · CONFIRMED: `đ)` xuất hiện 8 lần `[CORPUS: Ch3-LDD]`
- Known FP: "điểm a" trong cross-reference câu

---

## 4. Design Decisions & Reasoning (Quyết định Thiết kế & Lý giải)

### Đã chốt (v1 — có thể dùng, chưa phải cuối cùng)

| Quyết định | Lý giải |
|---|---|
| Regex là thành phần trung tâm | PDF/TXT không có Style. Style không nhất quán giữa DOCX khác nhau |
| Regex không giải quyết toàn bộ | Regex nhận diện candidate marker. Context + Hierarchy quyết định cấu trúc |
| Không dùng indentation làm luật chính | Module 1 normalize có thể làm mất indent. Corpus có 20+ giá trị indent khác nhau |
| Pattern phát triển theo corpus | Không viết parser riêng cho từng văn bản |
| Stack-based Hierarchy Builder | O(n), phù hợp với preorder traversal của văn bản |
| `parent_id` thay vì `ancestor_path` | Để Module 4 tự traverse khi build graph. Switch sang materialized path nếu cần |
| Prototype B dùng `text = direct text` *(implementation hiện tại, chưa phải design cuối cùng)* | Tránh duplicate content. Semantics cuối cùng của `text` và cách xử lý `title` vẫn chưa chốt — xem "Chưa nên chốt" |
| Không tạo Virtual Clause | Parser quan sát thực tế, không nội suy. Validation quyết định mức độ lỗi |
| Prototype B dùng `implicit_parent=true` cho Orphan POINT *(quyết định tạm thời — logic đang có bug ở TXT mode, cần verify ở 2.4)* | Flag để Module 3 phát hiện. Không tự sửa cấu trúc |
| Hierarchical ID tạm thời | `ldd-2024_dieu-26_khoan-1`. Có điểm yếu khi multi-doc |
| `đ` → `d` trong ID | Tương thích với Neo4j property key |
| 5 NodeType: CHAPTER/SECTION/ARTICLE/CLAUSE/POINT | Structural Taxonomy, không phải Legal Ontology (thuộc Module 7) |

### Chưa nên chốt (cần thêm evidence hoặc thống nhất team)

| Vấn đề | Lý do chưa chốt |
|---|---|
| Hierarchical ID vs UUID vs Hybrid | ID collision khi multi-doc đã có evidence. Cần team quyết định |
| Single-pass vs 2-pass vs Multi-signal | Chưa benchmark |
| Semantics cuối cùng của `text`: direct only, hay gộp `title`? | Implementation hiện tại là direct — nhưng chưa phải design cuối cùng. Ảnh hưởng M5, M6 |
| Regex vs Style là chiến lược chính | Chờ Prototype C2 để có evidence TXT |
| Schema Node cuối cùng | Phụ thuộc M3, M4, M5 requirements |
| Ancestor lookup strategy | Chờ M4 báo performance requirement |
| CLAUSE trong plain text | 🧊 Frozen — xem Mục 7 |

---

## 5. Alternatives (Các phương pháp thay thế)

### 5.1 Pure Regex

**Ưu**: đơn giản, nhanh, dễ debug, không cần AI.  
**Nhược**: false positive cao với `1.` và `a)` trong câu. Khó xử lý format bất thường.

### 5.2 Regex + Context (đang dùng)

**Ưu**: Giảm FP bằng cách giới hạn tìm CLAUSE trong ARTICLE, POINT trong CLAUSE.  
**Nhược**: Logic phức tạp hơn Regex thuần. Scope tracking cần đúng để không miss sibling.

**Bài học từ Prototype B**: Việc thêm `scope="inside_ARTICLE"` ban đầu gây miss CLAUSE vì scope reset sai khi parser di chuyển qua CLAUSE → cần bỏ strict scope và dùng `required_style` thay thế.

### 5.3 Style + Text + Context (đang dùng một phần)

**Ưu**: Tận dụng Word Style làm Lớp 1 tín hiệu. Tăng độ tin cậy với DOCX.  
**Nhược**: Không áp dụng được cho TXT/PDF. Phụ thuộc cách định dạng của từng tài liệu.

**Bằng chứng thực nghiệm từ Prototype B vs C**:
- DOCX với Style → 222 nodes (100% tất cả types)
- TXT không có Style → 37 nodes (CLAUSE = 0%, POINT = 100%)

### 5.4 Grammar Parser

Dựa trên định nghĩa ngữ pháp hình thức cho cấu trúc văn bản pháp luật.  
**Câu hỏi cần nghiên cứu**: Độ phức tạp có đáng đổi lấy tính tổng quát không? Regex + Context hiện tại đã đủ chưa? **Chưa có cơ sở để kết luận**.

### 5.5 Pure LLM

Không phải hướng của Module 2 vì chi phí, độ tái lập kém, nguy cơ thay đổi cấu trúc vật lý, không phù hợp với mục tiêu tuyến tĩnh.

---

## 6. Trade-offs (Sự đánh đổi)

| Chiều | Lựa chọn A | Lựa chọn B | Trạng thái |
|---|---|---|---|
| Tính đơn giản ↔ Khả năng tổng quát | Regex đơn giản dễ debug | Nhiều lớp tín hiệu đa năng hơn | Đang dùng B một phần |
| Độ chính xác ↔ Độ linh hoạt | Rule chặt → bỏ sót format mới | Rule rộng → tăng FP | Cân bằng bằng Pattern Registry |
| Plain Text ↔ Metadata | Chỉ dùng text → tổng quát hơn | Dùng Style → chính xác hơn trong DOCX | Dùng cả, ưu tiên text |
| Single-pass ↔ Context-aware | Đơn giản, 1 lần đọc | Giảm ambiguity, phức tạp hơn | **Chưa chốt — cần benchmark** |
| Hierarchical ID ↔ UUID | Human-readable, dễ debug | Unique tuyệt đối, stable | Đang dùng Hierarchical (v1 tạm thời) |
| Direct text ↔ Full text | Không duplicate, nhỏ gọn | LLM context đầy đủ hơn | Đang dùng Direct |

---

## 7. Current Limitations (Hạn chế Bản chất)

### 🧊 KL-01: CLAUSE Detection trong Plain Text = 0%

**Nguồn**: Prototype C — `luat_ch3_output.txt` (249 dòng, 65KB)

| | DOCX (B) | TXT (C) | Delta |
|---|---|---|---|
| CHAPTER | 1 | 1 | 0 |
| SECTION | 5 | 5 | 0 |
| ARTICLE | 23 | 23 | 0 |
| **CLAUSE** | **185** | **0** | **−185** |
| POINT | 8 | 8 | 0 |

**Nguyên nhân gốc**: Cấu trúc Khoản trong DOCX dùng Word Auto-numbering (List style). Số thứ tự là metadata của paragraph, không phải ký tự text. Khi export sang TXT, metadata bị loại bỏ. Pattern `^\d+\.\s+` không có gì để match.

**Hệ quả downstream**:
- Parser TXT mode chỉ sinh ra 37 nodes thay vì 222
- 8 POINTs bị gán parent thẳng lên ARTICLE (implicit orphan)
- 7/8 ID Collision — xem KL-02

**Hướng giải quyết tiềm năng (chưa implement — Prototype C2)**:
1. Heuristic context: paragraph sau ARTICLE, không phải marker Điểm → coi là CLAUSE
2. Position-based: đếm vị trí paragraph từ Điều, indent level 1 là CLAUSE
3. Regex fallback: pattern nhận diện không phụ thuộc số thứ tự

### 🧊 KL-02: Hierarchical ID Collision khi mất CLAUSE layer

**Nguồn**: Prototype C — POINT node analysis  
**Evidence**: 8 POINTs → 1 Unique ID (`ldd-2024-txt_..._diem-d`). 7 collision.  
**Nguyên nhân**: Khi CLAUSE = 0, mọi POINT đều nhảy lên ARTICLE → ID path là `{article_id}_diem-d` → trùng nhau khi nhiều Điều cùng có Điểm `đ)`.  
**Ghi chú**: Đây là failure mode của Hierarchical ID khi tầng giữa bị thiếu. UUID hoặc Hybrid ID không bị failure này — là evidence thực nghiệm ủng hộ việc xem xét lại ID strategy.

### KL-03: implicit_parent logic bug trong TXT mode

**Evidence**: 8 POINTs trong TXT có parent = ARTICLE, nhưng `implicit_parent = False`.  
**Nguyên nhân**: Logic dùng chuỗi `"_khoan-" not in parent_id` — cần kiểm tra lại với TXT law_prefix.  
**Trạng thái**: Chưa fix, sẽ giải quyết khi hoàn thiện 2.4.

### KL-04: Lỗi ở Module 1 có thể làm Module 2 thất bại

Nếu Module 1 (chuẩn hóa) trích xuất text sai → Regex đúng cũng không match được. Prototype A đã cho thấy: kết quả CLAUSE = 0 phải kiểm tra representation DOCX trước khi kết luận pattern sai.

### KL-05: Chưa kiểm chứng trên corpus thứ hai

Mọi kết quả từ Prototype A/B/C đều có scope `[CORPUS: Ch3-LDD]`. Chưa có bằng chứng các pattern hoạt động tốt trên Luật Doanh Nghiệp, Nghị định, Thông tư.

---

## 8. Research Gaps (Khoảng trống Nghiên cứu)

Chưa đủ bằng chứng để tuyên bố Research Gap mạnh rằng "chưa ai làm Regex Parser cho luật Việt Nam". Điểm có thể nghiên cứu thực tế hơn:

> **Liệu có thể xây dựng một bộ parser cấu trúc pháp luật Việt Nam theo hướng pattern-driven + context-aware, có khả năng mở rộng dần qua nhiều corpus mà không cần thiết kế lại parser cho từng loại văn bản?**

Các điểm đáng nghiên cứu cụ thể:

1. **Chuẩn hóa format variants**: Cùng một cấu trúc Điều/Khoản/Điểm có bao nhiêu biến thể thực tế trong văn bản VN?
2. **Giảm FP của marker mơ hồ**: `1.`, `a)`, `Điều X` xuất hiện trong câu thường xuyên như thế nào? Ngữ cảnh nào đủ để phân biệt?
3. **Xử lý văn bản nhiều dòng**: Boundary detection cho node multi-paragraph — chưa có chuẩn nào rõ ràng.
4. **Tận dụng metadata khi có nhưng vẫn hoạt động khi metadata mất**: Prototype B/C đã cho thấy khoảng cách lớn khi mất Style.
5. **Pattern Registry theo corpus**: Cách tổ chức, mở rộng và đánh giá Pattern Registry chưa có precedent rõ ràng.
6. **Đánh giá khả năng khái quát hóa**: Metric nào phù hợp để đo "parser generalize tốt" trên nhiều loại văn bản pháp luật?

---

## 9. Open Research Questions (Câu hỏi Nghiên cứu Mở)

### Về Pattern

- Một loại cấu trúc nên có bao nhiêu pattern? Thêm pattern mới khi nào?
- Khi nào sửa pattern cũ thay vì thêm pattern mới?
- Làm thế nào phân biệt "biến thể format" với "cấu trúc hoàn toàn khác"?

### Về Khoản (câu hỏi quan trọng nhất chưa giải quyết)

- `1.` được phân biệt với danh sách thông thường bằng tín hiệu nào khi không có Style?
- Khoản có thể xuất hiện dưới những format nào? Có format `Khoản 1.` hay `(1)` không? `[HYPOTHESIS]`
- Có nên giới hạn tìm CLAUSE trong ARTICLE không? (Prototype B cho thấy strict scope gây bug)

### Về Điểm

- Bộ ký tự Điểm đầy đủ là gì? Hiện mới xác nhận: `đ)` (8 lần). Các ký tự `a) b) c) d) e)` — chưa verify Word Style.
- Có format `a.` hoặc `(a)` không? `[HYPOTHESIS]`
- Có trường hợp chữ `Điểm` viết hoa không? `[HYPOTHESIS]`

### Về Boundary

- Node kết thúc dựa trên marker cấp nào? (Khi gặp cùng cấp, hay khi gặp cấp trên?)
- `text` của ARTICLE có bao gồm children không? → Chưa chốt. Hiện tại: direct text only.
- Một node chứa cả direct text và children — hai phần này tách và lưu thế nào?

### Về Hierarchy

- Stack-based hay `current_*` state variables? Stack đang dùng — chưa benchmark với alternative.
- Khi chuyển POINT → CLAUSE, stack pop đúng cấp nào?
- Điều không có Khoản biểu diễn thế nào? → Cần scan đủ corpus.

### Về Node ID & Schema

- Hierarchical ID hay UUID hay Hybrid? → Evidence từ KL-02 ủng hộ xem xét lại.
- `position` tính theo thứ tự xuất hiện hay theo marker number? Khi có Gap (thiếu Khoản 2 nhưng có Khoản 3) thì sao?
- `char_start/end` dựa trên Clean Text hay raw source? Hiện dùng `start_idx/end_idx` (paragraph index), không phải character offset.

### Về khả năng tổng quát hóa

- Pattern nào chỉ đúng với Chương III? Pattern nào đã đúng trên nhiều corpus?
- Khi corpus mới có format mới, parser có thể mở rộng mà không phá pattern cũ không?
- Single-pass hay 2-pass có khả năng tổng quát tốt hơn?

---

## 10. Research TODO (Những vấn đề cần nghiên cứu thêm)

### Giai đoạn hiện tại — Hoàn thiện 2.2/2.3/2.4

**2.2 Boundary Detector**
- [ ] Verify: node nhiều dòng — `content_lines` có đủ không?
- [ ] Verify: `start_idx` và `end_idx` chính xác theo paragraph index
- [ ] Kiểm tra: ARTICLE boundary — text trực tiếp của Điều được bắt đúng chưa?
- [ ] Kiểm tra: `full_content` vs `body_text` — phân tách title / body có đúng không?
- [ ] Edge case: paragraph trống giữa 2 marker (empty paragraph DOCX)
- [ ] Edge case: marker xuất hiện ngay sau marker khác (không có content giữa)

**2.3 Hierarchy Builder** *(verify_23_24.py — 12/12 PASS)*
- [x] Verify stack logic: CHAPTER → SECTION → ARTICLE → CLAUSE → POINT đúng thứ tự
- [x] Verify chuyển cấp: POINT pop về CLAUSE → pop về ARTICLE (depth 4 → 2 trong 1 bước)
- [x] Verify position counting: siblings cùng parent có position 1, 2, 3... đúng
- [x] Edge case EC-1: ARTICLE không có CLAUSE — `children_count=0`, text body thẳng vào ARTICLE (1 trường hợp: Điều 47, có text, không có Khoản)
- [x] Edge case EC-2: ARTICLE không có body — 22 ARTICLE chỉ có title, `text=""` — đúng hành vi
- [x] Edge case EC-3: POINT thiếu CLAUSE cha — `implicit_parent=True` được gán đúng (DOCX: 0, TXT: 8/8)
- [x] `implicit_parent` logic hoạt động cả ở TXT mode — fix hoàn tất
- [x] Không tự tạo node giả (Virtual Clause) — confirm Clean

**2.4 Node Creator**
- [ ] Chốt schema v1.1: `id, type, depth, title, text, parent_id, children_count, position, number, law_prefix, law_code, source_doc, word_style, start_idx, end_idx, implicit_parent`
- [ ] Verify ID không collision trong DOCX mode (222 nodes — tất cả unique?)
- [ ] Fix: `implicit_parent` logic bug trong TXT mode (KL-03)
- [ ] Verify: `text = direct text` đúng cho tất cả node types
- [ ] Verify: `normalize_marker` — `đ` → `d` đã đúng, test với `ă`, `â`... nếu có
- [ ] Document: các field nào sẽ là input cho Module 3, 4, 5, 6

### Sau khi 2.2/2.3/2.4 ổn — Pipeline review

- [ ] Review toàn bộ pipeline DOCX mode trên Chương III
- [ ] Kiểm tra 2-pass strategy
- [ ] Tạo test cases cho false positive / false negative
- [ ] Đo FP/FN theo từng node type

### Prototype C2 — CLAUSE trong TXT (🧊 Frozen)

- [ ] Thử heuristic context-based CLAUSE detection
- [ ] So sánh FP/FN với Prototype B (DOCX baseline)
- [ ] Quyết định có cần Regex fallback riêng cho TXT không

### Corpus tiếp theo

- [ ] Chọn Corpus 2 (Luật Doanh Nghiệp hoặc Nghị định)
- [ ] So sánh Pattern Taxonomy với Corpus 1
- [ ] Tìm format mới, xác định pattern nào promote từ `[CORPUS]` thành `[GENERAL]`

---

## 11. Future Improvements (Hướng phát triển)

Các hướng có thể nghiên cứu sau khi pipeline cơ bản ổn định:

- **Pattern Registry mở rộng tự động**: Gợi ý pattern mới khi gặp format chưa từng thấy
- **Cơ chế lựa chọn pattern theo loại văn bản**: Luật khác Nghị định khác Thông tư
- **Parser đa tầng theo mức độ tin cậy**: Kết quả HIGH-confidence vs HYPOTHESIS riêng
- **Kết hợp metadata + text + context**: Multi-signal với trọng số động
- **Xử lý OCR noise**: Ký tự bị nhận dạng sai (Đ→D, ọ→o...)
- **Hỗ trợ Phụ lục và cấp cấu trúc đặc biệt**: Phụ lục không theo cấu trúc Điều/Khoản chuẩn
- **Mở rộng từ Luật sang Nghị định, Thông tư, Quyết định**

> Không nên coi các hướng này là yêu cầu của Prototype hiện tại.

---

## 12. Evolution (Lịch sử tiến hóa)

```
Prototype A (DOCX)                              ← DONE
  Pattern Registry v1, Regex Engine
  → 29 nodes: CHAPTER(1) / SECTION(5) / ARTICLE(23)
  → Failure F1: CLAUSE = 0
  → Failure F2: POINT = 0
     ↓
Prototype B (DOCX, fixed)                       ← DONE
  + required_style cho CLAUSE (List Paragraph)
  + scope tracking (match_paragraphs stateful)
  + ID fix: đ → d
  + Schema v1.1: children_count, law_prefix, implicit_parent
  → 222 nodes: CHAPTER(1)/SECTION(5)/ARTICLE(23)/CLAUSE(185)/POINT(8)
     ↓
Prototype C (plain TXT)                         ← DONE
  → 37 nodes: CLAUSE = 0% MISS, POINT = 100% OK
  → Phát hiện ID Collision (7/8 POINT trùng ID)
  → CLAUSE TXT frozen thành Known Limitation
     ↓
Hoàn thiện 2.2 / 2.3 / 2.4                    ← ĐANG ĐÂY
     ↓
Pipeline review tổng thể
     ↓
Prototype C2 (TXT + CLAUSE fallback)
     ↓
Corpus 2 (Luật Doanh Nghiệp hoặc Nghị định)
     ↓
Cross-corpus Pattern Generalization
```

**Dự kiến lịch sử version parser**:

| Version | Đặc điểm | Trạng thái |
|---|---|---|
| V1 | Pattern cơ bản + Boundary | Prototype B ✅ |
| V2 | Pattern Registry + Context-aware Hierarchy | Đang làm |
| V3 | Multi-signal (Style + Text + Context) | Sau khi có đủ evidence |
| V4 | Cross-corpus Generalized Parser | Sau Corpus 2+ |

---

## 13. References (Tài liệu tham khảo)

**Bắt buộc đọc trước khi viết pattern**:
- [ ] **Nghị định 34/2016/NĐ-CP** — Quy định chi tiết về định dạng văn bản quy phạm pháp luật VN
- [ ] **TCVN 9245** — Tiêu chuẩn soạn thảo văn bản hành chính
- [ ] `python-docx` paragraph model documentation — hiểu paragraph/style structure đầy đủ

**Cần đọc để mở rộng parser**:
- [ ] Python `underthesea` — Vietnamese tokenizer
- [ ] Python `pyvi` — Vietnamese NLP
- [ ] Paper: *Parsing Legal Documents* — Stanford Legal NLP Group
- [ ] Tài liệu về parser / grammar / hierarchical document parsing

**Để nghiên cứu Research Gap**:
- [ ] Các nghiên cứu legal NLP có đề cập document structure parsing
- [ ] Các chuẩn hoặc ontology pháp lý (LKIF, Akoma Ntoso...) — hiểu cách cộng đồng quốc tế giải quyết bài toán tương tự

> Chỉ đưa tài liệu cụ thể vào References sau khi đã kiểm tra nguồn và xác định thực sự liên quan.

---

## 14. Defense Questions & Technical Answers (Câu hỏi phản biện)

**Regex có xử lý được tất cả văn bản pháp luật Việt Nam không?**  
Không nên khẳng định. Regex xử lý tốt các cấu trúc có tính quy luật, nhưng khả năng tổng quát cần kiểm chứng trên nhiều corpus. Prototype C đã chứng minh ngay cùng một corpus, khi mất Style thì CLAUSE = 0%.

**Tại sao không dùng LLM ngay từ đầu?**  
Module 2 khôi phục cấu trúc vật lý — rule-based parsing có ưu thế về tính xác định, chi phí và khả năng kiểm soát. LLM có thể tốn kém và không tái lập được cho bài toán có quy luật rõ ràng này.

**Nếu Regex gặp format mới thì sao?**  
Parser không coi đó là lỗi thiết kế. Format mới được ghi nhận, phân loại `[HYPOTHESIS]`, kiểm chứng trên corpus thực, sau đó thêm vào Pattern Registry. Pattern cũ không bị phá vỡ.

**Tại sao không dùng Word Style làm chính?**  
Vì không phải mọi input đều có metadata định dạng. PDF/TXT chỉ còn text. Style giữa các DOCX từ nguồn khác nhau có thể không nhất quán. Prototype C là bằng chứng thực nghiệm.

**Làm sao biết là Khoản nếu không có số `1.`?**  
Không thể chỉ dựa vào `1.`. Cần kết hợp vị trí (đầu paragraph sau ARTICLE), Style (List Paragraph), ngữ cảnh (cấp hiện tại là ARTICLE), và sequence (số tăng dần). Đây là câu hỏi chưa có câu trả lời hoàn chỉnh — là Research TODO cho Prototype C2.

**Module 2 có xử lý Cross-reference không?**  
Không. Module 2 chỉ cần **tránh nhầm** Cross-reference với structural marker. Ví dụ: `"Điều 37"` trong câu `"tại khoản 1 Điều 37 của Luật này"` không được xem là boundary. Cách hiện tại: anchor đầu dòng. Việc hiểu quan hệ dẫn chiếu thuộc Module 5–7.

**Vì sao phải tách Regex và Boundary Detector?**  
Regex trả lời "Node bắt đầu ở đâu?". Boundary Detector trả lời "Node kết thúc ở đâu?". Hai bài toán khác nhau, đặc biệt khi nội dung kéo dài nhiều dòng. Nếu ghép, sẽ không tái sử dụng được Regex Engine độc lập.

**Làm thế nào chứng minh parser có tính tổng quát?**  
Không dựa vào một corpus. Cần mở rộng corpus và đo Precision, Recall, F1, FP, FN theo từng loại Node. Hiện tại chỉ có số đếm node (DOCX: 222, TXT: 37) — chưa có ground truth để tính F1 thực sự.

**Tại sao không tạo Clause ảo khi POINT thiếu parent?**  
Parser quan sát thực tế và gắn flag (`implicit_parent=true`). Validation (Module 3) quyết định mức độ lỗi. Physical Graph (Module 4) quyết định có dùng cạnh này không. Tạo Clause ảo là giả mạo cấu trúc — vi phạm nguyên tắc "Validation chỉ phát hiện, không tự sửa".

---

*Tổng hợp từ: thảo luận 2026-08-14, Prototype A/B/C experiments, Pattern Taxonomy v1*  
*Cập nhật lần cuối: 2026-08-14 — sau Prototype C*
