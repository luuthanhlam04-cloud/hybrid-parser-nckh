import json
import os
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

class Annotation(BaseModel):
    model_config = ConfigDict(extra='ignore')
    created_by: Optional[str] = None
    verified: bool = False
    verified_by: Optional[str] = None
    notes: Optional[str] = None

class BenchmarkQuestion(BaseModel):
    model_config = ConfigDict(extra='ignore')
    question_id: str
    question_type: str
    difficulty_level: str
    question: str
    expected_answer: str
    ground_truth_context: Optional[Dict[str, Any]] = None
    hard_negative_context: Optional[Dict[str, Any]] = None
    hop_chain: Optional[List[str]] = None
    usable_tiers: List[str] = []
    annotation: Optional[Annotation] = None

class DatasetLoader:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.metadata = {}
        self.questions: List[BenchmarkQuestion] = []
        self._load()

    def _load(self):
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Dataset file not found: {self.filepath}")
        
        with open(self.filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        self.metadata = data.get('benchmark_metadata', {})
        raw_questions = data.get('questions', [])
        
        for q in raw_questions:
            self.questions.append(BenchmarkQuestion(**q))
            
    def get_questions_for_tier(self, tier: str) -> List[BenchmarkQuestion]:
        """Lọc và trả về danh sách câu hỏi được phép chạy cho Tầng (Tier) này."""
        return [q for q in self.questions if tier in q.usable_tiers]
        
    def __len__(self):
        return len(self.questions)
