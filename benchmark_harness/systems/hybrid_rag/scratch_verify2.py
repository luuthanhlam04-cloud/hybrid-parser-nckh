import json, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('outputs/canonical_graphs/canonical_semantic_graph.json', encoding='utf-8') as f:
    data = json.load(f)

node = data['active_nodes'][1]
print('Sample node fields:', list(node.keys()))
print('type_hierarchy:', node.get('type_hierarchy'))
print('neo4j_labels:', node.get('neo4j_labels', 'ABSENT - OK'))

print(f'\nActive nodes: {len(data["active_nodes"])}')
print(f'Active edges: {len(data["active_edges"])}')
print(f'Norms: {len(data["norms"])}')

print('\n--- Sample type_hierarchy sau refactor ---')
nodes_with_subtype = [n for n in data['active_nodes'] if n.get('subtype')][:6]
for n in nodes_with_subtype:
    text = n['raw_text'][:30]
    sub = n['subtype']
    hier = n['type_hierarchy']
    print(f"text={text} | sub={sub} | hier={hier}")
