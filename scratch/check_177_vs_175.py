import sys, io
import json
import csv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1. Load Local Candidates (routing_candidates.json)
with open("outputs/candidate_nodes/routing_candidates.json", "r", encoding="utf-8") as f:
    local_data = json.load(f)

# The ID in routing_candidates is the NEW ID (e.g. diem-e)
# We need to map local candidate node text to check against Kaggle.
# But actually, local_candidates are just those where route in ("LLM_CANDIDATE", "RULE_ONLY")
local_candidate_texts = []
for c in local_data["candidates"]:
    if c["route"] in ("LLM_CANDIDATE", "RULE_ONLY"):
        # We need the text of this node from physical_graph.json
        local_candidate_texts.append(c["node_id"])

# Let's map node_id -> text
with open("outputs/physical_graphs/physical_graph.json", "r", encoding="utf-8") as f:
    graph = json.load(f)
id_to_text = {n["id"]: n.get("properties", {}).get("text", "") for n in graph.get("nodes", [])}

local_texts = [id_to_text[nid] for nid in local_candidate_texts]

# 2. Load Benchmark Candidates (full_golden_set_annotation.csv)
benchmark_texts = []
with open("outputs/full_golden_set_annotation.csv", "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Check Kaggle logic: Qwen/Qwen2.5-0.5B, max(regex, embedding) -> EXP-C(Fusion)
        # Actually Kaggle already gave us 'EXP-C(Fusion)' column? 
        # Wait, the user said Kaggle got 175! Let's see what column has 175 Trues.
        # Let's just collect all texts where 'is_semantic_human' is 1 (or 'EXP-C(Fusion)' is 1)
        # We want to know why Local has 177 and Kaggle has 175.
        pass

# Let's just print the counts of True/False for the Kaggle columns
with open("outputs/full_golden_set_annotation.csv", "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

def count_true(col):
    return sum(1 for r in rows if str(r.get(col, "")).lower() in ("true", "1"))

print("=== KAGGLE COUNTS ===")
for col in ['is_semantic_human', 'AI_Suggest', 'EXP-A(Regex)', 'EXP-B(Embed)', 'EXP-C(Fusion)']:
    print(f"{col}: {count_true(col)}")

print(f"Local LLM_CANDIDATE + RULE_ONLY count: {len(local_candidate_texts)}")
