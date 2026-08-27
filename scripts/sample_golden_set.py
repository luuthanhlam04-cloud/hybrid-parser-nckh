import json
import random
import csv
import os

INPUT_GRAPH = "outputs/physical_graphs/physical_graph.json"
OUTPUT_CSV = "outputs/golden_set_annotation.csv"
SAMPLE_SIZE = 50

def main():
    if not os.path.exists(INPUT_GRAPH):
        print(f"Error: Not found {INPUT_GRAPH}")
        return
        
    with open(INPUT_GRAPH, "r", encoding="utf-8") as f:
        graph = json.load(f)
        
    nodes = graph.get("nodes", [])
    
    # Lọc bỏ CHAPTER và SECTION (vì default là RULE_ONLY, không cần annotate)
    eval_nodes = [
        n for n in nodes 
        if "CHAPTER" not in n.get("labels", []) and "SECTION" not in n.get("labels", [])
    ]
    
    # Random sample 50 nodes
    # Cố định random seed để mỗi lần chạy ra cùng kết quả (reproducibility)
    random.seed(42)
    sampled = random.sample(eval_nodes, min(SAMPLE_SIZE, len(eval_nodes)))
    
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    
    with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["node_id", "text", "is_semantic", "note"])
        
        for n in sampled:
            node_id = n["id"]
            text = n.get("properties", {}).get("text", "")
            writer.writerow([node_id, text, "", ""])
            
    print(f"Đã tạo file {OUTPUT_CSV} với {len(sampled)} nodes để dán nhãn.")

if __name__ == "__main__":
    main()
