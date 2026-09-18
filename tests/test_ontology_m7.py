import pytest
import os
import sys

# Đảm bảo pytest tìm thấy src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ontology.entity_normalizer import EntityNormalizer
from src.ontology.relation_normalizer import RelationNormalizer
from src.ontology.ontology_validator import OntologyValidator
from src.ontology.ontology_builder import OntologyBuilder

@pytest.fixture
def sample_taxonomy():
    return {
        "action.transaction.transfer": {
            "ontology_class": "LEGAL_ACTION",
            "canonical_text": "Chuyển nhượng",
            "aliases": ["chuyển nhượng", "mua bán"]
        },
        "subject.state": {
            "ontology_class": "LEGAL_SUBJECT",
            "canonical_text": "Nhà nước",
            "aliases": ["nhà nước", "chính phủ"]
        },
        "subject.test_ambiguous": {
            "ontology_class": "LEGAL_SUBJECT",
            "canonical_text": "Quyền giả lập",
            "aliases": ["quyền"]
        },
        "action.test_ambiguous": {
            "ontology_class": "LEGAL_ACTION",
            "canonical_text": "Thực hiện quyền",
            "aliases": ["quyền"]
        }
    }

def test_class_constrained_exact_match(sample_taxonomy):
    # Test 1: EXACT MATCH + Class Constrained
    # ACTION + "chuyển nhượng"
    normalizer = EntityNormalizer(sample_taxonomy)
    res = normalizer.normalize("chuyển nhượng", "ACTION", "node1", "e1")
    assert res["canonical_id"] == "action.transaction.transfer"
    assert res["match_method"] == "EXACT"

def test_cross_class_protection(sample_taxonomy):
    # Test 2: MUST NOT return LEGAL_SUBJECT when extracting ACTION
    # Dùng text "nhà nước" nhưng fallback type là ACTION
    normalizer = EntityNormalizer(sample_taxonomy)
    res = normalizer.normalize("nhà nước", "ACTION", "node1", "e1")
    assert res["match_method"] == "QUARANTINED"
    assert res["canonical_id"].startswith("UNRESOLVED:node1:e1")

def test_canonical_text_matching(sample_taxonomy):
    # Test 3: Exact match on canonical_text
    normalizer = EntityNormalizer(sample_taxonomy)
    res = normalizer.normalize("Chuyển nhượng", "ACTION", "node1", "e1")
    assert res["canonical_id"] == "action.transaction.transfer"

def test_ambiguous_alias(sample_taxonomy):
    # Test 4: Alias collision
    normalizer = EntityNormalizer(sample_taxonomy)
    # text "quyền" matches both subject.test_ambiguous and action.test_ambiguous
    res = normalizer.normalize("quyền", "ACTION", "node1", "e1")
    # Due to collision, the exact match list has > 1 items, which drops to QUARANTINE or FUZZY.
    # In FUZZY, only action class is kept (valid_can_ids).
    # Since "quyền" is exact match, fuzz.ratio is 100.
    # There is only ONE valid action candidate, so best_score = 100, second_best = 0.
    # Thus, it will resolve to action.test_ambiguous! Wait, this is fine because of class constraint.
    assert res["canonical_id"] == "action.test_ambiguous"
    
def test_fuzzy_match(sample_taxonomy):
    # Test 5: Small typo -> correct class
    normalizer = EntityNormalizer(sample_taxonomy)
    res = normalizer.normalize("chuyển nượng", "ACTION", "node1", "e1")
    assert res["canonical_id"] == "action.transaction.transfer"
    assert res["match_method"] == "FUZZY"

def test_fuzzy_ambiguity(sample_taxonomy):
    # Test 6: Two candidates with similar scores -> quarantine
    # Add two similar actions
    sample_taxonomy["action.buy1"] = {"ontology_class": "LEGAL_ACTION", "canonical_text": "chuyển giao nhà", "aliases": []}
    sample_taxonomy["action.buy2"] = {"ontology_class": "LEGAL_ACTION", "canonical_text": "chuyển giao đất", "aliases": []}
    normalizer = EntityNormalizer(sample_taxonomy)
    # text "chuyển giao" fuzz with "chuyển giao nhà" (92) and "chuyển giao đất" (92)
    # This triggers fuzzy ambiguity
    res = normalizer.normalize("chuyển giao", "ACTION", "node1", "e1")
    assert res["match_method"] == "QUARANTINED"
    
def test_unknown_apply_to(sample_taxonomy):
    # Test 12: UNKNOWN_RELATION for APPLY_TO
    class DummyMapper:
        def get_relation_constraints(self, rel_type):
            if rel_type == "ALLOW": return {"domain": ["LEGAL_SUBJECT"], "range": ["LEGAL_ACTION"]}
            return None
    validator = OntologyValidator(DummyMapper())
    canonical_entities = {
        "s1": {"ontology_class": "LEGAL_SUBJECT"},
        "a1": {"ontology_class": "LEGAL_ACTION"}
    }
    is_valid, reason = validator.validate_relation({"relation_type": "APPLY_TO", "source": "s1", "target": "a1"}, canonical_entities)
    assert not is_valid
    assert "UNKNOWN_M6_RELATION" in reason
