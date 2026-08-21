# Phan tich Huong Trien Khai: 2.3 Hierarchy Builder va 2.4 Node Creator

> Pham vi: Module 2 - Regex Parser
> Sub-modules: 2.3 HierarchyBuilder + 2.4 NodeGenerator (NodeCreator)
> Trang thai Prototype A: Da implement - CLAUSE/POINT chua duoc bat (failure F1, F2)

---

## 1. BUC TRANH TONG THE

```
2.1 RegexEngine       -> "Day co phai marker khong?"
2.2 BoundaryDetector  -> "Node nay bat dau va ket thuc o dau?"
2.3 HierarchyBuilder  -> "Node nay thuoc ve node nao?" (Tree construction)
2.4 NodeGenerator     -> "Dong goi node thanh JSON schema." (Serialization)
```

2.3 va 2.4 la hai bai toan HOAN TOAN DOC LAP:
- 2.3 la bai toan THUAT TOAN (tree construction tu linear input)
- 2.4 la bai toan SCHEMA VA SERIALIZATION (data model design)

---

## 2. PHAN TICH 2.3 - HIERARCHY BUILDER

### 2.3.1 Van de cot loi

Input: danh sach phang (linear) cac Boundary theo thu tu xuat hien trong van ban.
Output: cay phan cap (tree) CHAPTER -> SECTION -> ARTICLE -> CLAUSE -> POINT.

Day la bai toan "reconstruct tree from preorder traversal" - co loi giai toi uu bang Stack O(n).

### 2.3.2 Danh gia Implementation hien tai

Implementation hien tai dung Stack-based:
  while stack and stack[-1].depth >= current_depth: stack.pop()
  parent = stack[-1] if stack else None
  stack.append(current_node)

Danh gia:
  - Correctness: DUNG cho preorder traversal cua van ban phap luat
  - Time: O(n) - moi node push/pop toi da 1 lan
  - Space: O(d) - d = do sau toi da (=4 trong Ch3-LDD)

### 2.3.3 Edge Cases can nghien cuu [CORPUS: Ch3-LDD]

EC-1: Dieu khong co Khoan (Article khong co Clause)
  Vi du: Dieu 29 co the chi co 2 khoan nhung van ban viet khong danh so
  Xu ly: Neu List Paragraph KHONG bat dau bang "\d+." thi la body cua ARTICLE,
         khong phai CLAUSE. BoundaryDetector da xu ly - HierarchyBuilder khong can can thiep.

EC-2: Khoan ngay sau tieu de Dieu, khong co noi dung truc tiep
  Vi du: Dieu 27. Quyen chuyen doi... -> ngay la Khoan 1, 2...
  Xu ly: title cua ARTICLE lay tu match, text = "". Hop ly, khong can sua.

EC-3: POINT xuat hien truoc khi co CLAUSE (Orphan Point)
  Truong hop: ARTICLE -> POINT (bo qua CLAUSE)
  [CHUA CHOT] Gan parent = ARTICLE truc tiep, danh dau "implicit_parent": true
  KHONG tu tao virtual CLAUSE - khong co evidence tu corpus.

EC-4: Depth skip (CHAPTER -> POINT, bo qua SECTION + ARTICLE + CLAUSE)
  Stack-based tu xu ly dung: parent = node cuoi trong stack co depth < current.

### 2.3.4 Quan he nguoc - Ancestor Chain

Yeu cau: Point -> Clause -> Article -> Section -> Chapter

Phuong an A - Lazy traversal (theo parent_id):
  def get_ancestors(node_id, node_map):
      chain = []
      current = node_map[node_id]
      while current.parent_id:
          parent = node_map[current.parent_id]
          chain.append(parent)
          current = parent
      return chain  # [CLAUSE, ARTICLE, SECTION, CHAPTER]
  Uu: Khong can luu them field. O(depth) moi lan goi.

Phuong an B - Materialized path (luu full path vao node):
  "ancestor_path": "ldd-2024_chuong-iii_muc-1_dieu-26_khoan-1"
  Uu: O(1) lookup. Nhuoc: Trung lap data.

[CHUA CHOT] Recommendation: Phuong an A - luu parent_id, de Module 4 tự traverse khi build graph.
Chi switch sang B neu Module 4 bao performance issue.

### 2.3.5 Van de Position Counting hien tai

position_counter dang dem theo parent_id (temp string).
Van de: Khi CLAUSE chua match (F1), Diem a/b/c/ cua cung Khoan se bi dem position
theo ARTICLE, khong theo CLAUSE. Can re-verify sau khi fix F1/F2.

---

## 3. PHAN TICH 2.4 - NODE CREATOR (NodeGenerator)

### 3.1 Ba trach nhiem doc lap

  1. ID Generation    -> sinh dinh danh duy nhat
  2. Text Extraction  -> xac dinh noi dung "text" cua node
  3. Schema Packaging -> dong goi tat ca fields thanh JSON object

### 3.2 ID Generation - Phan tich

Option 1: Hierarchical ID (dang dung)
  ldd-2024_chuong-iii_muc-1_dieu-26_khoan-1_diem-a
  Uu: Human-readable, debug de, cross-reference resolution tot
  Nhuoc: Conflict khi 2 luat co cung so Dieu, Khoan

