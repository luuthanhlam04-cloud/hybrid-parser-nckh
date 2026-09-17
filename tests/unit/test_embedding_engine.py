import pytest
import numpy as np
from pathlib import Path
from src.semantic_router.embedding_engine import EmbeddingEngine

def test_embedding_engine_loading(tmp_path):
    # Prepare dummy data
    embeddings = np.random.rand(3, 1024)
    anchors = np.random.rand(2, 1024)
    node_ids = ["node_1", "node_2", "node_3"]
    
    emb_path = tmp_path / "embeddings.npy"
    anchors_path = tmp_path / "anchors.npy"
    node_ids_path = tmp_path / "node_ids.json"
    
    np.save(emb_path, embeddings)
    np.save(anchors_path, anchors)
    
    import json
    with open(node_ids_path, "w") as f:
        json.dump(node_ids, f)
        
    engine = EmbeddingEngine(embeddings_path=emb_path, node_ids_path=node_ids_path, anchors_path=anchors_path)
    
    assert engine.embeddings is not None
    assert engine.embeddings.shape == (3, 1024)
    assert engine.anchors is not None
    assert engine.anchors.shape == (2, 1024)
    
    # Test get_embedding
    vec = engine.get_embedding("node_2")
    assert np.allclose(vec, embeddings[1])
    
    # Test similarity
    query_vec = np.array([1, 0, 0], dtype=float)
    anchor_vecs = np.array([[1, 0, 0], [0, 1, 0]], dtype=float)
    sims = engine.similarity(query_vec, anchor_vecs)
    
    assert len(sims) == 2
    assert np.isclose(sims[0], 1.0)
    assert np.isclose(sims[1], 0.0)
