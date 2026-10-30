"""Apply reviewed, idempotent corrections to five M6 extraction nodes."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
M6 = ROOT / "outputs/semantic_graphs/semantic_extraction.json"
PHYSICAL = ROOT / "outputs/physical_graphs/physical_graph.json"


def apply_corrections(data, physical):
    nodes = {item["node_id"]: item["extraction"] for item in data["extracted_nodes"]}
    source = {item["id"]: item["properties"]["text"] for item in physical["nodes"]}

    def node(fragment):
        matches = [key for key in nodes if fragment in key]
        assert len(matches) == 1, (fragment, matches)
        return matches[0], nodes[matches[0]]

    def add_entity(extraction, entity):
        existing = {e["id"]: e for e in extraction["entities"]}
        if entity["id"] in existing:
            assert existing[entity["id"]] == entity
        else:
            extraction["entities"].append(entity)

    def add_relation(extraction, source_id, target_id, evidence, status="RESOLVED"):
        relation = dict(source=source_id, relation_type="HAS_CONDITION", target=target_id,
                        source_status=status, evidence=evidence)
        if relation not in extraction["relations"]:
            extraction["relations"].append(relation)

    def grounded(evidence, *physical_ids):
        assert any(evidence in source[key] for key in physical_ids), evidence
        return evidence

    n32, e32 = node("dieu-32_khoan-2_p10896")
    phrase32 = grounded("được Nhà nước giao đất không thu tiền sử dụng đất", n32)
    add_entity(e32, dict(id="e10", text="Được Nhà nước giao đất không thu tiền sử dụng đất",
                         entity_type="CONDITION", evidence=phrase32))
    for action_id in ("e4", "e5", "e6", "e7", "e8", "e9"):
        add_relation(e32, action_id, "e10", phrase32)

    n33, e33 = node("dieu-33_khoan-1_diem-dd_p12256")
    parent33 = next(key for key in source if "dieu-33_khoan-1_p11293" in key)
    phrase33 = grounded("được Nhà nước giao đất có thu tiền sử dụng đất, cho thuê đất thu tiền thuê đất một lần cho cả thời gian thuê", parent33)
    add_entity(e33, dict(id="e8", text="Giao đất có thu tiền sử dụng đất hoặc thuê đất trả tiền một lần",
                         entity_type="CONDITION", evidence=phrase33))
    add_relation(e33, "e2", "e8", phrase33, "CONTEXT_INFERRED")

    n34, e34 = node("dieu-34_khoan-1_diem-b_p14547")
    parent34 = next(key for key in source if "dieu-34_khoan-1_p14323" in key)
    phrase34 = grounded("được Nhà nước cho thuê đất thu tiền thuê đất hằng năm", parent34)
    action34 = next(e for e in e34["entities"] if e["id"] == "e4")
    action34["text"] = grounded("Thế chấp tài sản thuộc sở hữu của mình gắn liền với đất", n34)
    add_entity(e34, dict(id="e6", text="Được Nhà nước cho thuê đất thu tiền thuê đất hằng năm",
                         entity_type="CONDITION", evidence=phrase34))
    add_relation(e34, "e4", "e6", phrase34, "CONTEXT_INFERRED")

    n37, e37 = node("dieu-37_khoan-1_diem-g_p23125")
    for entity_id, phrase in (("e4", "tại tổ chức tín dụng được phép hoạt động tại Việt Nam"),
                              ("e5", "tại tổ chức kinh tế khác hoặc cá nhân")):
        entity = next(e for e in e37["entities"] if e["id"] == entity_id)
        entity["entity_type"] = "CONDITION"
        entity["text"] = phrase
        entity["evidence"] = grounded(phrase, n37)
        add_relation(e37, "e1", entity_id, phrase)

    n45, e45 = node("dieu-45_khoan-8_diem-c_p43247")
    condition = next(e for e in e45["entities"] if e["id"] == "e11")
    # One shared condition is the exact phrase in the physical node. Splitting
    # it into two invented quotations would break evidence grounding.
    condition["text"] = "Pháp luật không cho phép nhận chuyển nhượng, nhận tặng cho quyền sử dụng đất"
    condition["evidence"] = grounded("pháp luật không cho phép nhận chuyển nhượng, nhận tặng cho quyền sử dụng đất", n45)

    assert len(nodes) == data["metadata"]["total_candidates_processed"]
    for extraction in nodes.values():
        ids = {e["id"] for e in extraction["entities"]}
        assert len(ids) == len(extraction["entities"])
        for relation in extraction["relations"]:
            assert relation["target"] in ids
            assert relation["source"] is None or relation["source"] in ids
    return data


if __name__ == "__main__":
    data = json.loads(M6.read_text(encoding="utf-8"))
    physical = json.loads(PHYSICAL.read_text(encoding="utf-8"))
    corrected = apply_corrections(data, physical)
    M6.write_text(json.dumps(corrected, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Corrected five M6 nodes; metadata and 180-node count unchanged")
