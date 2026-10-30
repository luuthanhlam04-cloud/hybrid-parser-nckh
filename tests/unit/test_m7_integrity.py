from copy import deepcopy

from src.ontology.entity_normalizer import EntityNormalizer
from src.ontology.graph_integrity import GraphIntegrityFinalizer
from src.ontology.node_quality_filter import NodeQualityFilter
from src.ontology.norm_builder import NormBuilder
from src.ontology.relation_normalizer import RelationNormalizer
from src.ontology.schemas import (
    CanonicalSemanticGraph,
    LocalMention,
    MentionStatus,
    MentionType,
    NormAssertion,
    NormativeModality,
    ReferenceMention,
    RelationType,
    SemanticEdge,
    SemanticType,
)


def _mention(
    mention_id: str,
    semantic_type: SemanticType,
    mention_type: MentionType,
    provenance: str = "node-1",
) -> LocalMention:
    return LocalMention(
        id=mention_id,
        mention_type=mention_type,
        raw_text=mention_id,
        m6_local_id=mention_id,
        semantic_type=semantic_type,
        provenance_node_id=provenance,
        evidence=f"evidence {mention_id}",
        status=MentionStatus.VALID,
    )


def test_partial_norm_source_null_survives_quality_filter_and_builder():
    raw = {
        "node_id": "node-1",
        "extraction": {
            "entities": [
                {
                    "id": "e1",
                    "text": "Đăng ký",
                    "entity_type": "ACTION",
                    "evidence": "phải đăng ký",
                }
            ],
            "relations": [
                {
                    "source": None,
                    "source_status": "UNRESOLVED",
                    "relation_type": "REQUIRE",
                    "target": "e1",
                    "evidence": "phải đăng ký",
                }
            ],
        },
    }
    node_id, entities, relations = NodeQualityFilter().filter_node(raw)
    assert node_id == "node-1"
    assert len(relations) == 1

    mentions = EntityNormalizer().normalize_all(entities, node_id)
    mention_map = {mention.m6_local_id: mention for mention in mentions}
    normalized, modality = RelationNormalizer().normalize_all(
        relations, entities, mention_map
    )
    norms, edges = NormBuilder().build(
        mentions, normalized, modality, node_id, {}
    )

    assert len(norms) == 1
    assert norms[0].subject_ids == []
    assert norms[0].subject_status == "UNRESOLVED"
    assert norms[0].norm_completeness == "PARTIAL"
    assert any(edge.relation_type == RelationType.HAS_ACTION for edge in edges)


def test_invalid_source_null_structural_relation_is_rejected():
    raw = {
        "node_id": "node-1",
        "extraction": {
            "entities": [
                {
                    "id": "e1",
                    "text": "Có giấy chứng nhận",
                    "entity_type": "CONDITION",
                    "evidence": "Có giấy chứng nhận",
                }
            ],
            "relations": [
                {
                    "source": None,
                    "source_status": "UNRESOLVED",
                    "relation_type": "HAS_CONDITION",
                    "target": "e1",
                    "evidence": "Có giấy chứng nhận",
                }
            ],
        },
    }
    quality_filter = NodeQualityFilter()
    _, _, relations = quality_filter.filter_node(raw)
    assert relations == []
    assert quality_filter.summary()["relation_rejection"]["invalid_unresolved_source"] == 1


def test_subject_head_beats_document_substring_false_positive():
    entities = [
        {
            "id": "e1",
            "text": "Người mua tài sản gắn liền với đất trong hợp đồng thuê đất",
            "entity_type": "SUBJECT",
            "evidence": "Người mua tài sản gắn liền với đất trong hợp đồng thuê đất",
        },
        {
            "id": "e2",
            "text": "Người đại diện theo ủy quyền bằng văn bản",
            "entity_type": "SUBJECT",
            "evidence": "Người đại diện theo ủy quyền bằng văn bản",
        },
    ]
    mentions = EntityNormalizer().normalize_all(entities, "node-1")
    assert len(mentions) == 2
    assert all(m.semantic_type == SemanticType.LEGAL_SUBJECT for m in mentions)
    assert all(m.status != MentionStatus.QUARANTINED for m in mentions)


