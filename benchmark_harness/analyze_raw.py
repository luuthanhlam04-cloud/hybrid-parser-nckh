import pandas as pd
import numpy as np
import os

files = {
    'Vector': '../checkpoint_results_VECTOR.csv',
    'Hybrid': '../final_benchmark_results_HYBRID.csv',
    'LightRAG': '../backup_lightrag_512.csv'
}

print("=== TỔNG HỢP KẾT QUẢ BENCHMARK ===")
print(f"{'Hệ thống':<15} | {'Số câu':<8} | {'Faithfulness':<15} | {'Recall@5':<10} | {'MRR@5':<10} | {'Tổng chi phí':<15}")
print("-" * 80)

for name, f in files.items():
    if not os.path.exists(f):
        print(f"Error: {f} not found!")
        continue
    try:
        df = pd.read_csv(f)
        total_q = len(df)
        cost = df['estimated_cost'].sum() if 'estimated_cost' in df.columns else 0.0
        f_mean = df['faithfulness'].mean() if 'faithfulness' in df.columns else 0.0
        
        recall, mrr = 'N/A', 'N/A'
        if 'recall_at_5' in df.columns and name != 'LightRAG':
            recall = f"{df['recall_at_5'].mean():.4f}"
            mrr = f"{df['mrr_at_5'].mean():.4f}"
            
        print(f"{name:<15} | {total_q:<8} | {f_mean:<15.4f} | {recall:<10} | {mrr:<10} | ${cost:<15.4f}")
    except Exception as e:
        print(f'Error reading {name}: {e}')
