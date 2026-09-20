import sys, io
import json
import csv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1. Load Local Candidates
with open("outputs/candidate_nodes/routing_candidates.json", "r", encoding="utf-8") as f:
    local_data = json.load(f)
local_candidates = [c["node_id"] for c in local_data["candidates"] if c["route"] in ("LLM_CANDIDATE", "RULE_ONLY")]

# 2. Load Benchmark Candidates
benchmark_candidates = []
with open("outputs/benchmark_m5/benchmark_full_results.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Benchmark considers EXP-C. LLM_CANDIDATE is True if Max-Fusion == True?
        # Actually, benchmark_full_results might have Is_Semantic_Human column or something?
        if row.get("Max-Fusion") == "True" or row.get("Max-Fusion") == "1":
            benchmark_candidates.append(row["Node_id"])

# 3. Compare using SET INTERSECTION (User preference!)
local_set = set(local_candidates)
bench_set = set(benchmark_candidates)

extra_in_local = local_set - bench_set
missing_in_local = bench_set - local_set

print("=== SET INTERSECTION ===")
print(f"Local: {len(local_set)}")
print(f"Benchmark: {len(bench_set)}")

print("\n--- EXTRA IN LOCAL ---")
for x in sorted(list(extra_in_local)):
    print(x)
    
print("\n--- MISSING IN LOCAL ---")
for x in sorted(list(missing_in_local)):
    print(x)
