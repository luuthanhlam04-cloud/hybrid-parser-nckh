import json, csv, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('outputs/candidate_nodes/routing_candidates.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
with open('../full_golden_set_annotation_v2.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    csv_rows = {r['Node_id'].strip(): r for r in reader}

live_nodes = {c['node_id']: c for c in data.get('candidates', [])}

benchmark_nodes = []
for nid, row in csv_rows.items():
    label = str(row.get('is_semantic_human', '')).strip()
    text = str(row.get('Text', '')).strip()
    if label not in ['0', '1']: continue
    if text.isupper() or len(text) <= 5: continue
    if 'dieu' not in nid: continue
    benchmark_nodes.append(nid)

missing = [nid for nid in benchmark_nodes if nid not in live_nodes]
print(f'Benchmark nodes total: {len(benchmark_nodes)}')
print(f'Missing from live M5 routing_candidates.json: {len(missing)}')
for m in missing:
    row = csv_rows[m]
    label = row['is_semantic_human']
    csv_regex = row['EXP-A(Regex)']
    print(f'  {m}: label={label}, csv_regex={csv_regex}')
