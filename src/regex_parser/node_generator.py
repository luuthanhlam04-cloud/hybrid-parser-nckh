from enum import Enum
from typing import Optional
from pydantic import BaseModel

class NodeType(str, Enum):
    PART = "PART"
    CHAPTER = "CHAPTER"
    SECTION = "SECTION"
    ARTICLE = "ARTICLE"
    CLAUSE = "CLAUSE"
    POINT = "POINT"
    TEXT = "TEXT"

class Position(BaseModel):
    start: int
    end: int

class LegalNode(BaseModel):
    id: str
    type: NodeType
    title: Optional[str] = None
    text: str
    parent_id: Optional[str] = None
    position: Position

def generate_hybrid_id(prefix: str, start_index: int) -> str:
    """
    Generates a unique hybrid ID using the hierarchical prefix and position offset suffix.
    Example: article_27_point_d_p1859
    """
    return f"{prefix}_p{start_index}"
