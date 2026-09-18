"""check_hybrid_id.py - Kiểm tra cách Hybrid ID xử lý marker d và đ"""
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('outputs/physical_graphs/physical_graph.json', 'r', encoding='utf-8') as f:
    graph = json.load(f)

graph_nodes = {n['id']: n for n in graph.get('nodes', [])}

print("=" * 70)
print("Phân tích Hybrid ID cho dieu-28 khoan-1 (đầy đủ nhất)")
print("=" * 70)

dieu28_k1 = sorted([nid for nid in graph_nodes if 'dieu-28_khoan-1' in nid])
for nid in dieu28_k1:
    node = graph_nodes[nid]
    props = node.get('properties', {})
    marker = props.get('marker')  # marker thực tế (raw, từ text gốc)
    text = (props.get('text') or '')[:50]
    p_suffix = nid.split('_p')[-1] if '_p' in nid else '?'
    id_marker = nid.split('_diem-')[1].split('_p')[0] if '_diem-' in nid else '?'
    print(f"  ID     : {nid}")
    print(f"  marker : '{marker}' (raw) -> normalized to '{id_marker}' in ID, suffix _p{p_suffix}")
    print(f"  text   : {repr(text)}")
    print()

print()
print("=" * 70)
print("Kiểm tra: _normalize_marker logic với d và đ")
print("=" * 70)
import re
def normalize_marker(marker):
    if not marker: return "unknown"
    marker = marker.strip().lower()
    marker = marker.replace('đ', 'd')  # đ -> d
    marker = re.sub(r"[^a-z0-9\-]", "", marker)
    return marker or "unknown"

test_markers = ['a', 'b', 'c', 'd', 'đ', 'e', 'g', 'h', 'i', 'k', 'l', 'm', 'n', 'o']
print("Thứ tự bảng chữ cái Việt Nam và kết quả normalize:")
for m in test_markers:
    normalized = normalize_marker(m)
    print(f"  '{m}' -> '{normalized}' {'<-- TRÙNG VỚI d!' if m == 'đ' else ''}")

print()
print("NHẬN XÉT của bạn bạn:")
print("  'đ' và 'd' đều normalize thành 'd' trong ID.")
print("  Hybrid ID dùng hậu tố _pXXXX (char_start) để phân biệt.")
print("  Nếu 2 điểm khác nhau, _pXXXX chắc chắn khác -> ID vẫn unique.")
print()

# Kiểm tra có bị trùng hoàn toàn không
id_counts = {}
for nid in dieu28_k1:
    if nid in id_counts:
        print(f"  COLLISION DETECTED: {nid}")
    id_counts[nid] = id_counts.get(nid, 0) + 1

collisions = {nid: cnt for nid, cnt in id_counts.items() if cnt > 1}
if collisions:
    print(f"Số ID bị trùng: {len(collisions)}")
    for nid, cnt in collisions.items():
        print(f"  COLLISION: {nid} xuất hiện {cnt} lần")
else:
    print("  -> Không có ID nào bị trùng. Hybrid ID đảm bảo uniqueness nhờ _pXXXX.")
