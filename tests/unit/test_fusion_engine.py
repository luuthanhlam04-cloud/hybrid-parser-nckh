import json

from src.fusion.conflict_resolver import ConflictResolver
from src.fusion.confidence_calibration import (
    IsotonicConfidenceCalibrator,
    evaluate_confidence,
)
from src.fusion.delta_engine import DeltaEngine, Neo4jDeltaApplier
from src.fusion.edge_mapper import calibrated_confidence
from src.fusion.fusion_engine import FusionEngine
from src.fusion.graph_contract import GraphContractError
from src.fusion.node_mapper import NodeMapper
from src.fusion.quality_evaluation import evaluate_quality_csv
from src.fusion.shacl_validator import ShaclValidator
from scripts.sample_fusion_eval import sample_fusion_eval


def test_context_stack_resolves_article():
    nodes = [
        {"id": "article", "labels": ["ARTICLE"], "properties": {"parent_id": None}},
        {"id": "clause", "labels": ["CLAUSE"], "properties": {"parent_id": "article"}},
    ]
    assert NodeMapper(nodes).scope_for_text("clause", "theo quy định tại Điều này") == "article"


def test_reference_scope_classifies_document_general_and_external_scopes():
    mapper = NodeMapper([{
        "id": "article",
        "labels": ["ARTICLE"],
        "properties": {
            "law_code": "59/2024/QH15",
            "source_doc": "Luat_dat_dai_2024.docx",
        },
    }])
    assert mapper.classify_reference_scope(
        "Luật này", "SAME_DOCUMENT", "article"
    ) == "DOCUMENT_LEVEL_REF"
    assert mapper.classify_reference_scope(
        "theo quy định của pháp luật về đất đai", "", "article"
    ) == "GENERAL_LEGAL_SCOPE"
    assert mapper.classify_reference_scope(
        "Luật 12/2023/QH15", "", "article"
    ) == "EXTERNAL_SCOPE"


def test_deontic_conflict_is_reported_without_exception():
    edges = [
        {"source": "s", "target": "a", "type": "ALLOW", "properties": {"relation_id": "r1"}},
        {"source": "s", "target": "a", "type": "PROHIBIT", "properties": {"relation_id": "r2"}},
    ]
    conflicts = ConflictResolver().detect_deontic_conflicts(edges)
    assert conflicts[0]["flag"] == "POTENTIAL_LEGAL_CONFLICT"


def test_require_implies_allow_for_conflict_detection():
    edges = [
        {"source": "s", "target": "a", "type": "REQUIRE", "properties": {"relation_id": "r1"}},
        {"source": "s", "target": "a", "type": "PROHIBIT", "properties": {"relation_id": "r2"}},
    ]
    conflicts = ConflictResolver().detect_deontic_conflicts(edges)
    assert conflicts[0]["conflict_type"] == "REQUIRE_PROHIBIT"
    assert conflicts[0]["relation_ids"] == ["r1", "r2"]
    assert "REQUIRE" in conflicts[0]["message"]


def test_deontic_conflict_respects_distinct_explicit_conditions():
    edges = [
        {"source": "s", "target": "a", "type": "REQUIRE",
         "properties": {"relation_id": "r1", "source_node_id": "p1"}},
        {"source": "a", "target": "c1", "type": "HAS_CONDITION",
         "properties": {"source_node_id": "p1"}},
        {"source": "s", "target": "a", "type": "PROHIBIT",
         "properties": {"relation_id": "r2", "source_node_id": "p2"}},
        {"source": "a", "target": "c2", "type": "HAS_CONDITION",
         "properties": {"source_node_id": "p2"}},
    ]
    conflicts = ConflictResolver().detect_deontic_conflicts(edges)
    assert len(conflicts) == 1
    assert conflicts[0]["context_status"] == "DISTINCT_EXPLICIT_CONDITIONS_REQUIRES_REVIEW"


