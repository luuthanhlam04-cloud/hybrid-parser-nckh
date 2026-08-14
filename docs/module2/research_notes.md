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
| **2.3 Hierarchy Builder** | ✅ Prototype verified | Stack, position, edge cases | EC-1/EC-3 đúng. Children IDs có artifact nhỏ |
| **2.4 Node Creator** | ✅ Prototype verified / 🔄 Interface pending | implicit_parent TXT fix ✅ | POINT ID prefix artifact — cosmetic, ghi chú ở dưới |
| **Pipeline tổng thể** | ⏳ PENDING | — | Chỉ review sau khi 2.2–2.4 ổn |
| **Prototype C2 (TXT+CLAUSE)** | 🧊 FROZEN | CLAUSE TXT = 0% | Xem Mục 7 |
| **CLAUSE Detection v1 (DOCX+Numbering)** | 🔬 RESEARCH — đủ cơ sở chốt design | ilvl=0/decimal=CLAUSE, ilvl=1/lowerLetter=POINT | Xem Mục 3.5 |

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

### 3.3 Mô hình 4 tín hiệu `[DOCX mode — updated sau Numbering Investigation]`

Sau khi điều tra DOCX Numbering Metadata (xem 3.5), mô hình tín hiệu được cập nhật từ 3 lên 4:

```
              Legal Document (DOCX)
                   │
      ┌────────────┼────────────┬────────────┐
      │            │            │            │
  Word Style  Numbering    Text Pattern  Context
  (Heading 2, (ilvl, numFmt, (Điều \d+,  (parent node,
  List Para)  lvlText)      ^[a-zđ]\))   depth, sequence)
      │            │            │            │
      └────────────┴────────────┴────────────┘
                              ↓
                   Candidate Detection
                              ↓
                   Boundary Detection
                              ↓
                   Hierarchy Builder
                              ↓
                         Legal Node
```

**Ưu tiên tín hiệu theo độ tin cậy (DOCX)**:
- Tín hiệu mạnh nhất: `Style + Numbering (ilvl + numFmt)` — xác định CLAUSE/POINT mà không cần đọc text
- Tín hiệu trung bình: `Text Pattern` — xác định CHAPTER/SECTION/ARTICLE
- Tín hiệu bổ trợ: `Context` — giảm FP, validate candidate

**Với Plain Text (TXT/PDF)**:
- Không có Style và Numbering → chỉ còn Text Pattern + Context → xem KL-01

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
- `ilvl=0 + numFmt=decimal + lvlText=%1. + Style=List Paragraph` → **STRONGEST** `[CORPUS: Ch3-LDD]` — xác nhận từ Numbering Investigation (xem 3.5)
- `^\d+\.\s+` (Text Pattern fallback, chỉ dùng khi `current_node == ARTICLE`) → MEDIUM `[CORPUS: Ch3-LDD]`
- `required_style="List Paragraph"` (fallback cấp 2 khi không có số) → LOW — xem lưu ý về 20 separator paras ở 3.5
- `Khoản \d+.` → HYPOTHESIS
- Không dùng: `^\d+\.\s+[A-ZĐÁÀẢÃẠ]` — Khoản không bắt buộc bắt đầu bằng chữ hoa

**POINT**:
- `ilvl=1 + numFmt=lowerLetter + lvlText=%2) + Style=List Paragraph` → **STRONGEST** `[CORPUS: Ch3-LDD]` — xác nhận từ Numbering Investigation
- `[a-zđ]\)\s+` (Text Pattern) → MEDIUM · CONFIRMED: `đ)` xuất hiện 8 lần · Known FP: "Tiến **đ**ộ" (xem so sánh nội bộ Mục 8)
- Known FP: "điểm a" trong cross-reference câu

---

### 3.5 DOCX Numbering Metadata Investigation `[EVIDENCE — Ch3-LDD]`

