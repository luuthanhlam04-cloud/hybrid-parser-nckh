# -*- coding: utf-8 -*-
"""
routing_engine.py — Đánh giá Semantic Patterns và Embedding Similarity để ra quyết định định tuyến.
"""
import re
from dataclasses import dataclass
from typing import List, Tuple
import numpy as np

@dataclass
class SemanticPattern:
    name: str
    pattern: str
    category: str      # EXCEPTION, CROSS_REF, CONDITION
    strength: float    # 0.0 -> 1.0

# Lightweight Semantic Pattern Registry
SEMANTIC_REGISTRY = [
    # Cross-reference
    SemanticPattern("REF_THEO_QUY_DINH", r"theo quy định tại", "CROSS_REF", 1.0),
    SemanticPattern("REF_CAN_CU", r"căn cứ(?: khoản| điều| điểm)?", "CROSS_REF", 1.0),
    SemanticPattern("REF_QUY_DINH_TAI", r"quy định tại(?: khoản| điều| điểm)?", "CROSS_REF", 1.0),
    
    # Exception
    SemanticPattern("EXC_TRU_TRUONG_HOP", r"trừ trường hợp", "EXCEPTION", 1.0),
    SemanticPattern("EXC_NGOAI_LE", r"ngoại lệ", "EXCEPTION", 1.0),
    SemanticPattern("EXC_TRU_KHI", r"trừ khi", "EXCEPTION", 1.0),
    SemanticPattern("EXC_NGOAI_TRU", r"ngoại trừ", "EXCEPTION", 1.0),
    
    # Condition
    SemanticPattern("COND_TRONG_TRUONG_HOP", r"trong trường hợp", "CONDITION", 0.4),
    SemanticPattern("COND_DIEU_KIEN", r"điều kiện", "CONDITION", 0.4),
]

class RoutingEngine:
    def __init__(self, registry: List[SemanticPattern] = SEMANTIC_REGISTRY):
        self.registry = registry

    def evaluate_regex(self, text: str) -> Tuple[float, str]:
        """
        Đánh giá văn bản qua Semantic Pattern Registry.
        Trả về (max_strength, matched_category_or_none)
        """
        if not text:
            return 0.0, "NONE"
            
        lower_text = text.lower()
        
        max_score = 0.0
        best_category = "NONE"
        
        for sp in self.registry:
            if re.search(sp.pattern, lower_text):
                if sp.strength > max_score:
                    max_score = sp.strength
                    best_category = sp.category
                    
        return max_score, best_category

    def embed_score(self, text_vec: np.ndarray, anchor_vecs: np.ndarray, engine: 'EmbeddingEngine') -> float:
        """
        Tính điểm embedding similarity so với các anchor vectors.
        Trả về max similarity.
        """
        if text_vec is None or anchor_vecs is None or len(anchor_vecs) == 0:
            return 0.0
        
        sim_scores = engine.similarity(text_vec, anchor_vecs)
        return max(sim_scores) if sim_scores else 0.0

    def fuse(self, regex_s: float, embed_s: float, ablation_mode: str = "EXP-C") -> float:
        """
        Fusion logic tuỳ theo Ablation mode.
        EXP-A: Regex-only
        EXP-B: Embedding-only
        EXP-C: W1 (alpha * regex + (1 - alpha) * embed) - tạm dùng max hoặc trọng số.
        """
        if ablation_mode == "EXP-A":
            return regex_s
        elif ablation_mode == "EXP-B":
            return embed_s
        elif ablation_mode == "EXP-C":
            # Tạm thời dùng Max Fusion (hoặc có thể dùng công thức alpha)
            return max(regex_s, embed_s)
        return regex_s
