import json
from collections import Counter

with open("outputs/unified_graphs/unified_knowledge_graph.json", "r", encoding="utf-8") as f:
    data = json.load(f)

edges = data.get("edges", [])
nodes = {n["id"]: n for n in data.get("nodes", [])}

edge_types = Counter([e["type"] for e in edges])
print("Edge types count:", edge_types)

mentions_edges = [e for e in edges if e["type"] == "MENTIONS"]
print(f"Total MENTIONS edges: {len(mentions_edges)}")

if mentions_edges:
    sample_edge = mentions_edges[0]
    source_id = sample_edge["source"]
    target_id = sample_edge["target"]
    source_node = nodes.get(source_id)
    target_node = nodes.get(target_id)
    print("Sample MENTIONS edge:")
    print(f"  Source: {source_id} (Labels: {source_node.get('labels')})")
    print(f"  Target: {target_id} (Labels: {target_node.get('labels')})")

norm_edges = [e for e in edges if e["source"].endswith("#NORM") or e["target"].endswith("#NORM") or "NORM" in nodes.get(e["source"], {}).get("labels", []) or "NORM" in nodes.get(e["target"], {}).get("labels", [])]
print(f"Sample edges connected to Norms (first 3):")
for e in norm_edges[:3]:
    s = nodes.get(e["source"])
    t = nodes.get(e["target"])
    print(f"  {e['source']} ({s.get('labels')}) -[{e['type']}]-> {e['target']} ({t.get('labels')})")
