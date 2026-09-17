import json
import csv
import os

GOLDEN_CSV = "outputs/full_golden_set_annotation.csv"
EXP_A = "outputs/candidate_nodes/routing_candidates_expA.json"
EXP_B = "outputs/candidate_nodes/routing_candidates_expB.json"
EXP_C = "outputs/candidate_nodes/routing_candidates_expC.json"

def load_golden_labels(csv_path: str) -> dict:
    labels = {}
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            node_id = row["Node_id"]
            try:
                val = int(row["is_semantic_human"])
                labels[node_id] = val
            except ValueError:
                pass
    return labels

def load_predictions(json_path: str) -> dict:
    preds = {}
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        for cand in data.get("candidates", []):
            node_id = cand["node_id"]
            route = cand["route"]
            preds[node_id] = 1 if route == "LLM_CANDIDATE" else 0
    return preds

def evaluate(ground_truth: dict, predictions: dict) -> tuple:
    tp = 0
    fp = 0
    fn = 0
    tn = 0
    
    for node_id, true_val in ground_truth.items():
        pred_val = predictions.get(node_id, 0)
        
        if true_val == 1 and pred_val == 1:
            tp += 1
        elif true_val == 0 and pred_val == 1:
            fp += 1
        elif true_val == 1 and pred_val == 0:
            fn += 1
        elif true_val == 0 and pred_val == 0:
            tn += 1
            
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return precision, recall, f1, tp, fp, fn, tn

def main():
    if not os.path.exists(GOLDEN_CSV):
        print(f"Error: {GOLDEN_CSV} không tồn tại!")
        return
        
    ground_truth = load_golden_labels(GOLDEN_CSV)
    print(f"Đã nạp {len(ground_truth)} nodes từ Golden Set.\n")
    
    experiments = {
        "EXP-A (Regex-only)": EXP_A,
        "EXP-B (Embedding-only)": EXP_B,
        "EXP-C (Max-Fusion)": EXP_C,
    }
    
    print(f"{'Experiment':<25} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10} | {'TP/FP/FN/TN'}")
    print("-" * 85)
    
    for name, path in experiments.items():
        if not os.path.exists(path):
            print(f"{name:<25} | LỖI: Không tìm thấy file")
            continue
            
        preds = load_predictions(path)
        p, r, f1, tp, fp, fn, tn = evaluate(ground_truth, preds)
        
        print(f"{name:<25} | {p:<10.3f} | {r:<10.3f} | {f1:<10.3f} | {tp}/{fp}/{fn}/{tn}")
        
if __name__ == "__main__":
    main()
