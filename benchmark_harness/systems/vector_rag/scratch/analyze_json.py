import json

with open('outputs/canonical_graphs/canonical_semantic_graph.json', encoding='utf-8') as f:
    d = json.load(f)

print('--- Metadata ---')
print(json.dumps(d['metadata'], indent=2, ensure_ascii=False))

print('\n--- 1 Active Node ---')
print(json.dumps(d['active_nodes'][0] if d['active_nodes'] else {}, indent=2, ensure_ascii=False))

print('\n--- 1 Norm ---')
print(json.dumps(d['norms'][0] if d['norms'] else {}, indent=2, ensure_ascii=False))

print('\n--- 1 Concept ---')
print(json.dumps(d['concepts'][0] if d['concepts'] else {}, indent=2, ensure_ascii=False))

print('\n--- 1 Edge ---')
print(json.dumps(d['active_edges'][0] if d['active_edges'] else {}, indent=2, ensure_ascii=False))

q = d.get('quarantine', {})
print('\n--- Quarantine Stats ---')
print(f"Mentions: {len(q.get('mentions', []))}")
print(f"Relations: {len(q.get('relations', []))}")
print(f"Edges: {len(q.get('edges', []))}")

print('\n--- Validation Report ---')
print(json.dumps(d['validation_report'], indent=2, ensure_ascii=False))
