import os
import json
import hashlib
import numpy as np
from pathlib import Path
from typing import List, Dict, Any

def get_input_hash(texts: List[str]) -> str:
    """Tạo mã băm SHA-256 từ toàn bộ văn bản đầu vào để theo dõi thay đổi."""
    hasher = hashlib.sha256()
    for text in texts:
        hasher.update(text.encode('utf-8'))
    return hasher.hexdigest()

def ensure_embeddings(
    graph_path: str = "outputs/physical_graphs/physical_graph.json",
    anchor_path: str = "outputs/embeddings/luat_dat_dai_ch3/anchor_texts.json",
    out_dir: str = "outputs/embeddings/luat_dat_dai_ch3",
    model_name: str = "Qwen/Qwen2.5-0.5B"
) -> bool:
    """
    Kiểm tra và sinh embeddings nếu cần thiết.
    Return True nếu dùng cache, False nếu vừa sinh mới.
    """
    
    out_dir_path = Path(out_dir)
    out_dir_path.mkdir(parents=True, exist_ok=True)
    
    meta_path = out_dir_path / "embeddings.meta.json"
    embed_path = out_dir_path / "embeddings.npy"
    
    # 1. Nạp graph và trích xuất text
    print(f"[M5-Embed] Đọc dữ liệu từ {graph_path}...")
    if not os.path.exists(graph_path):
        raise FileNotFoundError(f"Không tìm thấy {graph_path}. Vui lòng chạy M4 trước.")
        
    with open(graph_path, "r", encoding="utf-8") as f:
        graph = json.load(f)
        
    nodes = graph.get("nodes", [])
    node_ids = []
    texts = []
    
    for node in nodes:
        node_ids.append(node["id"])
        texts.append(node.get("properties", {}).get("text", ""))
        
    current_input_hash = get_input_hash(texts)
    
    # 2. Kiểm tra Cache (Fingerprint)
    if meta_path.exists() and embed_path.exists():
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            
            if (meta.get("model") == model_name and 
                meta.get("node_count") == len(nodes) and 
                meta.get("input_hash") == current_input_hash):
                print("[M5-Embed] Cache Hit! Embeddings hợp lệ, bỏ qua sinh vector.")
                return True
            else:
                print("[M5-Embed] Cache Miss! Cấu hình hoặc dữ liệu đã thay đổi.")
        except json.JSONDecodeError:
            print("[M5-Embed] File meta lỗi. Cần sinh lại.")
    else:
        print("[M5-Embed] Không tìm thấy cache. Cần sinh mới.")

    # 3. Sinh vector mới
    print("=== GENERATE OFFLINE EMBEDDINGS ===")
    from sentence_transformers import SentenceTransformer
    
    print(f"Loading {model_name}...")
    model = SentenceTransformer(model_name, trust_remote_code=True)
    
    print(f"\nEmbedding {len(texts)} nodes...")
    embeddings = model.encode(texts, batch_size=4, show_progress_bar=True, normalize_embeddings=False)
    embeddings = embeddings.astype(np.float32)
    
    print(f"\nReading anchors from {anchor_path}...")
    with open(anchor_path, "r", encoding="utf-8") as f:
        anchor_texts = json.load(f)
        
    print(f"Embedding {len(anchor_texts)} anchors...")
    anchors_vec = model.encode(anchor_texts, batch_size=4, show_progress_bar=True, normalize_embeddings=False)
    anchors_vec = anchors_vec.astype(np.float32)
    
    # 4. Ghi file nguyên tử (Tránh lỗi nửa chừng)
    print(f"\nLưu file vào {out_dir}...")
    
    tmp_embed = out_dir_path / "embeddings.npy.tmp"
    tmp_anchor = out_dir_path / "anchors.npy.tmp"
    tmp_ids = out_dir_path / "node_ids.json.tmp"
    tmp_meta = out_dir_path / "embeddings.meta.json.tmp"
    
    with open(tmp_embed, "wb") as f:
        np.save(f, embeddings)
    with open(tmp_anchor, "wb") as f:
        np.save(f, anchors_vec)
    
    with open(tmp_ids, "w", encoding="utf-8") as f:
        json.dump(node_ids, f, indent=2)
        
    meta_info = {
        "model": model_name,
        "dimension": int(embeddings.shape[1]),
        "node_count": len(nodes),
        "input_hash": current_input_hash
    }
    with open(tmp_meta, "w", encoding="utf-8") as f:
        json.dump(meta_info, f, indent=2)
        
    # Replace (Atomic)
    os.replace(tmp_embed, embed_path)
    os.replace(tmp_anchor, out_dir_path / "anchors.npy")
    os.replace(tmp_ids, out_dir_path / "node_ids.json")
    os.replace(tmp_meta, meta_path)
    
    # Dọn dẹp config cũ nếu còn sót
    old_config = out_dir_path / "embedding_config.json"
    if old_config.exists():
        os.remove(old_config)
        
    print("[M5-Embed] DONE! Hoàn tất cập nhật embedding.")
    return False

if __name__ == "__main__":
    ensure_embeddings()
