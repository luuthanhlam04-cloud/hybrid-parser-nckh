from src.ontology.edge_quality_filter import EdgeQualityFilter


def _relation(**overrides):
    relation = {
        "source": "e1",
        "target": "e2",
        "relation_type": "ALLOW",
        "evidence": "Người sử dụng đất được cấp giấy chứng nhận.",
    }
    relation.update(overrides)
    return relation


def test_accepts_well_formed_relation():
    accepted, reason = EdgeQualityFilter({"ALLOW"}).check(_relation(), "node-1")
    assert accepted is True
    assert reason is None


def test_rejects_missing_evidence():
    accepted, reason = EdgeQualityFilter({"ALLOW"}).check(
        _relation(evidence="   "), "node-1"
    )
    assert accepted is False
    assert reason == "missing_evidence"


def test_rejects_unknown_relation_type():
    accepted, reason = EdgeQualityFilter({"ALLOW"}).check(
        _relation(relation_type="UNKNOWN"), "node-1"
    )
    assert accepted is False
    assert reason == "unknown_relation_type"


def test_rejects_exact_duplicate_only_within_same_source_node():
    edge_filter = EdgeQualityFilter({"ALLOW"})
    assert edge_filter.check(_relation(), "node-1")[0] is True
    assert edge_filter.check(_relation(), "node-1")[1] == "duplicate_edge"
    assert edge_filter.check(_relation(), "node-2")[0] is True
