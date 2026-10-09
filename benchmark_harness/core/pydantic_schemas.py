from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional, Any

# ==========================================
# 1. INPUT SCHEMAS (Đầu vào từ Data)
# ==========================================
class BenchmarkQuestion(BaseModel):
    """Cấu trúc một câu hỏi trong benchmark_rewritten.json"""
    model_config = ConfigDict(extra='ignore')
    
    question_id: str
    question: str
    relevant_articles: List[str]
    category: str
    law_name: Optional[str] = None
    num_articles: Optional[int] = None
    difficulty: Optional[Any] = None
    source: Optional[str] = None
    answer: Optional[str] = None

# ==========================================
# 2. OUTPUT SCHEMAS (Kết quả từ 3 hệ thống RAG)
# ==========================================
class RetrievalResult(BaseModel):
    """Cấu trúc một văn bản được Retrieve về"""
    article_id: str
    score: float = Field(default=0.0, description="Điểm số")
    text: str = Field(..., description="TOÀN BỘ văn bản điều luật để chấm Tầng 2,3")

class SystemResponse(BaseModel):
    """Kết quả trả về chuẩn hóa của mọi hệ thống RAG end-to-end"""
    question_id: str
    retrieved_docs: List[RetrievalResult] = Field(..., max_items=10, description="Top K kết quả")
    generation: str = Field(..., description="Câu trả lời sinh ra bởi LLM (bắt buộc cho cả 3 hệ thống)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Lưu latency_ms, tokens...")

# ==========================================
# 3. EVALUATION SCHEMAS (Kết quả chấm điểm của Harness)
# ==========================================
class EvaluationScore(BaseModel):
    """Cấu trúc lưu điểm số cho Từng Câu Hỏi"""
    question_id: str
    system_name: str
    
    # Tầng 1: Retrieval
    recall_at_5: float
    mrr_at_5: float
    refusal_correct: Optional[bool] = Field(default=None, description="Dành cho Negative")
    refusal_appropriate: Optional[bool] = Field(default=None, description="Dành cho Negative (có từ chối đúng lý do luật không quy định không)")
    false_positive: Optional[bool] = Field(default=None, description="Dành cho Negative")
    strict_match: Optional[bool] = Field(default=None, description="True nếu retrieve đủ TẤT CẢ relevant_articles trong top-5")
    
    # Tầng 2 & 3: Semantic & Legal (Chấm bằng LLM)
    context_precision: Optional[float] = None
    faithfulness: Optional[float] = None
    citation_accuracy: Optional[float] = None
    reasoning_coverage: Optional[float] = None
    
    # Metadata
    evaluator_model: Optional[str] = Field(default=None, description="Tên LLM giám khảo")
    eval_latency_ms: Optional[float] = None

# ==========================================
# 4. AGGREGATE SCHEMAS (Tổng hợp Báo Cáo)
# ==========================================
class AggregateScore(BaseModel):
    system_name: str
    total_questions: int
    avg_recall_at_5: float
    avg_mrr_at_5: float
    avg_context_precision: Optional[float] = None
    avg_faithfulness: Optional[float] = None
    avg_citation_accuracy: Optional[float] = None
    by_category: Dict[str, Dict[str, float]]
    by_source: Dict[str, Dict[str, float]]
