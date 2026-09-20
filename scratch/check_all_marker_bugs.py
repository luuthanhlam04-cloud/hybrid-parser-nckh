"""
check_all_marker_bugs.py - Kiểm tra toàn diện tất cả lỗi marker do DOCX metadata
trong physical_graph.json
"""
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('outputs/physical_graphs/physical_graph.json', 'r', encoding='utf-8') as f:
    graph = json.load(f)

graph_nodes = {n['id']: n for n in graph.get('nodes', [])}

# Bảng chữ cái điểm tiếng Việt đúng thứ tự
VN_ALPHA = ['a', 'b', 'c', 'd', 'đ', 'e', 'g', 'h', 'i', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'x', 'y']

def vn_order(marker):
    try:
        return VN_ALPHA.index(marker)
    except ValueError:
        return 999  # unknown marker

# Group nodes theo parent (khoản)
from collections import defaultdict
point_by_parent = defaultdict(list)
for nid, node in graph_nodes.items():
    labels = node.get('labels', [])
    if 'POINT' not in labels:
        continue
    props = node.get('properties', {})
    parent_id = props.get('parent_id') or 'NO_PARENT'
    raw_marker = props.get('marker')
    word_style = props.get('word_style') or ''
    point_by_parent[parent_id].append({
        'id': nid,
        'raw_marker': raw_marker,
        'order': vn_order(raw_marker) if raw_marker else 999,
        'text': (props.get('text') or '')[:60],
        'word_style': word_style,
    })

print("=" * 75)
print("KIỂM TRA TOÀN DIỆN MARKER BUG TRONG PHYSICAL_GRAPH")
print("=" * 75)

bug_categories = {
    'duplicate_marker': [],     # Trùng marker trong cùng khoản
    'out_of_order': [],         # Marker sai thứ tự
    'gap_in_sequence': [],      # Nhảy marker (a, c — thiếu b)
    'none_marker': [],          # Marker = None (ListParagraph fallback)
    'unknown_marker': [],       # Marker không thuộc VN_ALPHA
}

total_clauses = len(point_by_parent)
clauses_with_issues = set()

for parent_id in sorted(point_by_parent.keys()):
    points = sorted(point_by_parent[parent_id], key=lambda x: x['order'])
    markers = [p['raw_marker'] for p in points]

    issues = []

    # 1. Duplicate marker
    seen = {}
    for p in points:
        m = p['raw_marker']
        if m is not None:
            seen[m] = seen.get(m, 0) + 1
    dups = {m: c for m, c in seen.items() if c > 1}
    if dups:
        issues.append(('duplicate_marker', f"Trùng marker: {dups}"))
        bug_categories['duplicate_marker'].append(parent_id)

    # 2. None markers
    none_pts = [p for p in points if p['raw_marker'] is None]
    if none_pts:
        issues.append(('none_marker', f"{len(none_pts)} node có marker=None"))
        bug_categories['none_marker'].append(parent_id)

    # 3. Unknown markers
    unknown_pts = [p for p in points if p['raw_marker'] is not None and p['raw_marker'] not in VN_ALPHA]
    if unknown_pts:
        unk_markers = [p['raw_marker'] for p in unknown_pts]
        issues.append(('unknown_marker', f"Marker lạ: {unk_markers}"))
        bug_categories['unknown_marker'].append(parent_id)

    # 4. Out of order / gap detection (chỉ trên các node có marker hợp lệ)
    valid_pts = [p for p in points if p['raw_marker'] in VN_ALPHA]
    valid_markers = [p['raw_marker'] for p in valid_pts]
    if len(valid_markers) >= 2:
        expected_start = VN_ALPHA.index(valid_markers[0])
        for i, (current, next_m) in enumerate(zip(valid_markers, valid_markers[1:])):
            cur_idx = VN_ALPHA.index(current) if current in VN_ALPHA else -1
            next_idx = VN_ALPHA.index(next_m) if next_m in VN_ALPHA else -1
            if cur_idx >= 0 and next_idx >= 0:
                diff = next_idx - cur_idx
                if diff == 0:
                    pass  # duplicate đã check ở trên
                elif diff < 0:
                    issues.append(('out_of_order', f"Thứ tự ngược: '{current}' -> '{next_m}'"))
                    if parent_id not in bug_categories['out_of_order']:
                        bug_categories['out_of_order'].append(parent_id)
                elif diff > 1:
                    # Gap: bỏ qua marker giữa
                    missing = VN_ALPHA[cur_idx+1:next_idx]
                    issues.append(('gap_in_sequence', f"Bỏ qua marker {missing} giữa '{current}' và '{next_m}'"))
                    if parent_id not in bug_categories['gap_in_sequence']:
                        bug_categories['gap_in_sequence'].append(parent_id)

    if issues:
        clauses_with_issues.add(parent_id)
        print(f"\n[ISSUE] {parent_id}")
        print(f"  Markers: {markers}")
        for bug_type, desc in issues:
            print(f"  [{bug_type.upper()}] {desc}")
        # Chi tiết từng node
        for p in points:
            flag = ""
            m = p['raw_marker']
            if m is None:
                flag = " <-- NONE!"
            elif m not in VN_ALPHA:
                flag = f" <-- UNKNOWN!"
            elif markers.count(m) > 1:
                flag = f" <-- DUPLICATE!"
            print(f"    - {p['id']}: marker={repr(m)}{flag}")
            if flag:
                print(f"      text: {repr(p['text'])}")

# Tổng kết
print()
print("=" * 75)
print("TỔNG KẾT")
print("=" * 75)
print(f"Tổng số khoản có điểm (clauses with points): {total_clauses}")
print(f"Khoản bị lỗi marker: {len(clauses_with_issues)}")
print()
print("Phân loại lỗi:")
for category, affected in bug_categories.items():
    print(f"  [{category}]: {len(affected)} khoản")
    for pid in affected:
        print(f"    - {pid}")

# Đặc biệt: kiểm tra toàn bộ graph để tìm node có marker in VN_ALPHA
# nhưng ở vị trí sai so với position field
print()
print("=" * 75)
print("KIỂM TRA THÊM: Marker vs Position field")
print("(Nếu position=5 nhưng marker='a', đó là dấu hiệu bất thường)")
print("=" * 75)
position_vs_marker_issues = []
for parent_id in sorted(point_by_parent.keys()):
    points_sorted_by_pos = sorted(
        [p for p in point_by_parent[parent_id] if p['raw_marker'] is not None and p['raw_marker'] in VN_ALPHA],
        key=lambda x: x['order']
    )
    # Check: marker tại position 1 phải là 'a', position 2 là 'b', v.v.
    for i, p in enumerate(points_sorted_by_pos):
        expected_marker = VN_ALPHA[i] if i < len(VN_ALPHA) else '?'
        if p['raw_marker'] != expected_marker:
            position_vs_marker_issues.append({
                'parent': parent_id,
                'node_id': p['id'],
                'position_in_seq': i + 1,
                'expected_marker': expected_marker,
                'actual_marker': p['raw_marker'],
                'text': p['text']
            })

if position_vs_marker_issues:
    print(f"Tìm thấy {len(position_vs_marker_issues)} node có marker không khớp với vị trí trong chuỗi:")
    for issue in position_vs_marker_issues:
        print(f"  Position {issue['position_in_seq']} trong {issue['parent']}:")
        print(f"    Expected: '{issue['expected_marker']}', Actual: '{issue['actual_marker']}'")
        print(f"    Node: {issue['node_id']}")
        print(f"    Text: {repr(issue['text'])}")
else:
    print("Không phát hiện vấn đề marker vs position.")
