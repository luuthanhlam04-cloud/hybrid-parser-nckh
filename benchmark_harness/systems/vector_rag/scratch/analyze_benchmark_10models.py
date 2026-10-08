import csv
from collections import defaultdict

results = []
with open('c:/Users/luuth/NCKH/hybrid_parser_graphrag/outputs/benchmark_m5/benchmark_full_results.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Convert numeric columns
        for k in ['Threshold', 'Cost', 'Recall', 'Precision', 'F1', 'TP', 'FP', 'TN', 'FN']:
            row[k] = float(row[k])
        results.append(row)

# Group by Model and Strategy, find max F1
grouped = defaultdict(lambda: defaultdict(list))
for r in results:
    grouped[r['Model']][r['Strategy']].append(r)

print(f"{'Model':<20} | {'Strategy':<25} | {'Thresh':<6} | {'Cost':<5} | {'Recall':<6} | {'Prec':<6} | {'F1':<6}")
print("-" * 85)

for model, strategies in grouped.items():
    for strategy, rows in strategies.items():
        best_row = max(rows, key=lambda x: x['F1'])
        print(f"{model:<20} | {strategy:<25} | {best_row['Threshold']:<6.2f} | {best_row['Cost']:<5.0f} | {best_row['Recall']:<6.3f} | {best_row['Precision']:<6.3f} | {best_row['F1']:<6.3f}")
    print("-" * 85)
