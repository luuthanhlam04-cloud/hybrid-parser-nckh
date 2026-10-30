from src.fusion.conflict_resolver import ConflictResolver


def test_scope_classification_does_not_equate_different_condition_ids():
    classify = ConflictResolver._scope_status
    assert classify(["giao đất có thu tiền sử dụng đất"], ["giao đất không thu tiền sử dụng đất"], False)[0] == "CONTEXTUAL_DIFFERENCE"
    assert classify(["trong khu công nghiệp"], ["pháp luật không cho phép nhận chuyển nhượng"], False)[0] == "REVIEW_REQUIRED"
    assert classify(["trong thời hạn sử dụng đất"], ["trong thời hạn sử dụng đất"], False)[0] == "POTENTIAL_LEGAL_CONFLICT"
    assert classify([], [], False)[0] == "REVIEW_REQUIRED"
    assert classify(["có giấy chứng nhận"], ["có giấy chứng nhận"], True)[0] == "REVIEW_REQUIRED"


def test_detects_real_same_scope_pair_and_keeps_provenance():
    def norm(nid, modality, source):
        return {"id": nid, "properties": {"ontology_class": "GLOBAL_NORM", "modality": modality, "source_node_ids": [source]}}

    nodes = [norm("a", "ALLOW", "physical-a"), norm("p", "PROHIBIT", "physical-p"),
             {"id": "c", "properties": {"canonical_text": "Trong cùng trường hợp"}}]
    edges = [
        {"source": nid, "target": target, "type": rel}
        for nid in ("a", "p")
        for rel, target in (("HAS_SUBJECT", "subject"), ("HAS_ACTION", "action"), ("HAS_CONDITION", "c"))
    ]
    results = ConflictResolver().detect_deontic_conflicts(nodes, edges)
    assert len(results) == 1
    assert results[0]["flag"] == "POTENTIAL_LEGAL_CONFLICT"
    assert results[0]["source_node_ids"] == {"a": ["physical-a"], "p": ["physical-p"]}


def test_different_objects_require_review_even_with_same_conditions():
    nodes = [
        {"id": nid, "properties": {"ontology_class": "GLOBAL_NORM", "modality": modality}}
        for nid, modality in (("a", "ALLOW"), ("p", "PROHIBIT"))
    ]
    nodes.append({"id": "c", "properties": {"canonical_text": "trong cùng trường hợp"}})
    edges = [
        {"source": nid, "target": target, "type": rel}
        for nid in ("a", "p")
        for rel, target in (("HAS_SUBJECT", "s"), ("HAS_ACTION", "act"), ("HAS_CONDITION", "c"))
    ]
    edges.extend([
        {"source": "a", "target": "land", "type": "HAS_OBJECT"},
        {"source": "p", "target": "asset", "type": "HAS_OBJECT"},
    ])
    assert ConflictResolver().detect_deontic_conflicts(nodes, edges)[0]["context_status"] == "OBJECT_SCOPE_NOT_PROVEN_EQUAL"


def test_m6_corrections_are_grounded_and_repeatable():
    import json
    from pathlib import Path
    from scripts.correct_m6_conflict_nodes import apply_corrections

    root = Path(__file__).resolve().parents[2]
    m6 = json.loads((root / "outputs/semantic_graphs/semantic_extraction.json").read_text(encoding="utf-8"))
    physical = json.loads((root / "outputs/physical_graphs/physical_graph.json").read_text(encoding="utf-8"))
    snapshot = json.dumps(m6, ensure_ascii=False, sort_keys=True)
    result = apply_corrections(m6, physical)
    assert json.dumps(result, ensure_ascii=False, sort_keys=True) == snapshot
    assert result["metadata"]["total_candidates_processed"] == 180


def test_review_findings_are_materialized_as_queryable_links():
    from src.fusion.fusion_engine import FusionEngine

    nodes = [
        {"id": "norm-a", "node_kind": "SEMANTIC", "labels": [], "properties": {}},
        {"id": "norm-p", "node_kind": "SEMANTIC", "labels": [], "properties": {}},
        {"id": "physical-a", "node_kind": "PHYSICAL", "labels": [], "properties": {}},
        {"id": "physical-p", "node_kind": "PHYSICAL", "labels": [], "properties": {}},
    ]
    reviews = [{
        "flag": "REVIEW_REQUIRED",
        "conflict_type": "ALLOW_PROHIBIT",
        "context_status": "EXCEPTION_SCOPE_REQUIRES_REVIEW",
        "relation_types": ["ALLOW", "PROHIBIT"],
        "global_norm_ids": ["norm-a", "norm-p"],
        "source_node_ids": {"norm-a": ["physical-a"], "norm-p": ["physical-p"]},
    }]
    review_nodes, review_edges = FusionEngine._materialize_conflict_reviews(reviews, nodes)
    assert review_nodes[0]["labels"] == ["REVIEW_FINDING"]
    assert {(edge["type"], edge["target"]) for edge in review_edges} == {
        ("REVIEW_POSITIVE_NORM", "norm-a"),
        ("REVIEW_PROHIBITIVE_NORM", "norm-p"),
        ("REVIEW_SOURCE_NODE", "physical-a"),
        ("REVIEW_SOURCE_NODE", "physical-p"),
    }
