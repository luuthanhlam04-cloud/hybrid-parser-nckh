import os
import json
import pandas as pd

def load_all_results(system_dir: str):
    """Đọc toàn bộ file per-question JSON của 1 system"""
    rows = []
    if not os.path.exists(system_dir):
        return pd.DataFrame()
        
    for filename in os.listdir(system_dir):
        if filename.endswith(".json"):
            with open(os.path.join(system_dir, filename), 'r', encoding='utf-8') as f:
                rows.append(json.load(f))
    return pd.DataFrame(rows)

def get_valid_question_ids(systems: list, results_dir: str) -> set:
    """Listwise Deletion: Chỉ giữ lại những câu không bị lỗi ở CẢ 3 hệ thống"""
    valid_sets = []
    for system in systems:
        df = load_all_results(os.path.join(results_dir, system))
        if df.empty:
            print(f"Cảnh báo: Không có dữ liệu cho hệ thống {system}")
            continue
        
        # Chỉ lấy những câu error là null
        valid = set(df[df["error"].isna() | (df["error"] == None) | (df["error"] == "None")]["question_id"])
        valid_sets.append(valid)
        
    if not valid_sets:
        return set()
    return set.intersection(*valid_sets)

def aggregate_and_report(systems: list, results_dir: str, output_dir: str):
    """Gom dữ liệu per-question lại thành CSV và tính toán Percentile Latency"""
    os.makedirs(output_dir, exist_ok=True)
    valid_ids = get_valid_question_ids(systems, results_dir)
    print(f"N_effective (Sau khi Listwise Deletion qua {len(systems)} hệ thống): {len(valid_ids)}\n")
    
    for system in systems:
        df = load_all_results(os.path.join(results_dir, system))
        if df.empty:
            continue
            
        # Lọc danh sách hợp lệ (Listwise Deletion)
        df_clean = df[df["question_id"].isin(valid_ids)]
        
        # Tính Percentile Latency
        latency_p50 = df_clean["latency_ms"].quantile(0.50) if not df_clean.empty else 0
        latency_p95 = df_clean["latency_ms"].quantile(0.95) if not df_clean.empty else 0
        mean_latency = df_clean["latency_ms"].mean() if not df_clean.empty else 0
        
        print(f"[{system}]")
        print(f" - N_total: {len(df)}")
        print(f" - N_valid: {len(df_clean)}")
        print(f" - Latency (Mean): {mean_latency:.2f}ms")
        print(f" - Latency (p50):  {latency_p50:.2f}ms")
        print(f" - Latency (p95):  {latency_p95:.2f}ms\n")
        
        # Lưu file tổng hợp
        out_csv = os.path.join(output_dir, f"{system}_aggregated.csv")
        df_clean.to_csv(out_csv, index=False)
        print(f"Đã xuất file: {out_csv}")

if __name__ == "__main__":
    aggregate_and_report(
        systems=["Vector_RAG_Baseline", "Hybrid_RAG", "LightRAG"],
        results_dir="results/raw",
        output_dir="results/aggregated"
    )
