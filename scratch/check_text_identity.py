import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import csv
import json

with open("outputs/full_golden_set_annotation.csv", "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    benchmark_texts = [row["text"] for row in reader]

with open("outputs/physical_graphs/physical_graph.json", "r", encoding="utf-8") as f:
    graph = json.load(f)
    nodes = graph.get("nodes", graph)
    
local_texts = [n.get("properties", {}).get("text", "") for n in nodes]

# Find matches
missing_in_local = []
for t in benchmark_texts:
    if t not in local_texts:
        missing_in_local.append(t)
        
missing_in_benchmark = []
for t in local_texts:
    if t not in benchmark_texts:
        missing_in_benchmark.append(t)
        
print("=== VERIFY TEXT IDENTITY ===")
print(f"Total Benchmark Texts: {len(benchmark_texts)}")
print(f"Total Local Texts: {len(local_texts)}")
print(f"Intersection: {len(set(benchmark_texts).intersection(set(local_texts)))}")

if not missing_in_local and not missing_in_benchmark:
    print("SUCCESS: Text Identity matches perfectly!")
else:
    print(f"WARNING: {len(missing_in_local)} benchmark texts not in local graph.")
    print(f"WARNING: {len(missing_in_benchmark)} local texts not in benchmark.")