**Bối cảnh**: Prototype B nhận diện CLAUSE qua `Style=List Paragraph` nhưng không tận dụng Numbering metadata của DOCX — dẫn đến `number` field phải lấy từ `paragraph.text` (dễ gây FP và không đọc được số ẩn). Phần này ghi lại kết quả điều tra XML metadata của DOCX để chốt hướng Clause Detection v1.

#### Câu hỏi 1: Numbering trong DOCX hoạt động như thế nào?

**Câu trả lời**: Word lưu numbering qua cơ chế 3 tầng:
```
numbering.xml
  └─ abstractNum (định nghĩa format: numFmt, lvlText, start)
        ↑ được tham chiếu bởi
  └─ num (instance — mỗi danh sách cụ thể có 1 numId)
        ↑ được gắn vào paragraph qua
  └─ numPr trong paragraph XML (chứa numId + ilvl)
```

**Hệ quả quan trọng**: Số `1.` `2.` `3.` mà ta thấy trên màn hình **không có trong `paragraph.text`** — chúng được Word tính và render từ `abstractNum.start + số lần xuất hiện trong numId group`. Do đó: Regex `^\d+\.\s+` không match được CLAUSE trong DOCX (match 0 lần trên corpus).

#### Câu hỏi 2: numId có phải là loại node không?

**Câu trả lời**: **Không.** numId chỉ là định danh của một danh sách Word cụ thể (mỗi lần tạo list mới → numId mới). Corpus Ch3-LDD có **41 numId khác nhau** nhưng chỉ có 2 loại node (CLAUSE/POINT). Để nhận diện loại node phải nhìn:
```
ilvl + numFmt + lvlText (từ abstractNum)
```
chứ không phải numId.

#### Câu hỏi 3: ilvl=0 và ilvl=1 encode cấu trúc gì?

**Câu trả lời — xác nhận từ data**:

| ilvl | numFmt | lvlText | Word render | → Node Type |
|:---:|---|---|---|---|
| `0` | `decimal` | `%1.` | `1.` `2.` `3.` | **CLAUSE** |
| `1` | `lowerLetter` | `%2)` | `a)` `b)` `c)` ... `đ)` | **POINT** |

**Lưu ý quan trọng**: `lowerLetter` trong tiếng Việt render được `đ)` vì Word dùng Vietnamese locale. Đây là tín hiệu **mạnh hơn Regex** vì nó encode ý định của người soạn thảo, không phải text thô.

#### Câu hỏi 4: 20 List Paragraph có numId=None là gì?

**Câu trả lời**: **Tất cả 20 đều là paragraph rỗng (`text=""`)**. Đây là các separator paragraph — dòng trống Word tạo ra khi người soạn thảo nhấn Enter trong list. Chúng **không phải Khoản** và phải bị bỏ qua (skip) khi parse.

> **Lưu ý thiết kế**: Việc xác nhận 20/20 `numId=None` là empty loại bỏ hoàn toàn phương án C ("danh sách không phải Clause") và A ("Khoản mất numbering") đã đặt ra trước điều tra. Chỉ cần rule đơn giản: `text.strip() == "" → skip`.

#### Câu hỏi 5: Có nên dùng position làm number không?

**Câu trả lời**: **Không.** `position` và `number` là hai khái niệm khác nhau có ý nghĩa khác nhau:

```
Khoản 1         → number=1, position=1
Khoản 3         → number=3, position=2  ← position≠number
```

- `position`: Vị trí tương đối trong danh sách anh em (sequential 1,2,3...)
- `number`: Số thứ tự theo văn bản gốc (có thể không liên tục nếu có lỗi soạn thảo)

Chênh lệch `position vs number` chính là dữ liệu để **Module 3 (Validation)** phát hiện gap ("có khả năng thiếu Khoản 2"). Nếu gán `position` làm `number`, Module 3 sẽ mù với loại lỗi này.

