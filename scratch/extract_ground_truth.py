import json
import sys, io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load merged output
OUTPUT_FILE = Path(r"c:\Users\luuth\NCKH\hybrid_parser_graphrag\output_module2_merged.json")
with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
    nodes = json.load(f)

print("# Ground Truth Verification Samples\n")
id_map = {n['id']: n for n in nodes}

# ---------------------------------------------------------
# Nhóm 1 & 4 — bình thường + boundary: Điều 28 Khoản 1
# ---------------------------------------------------------
print("## Nhóm 1 & 4: Bình thường và Boundary (Điều 28 Khoản 1)\n")
d28_k1 = next((n for n in nodes if n['id'] == 'ldd-2024_chuong-iii_muc-1_dieu-28_khoan-1'), None)
if d28_k1:
    print(f"**Khoản 1 Điều 28** (Start: {d28_k1.get('start_idx')}, End: {d28_k1.get('end_idx')})")
    print(f"> {d28_k1['text'][:100]}...\n")
    
    points_d28_k1 = [n for n in nodes if n.get('parent_id') == d28_k1['id'] and n['type'] == 'POINT']
    print(f"Có {len(points_d28_k1)} Điểm con:")
    for p in points_d28_k1:
        text = p['text'].replace('\n', ' ')
        print(f"- Điểm {p['marker']}) (Start: {p.get('start_idx')}, End: {p.get('end_idx')}): {text[:60]}...")
        # Check multiline
        if (p.get('end_idx') or 0) - (p.get('start_idx') or 0) > 1:
            print(f"  --> [MULTILINE POINT] kéo dài từ đoạn {p.get('start_idx')} đến {p.get('end_idx') - 1}")
print("\n")

# ---------------------------------------------------------
# Nhóm 2 — Gap (position != number)
# ---------------------------------------------------------
print("## Nhóm 2: Gap (position != number)\n")
gap_clauses = [n for n in nodes if n['type'] == 'CLAUSE' and n.get('position') != n.get('number')]
print(f"Tìm thấy {len(gap_clauses)} Khoản có gap. Chọn mẫu:\n")
for c in gap_clauses[:3]:
    parent = id_map.get(c['parent_id'], {})
    print(f"- **{c['id']}** (Thuộc {parent.get('title', parent.get('id'))})")
    print(f"  + Position: {c.get('position')} | Number: {c.get('number')}")
    print(f"  + Text: {c['text'][:80]}...\n")

# ---------------------------------------------------------
# Nhóm 3 — Mixed representation (Point dùng Auto-numbering vs text cứng)
# ---------------------------------------------------------
print("## Nhóm 3: Mixed Representation (Auto-numbering vs Hardcoded)\n")
# Auto-numbering point: có thể dựa vào text ko chứa kí tự đ) ở đầu nhưng marker lại là 'đ', hoặc dựa vào word_style List Paragraph
auto_points = []
hard_points = []
for n in nodes:
    if n['type'] == 'POINT':
        text_start = n['text'][:5].lower()
        marker = n.get('marker', '')
        if f"{marker})" in text_start or f"{marker}." in text_start:
            hard_points.append(n)
        else:
            auto_points.append(n)

print(f"Tìm thấy {len(auto_points)} Điểm auto-numbering và {len(hard_points)} Điểm hardcoded (ước tính text).\n")
if auto_points:
    ap = auto_points[0]
    print(f"- **Mẫu Auto-numbering (Point {ap['marker']})**: {ap['id']}")
    print(f"  + Text gốc: '{ap['text'][:50]}...'")
    print(f"  + Word Style: {ap.get('word_style')}\n")
if hard_points:
    hp = next((p for p in hard_points if p.get('marker') == 'đ'), hard_points[0])
    print(f"- **Mẫu Hardcoded (Point {hp['marker']})**: {hp['id']}")
    print(f"  + Text gốc: '{hp['text'][:50]}...'")
    print(f"  + Word Style: {hp.get('word_style')}\n")