def test_linked_exception_in_same_physical_scope_suppresses_conflict():
    edges = [
        {"source": "s", "target": "a", "type": "REQUIRE",
         "properties": {"relation_id": "r1", "source_node_id": "p"}},
        {"source": "s", "target": "a", "type": "PROHIBIT",
         "properties": {"relation_id": "r2", "source_node_id": "p"}},
        {"source": "a", "target": "exception", "type": "HAS_EXCEPTION",
         "properties": {"source_node_id": "p"}},
    ]
    assert ConflictResolver().detect_deontic_conflicts(edges) == []


def test_confidence_is_bounded_and_combines_signals():
    assert calibrated_confidence(
        {"properties": {"confidence_m6": 1.0, "similarity": 1.0}},
        {},
    ) == 1.0
    assert 0.0 <= calibrated_confidence({"properties": {}}, {}) <= 1.0
    assert calibrated_confidence(
        {"properties": {"confidence_m6": 0.8, "similarity": 0.5}},
        {"source_confidence": 0.5},
    ) == 0.45
    class Calibrator:
        def predict(self, score):
            return score / 2

    from src.fusion.edge_mapper import EdgeMapper

    calibrated = EdgeMapper(Calibrator()).semantic(
        {
            "relation_id": "r",
            "relation_type": "ALLOW",
            "source": "s",
            "target": "a",
            "confidence_m6": 1.0,
            "similarity": 1.0,
        },
        {},
    )
    assert calibrated["properties"]["confidence"] == 0.5
    assert calibrated["properties"]["confidence_status"] == "calibrated"


def test_isotonic_confidence_calibration_and_metrics(tmp_path):
    calibrator = IsotonicConfidenceCalibrator().fit(
        [0.1, 0.2, 0.8, 0.9], [0, 0, 1, 1]
    )
    assert calibrator.predict(0.15) == 0.0
    assert calibrator.predict(0.85) == 1.0
    path = tmp_path / "calibrator.json"
    calibrator.save(path)
    loaded = IsotonicConfidenceCalibrator.load(path)
    assert loaded.predict(0.85) == 1.0
    report = evaluate_confidence([0, 1], [0.1, 0.9])
    assert report["brier_score"] == 0.01
    assert report["precision_at_threshold"] == 1.0
    tied = IsotonicConfidenceCalibrator().fit(
        [0.5, 0.5, 0.8], [0, 1, 1]
    )
    assert tied.predict(0.5) == 0.5


def test_quality_evaluation_reports_metrics_and_annotator_agreement(tmp_path):
    path = tmp_path / "quality.csv"
    path.write_text(
        "task,case_id,expected,predicted,split,reviewer,annotation,notes\n"
        "deontic_conflict,c1,1,1,test,r1,1,\n"
        "deontic_conflict,c1,1,1,test,r2,1,\n"
        "deontic_conflict,c2,0,1,test,r1,0,\n"
        "deontic_conflict,c2,0,1,test,r2,0,\n",
        encoding="utf-8",
    )
    report = evaluate_quality_csv(path, "deontic_conflict")
    assert report["count"] == 2
    assert report["annotator_agreement_kappa"] == 1.0
    assert report["precision_positive"] == 0.5


def test_fusion_preserves_physical_edges_and_writes_output(tmp_path):
    physical = {
        "nodes": [
            {"id": "p1", "labels": ["ARTICLE"], "properties": {"parent_id": None}},
        ],
        "edges": [{"source": "p1", "target": "p1", "type": "NEXT", "properties": {}}],
    }
    semantic = {
        "entities": [
            {"canonical_id": "s", "ontology_class": "LEGAL_SUBJECT"},
            {"canonical_id": "a", "ontology_class": "LEGAL_ACTION"},
        ],
        "relations": [{
            "relation_id": "r1", "relation_type": "ALLOW", "source": "s",
            "target": "a", "source_node_id": "p1", "evidence": "được phép",
        }],
    }
    physical_path = tmp_path / "physical.json"
    semantic_path = tmp_path / "semantic.json"
    output_path = tmp_path / "unified.json"
    physical_path.write_text(json.dumps(physical), encoding="utf-8")
    semantic_path.write_text(json.dumps(semantic), encoding="utf-8")
    result = FusionEngine().fuse(physical_path, semantic_path, output_path)
    assert result["metadata"]["physical_edge_count"] == 1
    assert any(edge["type"] == "MENTIONS" for edge in result["edges"])
    assert output_path.exists()