> **Ghi chú**: Với DOCX + Auto-numbering, `number` được tính từ `abstractNum.start + offset trong numId group` — **không cần đọc text**.

#### Kết luận và Clause Detection v1 (DOCX scope)

```
DOCX Paragraph
      ↓
┌─────────────────────────────┐
│ Signal 1: Style             │ List Paragraph
│ Signal 2: ilvl              │ 0 = CLAUSE, 1 = POINT
│ Signal 3: numFmt + lvlText  │ decimal/%1. hoặc lowerLetter/%2)
│ Signal 4: Context           │ paragraph nằm trong ARTICLE
└─────────────────────────────┘
      ↓
  Clause/Point Candidate
      ↓
  number = counted per numId group (từ abstractNum.start)
  position = sequential rank trong siblings
```

**Ưu tiên implement**:
- Mức 1 (DOCX + numbering): Style + ilvl + numFmt + Context → **tuyến chính**
- Mức 2 (DOCX + style, mất numbering): Style + Text Pattern + Context → fallback
- Mức 3 (Plain text): Text Pattern + Context → 🧊 Frozen (xem KL-01)

**Interface Module 1 → Module 2**: Module 1 cần pass thêm `numbering_id` (numId) và `numbering_level` (ilvl) cho mỗi paragraph. Module 2 diễn giải — không tự đọc XML.

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
| `implicit_parent=True` cho Orphan POINT (✅ fix xong — 8/8 đúng ở TXT mode) | Flag để Module 3 phát hiện. Không tự sửa cấu trúc |
| Hierarchical ID tạm thời | `ldd-2024_dieu-26_khoan-1`. Có điểm yếu khi multi-doc |
| `đ` → `d` trong ID | Tương thích với Neo4j property key |
| `position ≠ number` — phải giữ riêng hai field | `position`: thứ tự tương đối trong siblings (sequential). `number`: số theo văn bản gốc (có thể không liên tục). Module 3 dùng gap giữa chúng để phát hiện lỗi soạn thảo |
| numId không phải loại node | 41 numId khác nhau trong corpus nhưng chỉ có 2 loại (CLAUSE/POINT). Loại node xác định từ `ilvl + numFmt + lvlText` — không phải numId |
| CLAUSE detection ưu tiên Numbering Metadata (ilvl=0, decimal) thay vì Text Regex | Trong DOCX mode, tại corpus Ch3-LDD: Số `1.` `2.` `3.` không có trong `paragraph.text` — Word render từ metadata. Text Regex = fallback khi mất metadata |
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

**Nguyên nhân gốc** (đã làm rõ sau Numbering Investigation — xem 3.5): Cấu trúc Khoản trong DOCX dùng Word Auto-numbering. Số thứ tự (`1.` `2.` `3.`) là metadata trong `numbering.xml` — được Word render khi hiển thị, **không bao giờ xuất hiện trong `paragraph.text`**. Khi export sang TXT, metadata bị loại bỏ, `paragraph.text` chỉ chứa nội dung thuần túy. Pattern `^\d+\.\s+` không có gì để match vì số không nằm trong text.

**Hệ quả downstream**:
- Parser TXT mode chỉ sinh ra 37 nodes thay vì 222
- 8 POINTs bị gán parent thẳng lên ARTICLE (implicit orphan)
- KL-02: ID Collision do mất CLAUSE layer

**Lưu ý bổ sung từ Internal Comparison** (xem Mục 8): `code_minh` (implementation bạn cùng nhóm) cũng đối mặt với KL-01 trên cùng input plain text → CLAUSE = 0. Điều này xác nhận đây là bottleneck của input representation, không phải lỗi implementation cụ thể. Chưa đủ evidence để gọi là "research gap" — cần khảo sát literature.

