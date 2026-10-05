import json
import csv
from pathlib import Path

def classify_correction(audit_note: str) -> str:
    """Phân loại 4 nhóm CORRECTED dựa trên nội dung audit_note."""
    if not audit_note:
        return "UNKNOWN"
    audit_note = audit_note.lower()
    
    # Giả định phân loại logic (M7 v1.0)
    if "auto-corrected:" in audit_note:
        if "subtype=" in audit_note and "concept=" in audit_note:
            return "CONCEPT_MAP"
        return "NORMALIZE"
    return "INFER"

def export_audit_log(json_path: str, csv_path: str):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    records = []
    
    # 1. Quét LocalMentions
    for node in data.get("nodes", []):
        status = node.get("status", "VALID")
        if status in ["CORRECTED", "QUARANTINED", "UNRESOLVED"]:
            category = ""
            if status == "CORRECTED":
                category = classify_correction(node.get("audit_note", ""))
            elif status == "QUARANTINED":
                category = "ANTI_AUTO_CAST"
            else:
                category = "CONFLICT"
                
            records.append({
                "ID": node.get("id"),
                "Type": "LocalMention",
                "M6_Raw": node.get("raw_text"),
                "SemanticType": node.get("semantic_type"),
                "Status": status,
                "Category": category,
                "AuditNote": node.get("audit_note", ""),
                "RuleID": node.get("audit_note", "").split("]")[0].strip("[") if "]" in node.get("audit_note", "") else ""
            })
            
    # 2. Quét SemanticEdges
    for edge in data.get("edges", []):
        status = edge.get("status", "VALID")
        if status == "QUARANTINED":
            records.append({
                "ID": f"{edge.get('source_id')} --{edge.get('relation_type')}--> {edge.get('target_id')}",
                "Type": "SemanticEdge",
                "M6_Raw": "",
                "SemanticType": edge.get("relation_type"),
                "Status": status,
                "Category": "DOMAIN_RANGE_VIOLATION",
                "AuditNote": edge.get("rule_id", ""),
                "RuleID": edge.get("rule_id", "")
            })
            
    # Ghi ra CSV
    fieldnames = ["ID", "Type", "M6_Raw", "SemanticType", "Status", "Category", "AuditNote", "RuleID"]
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
        
    print(f"Exported {len(records)} audit records to {csv_path}")

if __name__ == "__main__":
    export_audit_log(
        "outputs/canonical_graphs/canonical_semantic_graph.json",
        "outputs/m7_audit_log.csv"
    )
