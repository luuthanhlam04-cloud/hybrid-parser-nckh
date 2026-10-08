from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class Chunk(BaseModel):
    model_config = ConfigDict(extra='forbid')
    text: str
    article_id: Optional[str] = None
    rank: Optional[int] = None
    score: Optional[float] = None

class Entity(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str
    entity_type: str
    score: Optional[float] = None

class Relation(BaseModel):
    model_config = ConfigDict(extra='forbid')
    source: str
    target: str
    relation_type: str

class RetrievalResult(BaseModel):
    model_config = ConfigDict(extra='forbid')
    query_id: str
    chunks: List[Chunk] = []
    entities: List[Entity] = []
    relations: List[Relation] = []
    latency_ms: float = 0.0
    error: Optional[str] = None

class BaseRAGSystem(ABC):
    @abstractmethod
    def index(self, corpus_path: str) -> None:
        """Thực hiện Indexing toàn bộ corpus. Bắt buộc set fixed random seed."""
        pass
        
    @abstractmethod
    def retrieve(self, query_id: str, query: str) -> RetrievalResult:
        """Thực hiện tìm kiếm, trả về DTO nghiêm ngặt."""
        pass
        
    @abstractmethod
    def generate_answer(self, query: str, retrieval: RetrievalResult) -> str:
        """Sinh câu trả lời từ LLM."""
        pass
