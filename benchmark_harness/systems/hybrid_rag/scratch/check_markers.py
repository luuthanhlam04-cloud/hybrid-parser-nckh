"""check_markers.py - Kiểm tra vụ đổi marker e->d sau bản fix M2"""
import json, csv, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('../full_golden_set_annotation_v2.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    csv_rows = {r['Node_id'].strip(): r for r in reader}

diem_e_in_csv = {nid for nid in csv_rows if 'diem-e' in nid}
print('IDs in CSV with diem-e:')
for nid in sorted(diem_e_in_csv):
    print(f'  {nid}')

with open('outputs/physical_graphs/physical_graph.json', 'r', encoding='utf-8') as f:
    graph = json.load(f)

graph_nodes = {n['id']: n for n in graph.get('nodes', [])}
benchmark_ids = set(csv_rows.keys())
all_graph_ids = set(n['id'] for n in graph.get('nodes', []))
extra_in_graph = sorted(all_graph_ids - benchmark_ids)

print('\n\nExtra nodes (in graph, NOT in CSV):')
for nid in extra_in_graph:
    node = graph_nodes[nid]
    props = node.get('properties', {})
    marker = props.get('marker')
    print(f'  {nid}: marker={marker}')

# Check dieu-28_khoan-1 full structure in graph
dieu28_k1 = sorted([nid for nid in all_graph_ids if 'dieu-28_khoan-1_diem' in nid])
print('\nAll diem nodes of dieu-28 khoan-1 in graph:')
for nid in dieu28_k1:
    node = graph_nodes[nid]
    props = node.get('properties', {})
    marker = props.get('marker')
    in_csv = nid in benchmark_ids
    print(f'  {nid}: marker={marker}, in_csv={in_csv}')

# Khớp từng node extra với CSV
print('\n\nID mapping (extra in graph -> expected CSV id by char_pos):')
for nid in extra_in_graph:
    # Extract pXXX from graph node id
    p_val = nid.split('_p')[-1] if '_p' in nid else '?'
    # Find matching in CSV by same char offset
    matches = [cid for cid in csv_rows if cid.endswith(f'_p{p_val}')]
    print(f'  GRAPH: {nid} -> CSV matches: {matches}')
