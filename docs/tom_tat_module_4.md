# Tổng kết Module 4 — Physical Graph Builder

Module 4 đóng vai trò là **cầu nối** giữa Physical Pipeline (M1→M2→M3) và Graph Database (Neo4j). Nhiệm vụ của module là nhận mảng node đã được kiểm định (`validated_nodes.json`) từ Module 3, chuyển đổi và lắp ráp thành một **Đồ thị Vật lý (Physical Graph)** hoàn chỉnh — bao gồm toàn bộ nodes và các cạnh có hướng — rồi xuất ra file `physical_graph.json` theo Graph Serialization Format chuẩn, sẵn sàng để nạp lên Neo4j ở Module tiếp theo.

## 1. Công nghệ và Nguyên tắc thiết kế

- **Ngôn ngữ & Thư viện:** Python 3, **stdlib only** — `json`, `pathlib`, `dataclasses`, `collections`, `logging`. Không có dependency ngoài hệ sinh thái Python.
- **Nguyên tắc:**
  - **Single Responsibility:** Mỗi file đảm nhận đúng một mối quan tâm: sinh cạnh (`edge_generator.py`), format và I/O (`json_exporter.py`), điều phối pipeline (`graph_builder.py`).
  - **100% Deterministic:** Cùng `validated_nodes.json` → cùng `physical_graph.json`. Thứ tự cạnh trong output cố định: BELONG_TO → NEXT → PREVIOUS.
  - **No External State:** Module không kết nối database, không gọi API. Chỉ đọc và ghi file trên filesystem.
  - **Stdlib-only:** Loại bỏ mọi nguy cơ dependency hell; module chạy được ngay trên bất kỳ môi trường Python 3.8+ nào.

## 2. Luồng dữ liệu (Data Flow)

```
validated_nodes.json (Module 3)
       │
       ▼
  ┌─────────────────────┐
  │  graph_builder.py   │  ← Main Orchestrator
  │  PhysicalGraphBuilder│
  └──────┬──────────────┘
         │
         ├──► edge_generator.py
         │      ├── generate_belong_to_edges()   → BELONG_TO edges
         │      └── generate_sequential_edges()  → NEXT + PREVIOUS edges
         │
         └──► json_exporter.py
                ├── node_to_graph_node()   → Graph Node format
                └── assemble() + export()  → physical_graph.json
```

## 3. Vai trò và Workflow của từng file

- **`edge_generator.py`**:
  - *Vai trò:* Trái tim thuật toán của module. Định nghĩa `Edge` dataclass và class `EdgeGenerator`.
  - *Workflow sinh BELONG_TO:* Duyệt từng node; nếu `parent_id != null` → tạo cạnh có hướng từ node con (`source`) lên node cha (`target`). Property `implicit` lấy trực tiếp từ trường `implicit_parent` của node — phản ánh đúng các trường hợp khuyết cha trực tiếp (đã được Module 2 đánh dấu và Module 3 xác nhận).
  - *Workflow sinh NEXT/PREVIOUS:* Nhóm tất cả non-root nodes theo khóa `(parent_id, type)`. Trong mỗi nhóm, **sắp xếp theo `start_idx` tăng dần** (tọa độ vật lý tuyệt đối trên tài liệu gốc, đảm bảo đúng reading flow). Với mỗi cặp liền kề `(curr, next)` → tạo cạnh `NEXT: curr → next` và cạnh `PREVIOUS: next → curr`.

- **`json_exporter.py`**:
  - *Vai trò:* Bộ chuyển đổi định dạng (Formatter) và I/O.
  - *Workflow:*
    1. `node_to_graph_node()`: Chuyển raw node dict thành Graph Node format. `labels = ["LegalNode", type]`. `properties` gom **TẤT CẢ fields** trừ `id`, `type`, `parent_id` — bao gồm cả `word_style`, `law_code`, `depth`, phục vụ metadata-filtering cho Module 10 (Retrieval) sau này.
    2. `assemble()`: Kết hợp nodes và edges, gắn `graph_metadata`.
    3. `export()`: Ghi file `physical_graph.json` với `ensure_ascii=False` (giữ nguyên Unicode tiếng Việt), `indent=2` (human-readable).

- **`graph_builder.py`** (Main Orchestrator):
  - *Vai trò:* Nhạc trưởng điều phối toàn bộ pipeline, cung cấp CLI entry point.
  - *Workflow:* `load()` → `EdgeGenerator.generate_all()` → `GraphExporter.assemble()` → `export()`. Log chi tiết từng bước (số nodes loaded, breakdown edges theo loại, tổng kết cuối).
  - *CLI:* `python -m src.physical_graph.graph_builder` — chạy trực tiếp từ project root, không cần tham số.

