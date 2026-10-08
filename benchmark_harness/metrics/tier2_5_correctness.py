import json
from pydantic import BaseModel
from core.cost_tracker import CostTracker

class AnswerCorrectnessScore(BaseModel):
    reasoning: str
    score: float

class Tier25Correctness:
    """
    Tầng 2.5: Đánh giá độ chính xác của câu trả lời bằng LLM Judge (Pure Decimal).
    Áp dụng Anchor Rubric 6 mức. Model: GPT-4o-mini hoặc Gemini 1.5 Pro.
    """
    def __init__(self, cost_tracker: CostTracker):
        self.cost_tracker = cost_tracker
        # TODO: Load prompt template from prompts/tier2_5_prompts.json
        
    def evaluate(self, question: str, system_answer: str, gold_answer: str) -> AnswerCorrectnessScore:
        # TODO: Gọi API LLM thực tế tại đây
        # Tính phí vào budget
        estimated_cost = 0.002 # Ví dụ
        self.cost_tracker.add_cost("eval_judge", estimated_cost)
        
        # Dummy return để test flow
        return AnswerCorrectnessScore(reasoning="Mock evaluation based on 6-anchor rubric.", score=0.7)
