"""
investigate_bugs.py - Điều tra nguyên nhân chênh lệch M5 vs Benchmark
"""
import json
import csv
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# ---- Load physical graph ----
with open('outputs/physical_graphs/physical_graph.json', 'r', encoding='utf-8') as f:
    graph = json.load(f)

graph_nodes = {}
for n in graph.get('nodes', []):
    graph_nodes[n['id']] = n

# ---- Load CSV benchmark v2 ----
csv_rows = {}
with open('../full_golden_set_annotation_v2.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        csv_rows[row['Node_id'].strip()] = row

# ---- Bug 1: Nodes with empty text in physical_graph ----
print("=" * 70)
print("BUG 1: NODES HAVE TEXT IN CSV BUT EMPTY IN PHYSICAL_GRAPH")
print("=" * 70)
empty_with_csv_text = []
for nid, row in csv_rows.items():
    csv_text = row.get('Text', '').strip()
    node = graph_nodes.get(nid)
    if node is None:
        live_text = None
    else:
        live_text = node.get('properties', {}).get('text', '').strip()
    
    if csv_text and len(csv_text) > 5 and not csv_text.isupper() and 'dieu' in nid:
        if live_text is not None and len(live_text) <= 5:
            empty_with_csv_text.append({
                'node_id': nid,
                'csv_text': csv_text[:80],
                'live_text': live_text,
                'label': row.get('is_semantic_human', '?')
            })

print(f"Total: {len(empty_with_csv_text)}")
for item in empty_with_csv_text:
    print(f"\n  Node: {item['node_id']}")
    print(f"  Label: {item['label']}")
    print(f"  CSV Text: {item['csv_text']}")
    print(f"  Live Text: {repr(item['live_text'])}")

# ---- Bug 2: Regex score mismatch ----
print("\n" + "=" * 70)
print("BUG 2: REGEX SCORE MISMATCH")
print("=" * 70)

from src.semantic_router.routing_engine import RoutingEngine
routing = RoutingEngine()

regex_diffs = []
for nid, row in csv_rows.items():
    csv_text = row.get('Text', '').strip()
    label = row.get('is_semantic_human', '').strip()
    if label not in ['0', '1']: continue
    if csv_text.isupper() or len(csv_text) <= 5: continue
    if 'dieu' not in nid: continue

    csv_regex = float(row.get('EXP-A(Regex)', 0.0))
    node = graph_nodes.get(nid)
    live_text = node.get('properties', {}).get('text', '').strip() if node else ''
    live_regex, category = routing.evaluate_regex(live_text)
    
    if abs(csv_regex - live_regex) > 0.01:
        regex_diffs.append({
            'node_id': nid,
            'label': label,
            'csv_regex': csv_regex,
            'live_regex': live_regex,
            'category': category,
        })

print(f"Total: {len(regex_diffs)}")
for item in regex_diffs:
    print(f"  {item['node_id']}: label={item['label']}, csv={item['csv_regex']} -> live={item['live_regex']} ({item['category']})")

# ---- Bug 3: Extra nodes not in benchmark ----
print("\n" + "=" * 70)
print("BUG 3: EXTRA NODES IN PHYSICAL_GRAPH NOT IN BENCHMARK CSV")
print("=" * 70)

benchmark_ids = set(csv_rows.keys())
all_graph_ids = set(n['id'] for n in graph.get('nodes', []))
extra_in_graph = all_graph_ids - benchmark_ids

out_file = open('scratch/investigate_extra_nodes.txt', 'w', encoding='utf-8')
out_file.write(f"Total extra nodes: {len(extra_in_graph)}\n")
for nid in sorted(extra_in_graph):
    node = graph_nodes.get(nid, {})
    text = node.get('properties', {}).get('text', '').strip()
    labels = node.get('labels', [])
    regex_s, cat = routing.evaluate_regex(text)
    r = "CANDIDATE" if regex_s >= 0.85 else "reject"
    out_file.write(f"  {nid}: labels={labels}, regex={regex_s}({cat}) -> {r}, text={repr(text[:80])}\n")
out_file.close()
print("Written to scratch/investigate_extra_nodes.txt")