**Hướng giải quyết** (cho DOCX scope hiện tại — đã có evidence từ 3.5):
1. Mức 1: `Style=List Paragraph + ilvl=0 + numFmt=decimal` → CLAUSE — **khả thi, đủ cơ sở**
2. Mức 2: `Style=List Paragraph + Text Pattern + context=ARTICLE` → fallback
3. Mức 3 (TXT): heuristic context / position-based → 🧊 Frozen (Prototype C2)

### 🧊 KL-02: Hierarchical ID Collision khi mất CLAUSE layer

**Nguồn**: Prototype C — POINT node analysis  
**Evidence**: 8 POINTs → 1 Unique ID (`ldd-2024-txt_..._diem-d`). 7 collision.  
**Nguyên nhân**: Khi CLAUSE = 0, mọi POINT đều nhảy lên ARTICLE → ID path là `{article_id}_diem-d` → trùng nhau khi nhiều Điều cùng có Điểm `đ)`.  
**Ghi chú**: Đây là failure mode của Hierarchical ID khi tầng giữa bị thiếu. UUID hoặc Hybrid ID không bị failure này — là evidence thực nghiệm ủng hộ việc xem xét lại ID strategy.

### KL-03: implicit_parent logic bug trong TXT mode

**Evidence**: 8 POINTs trong TXT có parent = ARTICLE, nhưng `implicit_parent = False`.  
**Nguyên nhân**: Logic dùng chuỗi `"_khoan-" not in parent_id` — cần kiểm tra lại với TXT law_prefix.  
**Trạng thái**: Resolved in current prototype: 8/8 orphan POINTs correctly flagged in TXT mode.

### KL-04: Lỗi ở Module 1 có thể làm Module 2 thất bại

Nếu Module 1 (chuẩn hóa) trích xuất text sai → Regex đúng cũng không match được. Prototype A đã cho thấy: kết quả CLAUSE = 0 phải kiểm tra representation DOCX trước khi kết luận pattern sai.

### KL-05: Chưa kiểm chứng trên corpus thứ hai

Mọi kết quả từ Prototype A/B/C đều có scope `[CORPUS: Ch3-LDD]`. Chưa có bằng chứng các pattern hoạt động tốt trên Luật Doanh Nghiệp, Nghị định, Thông tư.

---

## 8. Empirical Comparison (Đối chiếu Thực nghiệm nội bộ)

Để có cái nhìn khách quan về các chiến lược thiết kế (parsing strategies) khác nhau trên cùng một dạng biểu diễn đầu vào (Plain text [CORPUS: Ch3-LDD]), chúng tôi đã thực hiện một baseline comparison nội bộ giữa implementation của Minh (code_minh) và hybrid_parser.

Kết quả thu được như sau:

| Node Type | code_minh | hybrid_parser |
|---|:---:|:---:|
| CHAPTER | 1 | 1 |
| SECTION | 5 | 5 |
| ARTICLE | 23 | 23 |
| CLAUSE (Khoản) | 0 | 0 |
| POINT (Điểm) | 9 | 8 |
| TEXT (Noise) | 1 | 0 |

**Phân tích Trade-off và Lỗi hệ thống:**

1. **KL-01 là bottleneck của Input Representation**: Cả hai implementation đều trả về 0 CLAUSE. Điều này chứng minh KL-01 không phải là lỗi cá biệt của riêng implementation nào, mà là giới hạn cố hữu khi input mất hoàn toàn tín hiệu cấu trúc (Word Style).
2. **False Positive của POINT**: code_minh sinh ra 9 Điểm, trong đó có 1 Node dư (bắt nhầm chữ đ trong văn bản). Điều này cung cấp evidence thực chứng ủng hộ phương pháp **Regex + Context** của hybrid_parser (bắt chuẩn xác 8 Điểm) thay vì chỉ dùng Regex Pattern đơn giản.
3. **Bài toán định danh ID (ID Collision)**:
   - Kiến trúc code_minh sử dụng chuỗi ghép tĩnh (VD: rticle_37_point_đ), dẫn đến việc nếu một Điều có nhiều Điểm đ) thuộc các Khoản khác nhau, ID sẽ bị trùng (đã phát hiện 3 cặp trùng trong corpus hiện tại). Điều này có nguy cơ gây lỗi merge/override tùy thuộc vào logic Ingestion của Module 9.
   - Kiến trúc hybrid_parser sinh ID phân cấp đầy đủ (path mapping từ law -> chapter -> section -> article -> clause -> point). Path ID cung cấp khả năng debug và truy vết (traceability) tốt hơn hẳn. Prototype hiện tại đạt ID uniqueness 100% trên corpus Chương III được kiểm thử.

