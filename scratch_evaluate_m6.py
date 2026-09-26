import json
from collections import Counter

file_path = r"d:\code\hybrid-parser-nckh\outputs\semantic_graphs\semantic_extraction.json"

with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

nodes = data.get("extracted_nodes", [])
print(f"Total Nodes Processed: {len(nodes)}")

total_entities = 0
total_relations = 0
entity_types = Counter()
relation_types = Counter()
nodes_with_extraction = 0
grounded_entities = 0

for node in nodes:
    ext = node.get("extraction", {})
    ents = ext.get("entities", [])
    rels = ext.get("relations", [])
    
    if ents or rels:
        nodes_with_extraction += 1
        
    total_entities += len(ents)
    total_relations += len(rels)
    
    for e in ents:
        entity_types[e.get("entity_type", "UNKNOWN")] += 1
        if e.get("evidence"):
            grounded_entities += 1
            
    for r in rels:
        relation_types[r.get("relation_type", "UNKNOWN")] += 1

print(f"Nodes with extraction: {nodes_with_extraction}")
print(f"Total Entities: {total_entities}")
print(f"Total Relations: {total_relations}")
print(f"Grounded Entities: {grounded_entities}")
print(f"Grounding Ratio: {grounded_entities / total_entities * 100:.2f}%" if total_entities > 0 else "0%")
print("\nEntity Types:")
for k, v in entity_types.most_common():
    print(f"  {k}: {v}")
print("\nRelation Types:")
for k, v in relation_types.most_common():
    print(f"  {k}: {v}")
