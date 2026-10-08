# -*- coding: utf-8 -*-
"""
embedding_engine.py — Quản lý và cung cấp embedding vectors.

Trong Iteration 1 (Kaggle), engine hoạt động ở chế độ "precomputed":
Nó tải `embeddings.npy` và `node_ids.json` đã được tính toán từ trước.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np

logger = logging.getLogger("embedding_engine")

class EmbeddingEngine:
    def __init__(self, embeddings_path: str | Path, node_ids_path: str | Path, anchors_path: str | Path = "outputs/embeddings/anchors.npy"):
        self.embeddings_path = Path(embeddings_path)
        self.node_ids_path = Path(node_ids_path)
        self.anchors_path = Path(anchors_path)
        
        self.embeddings: Optional[np.ndarray] = None
        self.anchors: Optional[np.ndarray] = None
        self.id_to_index: Dict[str, int] = {}
        
        self.load_precomputed()

    def load_precomputed(self) -> None:
        """Nạp embeddings và node mapping vào RAM."""
        if not self.embeddings_path.exists() or not self.node_ids_path.exists():
            raise FileNotFoundError(
                f"Không tìm thấy file embeddings. Cần có:\n- {self.embeddings_path}\n- {self.node_ids_path}"
            )
            
        logger.info("Đang nạp embeddings từ %s...", self.embeddings_path)
        self.embeddings = np.load(self.embeddings_path)
        
        with open(self.node_ids_path, "r", encoding="utf-8") as f:
            node_ids = json.load(f)
            
        if len(node_ids) != self.embeddings.shape[0]:
            raise ValueError(f"Kích thước không khớp! node_ids có {len(node_ids)} nhưng embeddings có {self.embeddings.shape[0]}")
            
        self.id_to_index = {node_id: idx for idx, node_id in enumerate(node_ids)}
        logger.info("Đã nạp thành công %d embeddings (dim=%d).", self.embeddings.shape[0], self.embeddings.shape[1])
        
        if self.anchors_path.exists():
            self.anchors = np.load(self.anchors_path)
            logger.info("Đã nạp anchors.npy với shape %s", self.anchors.shape)
        else:
            logger.warning("Không tìm thấy anchors tại %s", self.anchors_path)

    def get_embedding(self, node_id: str) -> Optional[np.ndarray]:
        """Lấy vector của 1 node cụ thể."""
        idx = self.id_to_index.get(node_id)
        if idx is not None and self.embeddings is not None:
            return self.embeddings[idx]
        return None

    def similarity(self, query_vec: np.ndarray, anchor_vecs: np.ndarray) -> List[float]:
        """
        Tính cosine similarity giữa 1 query_vec và danh sách anchor_vecs.
        Qwen3-Embedding dùng cosine similarity chuẩn.
        """
        if query_vec is None or anchor_vecs is None or len(anchor_vecs) == 0:
            return []
            
        # Reshape query nếu cần
        if len(query_vec.shape) == 1:
            query_vec = query_vec.reshape(1, -1)
            
        if len(anchor_vecs.shape) == 1:
            anchor_vecs = anchor_vecs.reshape(1, -1)
            
        # Normalize
        q_norm = np.linalg.norm(query_vec, axis=1, keepdims=True)
        a_norm = np.linalg.norm(anchor_vecs, axis=1, keepdims=True)
        
        # Avoid division by zero
        q_norm = np.where(q_norm == 0, 1e-10, q_norm)
        a_norm = np.where(a_norm == 0, 1e-10, a_norm)
        
        query_normalized = query_vec / q_norm
        anchors_normalized = anchor_vecs / a_norm
        
        # Dot product
        sim_scores = np.dot(query_normalized, anchors_normalized.T)
        
        return sim_scores.flatten().tolist()