So sánh này không nhằm kết luận implementation nào tốt hơn, mà để làm rõ các lỗi, trade-off và giới hạn kỹ thuật của hai chiến lược parsing khác nhau.

### Quan sát từ 5 thách thức kỹ thuật của `code_minh` (nguồn: `tom_tat_module_2.md`)

Một số đã xuất hiện ở `hybrid_parser`, một số là edge case chưa được kiểm thử, một số có cách tiếp cận đáng tham khảo khi merge.

**1. Nhiều Điểm trên cùng 1 dòng (Multiple Points per Line)**
- *Thực trạng*: Văn bản luật có thể viết gộp `a) ...; b) ...; đ) ...` trên 1 dòng. Regex `^[a-zđ]\)\s+` chỉ bắt Điểm đầu tiên.
- *Giải pháp `code_minh`*: `re.finditer()` quét toàn bộ dòng, tính index toán học để cắt thành nhiều Node Điểm.
- *Đối chiếu `hybrid_parser`*: **Chưa có test case này trong corpus Ch3-LDD**. Cần thêm vào checklist 2.2 Boundary Detector.

**2. Đứt gãy nội dung Điểm nhiều đoạn (Point Continuation)**
- *Thực trạng*: Một Điểm trải nhiều đoạn văn — đoạn 2 dễ thành TEXT node mồ côi hoặc trỏ nhầm lên Khoản.
- *Giải pháp `code_minh`*: Thêm `POINT` vào Context Memory. BoundaryDetector giữ Node ở trạng thái `pending`, absorb các dòng tiếp theo đến khi gặp Marker mới.
- *Đối chiếu `hybrid_parser`*: `pending_chunk` đã có nhưng **chưa verify với multiline POINT**. Một trong các mục mở ở checklist 2.2.

**3. Chồng lấp vị trí ký tự (Position Overlap)**
- *Thực trạng*: `end` của Khoản 2 dễ đè lên `start` của Điểm a do độ trễ khi chốt node.
- *Giải pháp `code_minh`*: `flush_pending(end_index)` ép `position.end = line_start_idx` của dòng chứa node con tiếp theo.
- *Đối chiếu `hybrid_parser`*: `start_idx`/`end_idx` có trong schema v1.1 nhưng **chưa verify kỹ** (checklist 2.2 chưa hoàn thành). Kỹ thuật `flush_pending` là tham khảo tốt.

**4. Trùng lặp Title và Text**
- *Thực trạng*: Parser ban đầu đưa toàn bộ câu vào cả `title` và `text`.
- *Giải pháp `code_minh`*: Cắt marker (`"2."`, `"a)"`) làm `title`, slice phần còn lại làm `text`.
- *Đối chiếu `hybrid_parser`*: `text = direct text` (không gộp title) — đúng hướng. Nhưng semantics field `text` vs `title` **vẫn chưa chốt** (xem Mục 4).

**5. Sinh Node Rác (Empty Nodes)**
- *Thực trạng*: Ngắt dòng dư thừa tạo TEXT node chỉ chứa `\n`.
- *Giải pháp `code_minh`*: HierarchyBuilder lọc `chunk.type == TEXT và strip() == ""`.
- *Đối chiếu `hybrid_parser`*: 20 separator paragraphs (`numId=None, text=""`) được skip ở Regex Engine. Cần xác nhận TXT mode cũng lọc được.

