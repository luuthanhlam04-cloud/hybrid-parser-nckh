import json
import os

file_path = r"d:\code\hybrid-parser-nckh\outputs\semantic_graphs\semantic_extraction.json"

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    exit(1)

with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

nodes = data.get("extracted_nodes", [])

total_candidates = len(nodes)
total_entities = 0
total_relations = 0
schema_errors = 0
ontology_errors = 0
grounded_entities = 0

VALID_ENTITY_TYPES = {"SUBJECT", "ACTION", "OBJECT", "CONDITION", "EXCEPTION", "REFERENCE", "PENALTY", "PERMISSION", "OBLIGATION"}
VALID_RELATION_TYPES = {"ALLOW", "REQUIRE", "PROHIBIT", "HAS_OBJECT", "HAS_CONDITION", "HAS_EXCEPTION", "REFERENCE_TO", "HAS_PENALTY", "APPLY_TO"}

for node in nodes:
    ext = node.get("extraction", {})
    entities = ext.get("entities", [])
    relations = ext.get("relations", [])
    
    total_entities += len(entities)
    total_relations += len(relations)
    
    for e in entities:
        if "id" not in e or "text" not in e or "entity_type" not in e or "evidence" not in e:
            schema_errors += 1
            
        if e.get("entity_type") not in VALID_ENTITY_TYPES:
            ontology_errors += 1
            
        if e.get("evidence"):
            grounded_entities += 1
            
    for r in relations:
        if ("source" not in r and "source_id" not in r) or ("target" not in r and "target_id" not in r) or "relation_type" not in r or "evidence" not in r:
            schema_errors += 1
            
        if r.get("relation_type") not in VALID_RELATION_TYPES:
            ontology_errors += 1

print("--- EVALUATION RESULTS ---")
print(f"Total Candidates Processed: {total_candidates}")
print(f"Total Entities: {total_entities}")
print(f"Total Relations: {total_relations}")
print(f"Schema Errors: {schema_errors}")
print(f"Ontology Errors: {ontology_errors}")
print(f"Grounded Entities: {grounded_entities} ({grounded_entities/total_entities*100:.2f}% if total_entities > 0 else 0%)")
