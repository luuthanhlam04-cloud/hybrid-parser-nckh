import json

from src.fusion.fusion_engine import FusionEngine
from src.fusion.m7_adapter import M7GraphAdapter
from src.fusion.norm_fuser import NormFuser


def test_adapter_preserves_norm_modifiers_in_global_norm_hub():
    graph = {
        "active_nodes": [
            {"id": "subject-1", "semantic_type": "LegalSubject", "raw_text": "Người dùng đất"},
            {"id": "action-1", "semantic_type": "LegalAction", "raw_text": "chuyển nhượng"},
            {"id": "condition-1", "semantic_type": "Condition", "raw_text": "có giấy chứng nhận"},
            {"id": "exception-1", "semantic_type": "Exception", "raw_text": "trừ trường hợp thừa kế"},
        ],
        "norms": [
            {
                "id": "physical-1#NORM#1",
                "modality": "PROHIBIT",
                "subject_ids": ["subject-1"],
                "action_ids": ["action-1"],
                "condition_ids": ["condition-1"],
                "condition_groups": [
                    {
                        "group_id": "G1",
                        "operator": "OR",
                        "condition_ids": ["condition-1"],
                        "is_complex": False,
                    }
                ],
                "exception_ids": ["exception-1"],
                "provenance_node_id": "physical-1",
                "evidence": "Test evidence",
                "status": "VALID",
            }
        ],
    }

    adapted = M7GraphAdapter.adapt(graph)
    norms, edges, _ = NormFuser().fuse(adapted["relations"])

    assert len(norms) == 1
    norm = norms[0]
    properties = norm["properties"]
    edge_types = {edge["relation_type"] for edge in edges}
    assert properties["modality"] == "PROHIBIT"
    assert properties["condition_ids"] == ["condition-1"]
    assert properties["exception_ids"] == ["exception-1"]
    assert properties["condition_groups"][0]["operator"] == "OR"
    assert properties["source_norm_ids"] == ["physical-1#NORM#1"]
    assert {"HAS_SUBJECT", "HAS_ACTION", "HAS_CONDITION", "HAS_EXCEPTION"} <= edge_types


def test_fusion_keeps_required_norm_arguments_but_prunes_unused_mentions(tmp_path):
    physical_path = tmp_path / "physical.json"
    semantic_path = tmp_path / "semantic.json"
    physical_path.write_text(
        json.dumps({
            "nodes": [{
                "id": "physical-1",
                "labels": ["LegalNode", "CLAUSE"],
                "properties": {"text": "Test clause", "parent_id": None},
            }],
            "edges": [],
        }),
        encoding="utf-8",
    )
    semantic_path.write_text(
        json.dumps({
            "active_nodes": [
                {"id": "subject-1", "semantic_type": "LegalSubject", "raw_text": "Người sử dụng đất"},
                {"id": "action-1", "semantic_type": "LegalAction", "raw_text": "chuyển nhượng"},
                {"id": "condition-1", "semantic_type": "Condition", "raw_text": "có giấy chứng nhận"},
                {"id": "exception-1", "semantic_type": "Exception", "raw_text": "trừ trường hợp thừa kế"},
                {"id": "unused-1", "semantic_type": "Condition", "raw_text": "điều kiện không dùng"},
            ],
            "norms": [{
                "id": "physical-1#NORM#1",
                "modality": "PROHIBIT",
                "subject_ids": ["subject-1"],
                "action_ids": ["action-1"],
                "condition_ids": ["condition-1"],
                "condition_groups": [{
                    "group_id": "G1",
                    "operator": "AND",
                    "condition_ids": ["condition-1"],
                    "is_complex": False,
                }],
                "exception_ids": ["exception-1"],
                "provenance_node_id": "physical-1",
                "evidence": "Người sử dụng đất không được chuyển nhượng nếu không có giấy chứng nhận.",
                "status": "VALID",
            }],
        }),
        encoding="utf-8",
    )

    graph = FusionEngine().fuse(physical_path, semantic_path)

    nodes_by_id = {node["id"]: node for node in graph["nodes"]}
    norm = next(node for node in graph["nodes"] if "GLOBAL_NORM" in node["labels"])
    norm_edges = [edge for edge in graph["edges"] if edge["source"] == norm["id"]]
    assert any(edge["type"] == "HAS_CONDITION" and edge["target"] == "condition-1" for edge in norm_edges)
    assert any(edge["type"] == "HAS_EXCEPTION" and edge["target"] == "exception-1" for edge in norm_edges)
    assert "condition-1" in nodes_by_id
    assert "exception-1" in nodes_by_id
    assert "unused-1" not in nodes_by_id