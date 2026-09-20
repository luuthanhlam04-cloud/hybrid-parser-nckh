import json
import sys
import io
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def validate_m6_output(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return

    nodes = data.get("extracted_nodes", [])
    print(f"Total nodes: {len(nodes)}")

    valid_entities = {"SUBJECT", "ACTION", "OBJECT", "CONDITION", "EXCEPTION", "REFERENCE", "PENALTY"}
    valid_relations = {"ALLOW", "PROHIBIT", "REQUIRE", "HAS_CONDITION", "HAS_EXCEPTION", "REFERENCE_TO", "HAS_OBJECT", "HAS_PENALTY"}

    domain_range = {
        "ALLOW": ({"SUBJECT"}, {"ACTION"}),
        "REQUIRE": ({"SUBJECT", "ACTION"}, {"ACTION"}),
        "PROHIBIT": ({"SUBJECT"}, {"ACTION"}),
        "HAS_CONDITION": ({"SUBJECT", "ACTION"}, {"CONDITION"}),
        "HAS_EXCEPTION": ({"ACTION", "CONDITION"}, {"EXCEPTION"}),
        "REFERENCE_TO": (None, {"REFERENCE"}),
        "HAS_OBJECT": ({"ACTION", "SUBJECT"}, {"OBJECT"}),
        "HAS_PENALTY": ({"ACTION"}, {"PENALTY"})
    }

    errors = []

    for i, node in enumerate(nodes):
        node_id = node.get("node_id")
        extraction = node.get("extraction", {})
        
        entities = extraction.get("entities", [])
        relations = extraction.get("relations", [])
        
        if not entities and not relations:
            continue
            
        entity_map = {e["id"]: e for e in entities}
        
        # Check entities
        for e in entities:
            if e.get("entity_type") not in valid_entities:
                errors.append(f"Node {node_id}: Invalid entity_type '{e.get('entity_type')}' in entity {e['id']}")
            if not e.get("evidence"):
                errors.append(f"Node {node_id}: Empty evidence in entity {e['id']}")
                
        # Check relations
        for r in relations:
            rel_type = r.get("relation_type")
            src_id = r.get("source")
            tgt_id = r.get("target")
            
            if rel_type not in valid_relations:
                errors.append(f"Node {node_id}: Invalid relation_type '{rel_type}'")
                continue
                
            src_entity = entity_map.get(src_id)
            tgt_entity = entity_map.get(tgt_id)
            
            if not src_entity or not tgt_entity:
                errors.append(f"Node {node_id}: Missing source or target entity in relation {rel_type}")
                continue
                
            src_type = src_entity["entity_type"]
            tgt_type = tgt_entity["entity_type"]
            
            allowed_domains, allowed_ranges = domain_range[rel_type]
            
            if allowed_domains and src_type not in allowed_domains:
                errors.append(f"Node {node_id}: Domain violation for {rel_type}. Source '{src_type}' not allowed.")
                
            if allowed_ranges and tgt_type not in allowed_ranges:
                errors.append(f"Node {node_id}: Range violation for {rel_type}. Target '{tgt_type}' not allowed.")

    if errors:
        print("CÁC LỖI PHÁT HIỆN ĐƯỢC BỞI LLM:")
        for err in errors:
            print(err)
    else:
        print("Tuyệt vời! Không phát hiện lỗi Domain/Range, EntityType, RelationType, hay Referential Integrity nào. LLM tuân thủ hợp đồng 100% về mặt cấu trúc.")
        
if __name__ == "__main__":
    validate_m6_output("outputs/semantic_graphs/semantic_extraction_test.json")