Option 2: UUID4
  7f3a9c2e-4b1d-4e8f-a9c2-1d4e8fa9c21d
  Uu: Unique tuyet doi. Nhuoc: Opaque, kho trace.

Option 3: Hybrid (Recommended)
  {
    "id":    "7f3a9c2e-4b1d-4e8f-a9c2-1d4e8fa9c21d",   <- system key
    "label": "ldd-2024_chuong-iii_muc-1_dieu-26"       <- human label
  }

[CHUA CHOT] Can team thong nhat truoc khi downstream modules (M4, M5, M6) code query.

Van de cu the trong code hien tai:
  normalize_marker dung: re.sub(r"[^a-z0-9d\-]", "", marker)
  Ky tu 'd' (Unicode) se duoc giu lai -> "diem-d" trong ID.
  Khi dung lam Neo4j property key, 'd' co the gay loi.
  [CAN SUA] Transliterate 'd' -> 'd': d_map = {'d': 'd', 'D': 'D'}

### 3.3 Text Field - Quyet dinh quan trong nhat

Van de: "text" cua ARTICLE la gi?

Xet ARTICLE 26:
  Dieu 26. Quyen chung cua nguoi su dung dat   <- title
    1. Duoc cap Giay chung nhan...             <- CLAUSE 1
    2. Huong thanh qua lao dong...             <- CLAUSE 2
    ...

3 lua chon:
  A - Direct only: text = "" (khong co body truc tiep)
  B - Direct + title: text = "Quyen chung cua nguoi su dung dat"
  C - Full: text = "Quyen chung... 1. Duoc cap... 2. Huong..."

Anh huong downstream:
  Module 5 (Semantic Router): can text du nghia de tao vector embedding
  Module 6 (LLM): can text la input prompt - neu qua dai -> ton token
  Module 4 (Physical Graph): khong can text

[CHUA CHOT] Recommendation: text = direct text (title + inline body).
Module 4 tu build "full_text" khi can bang cach traverse children trong graph.
Tranh luu duplicate content trong JSON.

### 3.4 Schema v1.1 de xuat (bo sung so voi v1.0)

{
  "id":              "ldd-2024_chuong-iii_muc-1_dieu-26",
  "type":            "ARTICLE",
  "depth":           2,
  "title":           "Quyen chung cua nguoi su dung dat",
  "text":            "",
  "parent_id":       "ldd-2024_chuong-iii_muc-1",
  "children_count":  8,         <- MOI: Module 3 Validation can
  "position":        1,
  "number":          "26",
  "law_prefix":      "ldd-2024", <- MOI: cho Multi-doc Fusion M9
  "law_code":        "59/2024/QH15",
  "source_doc":      "Luat_dat_dai_chuong_3.docx",
  "word_style":      "Heading 2",
  "start_idx":       8,
  "end_idx":         17,
  "implicit_parent": false       <- MOI: danh dau EC-3 (Point khong co Clause cha)
}

---

## 4. FAILURE CASES CAN SUA (tu Prototype A)

F1: CLAUSE = 0
  Script debug:
    for p in paragraphs:
        if p.get("style") == "List Paragraph":
            result = engine.match_text(p["text"], word_style=p["style"])
            print(f"TEXT='{p['text'][:60]}' -> {result}")
  Hypothesis: List Paragraph bat dau bang ky tu khong phai digit, hoac khong co dau cham.

F2: POINT = 0
  Script debug:
    for p in paragraphs:
        if p.get("style") == "Body Text":
            result = engine.match_text(p["text"], word_style=p["style"])
            print(f"TEXT='{p['text'][:60]}' -> {result}")
  Hypothesis: paragraph text bi strip/transform truoc khi match, lam mat 'd)' o dau chuoi.

---

## 5. QUYET DINH CAN CHOT (theo thu tu uu tien)

1. [DO] "text" field policy: direct only vs. include title?       -> Anh huong M5, M6
2. [DO] ID strategy: hierarchical vs. UUID vs. hybrid?            -> Anh huong M4, M5, M6, M9
3. [SAU F1] Orphan POINT: gan truc tiep ARTICLE hay virtual CLAUSE? -> Anh huong M3, M4
4. [KHI M4] Ancestor lookup: lazy hay materialized path?          -> Anh huong M4
5. [MINOR] 'd' trong ID: giu hay transliterate -> 'd'?           -> Anh huong M4, Neo4j

---

## 6. NEXT ACTIONS

[ ] 1. Chay debug script F1: xem text thuc te cua List Paragraph
[ ] 2. Chay debug script F2: xem text thuc te cua Body Text
[ ] 3. Fix regex pattern -> target CLAUSE > 0, POINT > 0
[ ] 4. Quyet dinh text field policy -> update node_generator.py
[ ] 5. Quyet dinh ID strategy -> update node_generator.py
[ ] 6. Fix 'd' transliteration trong normalize_marker
[ ] 7. Them children_count, law_prefix, implicit_parent vao schema
[ ] 8. Re-run Prototype A -> verify CLAUSE + POINT duoc nhan dien
[ ] 9. Viet test cases cho HierarchyBuilder (EC-1, EC-2, EC-3, EC-4)
