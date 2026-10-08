import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "Qwen/Qwen3-Embedding-0.6B"
TASK_DESCRIPTION = "Given a legal clause from Vietnamese law, extract its embedding for semantic routing and finding legal exceptions or conditions."
OUTPUT_DIR = "outputs/embeddings/"

ANCHORS = [
    "trừ trường hợp",
    "ngoại lệ",
    "trừ khi",
    "ngoại trừ",
    "trong trường hợp",
    "điều kiện",
    "theo quy định tại",
    "căn cứ khoản",
    "căn cứ điều",
    "quy định tại"
]

def main():
    print(f"Đang nạp model {MODEL_NAME} để compute anchors...")
    model = SentenceTransformer(MODEL_NAME, trust_remote_code=True)
    
    print("Đang embed anchors...")
    anchor_embeddings = model.encode(
        ANCHORS,
        show_progress_bar=True,
        prompt=TASK_DESCRIPTION
    )
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    np.save(os.path.join(OUTPUT_DIR, "anchors.npy"), anchor_embeddings)
    
    with open(os.path.join(OUTPUT_DIR, "anchor_texts.json"), "w", encoding="utf-8") as f:
        json.dump(ANCHORS, f, ensure_ascii=False, indent=2)
        
    print(f"Hoàn thành! Đã lưu anchors.npy ({anchor_embeddings.shape})")

if __name__ == "__main__":
    main()