- **`__init__.py`**:
  - Export lazy các class public (`Edge`, `EdgeGenerator`, `GraphExporter`, `PhysicalGraphBuilder`) để tránh circular import khi chạy bằng `-m`.

## 4. Schema đầu ra (Graph Serialization Format)

```json
{
  "graph_metadata": {
    "total_nodes": 222,
    "total_edges": 551
  },
  "nodes": [
    {
      "id": "doc_chuong-iii_muc-1_dieu-26_p180",
      "labels": ["LegalNode", "ARTICLE"],
      "properties": {
        "depth": 2,
        "title": "Quyền chung của người sử dụng đất",
        "text": "",
        "children_count": 8,
        "position": 1,
        "number": "26",
        "marker": null,
        "law_prefix": "doc",
        "law_code": "59/2024/QH15",
        "source_doc": "Luat_dat_dai_chuong_3.docx",
        "word_style": "Heading2",
        "start_idx": 13,
        "end_idx": 14,
        "implicit_parent": false
      }
    }
  ],
  "edges": [
    {
      "source": "doc_chuong-iii_muc-1_dieu-26_khoan-1_p223",
      "target": "doc_chuong-iii_muc-1_dieu-26_p180",
      "type": "BELONG_TO",
      "properties": { "implicit": false }
    },
    {
      "source": "doc_chuong-iii_muc-1_dieu-26_khoan-1_p223",
      "target": "doc_chuong-iii_muc-1_dieu-26_khoan-2_p365",
      "type": "NEXT",
      "properties": {}
    }
  ]
}
```

**Quy tắc label:** `labels` luôn là mảng 2 phần tử `["LegalNode", NodeType]`. `NodeType` nhận 5 giá trị: `CHAPTER`, `SECTION`, `ARTICLE`, `CLAUSE`, `POINT`.

## 5. Thuật toán sinh cạnh — Chi tiết kỹ thuật

### A. BELONG_TO (Con → Cha)

| Trường | Ý nghĩa |
|---|---|
| `source` | `node.id` (node con) |
| `target` | `node.parent_id` (node cha) |
| `properties.implicit` | `node.implicit_parent` — `true` nếu node đã bị khuyết cha trực tiếp (được M2 đánh dấu) |

Điều kiện: Chỉ tạo khi `parent_id != null`. Root node (CHAPTER ở đây) không có cạnh BELONG_TO.

### B. NEXT / PREVIOUS (Sibling Ordering)

**Quyết định thiết kế quan trọng:**

> **Primary sort key: `start_idx`** (tọa độ vật lý tuyệt đối — vị trí đoạn văn bản gốc trong tài liệu).
>
> **Lý do bác bỏ `position`:** `position` là thứ tự logic pháp lý, có thể bị khuyết hoặc nhảy số trong văn bản có lỗi. `start_idx` là tọa độ vật lý bất biến — đảm bảo 100% cạnh NEXT/PREVIOUS phản ánh đúng luồng đọc (reading flow) từ trên xuống dưới của con người.

**Grouping key:** `(parent_id, type)` — đảm bảo chỉ nối các node **cùng cha, cùng loại**. Hai SECTION cùng cha tạo NEXT/PREVIOUS với nhau; CLAUSE và POINT dù cùng cha sẽ không bị nối chéo loại.

## 6. Kết quả chạy thực tế (Luật Đất Đai — Chương III)

```
=== PHYSICAL GRAPH BUILDER RESULTS ===
Input  : validated_nodes.json  (222 nodes — Module 3 output)
Output : physical_graph.json   (310 KB)

Edge breakdown:
  BELONG_TO : 221  (tất cả non-root nodes → parent)
  NEXT      : 165  (165 nhóm sibling liền kề)
  PREVIOUS  : 165  (đối xứng với NEXT)
  ─────────────────
  TOTAL     : 551

Runtime: < 1s (thuần Python, không có I/O nặng)
```

**Tỷ lệ edges/nodes = 551/222 ≈ 2.48x** — đây là mật độ cạnh hợp lý cho một cây phân cấp pháp luật 5 cấp với quan hệ sibling song hướng.

## 7. Kiểm thử (Test Coverage)

File `tests/unit/test_physical_graph.py` — **41 unit tests, 0 fail**.

| Test Class | Nội dung kiểm thử | Số tests |
|---|---|---|
| `TestEdgeDataclass` | `Edge.to_dict()` format | 2 |
| `TestNodeTransformation` | labels đúng, properties đầy đủ, 3 keys top-level bị loại | 8 |
| `TestBelongToEdges` | Root không có edge; hướng Con→Cha; `implicit` property | 7 |
| `TestNextPreviousEdges` | Sort bởi `start_idx`; group `(parent_id, type)`; properties rỗng | 9 |
| `TestGraphExporter` | Schema đầu ra: metadata, nodes, edges | 6 |
| `TestEndToEnd` | 5-node fixture → đếm chính xác 8 edges tổng | 9 |

