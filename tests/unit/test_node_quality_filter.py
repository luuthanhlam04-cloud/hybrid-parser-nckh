from src.ontology.node_quality_filter import NodeQualityFilter


def test_filters_invalid_entity_and_orphan_relation():
    node_id, entities, relations = NodeQualityFilter().filter_node(
        {
            "node_id": "node-1",
            "extraction": {
                "entities": [
                    {
                        "id": "e1",
                        "text": "Người sử dụng đất",
                        "entity_type": "SUBJECT",
                        "evidence": "Người sử dụng đất có quyền.",
                    },
                    {
                        "id": "e2",
                        "text": "",
                        "entity_type": "ACTION",
                        "evidence": "x",
                    },
                ],
                "relations": [
                    {
                        "source": "e1",
                        "target": "e2",
                        "relation_type": "ALLOW",
                        "evidence": "Người sử dụng đất có quyền.",
                    }
                ],
            },
        }
    )
    assert node_id == "node-1"
    assert [entity["id"] for entity in entities] == ["e1"]
    assert relations == []


def test_drops_empty_node():
    node_id, entities, relations = NodeQualityFilter().filter_node(
        {"node_id": "node-2", "extraction": {"entities": [], "relations": []}}
    )
    assert node_id is None
    assert entities == []
    assert relations == []
