import os, json
import numpy as np
from sentence_transformers import SentenceTransformer

# 1. Load Local Nodes
with open("outputs/physical_graphs/physical_graph.json", "r", encoding="utf-8") as f:
    graph = json.load(f)
nodes = graph.get("nodes", [])
# filter out RULE_ONLY chapters/sections just to be safe, or just compute for all
node_texts = [n.get("properties", {}).get("text", "") for n in nodes]
node_ids = [n["id"] for n in nodes]

# 2. Load Anchors
with open("outputs/embeddings/luat_dat_dai_ch3/anchor_texts.json", "r", encoding="utf-8") as f:
    anchor_texts = json.load(f)

# 3. Simulate Kaggle logic (normalize within PyTorch)
model = SentenceTransformer("Qwen/Qwen2.5-0.5B", trust_remote_code=True)
print("Encoding texts with PyTorch normalize...")
embeddings = model.encode(node_texts, normalize_embeddings=True, show_progress_bar=False)
anchor_vecs = model.encode(anchor_texts, normalize_embeddings=True, show_progress_bar=False)

# 4. Compute similarities
similarities = np.dot(embeddings, anchor_vecs.T)
max_sims = np.max(similarities, axis=1)

# 5. Output
results = []
for nid, sim in zip(node_ids, max_sims):
    results.append((nid, float(sim)))

results.sort(key=lambda x: x[1], reverse=True)

print("Kaggle Embed Scores >= 0.84:")
for nid, sim in results:
    if 0.84 <= sim <= 0.86:
        print(f"{nid}: {sim}")
