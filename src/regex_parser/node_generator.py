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
