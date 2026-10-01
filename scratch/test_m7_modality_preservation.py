import sys
from pathlib import Path
sys.path.append(r"c:\Users\luuth\NCKH\hybrid_parser_graphrag")

from src.ontology.schemas import LocalMention, MentionType, SemanticType, MentionStatus, RelationType, NormativeModality, NormAssertion
from src.ontology.relation_normalizer import NormalizedRelation, ModalityContext
from src.ontology.norm_builder import NormBuilder
from src.ontology.ontology_validator import OntologyValidator
from src.ontology.schemas import CanonicalSemanticGraph

def test_norm_builder_partial_norm():
    builder = NormBuilder()
    
    # 1. Tạo mentions
    action_mention = LocalMention(
        id="node1#ACTION#1",
        mention_type=MentionType.ACTION,
        raw_text="công chứng",
        m6_local_id="e2",
        semantic_type=SemanticType.LEGAL_ACTION,
        provenance_node_id="node1",
        evidence="phải được công chứng"
    )
    
    # 2. Tạo relations (REQUIRE null source)
    rel = NormalizedRelation(
        source_mention_id=None,
        target_mention_id=action_mention.id,
        relation_type=RelationType.REQUIRE,
        evidence="phải được công chứng",
        source_status="UNRESOLVED"
    )
    
    ctx = ModalityContext(suggested_modality=NormativeModality.REQUIRE)
    counter = {}
    
    norms, edges = builder.build(
        mentions=[action_mention],
        normalized_relations=[rel],
        modality_ctx=ctx,
        provenance_node_id="node1",
        norm_index_counter=counter
    )
    
    assert len(norms) == 1, "Phải tạo ra 1 NormAssertion"
    norm = norms[0]
    assert norm.subject_status == "UNRESOLVED", "Norm phải có status UNRESOLVED"
    assert len(norm.subject_ids) == 0, "Không được có subject"
    assert norm.action_ids == [action_mention.id], "Phải có action"
    
    # Kiểm tra edges
    has_subject_edges = [e for e in edges if e.relation_type == RelationType.HAS_SUBJECT]
    has_action_edges = [e for e in edges if e.relation_type == RelationType.HAS_ACTION]
    
    assert len(has_subject_edges) == 0, "Không được sinh HAS_SUBJECT edge"
    assert len(has_action_edges) == 1, "Phải sinh HAS_ACTION edge"
    
    print("[PASS] TEST_M7_NORMBUILDER_PARTIAL_NORM")
    return norm, edges, [action_mention]

def test_gate2_partial_norm(norm: NormAssertion, edges: list, mentions: list):
    validator = OntologyValidator()
    
    graph = CanonicalSemanticGraph(
        active_nodes=mentions,
        active_edges=edges,
        norms=[norm],
        concepts=[],
        references=[]
    )
    
    validated_graph = validator.validate(graph)
    
    assert validated_graph.norms[0].status.value == "VALID", "Gate 2 không được quarantine Partial Norm"
    print("[PASS] TEST_M7_GATE2_PARTIAL_NORM")

if __name__ == "__main__":
    try:
        norm, edges, mentions = test_norm_builder_partial_norm()
        test_gate2_partial_norm(norm, edges, mentions)
        print("\n[SUCCESS] Tất cả bài test kiến trúc M6 V2 / M7 PASS!")
    except AssertionError as e:
        print(f"[FAIL] TEST FAIL: {e}")
        sys.exit(1)