def test_fusion_report_counts_require_prohibit_conflict(tmp_path):
    physical_path = tmp_path / "physical.json"
    semantic_path = tmp_path / "semantic.json"
    physical_path.write_text(json.dumps({
        "nodes": [{"id": "p", "labels": ["ARTICLE"], "properties": {}}],
        "edges": [],
    }), encoding="utf-8")
    semantic_path.write_text(json.dumps({
        "entities": [
            {"canonical_id": "s", "ontology_class": "LEGAL_SUBJECT"},
            {"canonical_id": "a", "ontology_class": "LEGAL_ACTION"},
        ],
        "relations": [
            {
                "relation_id": "r1", "relation_type": "REQUIRE",
                "source_node_id": "p", "source": "s", "target": "a",
                "evidence": "phải thực hiện",
            },
            {
                "relation_id": "r2", "relation_type": "PROHIBIT",
                "source_node_id": "p", "source": "s", "target": "a",
                "evidence": "nghiêm cấm",
            },
        ],
    }), encoding="utf-8")
    result = FusionEngine().fuse(physical_path, semantic_path)
    assert result["fusion_report"]["deontic_conflict_count"] == 1
    assert result["conflicts"][0]["relation_ids"] == ["r1", "r2"]


def test_resolves_explicit_clause_article_reference():
    nodes = [
        {"id": "chapter", "labels": ["CHAPTER"], "properties": {
            "number": "III", "law_code": "L1",
            "source_doc": "Luat_dat_dai_chuong_3.docx", "parent_id": None,
        }},
        {"id": "article10", "labels": ["ARTICLE"], "properties": {
            "number": "10", "law_code": "L1", "parent_id": "chapter",
        }},
        {"id": "clause2", "labels": ["CLAUSE"], "properties": {
            "number": "2", "law_code": "L1", "parent_id": "article10",
        }},
        {"id": "source", "labels": ["CLAUSE"], "properties": {
            "number": "1", "law_code": "L1", "parent_id": "article10",
        }},
    ]
    mapper = NodeMapper(nodes)
    assert mapper.resolve_reference_text("khoản 2 Điều 10", "source") == ["clause2"]
    assert mapper.resolve_anaphoric_reference(
        "khoản 2 Điều này", "source"
    ) == ["clause2"]
    assert mapper.resolve_reference_text("Điều 10 Luật Nhà ở", "source") == []
    assert mapper.resolve_reference_text(
        "Điều 10 Luật Đất đai 2024", "source"
    ) == ["article10"]
    assert mapper.resolve_anaphoric_reference("Điều này", "source") == ["article10"]


def test_ambiguous_reference_does_not_resolve_to_multiple_physical_nodes():
    nodes = [
        {"id": "article-a", "labels": ["ARTICLE"], "properties": {
            "number": "10", "law_code": "L1", "parent_id": None,
        }},
        {"id": "article-b", "labels": ["ARTICLE"], "properties": {
            "number": "10", "law_code": "L1", "parent_id": None,
        }},
        {"id": "source", "labels": ["CLAUSE"], "properties": {
            "number": "1", "law_code": "L1", "parent_id": "article-a",
        }},
    ]
    assert NodeMapper(nodes).resolve_reference_text("Điều 10", "source") == []