---


## 9. Research Gaps (Khoảng trống Nghiên cứu)

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

## 10. Open Research Questions (Câu hỏi Nghiên cứu Mở)

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

## 11. Research TODO (Những vấn đề cần nghiên cứu thêm)

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
- [x] Verify ID không collision trong DOCX mode (222 nodes — tất cả unique?)
- [x] Fix: `implicit_parent` logic bug trong TXT mode (KL-03)
- [ ] Verify ID path correctness / ancestor path consistency after current fix
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

## 12. Future Improvements (Hướng phát triển)

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

## 13. Evolution (Lịch sử tiến hóa)

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

## 14. References (Tài liệu tham khảo)

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

## 15. Defense Questions & Technical Answers (Câu hỏi phản biện)

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

## 16. Kế hoạch Merge & Đàm phán Data Contract (M1 -> M2)

*Dựa trên kết quả thực nghiệm sinh JSON thực tế (ngày 2026-08-15).*

### 🛑 Vấn đề nghiêm trọng trước khi Merge
JSON output hiện tại của Module 2 (trên DOCX) cho thấy:
```json
"position": 1,
"number": null
```
**Bản chất vấn đề:** 
- `position` (thứ tự xuất hiện trong parent) khác với `number` (số thứ tự pháp lý thực tế). Ví dụ: Một Điều bị bãi bỏ Khoản 2, thì Khoản 3 sẽ có `position=2` nhưng `number=3`.
- Sự chênh lệch (`position != number`) chính là căn cứ duy nhất để Module 3 (Validation) phát hiện ra các Gap (lỗ hổng cấu trúc).
- Tuyệt đối **KHÔNG ĐƯỢC** giải quyết bằng cách gán `number = position` (vì sẽ phá hỏng dữ liệu).
- Nguyên nhân: Số của Khoản nằm trong metadata ẩn của DOCX. Module 1 của nhóm (code_minh) có trích xuất được số này nhưng lại render thẳng vào text thay vì giữ dưới dạng metadata độc lập. Giao tiếp hiện tại giữa Module 1 và 2 chưa đủ thông tin.

### 📝 Đề xuất Data Contract M1 -> M2 mới
Thay vì chỉ nhận text thuần, Module 2 cần Module 1 truyền cấu trúc `paragraph` với đầy đủ metadata chưa bị bóp méo:

```json
{
  "text": "Cá nhân được phép...",
  "word_style": "List Paragraph",
  "numbering_id": 25,
  "numbering_level": 0,
  "numbering_format": "decimal",
  "number": 1,
  "paragraph_index": 138
}
```

**Tại sao cần Contract này?**
- Cho phép Module 2 cross-validate: Kết hợp giữa `numbering metadata` + `context` + `text` thay vì tin vào một field duy nhất.
- Hỗ trợ giải quyết dứt điểm KL-01 (Mất Clause trong Plain Text) và hạn chế False Positive.

### ⚠️ Lưu ý giới hạn dữ liệu (Overfitting Risk)
Việc sử dụng `numbering_level = 0 -> CLAUSE` hay `numbering_level = 1 -> POINT` phải được gắn tag **[CORPUS: Ch3-LDD]**. Nó đúng tuyệt đối trên Chương III Luật Đất đai nhưng chưa được kiểm chứng quy luật trên các văn bản luật khác. Không nên biến nó thành quy tắc cứng (hard-coded) cho toàn hệ thống.

**Hành động tiếp theo:** Đóng băng Module 2. Ưu tiên đàm phán Data Contract với tác giả Module 1.

---

*Tổng hợp từ: thảo luận 2026-08-14 và 2026-08-15, Prototype A/B/C experiments, Pattern Taxonomy v1*  
*Cập nhật lần cuối: 2026-08-15 — chuẩn bị Merge Module 1*
