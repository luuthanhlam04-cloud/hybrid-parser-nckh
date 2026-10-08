import json
import csv
import os

INPUT_GRAPH = "outputs/physical_graphs/physical_graph.json"
OUTPUT_CSV = "outputs/full_golden_set_annotation.csv"

# Các file dự đoán (để đưa thêm thông tin vào file excel cho dễ đối chiếu)
EXP_A = "outputs/candidate_nodes/routing_candidates_expA.json"
EXP_B = "outputs/candidate_nodes/routing_candidates_expB.json"
EXP_C = "outputs/candidate_nodes/routing_candidates_expC.json"

def load_predictions(json_path: str) -> dict:
    preds = {}
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for cand in data.get("candidates", []):
                preds[cand["node_id"]] = 1 if cand["route"] == "LLM_CANDIDATE" else 0
    return preds

def is_semantic(text: str) -> int:
    text_lower = text.lower()
    if not text.strip(): return 0
        
    keywords = [
        "trừ trường hợp", "ngoại trừ", "trừ khi",
        "theo quy định", "quy định tại", "quy định của pháp luật", "quy định của chính phủ",
        "trường hợp", "trong trường hợp", 
        "khi có đủ điều kiện", "khi đáp ứng điều kiện",
        "các trường hợp không được"
    ]
    
    for kw in keywords:
        if kw in text_lower:
            if kw == "trường hợp" and "các trường hợp không được" not in text_lower and not text_lower.startswith("trường hợp"):
                pass
            return 1
    return 0

def main():
    if not os.path.exists(INPUT_GRAPH):
        print(f"Error: Not found {INPUT_GRAPH}")
        return
        
    preds_a = load_predictions(EXP_A)
    preds_b = load_predictions(EXP_B)
    preds_c = load_predictions(EXP_C)
        
    with open(INPUT_GRAPH, "r", encoding="utf-8") as f:
        graph = json.load(f)
        
    nodes = graph.get("nodes", [])
    
    # Bỏ qua CHAPTER, SECTION
    eval_nodes = [
        n for n in nodes 
        if "CHAPTER" not in n.get("labels", []) and "SECTION" not in n.get("labels", [])
    ]
    
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    
    with open(OUTPUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["node_id", "text", "is_semantic_human", "AI_Suggest", "EXP-A(Regex)", "EXP-B(Embed)", "EXP-C(Fusion)", "note"])
        
        for n in eval_nodes:
            node_id = n["id"]
            text = n.get("properties", {}).get("text", "")
            ai_suggest = is_semantic(text)
            pred_a = preds_a.get(node_id, 0)
            pred_b = preds_b.get(node_id, 0)
            pred_c = preds_c.get(node_id, 0)
            
            # Bỏ trống cột is_semantic_human để user tự điền
            writer.writerow([node_id, text, "", str(ai_suggest), str(pred_a), str(pred_b), str(pred_c), ""])
            
    print(f"Đã tạo file {OUTPUT_CSV} với {len(eval_nodes)} nodes (Toàn bộ dữ liệu).")

if __name__ == "__main__":
    main()
