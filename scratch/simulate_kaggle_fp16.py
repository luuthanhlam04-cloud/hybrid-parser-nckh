import os, json
import numpy as np
import torch
from sentence_transformers import SentenceTransformer

# 1. Load Local Nodes
with open("outputs/physical_graphs/physical_graph.json", "r", encoding="utf-8") as f:
    graph = json.load(f)
nodes = graph.get("nodes", [])
node_texts = []
node_ids = []
for n in nodes:
    text = n.get("properties", {}).get("text", "")
    nid = n["id"]
    if "chuong-" in nid and "dieu-" not in nid: # skip RULE_ONLY
        continue
    node_texts.append(text)
    node_ids.append(nid)

# 2. Load Anchors
with open("outputs/embeddings/luat_dat_dai_ch3/anchor_texts.json", "r", encoding="utf-8") as f:
    anchor_texts = json.load(f)

# 3. Simulate Kaggle logic (Float16 precision on GPU/CPU)
# We cast model to float16 to simulate Kaggle GPU inference
model = SentenceTransformer("Qwen/Qwen2.5-0.5B", trust_remote_code=True, model_kwargs={"torch_dtype": torch.float16})

# CPU doesn't support half precision operations for all ops, but let's try autocast
with torch.autocast(device_type="cpu", dtype=torch.bfloat16):
    embeddings = model.encode(node_texts, normalize_embeddings=True, show_progress_bar=False, convert_to_numpy=True)
    anchor_vecs = model.encode(anchor_texts, normalize_embeddings=True, show_progress_bar=False, convert_to_numpy=True)

# 4. Compute similarities
similarities = np.dot(embeddings, anchor_vecs.T)
max_sims = np.max(similarities, axis=1)

# 5. Output boundary nodes
results = []
for nid, sim in zip(node_ids, max_sims):
    results.append((nid, float(sim)))

results.sort(key=lambda x: x[1], reverse=True)

print("Kaggle Simulated (Float16) Scores around 0.85:")
for nid, sim in results:
    if 0.84 <= sim <= 0.86:
        print(f"{nid}: {sim}")