**Fixture EndToEnd (5 nodes):**
```
ROOT (CHAPTER, parent=None, start_idx=0)
  ├── SECTION-1 (parent=ROOT, start_idx=1)  ─┐
  │     ├── CLAUSE-1 (start_idx=2)  ─┐        │  cùng group (ROOT, SECTION)
  │     └── CLAUSE-2 (start_idx=3)  ─┘        │
  └── SECTION-2 (parent=ROOT, start_idx=4)   ─┘

Expected: 4 BELONG_TO + 2 NEXT + 2 PREVIOUS = 8 edges
```

## 8. Quyết định Kiến trúc & Trade-offs

### A. Stdlib-only — Không dùng thư viện đồ thị

- **Lý do:** NetworkX hay igraph mang lại overhead không cần thiết. Module 4 chỉ cần tính toán tuyến tính trên list/dict — không cần traversal, path-finding hay graph algorithm phức tạp.
- **Kết quả:** Zero new dependency, runtime < 1s, dễ audit toàn bộ logic.

### B. Giữ TẤT CẢ metadata trong `properties`

- **Lý do:** Neo4j là Property Graph Database — node có nhiều property là bình thường và hiệu quả. Các trường như `word_style`, `law_code`, `depth`, `source_doc` sẽ trở thành metadata filter cực kỳ hữu ích cho Module 10 (Retrieval), ví dụ: "Tìm tất cả CLAUSE thuộc luật 59/2024/QH15 có depth=3".
- **Trade-off chấp nhận:** File JSON lớn hơn một chút (~310KB thay vì ~200KB nếu bỏ bớt field). Không đáng kể.

### C. `start_idx` là sole sort key — Bác bỏ `position`

- **Lý do:** Xem mục 5B. `position` phụ thuộc vào logic pháp lý có thể sai; `start_idx` là thực tế vật lý bất biến.
- **Trade-off:** Nếu một ngày nào đó xuất hiện văn bản có các node thuộc cùng nhóm nhưng `start_idx` trùng nhau (trường hợp lý thuyết), thứ tự trong nhóm đó sẽ không xác định. Hiện tại không gặp trường hợp này trên corpus Ch3-LDD.

### D. Lazy import trong `__init__.py`

- **Lý do:** Khi chạy `python -m src.physical_graph.graph_builder`, Python thực thi `__init__.py` trước rồi mới chạy `graph_builder.py`. Nếu `__init__.py` import `graph_builder` thẳng → `RuntimeWarning: found in sys.modules`. Lazy import thông qua `__getattr__` giải quyết hoàn toàn.

## 9. Vấn đề bỏ ngỏ (Open Issues & Next Steps)

1. **Module 5 (Neo4j Ingestion):** `physical_graph.json` đã sẵn sàng làm input. Cần map `type` của edge và `labels` của node sang Cypher `CREATE` / `MERGE` statements.

2. **Multi-document support:** Pipeline hiện tại xử lý 1 file DOCX → 1 `physical_graph.json`. Khi scale lên nhiều văn bản, cần:
   - Namespace hóa `law_prefix` để tránh ID collision cross-document.
   - Hoặc merge nhiều `physical_graph.json` trước khi nạp Neo4j.

3. **Cross-reference edges:** Khi text chứa "theo quy định tại Khoản 2 Điều này", đây là cạnh `REFERENCES` cần được giải quyết bởi một module Semantic khác. Module 4 **không** xử lý loại cạnh này.

4. **Benchmark thời gian:** Với corpus lớn hơn (nghị định 1000+ điều), cần đo lại runtime. Thuật toán O(n log n) (do sort) nên vẫn nhanh, nhưng cần profile nếu sinh > 10,000 edges.

## 10. Vị trí trong toàn bộ Physical Pipeline

```
M1 (Preprocessing)
   │  StructuredParagraph
   ▼
M2 (Regex Parser)
   │  raw_nodes.json  (222 nodes)
   ▼
M3 (Validation Engine)
   │  validated_nodes.json  (222 nodes, score=100%)
   ▼
M4 (Physical Graph Builder)  ← Đây
   │  physical_graph.json  (222 nodes, 551 edges)
   ▼
M5 (Neo4j Ingestion)  ← Tiếp theo
```

Module 4 khép lại **Physical Pipeline** — chuyển đổi hoàn toàn văn bản luật thô thành một đồ thị có cấu trúc rõ ràng, sẵn sàng cho các lớp Semantic và Retrieval ở phase sau.
