# -*- coding: utf-8 -*-
from typing import List, Literal
from pydantic import BaseModel, Field, model_validator

EntityType = Literal[
    "SUBJECT", "ACTION", "CONDITION", "EXCEPTION",
    "PERMISSION", "OBLIGATION", "REFERENCE", "PENALTY"
]

RelationType = Literal[
    "ALLOW", "PROHIBIT", "REQUIRE", "HAS_CONDITION",
    "HAS_EXCEPTION", "REFERENCE_TO", "APPLY_TO"
]

class LegalEntity(BaseModel):
    id: str = Field(description="Mã định danh cục bộ, VD: e1, e2, e3")
    text: str = Field(description="Chuỗi văn bản trích xuất nguyên văn")
    entity_type: EntityType = Field(description="Loại thực thể theo Ontology chuẩn")
    evidence: str = Field(min_length=1, description="Đoạn trích nguyên văn làm bằng chứng, KHÔNG ĐỂ RỖNG")

class LegalRelation(BaseModel):
    source: str = Field(description="ID của thực thể nguồn (phải tồn tại trong entities)")
    relation_type: RelationType = Field(description="Loại quan hệ theo Ontology chuẩn")
    target: str = Field(description="ID của thực thể đích (phải tồn tại trong entities)")
    evidence: str = Field(min_length=1, description="Đoạn trích nguyên văn làm bằng chứng, KHÔNG ĐỂ RỖNG")

# Alias để tương thích ngược nếu có module khác gọi tới
LegalRelationship = LegalRelation

class SemanticExtraction(BaseModel):
    entities: List[LegalEntity] = Field(default_factory=list)
    relations: List[LegalRelation] = Field(default_factory=list)

    @model_validator(mode='after')
    def validate_referential_integrity(self) -> 'SemanticExtraction':
        # 1. Kiểm tra trùng lặp ID thực thể (Local ID Unique Check)
        entity_ids = [entity.id for entity in self.entities]
        if len(entity_ids) != len(set(entity_ids)):
            raise ValueError("Lỗi: Các thực thể đang bị trùng lặp ID. Mỗi thực thể phải có một ID duy nhất (e1, e2,...)!")

        # 2. Kiểm tra tính toàn vẹn tham chiếu của quan hệ
        valid_entity_ids = set(entity_ids)
        for rel in self.relations:
            if rel.source not in valid_entity_ids:
                raise ValueError(f"Source ID '{rel.source}' không tồn tại trong mảng entities!")
            if rel.target not in valid_entity_ids:
                raise ValueError(f"Target ID '{rel.target}' không tồn tại trong mảng entities!")
        return self