def test_fuses_norm_based_m7_output_and_resolves_reference(tmp_path):
    physical = {
        "nodes": [
            {"id": "article9", "labels": ["LegalNode", "ARTICLE"],
             "properties": {"number": "9", "law_code": "L1", "parent_id": None}},
            {"id": "source", "labels": ["LegalNode", "CLAUSE"],
             "properties": {"number": "1", "law_code": "L1", "parent_id": "article9"}},
            {"id": "article10", "labels": ["LegalNode", "ARTICLE"],
             "properties": {"number": "10", "law_code": "L1", "parent_id": None}},
            {"id": "clause2", "labels": ["LegalNode", "CLAUSE"],
             "properties": {"number": "2", "law_code": "L1", "parent_id": "article10"}},
        ],
        "edges": [],
    }
    semantic = {
        "concepts": [
            {"id": "concept.subject", "concept_type": "LegalSubject",
             "preferred_name": "Chủ thể", "alt_labels": []},
            {"id": "concept.action", "concept_type": "LegalAction",
             "preferred_name": "Hành động", "alt_labels": []},
        ],
        "active_nodes": [
            {"id": "mention.subject", "semantic_type": "LegalSubject",
             "mention_type": "SUBJECT", "raw_text": "Chủ thể",
             "canonical_concept_id": "concept.subject", "provenance_node_id": "source",
             "evidence": "Chủ thể phải thực hiện hành động."},
            {"id": "mention.action", "semantic_type": "LegalAction",
             "mention_type": "ACTION", "raw_text": "Hành động",
             "canonical_concept_id": "concept.action", "provenance_node_id": "source",
             "evidence": "phải thực hiện hành động"},
        ],
        "active_edges": [
            {"source_id": "mention.subject", "target_id": "concept.subject",
             "relation_type": "DENOTES", "evidence": "Chủ thể"},
            {"source_id": "mention.action", "target_id": "concept.action",
             "relation_type": "DENOTES", "evidence": "Hành động"},
        ],
        "norms": [{
            "id": "norm.1", "modality": "REQUIRE",
            "subject_ids": ["mention.subject"], "action_ids": ["mention.action"],
            "condition_ids": [], "exception_ids": [],
            "provenance_node_id": "source",
            "evidence": "Chủ thể phải thực hiện hành động.",
            "status": "VALID",
        }],
        "references": [{
            "id": "ref.1", "raw_text": "khoản 2 Điều 10",
            "scope": "SAME_DOCUMENT", "provenance_node_id": "source",
            "evidence": "theo khoản 2 Điều 10",
            "owner_norm_id": "norm.1",
        }, {
            "id": "ref.2", "raw_text": "khoản 2 Điều 10",
            "scope": "EXTERNAL", "provenance_node_id": "source",
            "evidence": "theo khoản 2 Điều 10 của luật khác",
            "owner_norm_id": "norm.1",
        }],
    }
    physical_path = tmp_path / "physical-m7v12.json"
    semantic_path = tmp_path / "semantic-m7v12.json"
    physical_path.write_text(json.dumps(physical), encoding="utf-8")
    semantic_path.write_text(json.dumps(semantic), encoding="utf-8")
    result = FusionEngine().fuse(physical_path, semantic_path)
    assert any(edge["type"] == "REQUIRE" for edge in result["edges"])
    assert any(edge["type"] == "DENOTES" for edge in result["edges"])
    assert any(
        edge["type"] == "RESOLVES_TO" and edge["target"] == "clause2"
        for edge in result["edges"]
    )
    assert not any(
        edge["type"] == "RESOLVES_TO" and edge["source"] == "ref.2"
        for edge in result["edges"]
    )
    assert result["fusion_report"]["unresolved_reference_count"] == 0
    assert result["fusion_report"]["external_scope_reference_count"] == 1
    assert ShaclValidator().validate(result)[0]


