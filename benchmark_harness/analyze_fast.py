import csv
import os
import sys

files = {
    'Vector': '../final_benchmark_results_VECTOR.csv',
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
        with open(f, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            count = 0
            cost = 0.0
            faith = 0.0
            recall = 0.0
            mrr = 0.0
            
            for row in reader:
                count += 1
                if 'estimated_cost' in row and row['estimated_cost']:
                    cost += float(row['estimated_cost'])
                if 'faithfulness' in row and row['faithfulness']:
                    faith += float(row['faithfulness'])
                if 'recall_at_5' in row and row['recall_at_5'] and name != 'LightRAG':
                    recall += float(row['recall_at_5'])
                if 'mrr_at_5' in row and row['mrr_at_5'] and name != 'LightRAG':
                    mrr += float(row['mrr_at_5'])
                    
            f_mean = faith / count if count > 0 else 0
            r_mean = f"{recall / count:.4f}" if count > 0 and name != 'LightRAG' else "N/A"
            m_mean = f"{mrr / count:.4f}" if count > 0 and name != 'LightRAG' else "N/A"
            
            print(f"{name:<15} | {count:<8} | {f_mean:<15.4f} | {r_mean:<10} | {m_mean:<10} | ${cost:<15.4f}")
    except Exception as e:
        print(f'Error reading {name}: {e}')

sys.exit(0)
