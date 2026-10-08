import csv

with open('c:/Users/luuth/NCKH/hybrid_parser_graphrag/outputs/benchmark_m5/benchmark_full_results.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    print("Thresh | Cost | Recall | Prec  | F1    | TP  | FP  | FN")
    print("-" * 65)
    
    rows = []
    for row in reader:
        if row['Model'] == 'Qwen-0.5B (Causal)' and row['Strategy'] == 'Max-Fusion':
            rows.append(row)
            
    # Sort by threshold
    rows.sort(key=lambda x: float(x['Threshold']))
    
    for row in rows:
        print(f"{float(row['Threshold']):.2f}   | {row['Cost']:<4} | {float(row['Recall']):.3f}  | {float(row['Precision']):.3f} | {float(row['F1']):.3f} | {row['TP']:<3} | {row['FP']:<3} | {row['FN']:<3}")