def test_graph_contract_rejects_duplicate_orphan_and_unknown_ids(tmp_path):
    physical = {
        "nodes": [
            {"id": "p", "labels": ["LegalNode", "ARTICLE"], "properties": {}},
            {"id": "p", "labels": ["LegalNode", "ARTICLE"], "properties": {}},
        ],
        "edges": [],
    }
    semantic = {"entities": [], "relations": []}
    physical_path = tmp_path / "physical.json"
    semantic_path = tmp_path / "semantic.json"
    physical_path.write_text(json.dumps(physical), encoding="utf-8")
    semantic_path.write_text(json.dumps(semantic), encoding="utf-8")
    try:
        FusionEngine().fuse(physical_path, semantic_path)
    except GraphContractError as exc:
        assert "Duplicate physical.nodes ID" in str(exc)
    else:
        raise AssertionError("duplicate node IDs must reject the input")


def test_shacl_checks_domain_range_and_article_number():
    validator = ShaclValidator()
    valid_graph = {
        "nodes": [
            {"id": "article", "node_kind": "PHYSICAL", "labels": ["ARTICLE"],
             "properties": {"number": "10"}},
            {"id": "subject", "node_kind": "SEMANTIC", "properties": {
                "ontology_class": "LEGAL_SUBJECT",
            }},
            {"id": "action", "node_kind": "SEMANTIC", "properties": {
                "ontology_class": "LEGAL_ACTION",
            }},
        ],
        "edges": [{
            "source": "subject", "target": "action", "type": "ALLOW",
            "properties": {},
        }],
    }
    conforms, _, _ = validator.validate(valid_graph)
    assert conforms

    invalid_graph = {
        **valid_graph,
        "nodes": [
            {**valid_graph["nodes"][0], "properties": {"number": "zero"}},
            valid_graph["nodes"][1],
            valid_graph["nodes"][2],
        ],
        "edges": [{
            "source": "subject", "target": "subject", "type": "ALLOW",
            "properties": {},
        }],
    }
    conforms, report_text, _ = validator.validate(invalid_graph)
    assert not conforms
    assert "domain/range" in report_text or "positive integer" in report_text


def test_shacl_rejects_belong_to_cycle():
    graph = {
        "nodes": [
            {
                "id": "parent", "node_kind": "PHYSICAL", "labels": ["ARTICLE"],
                "properties": {"number": "1", "parent_id": "child"},
            },
            {
                "id": "child", "node_kind": "PHYSICAL", "labels": ["CLAUSE"],
                "properties": {"number": "1", "parent_id": "parent"},
            },
        ],
        "edges": [{
            "source": "child", "target": "parent", "type": "BELONG_TO",
            "properties": {},
        }],
    }
    conforms, report_text, _ = ShaclValidator().validate(graph)
    assert not conforms
    assert "acyclic" in report_text


def test_document_level_reference_creates_document_anchor(tmp_path):
    physical_path = tmp_path / "physical-document-ref.json"
    semantic_path = tmp_path / "semantic-document-ref.json"
    physical_path.write_text(json.dumps({
        "nodes": [{
            "id": "article",
            "labels": ["ARTICLE"],
            "properties": {
                "law_code": "59/2024/QH15",
                "source_doc": "Luat_dat_dai_2024.docx",
            },
        }],
        "edges": [],
    }), encoding="utf-8")
    semantic_path.write_text(json.dumps({
        "entities": [
            {"canonical_id": "action", "ontology_class": "LEGAL_ACTION"},
            {
                "canonical_id": "ref-law",
                "ontology_class": "LEGAL_DOCUMENT_REF",
                "canonical_text": "Luật này",
            },
        ],
        "relations": [{
            "relation_id": "r-law",
            "relation_type": "REFERENCE_TO",
            "source": "action",
            "target": "ref-law",
            "source_node_id": "article",
            "reference_scope": "SAME_DOCUMENT",
            "evidence": "theo Luật này",
        }],
    }), encoding="utf-8")

    result = FusionEngine().fuse(physical_path, semantic_path)
    anchors = [node for node in result["nodes"] if node["node_kind"] == "DOCUMENT"]
    assert len(anchors) == 1
    assert any(
        edge["type"] == "RESOLVES_TO"
        and edge["source"] == "ref-law"
        and edge["target"] == anchors[0]["id"]
        for edge in result["edges"]
    )
    assert result["fusion_report"]["document_level_reference_count"] == 1