def test_modifier_edges_are_reanchored_to_norm():
    subject = _mention("s", SemanticType.LEGAL_SUBJECT, MentionType.SUBJECT)
    action = _mention("a", SemanticType.LEGAL_ACTION, MentionType.ACTION)
    condition = _mention("c", SemanticType.CONDITION, MentionType.CONDITION)
    from src.ontology.relation_normalizer import ModalityContext, NormalizedRelation

    relations = [
        NormalizedRelation("s", "a", RelationType.ALLOW, "được làm"),
        NormalizedRelation("a", "c", RelationType.HAS_CONDITION, "khi đủ điều kiện"),
    ]
    norms, edges = NormBuilder().build(
        [subject, action, condition],
        relations,
        ModalityContext(suggested_modality=NormativeModality.ALLOW),
        "node-1",
        {},
    )
    assert len(norms) == 1
    condition_edges = [e for e in edges if e.relation_type == RelationType.HAS_CONDITION]
    assert len(condition_edges) == 1
    assert condition_edges[0].source_id == norms[0].id
    assert condition_edges[0].target_id == condition.id


def test_quarantined_dependency_turns_norm_partial_and_removes_dangling_edge():
    action = _mention("a", SemanticType.LEGAL_ACTION, MentionType.ACTION)
    norm = NormAssertion(
        id="norm-1",
        modality=NormativeModality.REQUIRE,
        subject_ids=["missing-subject"],
        action_ids=["a"],
        provenance_node_id="node-1",
        evidence="phải làm",
        rule_id="test",
    )
    graph = CanonicalSemanticGraph(
        active_nodes=[action],
        norms=[norm],
        active_edges=[
            SemanticEdge(
                source_id="norm-1",
                target_id="missing-subject",
                relation_type=RelationType.HAS_SUBJECT,
                evidence="phải làm",
            ),
            SemanticEdge(
                source_id="norm-1",
                target_id="a",
                relation_type=RelationType.HAS_ACTION,
                evidence="phải làm",
            ),
        ],
    )
    finalized = GraphIntegrityFinalizer().finalize(graph)
    assert finalized.norms[0].subject_ids == []
    assert finalized.norms[0].norm_completeness == "PARTIAL"
    assert len(finalized.active_edges) == 1
    assert len(finalized.quarantine.edges) == 1
    assert finalized.validation_report.broken_endpoints == 0


def test_reference_owner_prevents_orphan_classification():
    owner = _mention("owner", SemanticType.LEGAL_ACTION, MentionType.ACTION)
    ref = ReferenceMention(
        id="ref-1",
        raw_text="Điều 26",
        scope="SAME_DOCUMENT",
        target_hint={"article": "26"},
        provenance_node_id="node-1",
        evidence="theo Điều 26",
        owner_mention_id="owner",
    )
    graph = CanonicalSemanticGraph(active_nodes=[owner], references=[ref])
    finalized = GraphIntegrityFinalizer().finalize(graph)
    assert [node.id for node in finalized.active_nodes] == ["owner"]
    assert finalized.references[0].owner_mention_id == "owner"
    assert finalized.metadata["orphan_audit"]["reference_owner"] == 1


def test_valid_unlinked_evidence_remains_active():
    evidence = _mention("object", SemanticType.LEGAL_OBJECT, MentionType.OBJECT)
    graph = CanonicalSemanticGraph(active_nodes=[evidence])
    finalized = GraphIntegrityFinalizer().finalize(graph)
    assert [node.id for node in finalized.active_nodes] == ["object"]
    assert finalized.metadata["orphan_audit"]["unlinked_evidence"] == 1
    assert finalized.quarantine.mentions == []


def test_finalizer_is_idempotent_and_report_matches_payload():
    subject = _mention("s", SemanticType.LEGAL_SUBJECT, MentionType.SUBJECT)
    action = _mention("a", SemanticType.LEGAL_ACTION, MentionType.ACTION)
    graph = CanonicalSemanticGraph(
        active_nodes=[subject, action],
        active_edges=[
            SemanticEdge(
                source_id="s",
                target_id="a",
                relation_type=RelationType.ALLOW,
                evidence="được làm",
            )
        ],
    )
    finalizer = GraphIntegrityFinalizer()
    once = finalizer.finalize(graph)
    snapshot = deepcopy(once.model_dump())
    twice = finalizer.finalize(once)
    assert twice.model_dump() == snapshot
    report = twice.validation_report
    assert report.active_mentions == len(twice.active_nodes)
    assert report.active_edges == len(twice.active_edges)
    assert report.input_edges == report.active_edges + report.quarantined_edges
    assert report.conservation_ok is True
