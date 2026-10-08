from typing import Dict
from core.config import EVAL_SOFT_LIMIT_USD, EVAL_HARD_LIMIT_USD

class CostTracker:
    """
    CostTracker acts strictly as an operational guardrail.
    It does not measure system tokens as an academic contribution.
    """
    def __init__(self):
        self.total_cost = 0.0
        # Thống kê chi tiết theo từng tag để dễ debug
        self.tag_costs: Dict[str, float] = {
            "system": 0.0,        # LightRAG extraction
            "eval_judge": 0.0,    # T2, T2.5, T4-judge
            "eval_lsv": 0.0,      # T4-LSV extractor (GPT-4o-mini)
        }

    def add_cost(self, tag: str, cost: float):
        if tag not in self.tag_costs:
            self.tag_costs[tag] = 0.0
        
        self.tag_costs[tag] += cost
        self.total_cost += cost
        self.check_limit()
        
    def check_limit(self):
        if self.total_cost > EVAL_HARD_LIMIT_USD:
            raise RuntimeError(f"HARD LIMIT REACHED: Total cost ${self.total_cost:.4f} exceeded limit ${EVAL_HARD_LIMIT_USD}")
        elif self.total_cost > EVAL_SOFT_LIMIT_USD:
            print(f"[WARNING] SOFT LIMIT EXCEEDED: Total cost ${self.total_cost:.4f} > ${EVAL_SOFT_LIMIT_USD}")

    def report(self) -> str:
        return (
            f"Total: ${self.total_cost:.4f} | "
            f"System: ${self.tag_costs.get('system', 0):.4f} | "
            f"Eval-Judge: ${self.tag_costs.get('eval_judge', 0):.4f} | "
            f"Eval-LSV: ${self.tag_costs.get('eval_lsv', 0):.4f}"
        )
