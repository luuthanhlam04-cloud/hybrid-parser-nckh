import os, json
import numpy as np
import torch
from sentence_transformers import SentenceTransformer

def main():
    # 1. Load Local Nodes
    with open("outputs/physical_graphs/physical_graph.json", "r", encoding="utf-8") as f:
        graph = json.load(f)
    nodes = graph.get("nodes", [])
    node_texts = []
    node_ids = []
    for n in nodes:
        text = n.get("properties", {}).get("text", "")
        nid = n["id"]
        # In run_semantic_router.py, CHAPTER/SECTION are evaluated separately.
        # Let's collect ALL texts to match the evaluation size.
        node_texts.append(text)
        node_ids.append(nid)

    # 2. Load Anchors
    with open("outputs/embeddings/luat_dat_dai_ch3/anchor_texts.json", "r", encoding="utf-8") as f:
        anchor_texts = json.load(f)

    # 3. Encode with explicit float16
    print("Loading model in float16...")
    model = SentenceTransformer("Qwen/Qwen2.5-0.5B", trust_remote_code=True, model_kwargs={"torch_dtype": torch.float16})
    
    print("Encoding...")
    embeddings = model.encode(node_texts, normalize_embeddings=True, show_progress_bar=False, convert_to_numpy=True)
    anchor_vecs = model.encode(anchor_texts, normalize_embeddings=True, show_progress_bar=False, convert_to_numpy=True)

    # 4. Compute similarities
    similarities = np.dot(embeddings, anchor_vecs.T)
    max_sims = np.max(similarities, axis=1)

    # 5. Count candidates >= 0.85
    # Keep in mind some nodes might have regex match = 1.0. 
    # But let's just count how many have embed >= 0.85 (since we know regex=69)
    # Actually, let's load regex scores from routing_candidates.json
    with open("outputs/candidate_nodes/routing_candidates.json", "r", encoding="utf-8") as f:
        routing_data = json.load(f)
    
    # We will compute the MAX FUSION score for all nodes (excluding RULE_ONLY which are 1.0)
    # routing_candidates.json contains 'routing_score'. Wait, we want to know what it WOULD BE under float16.
    
    # Let's map node_id -> regex_score
    # Wait, regex_score is not saved directly, but we can compute it if we want.
    # We just know that the two boundary nodes (dieu-42_khoan-2_p31859 and dieu-27_khoan-3_p2476) DO NOT have regex match (their routing score = their embed score).
    
    # Let's just output the float16 embed score for those 2 specific nodes!
    
    target_nodes = ["doc_chuong-iii_muc-4_dieu-42_khoan-2_p31859", "doc_chuong-iii_muc-1_dieu-27_khoan-3_p2476", "doc_chuong-iii_muc-2_dieu-33_khoan-1_p11236"]
    
    print("\n--- Float16 Scores ---")
    for nid, sim in zip(node_ids, max_sims):
        if nid in target_nodes:
            print(f"{nid}: {sim}")
    
    count_85 = sum(1 for sim in max_sims if sim >= 0.85)
    print(f"Total nodes with float16 embed score >= 0.85: {count_85}")

if __name__ == "__main__":
    main()
