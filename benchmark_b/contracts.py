"""Versioned, system-independent evaluation contracts."""
from typing import Literal
from pydantic import BaseModel, Field


class CanonicalLocator(BaseModel):
    law_code: str = '31/2024/QH15'
    article: str
    clause: str | None = None
    point: str | None = None

    @property
    def canonical_locator(self):
        return f'LD2024:A{self.article}' + (f':K{self.clause}' if self.clause else '') + (f':D{self.point}' if self.point else '')


class EvidenceItem(BaseModel):
    rank: int = Field(ge=1)
    raw_source_id: str
    canonical_locators: list[str] = Field(default_factory=list)
    granularity: str
    alignment_status: Literal['EXACT', 'ANCESTOR_ONLY', 'ARTICLE_ONLY', 'UNRESOLVED']
    retrieval_score: float | None = None
    text: str
    stage: str = 'retrieved'


class ReferenceStep(BaseModel):
    source: str
    relation_type: Literal['DIRECT_REFERENCE', 'REQUIRES_CONDITION_FROM', 'EXCEPTION_REFERENCE', 'PARENT_CHILD_CONTEXT', 'INHERITS_RIGHTS_OBLIGATIONS', 'EXTERNAL_REFERENCE']
    target: str
    review_status: str = 'HUMAN_REVIEW_REQUIRED'


class AtomicFact(BaseModel):
    fact_id: str
    text: str
    role: str
    required: bool = True
    weight: float = Field(default=1, gt=0)
    evidence_any_of: list[str]
    review_status: str = 'HUMAN_REVIEW_REQUIRED'
