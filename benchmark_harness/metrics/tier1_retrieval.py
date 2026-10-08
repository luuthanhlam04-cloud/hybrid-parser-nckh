from typing import Dict, Any
from core.base_system import RetrievalResult

class Tier1RetrievalMetrics:
    """
    Đánh giá độ chính xác của tầng truy xuất văn bản pháp luật (T1).
    Chỉ chạy trên 165 câu có verified gold (Tier A + Tier B).
    """
    @staticmethod
    def calculate_context_inclusion(result: RetrievalResult, ground_truth_context: Dict[str, Any]) -> float:
        gold_id = ground_truth_context.get("article_id")
        if not gold_id:
            return 0.0
            
        for chunk in result.chunks:
            if chunk.article_id == gold_id:
                return 1.0 # Tìm thấy văn bản đúng
        return 0.0

    @staticmethod
    def calculate_mrr(result: RetrievalResult, ground_truth_context: Dict[str, Any]) -> float:
        gold_id = ground_truth_context.get("article_id")
        if not gold_id:
            return 0.0
            
        for i, chunk in enumerate(result.chunks):
            if chunk.article_id == gold_id:
                return 1.0 / (i + 1) # Mean Reciprocal Rank
        return 0.0