def test_sampler_creates_unlabeled_stratified_rows_and_grouped_splits(tmp_path):
    graph_path = tmp_path / "ukg.json"
    confidence_path = tmp_path / "confidence.csv"
    quality_path = tmp_path / "quality.csv"
    relation_types = ["ALLOW", "REQUIRE", "PROHIBIT", "RESOLVES_TO", "HAS_EXCEPTION"]
    graph_path.write_text(json.dumps({
        "nodes": [{"id": "n1"}],
        "edges": [{
            "id": f"r-{index}",
            "source": "n1",
            "target": "n1",
            "type": relation_type,
            "properties": {
                "source_node_id": "article-1",
                "confidence": 0.8,
                "evidence": "evidence",
            },
        } for index, relation_type in enumerate(relation_types)],
    }), encoding="utf-8")

    confidence_count, quality_count = sample_fusion_eval(
        graph_path, confidence_path, quality_path, size=5, seed=1
    )
    assert confidence_count == 5
    assert quality_count >= 5
    import csv

    with confidence_path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert {row["relation_type"] for row in rows} == set(relation_types)
    assert all(row["label"] == "" for row in rows)
    assert len({row["split"] for row in rows}) == 1
    with quality_path.open(encoding="utf-8-sig", newline="") as stream:
        quality_rows = list(csv.DictReader(stream))
    support_rows = [
        row for row in quality_rows if row["task"] == "relation_support"
    ]
    assert len(support_rows) == 5
    assert all(row["expected"] == "" and row["annotation"] == "" for row in quality_rows)


def test_quality_evaluation_accepts_reviewer_annotation_as_gold(tmp_path):
    path = tmp_path / "quality-annotations.csv"
    path.write_text(
        "task,case_id,expected,predicted,split,reviewer,annotation,notes\n"
        "relation_support,c1,,1,test,r1,1,\n",
        encoding="utf-8",
    )
    report = evaluate_quality_csv(path, "relation_support")
    assert report["exact_match_accuracy"] == 1.0


def test_delta_reports_updated_edges_and_neo4j_applier_uses_transaction():
    previous = {
        "nodes": [{"id": "n1", "node_kind": "PHYSICAL"}],
        "edges": [{
            "source": "n1", "target": "n1", "type": "NEXT",
            "properties": {"relation_id": "r", "version": 1},
        }],
    }
    current = {
        "nodes": [{"id": "n1", "node_kind": "PHYSICAL"}],
        "edges": [{
            "source": "n1", "target": "n1", "type": "NEXT",
            "properties": {"relation_id": "r", "version": 2},
        }],
    }
    delta = DeltaEngine().diff(previous, current)
    assert len(delta["updated_edges"]) == 1

    class Transaction:
        def __init__(self):
            self.queries = []

        def run(self, query, **parameters):
            self.queries.append((query, parameters))
            return QueryResult()

    class QueryResult:
        def single(self):
            return {"edge_key": "created"}

        def consume(self):
            return None

    class Session:
        def __init__(self):
            self.tx = Transaction()

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def execute_write(self, callback, value):
            callback(self.tx, value)

    class Driver:
        def __init__(self):
            self.session_instance = Session()

        def session(self, database=None):
            return self.session_instance

    driver = Driver()
    Neo4jDeltaApplier(driver).apply(delta)
    assert len(driver.session_instance.tx.queries) == 2
