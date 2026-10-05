# -*- coding: utf-8 -*-
# pyrefly: ignore [missing-import]
import pytest
from pydantic import ValidationError
from src.llm_extraction.schema_manager import (
    SemanticExtraction, LegalEntity, LegalRelation
)
from src.llm_extraction.retry_controller import safe_retry_extractor

def test_valid_extraction():
    data = SemanticExtraction(
        entities=[
            LegalEntity(id="e1", text="Người sử dụng đất", entity_type="SUBJECT", evidence="Người sử dụng đất có quyền..."),
            LegalEntity(id="e2", text="chuyển nhượng quyền sử dụng đất", entity_type="ACTION", evidence="chuyển nhượng quyền sử dụng đất")
        ],
        relations=[
            LegalRelation(source="e1", relation_type="ALLOW", target="e2", evidence="Người sử dụng đất có quyền chuyển nhượng quyền sử dụng đất")
        ]
    )
    assert len(data.entities) == 2
    assert len(data.relations) == 1
    assert data.relations[0].relation_type == "ALLOW"

def test_duplicate_entity_id():
    with pytest.raises(ValidationError) as excinfo:
        SemanticExtraction(
            entities=[
                LegalEntity(id="e1", text="Người sử dụng đất", entity_type="SUBJECT", evidence="Người sử dụng đất"),
                LegalEntity(id="e1", text="Nhà nước", entity_type="SUBJECT", evidence="Nhà nước")
            ],
            relations=[]
        )
    assert "trùng lặp ID" in str(excinfo.value)

def test_broken_referential_integrity():
    with pytest.raises(ValidationError) as excinfo:
        SemanticExtraction(
            entities=[
                LegalEntity(id="e1", text="Người sử dụng đất", entity_type="SUBJECT", evidence="Người sử dụng đất")
            ],
            relations=[
                LegalRelation(source="e1", relation_type="ALLOW", target="e99", evidence="bằng chứng")
            ]
        )
    assert "Target ID 'e99' không tồn tại" in str(excinfo.value)

def test_empty_evidence():
    with pytest.raises(ValidationError):
        LegalEntity(id="e1", text="Người sử dụng đất", entity_type="SUBJECT", evidence="")

def test_invalid_relation_type():
    with pytest.raises(ValidationError):
        LegalRelation(source="e1", relation_type="HAS_RIGHT", target="e2", evidence="evidence snippet")

def test_invalid_entity_type():
    with pytest.raises(ValidationError):
        LegalEntity(id="e1", text="test", entity_type="INVALID_TYPE", evidence="evidence")

def test_hohfeld_relation_types():
    for rel_type in ["ALLOW", "REQUIRE", "PROHIBIT"]:
        rel = LegalRelation(source="e1", relation_type=rel_type, target="e2", evidence="ev")
        assert rel.relation_type == rel_type

def test_fail_safe_retry_controller():
    @safe_retry_extractor(max_attempts=2)
    def buggy_extractor():
        # Cố tình ném ValidationError
        LegalEntity(id="e1", text="test", entity_type="INVALID", evidence="test")

    # Hàm phải bắt ValidationError và trả về SemanticExtraction rỗng an toàn
    result = buggy_extractor()
    assert isinstance(result, SemanticExtraction)
    assert result.entities == []
    assert result.relations == []
