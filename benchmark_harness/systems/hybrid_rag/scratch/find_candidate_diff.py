import sys, io
import json
import csv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1. Local LLM Candidates
with open("outputs/candidate_nodes/routing_candidates.json", "r", encoding="utf-8") as f:
    local_data = json.load(f)
local_candidate_ids = [c["node_id"] for c in local_data["candidates"] if c["route"] == "LLM_CANDIDATE"]

with open("outputs/physical_graphs/physical_graph.json", "r", encoding="utf-8") as f:
    graph = json.load(f)
id_to_text = {n["id"]: n.get("properties", {}).get("text", "") for n in graph.get("nodes", [])}
local_candidate_texts = {id_to_text[nid] for nid in local_candidate_ids}

# 2. Kaggle Candidates
kaggle_texts = set()
with open("outputs/full_golden_set_annotation.csv", "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        # EXP-C(Fusion) True
        if str(row.get("EXP-C(Fusion)", "")).lower() in ("true", "1"):
            kaggle_texts.add(row["text"])

# 3. Diff
extra_in_local = local_candidate_texts - kaggle_texts
print("=== TEXTS IN LOCAL BUT NOT KAGGLE ===")
for t in extra_in_local:
    print(repr(t))

print(f"\nLocal candidates count: {len(local_candidate_texts)}")
print(f"Kaggle candidates count: {len(kaggle_texts)}")
