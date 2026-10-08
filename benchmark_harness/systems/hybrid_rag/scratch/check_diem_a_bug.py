"""
check_diem_a_bug.py - Kiểm tra bug marker 'o' bị nhận thành 'a' trong Hybrid ID
và kiểm tra toàn bộ chuỗi điểm trong physical_graph
"""
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('outputs/physical_graphs/physical_graph.json', 'r', encoding='utf-8') as f:
    graph = json.load(f)

graph_nodes = {n['id']: n for n in graph.get('nodes', [])}

# Bảng chữ cái tiếng Việt (thứ tự điểm trong văn bản pháp luật)
VIET_ALPHA_ORDER = ['a', 'b', 'c', 'd', 'đ', 'e', 'g', 'h', 'i', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't']

def get_viet_order(marker):
    try:
        return VIET_ALPHA_ORDER.index(marker)
    except ValueError:
        return 999

print("=" * 70)
print("KIỂM TRA: Chuỗi marker điểm trong từng Khoản của đồ thị")
print("Phát hiện: đứt gãy, lặp, hoặc sai thứ tự")
print("=" * 70)

# Group nodes theo parent (khoản)
from collections import defaultdict
point_by_parent = defaultdict(list)
for nid, node in graph_nodes.items():
    if 'POINT' in node.get('labels', []):
        props = node.get('properties', {})
        parent_id = props.get('parent_id') or 'NO_PARENT'
        marker = props.get('marker')
        point_by_parent[parent_id].append({
            'id': nid,
            'marker': marker,
            'order': get_viet_order(marker) if marker else 999,
            'text': (props.get('text') or '')[:50]
        })

issues_found = False
for parent_id in sorted(point_by_parent.keys()):
    points = sorted(point_by_parent[parent_id], key=lambda x: x['order'])
    markers = [p['marker'] for p in points]

    # Kiểm tra marker 'a' xuất hiện nhiều hơn 1 lần trong cùng 1 khoản
    a_count = markers.count('a')
    d_count = markers.count('d')  # sau normalize cả d và đ đều thành d

    # Phát hiện chuỗi bất thường
    issues = []
    if a_count > 1:
        issues.append(f"DUPLICATE MARKER 'a': {a_count} lần")
    if d_count > 1:
        issues.append(f"DUPLICATE MARKER 'd' (có thể cả d và đ): {d_count} lần")
    
    # Kiểm tra thứ tự có đúng không
    orders = [p['order'] for p in points]
    for i in range(len(orders)-1):
        if orders[i] >= orders[i+1]:
            issues.append(f"SAI THỨ TỰ: '{markers[i]}' ({orders[i]}) -> '{markers[i+1]}' ({orders[i+1]})")
    
    # Kiểm tra marker None
    none_markers = [p for p in points if p['marker'] is None]
    if none_markers:
        issues.append(f"MARKER=None: {len(none_markers)} node")

    if issues:
        issues_found = True
        print(f"\n[ISSUE] {parent_id}")
        print(f"  Markers: {markers}")
        for issue in issues:
            print(f"  !! {issue}")
        for p in points:
            raw_marker = graph_nodes[p['id']].get('properties', {}).get('marker')
            print(f"  - {p['id']}: raw_marker={repr(raw_marker)}, text={repr(p['text'])}")

if not issues_found:
    print("Không phát hiện vấn đề gì về chuỗi marker!")

print()
print("=" * 70)
print("KIỂM TRA ĐẶC BIỆT: Node 'diem-a_p6776' trong dieu-28 khoan-1")
print("(Nghi ngờ là 'diem-o' bị nhận nhầm thành 'diem-a')")
print("=" * 70)
suspect = graph_nodes.get('doc_chuong-iii_muc-1_dieu-28_khoan-1_diem-a_p6776')
if suspect:
    props = suspect.get('properties', {})
    print(f"raw marker: {repr(props.get('marker'))}")
    print(f"text: {repr(props.get('text'))}")
    print(f"word_style: {repr(props.get('word_style'))}")
    print(f"start_idx: {props.get('start_idx')}")
    print(f"parent_id: {repr(props.get('parent_id'))}")
else:
    print("Không tìm thấy node này trong graph!")

print()
print("=" * 70)
print("KIỂM TRA: _normalize_marker với bộ ký tự đầy đủ")
print("=" * 70)
import re
def normalize_marker(marker):
    if not marker: return "unknown"
    marker = marker.strip().lower()
    marker = marker.replace('đ', 'd')
    marker = re.sub(r"[^a-z0-9\-]", "", marker)
    return marker or "unknown"

# Thử với o và a - có bị trùng nhau không?
test_cases = ['a', 'o', 'đ', 'd', 'k', 'l']
print("Kiểm tra các marker dễ gây nhầm lẫn:")
for m in test_cases:
    print(f"  '{m}' -> '{normalize_marker(m)}'")

print()
print("NOTE: Pattern regex bắt điểm: r\"^\\s*(?P<marker>[a-zđ])\\)\\s+(?P<text>.+)$\"")
print("Ký tự 'o' hoàn toàn hợp lệ trong [a-zđ]")
print("=> Nếu node có raw_marker='a' mà text là của điểm o, đó là lỗi parser đọc sai marker từ DOCX")
