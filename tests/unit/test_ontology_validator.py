from src.ontology.ontology_validator import OntologyValidator


class _Mapper:
    schema = {
        "relations": {
            "HAS_CONDITION": {
                "domain": ["NODE"],
                "range": ["NODE"],
                "self_loop": False,
                "max_depth": 2,
            }
        }
    }

    def get_relation_constraints(self, relation_type):
        return self.schema["relations"].get(relation_type)


def _entities(*pairs):
    return {
        entity_id: {"ontology_class": entity_class}
        for entity_id, entity_class in pairs
    }


def _relation(source, target):
    return {
        "relation_type": "HAS_CONDITION",
        "source": source,
        "target": target,
    }


def test_allows_relation_chain_up_to_max_depth():
    validator = OntologyValidator(_Mapper())
    entities = _entities(
        ("a", "NODE"),
        ("condition", "NODE"),
        ("b", "NODE"),
    )
    first = _relation("a", "condition")
    assert validator.validate_relation(first, entities)[0] is True
    validator.register_accepted_relation(first)

    second = _relation("condition", "b")
    assert validator.validate_relation(second, entities)[0] is True


def test_rejects_third_level_same_type_chain():
    validator = OntologyValidator(_Mapper())
    entities = _entities(
        ("a", "NODE"),
        ("x", "NODE"),
        ("y", "NODE"),
        ("z", "NODE"),
    )
    first = _relation("a", "x")
    second = _relation("x", "y")
    third = _relation("y", "z")

    assert validator.validate_relation(first, entities)[0] is True
    validator.register_accepted_relation(first)
    assert validator.validate_relation(second, entities)[0] is True
    validator.register_accepted_relation(second)
    accepted, reason = validator.validate_relation(third, entities)
    assert accepted is False
    assert reason.startswith("MAX_DEPTH:")
