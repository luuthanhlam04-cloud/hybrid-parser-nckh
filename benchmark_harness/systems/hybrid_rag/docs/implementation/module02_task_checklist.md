# MODULE 2 — Implementation Task Checklist

## Mục tiêu hiện tại
Hoàn thiện 2.2 Boundary Detector, 2.3 Hierarchy Builder, và 2.4 Node Creator.

## 2.2 Boundary Detector
- [ ] Verify: node nhiều dòng — `content_lines` có đủ không?
- [ ] Verify: `start_idx` và `end_idx` chính xác theo paragraph index
- [ ] Kiểm tra: ARTICLE boundary — text trực tiếp của Điều được bắt đúng chưa?
- [ ] Kiểm tra: `full_content` vs `body_text` — phân tách title / body có đúng không?
- [ ] Edge case: paragraph trống giữa 2 marker (empty paragraph DOCX)
- [ ] Edge case: marker xuất hiện ngay sau marker khác (không có content giữa)

## 2.3 Hierarchy Builder (Đã verify trên prototype 12/12 PASS)
- [x] Verify stack logic: CHAPTER → SECTION → ARTICLE → CLAUSE → POINT đúng thứ tự
- [x] Verify chuyển cấp: POINT pop về CLAUSE → pop về ARTICLE (depth 4 → 2 trong 1 bước)
- [x] Verify position counting: siblings cùng parent có position 1, 2, 3... đúng
- [x] Edge case EC-1: ARTICLE không có CLAUSE — `children_count=0`, text body thẳng vào ARTICLE (Điều 47)
- [x] Edge case EC-2: ARTICLE không có body — 22 ARTICLE chỉ có title, `text=""`
- [x] Edge case EC-3: POINT thiếu CLAUSE cha — `implicit_parent=True` được gán đúng (TXT: 8/8)
- [x] `implicit_parent` logic hoạt động cả ở TXT mode — fix hoàn tất
- [x] Không tự tạo node giả (Virtual Clause)

## 2.4 Node Creator
- [ ] Chốt schema v1.1: `id, type, depth, title, text, parent_id, children_count, position, number, law_prefix, law_code, source_doc, word_style, start_idx, end_idx, implicit_parent`
- [x] Verify ID không collision trong DOCX mode (222 nodes — unique)
- [x] Fix: `implicit_parent` logic bug trong TXT mode (KL-03)
- [ ] Verify ID path correctness / ancestor path consistency after current fix
- [ ] Verify: `text = direct text` đúng cho tất cả node types
- [ ] Verify: `normalize_marker` — `đ` → `d` đã đúng, test với `ă`, `â`... nếu có
- [ ] Document: các trường nào sẽ là input cho Module 3, 4, 5, 6

## Pipeline Review & Next Steps
- [ ] Review toàn bộ pipeline DOCX mode trên Chương III
- [ ] Kiểm tra 2-pass strategy
- [ ] Tạo test cases cho false positive / false negative
- [ ] Đo FP/FN theo từng node type
- [ ] Thử heuristic context-based CLAUSE detection cho TXT mode
- [ ] So sánh FP/FN với Prototype B (DOCX baseline)
- [ ] Chọn Corpus 2 (Luật Doanh Nghiệp hoặc Nghị định) để test cross-corpus.
