"""
verify_nodefilter_position.py
Verify 2: NodeQualityFilter phải đứng trước Gate 1.
Test với garbage input — kỳ vọng không crash, bị filter sớm.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

# Thêm project root vào path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ontology.entity_normalizer import EntityNormalizer

# ── Garbage inputs ─────────────────────────────────────────────────────────────
garbage_cases = [
    {
        "label": "text rỗng",
        "node": {"node_id": "test_node_1", "extraction": {
            "entities": [{"id": "e1", "text": "", "entity_type": "SUBJECT", "evidence": "some text"}],
            "relations": []
        }}
    },
    {
        "label": "entity_type null/unknown",
        "node": {"node_id": "test_node_2", "extraction": {
            "entities": [{"id": "e1", "text": "Nhà nước", "entity_type": "null", "evidence": "Nhà nước có quyền"}],
            "relations": []
        }}
    },
    {
        "label": "node_id thiếu",
        "node": {"node_id": None, "extraction": {
            "entities": [{"id": "e1", "text": "Nhà nước", "entity_type": "SUBJECT", "evidence": "ok"}],
            "relations": []
        }}
    },
    {
        "label": "evidence là placeholder",
        "node": {"node_id": "test_node_3", "extraction": {
            "entities": [{"id": "e1", "text": "Người sử dụng đất", "entity_type": "SUBJECT", "evidence": "..."}],
            "relations": []
        }}
    },
    {
        "label": "entity text là placeholder",
        "node": {"node_id": "test_node_4", "extraction": {
            "entities": [{"id": "e1", "text": "n/a", "entity_type": "SUBJECT", "evidence": "Điều 27 quy định"}],
            "relations": []
        }}
    },
    {
        "label": "full garbage node",
        "node": {"node_id": None, "extraction": None}
    },
]

# ── Dương's NodeQualityFilter (copy minimal logic để test) ─────────────────────
import re
from collections import Counter

_PLACEHOLDERS = {"", "n/a", "na", "none", "null", "unknown", "test", "...", "không có", "khong co"}
_ENTITY_TYPES  = {"SUBJECT", "ACTION", "OBJECT", "CONDITION", "EXCEPTION", "REFERENCE", "PENALTY"}

def is_placeholder(text: str) -> bool:
    norm = re.sub(r"\s+", " ", text).strip().casefold()
    return norm in _PLACEHOLDERS

def valid_evidence(value: str) -> bool:
    return bool(value) and not is_placeholder(value) and any(c.isalnum() for c in value)

def node_quality_filter(node: dict) -> tuple:
    """Returns (node_id, entities, relations) or (None, [], []) if garbage."""
    if not isinstance(node, dict):
        return None, [], []
    node_id = node.get("node_id")
    if not node_id:
        return None, [], []
    extraction = node.get("extraction")
    if not isinstance(extraction, dict):
        return None, [], []

    raw_entities = extraction.get("entities", [])
    valid_entities = []
    for e in raw_entities:
        if not isinstance(e, dict):
            continue
        text = e.get("text", "").strip()
        etype = e.get("entity_type", "")
        etype = str(etype).upper() if etype else ""
        ev = e.get("evidence", "").strip()
        if not text or is_placeholder(text):
            continue
        if etype not in _ENTITY_TYPES:
            continue
        if not valid_evidence(ev):
            continue
        valid_entities.append(e)

    if not valid_entities:
        return None, [], []

    return node_id, valid_entities, extraction.get("relations", [])

# ── Test EntityNormalizer với garbage trực tiếp (không có filter) ──────────────
normalizer = EntityNormalizer()

print("=" * 60)
print("VERIFY 2: NodeQualityFilter position test")
print("=" * 60)

for case in garbage_cases:
    label = case["label"]
    node = case["node"]
    entities = (node.get("extraction") or {}).get("entities", [])

    print(f"\n[Case: {label}]")

    # Test A: với NodeQualityFilter
    nid, valid_ents, _ = node_quality_filter(node)
    filter_result = "BLOCKED ✅" if nid is None or not valid_ents else f"PASSED ({len(valid_ents)} entities)"
    print(f"  NodeQualityFilter: {filter_result}")

    # Test B: không có filter → trực tiếp vào normalizer
    if entities:
        try:
            raw = entities[0]
            result = normalizer.normalize_all(
                m6_entities=[raw],
                provenance_node_id="test_garbage"
            )
            print(f"  Direct normalize (no filter): returned {len(result)} mentions — "
                  f"{'⚠️ garbage survived' if result else '✅ naturally filtered'}")
        except Exception as e:
            print(f"  Direct normalize (no filter): 💥 CRASH — {type(e).__name__}: {e}")
    else:
        print(f"  Direct normalize: skipped (empty entities)")

print("\n" + "=" * 60)
print("VERDICT:")
print("Nếu tất cả case có NodeQualityFilter = BLOCKED → filter đúng vị trí")
print("Nếu có case nào CRASH ở direct normalize → NodeQualityFilter là REQUIRED blocker")
print("=" * 60)
