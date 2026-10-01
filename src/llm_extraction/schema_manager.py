# -*- coding: utf-8 -*-
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, model_validator

EntityType = Literal[
    "SUBJECT", "ACTION", "OBJECT", "CONDITION",
    "EXCEPTION", "REFERENCE", "PENALTY"
]

RelationType = Literal[
    "ALLOW", "PROHIBIT", "REQUIRE", "HAS_CONDITION",
    "HAS_EXCEPTION", "REFERENCE_TO", "HAS_OBJECT", "HAS_PENALTY"
]

class LegalEntity(BaseModel):
    id: str = Field(description="Mã định danh cục bộ, VD: e1, e2, e3")
    text: str = Field(description="Chuỗi văn bản trích xuất nguyên văn")
    entity_type: EntityType = Field(description="Loại thực thể theo Ontology chuẩn")
    evidence: str = Field(min_length=1, description="Đoạn trích nguyên văn làm bằng chứng, KHÔNG ĐỂ RỖNG")

class LegalRelation(BaseModel):
    source: Optional[str] = Field(default=None, description="ID của thực thể nguồn (phải tồn tại trong entities hoặc null)")
    relation_type: RelationType = Field(description="Loại quan hệ theo Ontology chuẩn")
    target: str = Field(description="ID của thực thể đích (phải tồn tại trong entities)")
    source_status: Literal["RESOLVED", "CONTEXT_INFERRED", "UNRESOLVED"] = Field(
        default="RESOLVED",
        description="Trạng thái nguồn: Đã xác định, Suy luận từ bối cảnh, Không xác định"
    )
    evidence: str = Field(min_length=1, description="Đoạn trích nguyên văn làm bằng chứng, KHÔNG ĐỂ RỖNG")

    @model_validator(mode='after')
    def validate_source_logic(self) -> 'LegalRelation':
        if self.source is None and self.source_status != "UNRESOLVED":
            raise ValueError(f"Relation {self.relation_type}: source=None bắt buộc source_status='UNRESOLVED'")
        if self.source is not None and self.source_status == "UNRESOLVED":
            raise ValueError(f"Relation {self.relation_type}: source có ID không thể UNRESOLVED")
        if self.source is None and self.relation_type not in {"ALLOW", "REQUIRE", "PROHIBIT"}:
            raise ValueError(f"Relation {self.relation_type} KHÔNG ĐƯỢC PHÉP khuyết source")
        return self

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
            if rel.source is not None and rel.source not in valid_entity_ids:
                raise ValueError(f"Source ID '{rel.source}' không tồn tại trong mảng entities!")
            if rel.target not in valid_entity_ids:
                raise ValueError(f"Target ID '{rel.target}' không tồn tại trong mảng entities!")
        return self
