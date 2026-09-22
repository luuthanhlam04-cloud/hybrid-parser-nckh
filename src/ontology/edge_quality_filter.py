import re
from collections import Counter
from typing import Any, Dict, Set, Tuple


class EdgeQualityFilter:
    """Reject malformed or duplicate relations before ontology validation."""

    _PLACEHOLDER_EVIDENCE = {
        "n/a",
        "na",
        "none",
        "null",
        "unknown",
        "không có",
        "khong co",
        "test",
        "...",
    }

    def __init__(self, relation_types: Set[str]):
        self.relation_types = relation_types
        self.seen_edges: Set[Tuple[str, str, str, str, str]] = set()
        self.rejection_breakdown: Counter[str] = Counter()

    def check(self, relation: Any, source_node_id: str) -> tuple[bool, str | None]:
        if not isinstance(relation, dict):
            return False, self._reject("invalid_relation")

        relation_type = relation.get("relation_type")
        source = relation.get("source")
        target = relation.get("target")
        evidence = relation.get("evidence")

        if not isinstance(relation_type, str) or not relation_type.strip():
            return False, self._reject("missing_relation_type")
        if relation_type not in self.relation_types:
            return False, self._reject("unknown_relation_type")
        if not isinstance(source, str) or not source.strip():
            return False, self._reject("missing_source")
        if not isinstance(target, str) or not target.strip():
            return False, self._reject("missing_target")
        if not isinstance(evidence, str) or not evidence.strip():
            return False, self._reject("missing_evidence")

        normalized_evidence = re.sub(r"\s+", " ", evidence).strip().casefold()
        if normalized_evidence in self._PLACEHOLDER_EVIDENCE:
            return False, self._reject("placeholder_evidence")
        if not any(char.isalnum() for char in normalized_evidence):
            return False, self._reject("non_text_evidence")

        edge_key = (
            source_node_id or "",
            relation_type.strip(),
            source.strip(),
            target.strip(),
            normalized_evidence,
        )
        if edge_key in self.seen_edges:
            return False, self._reject("duplicate_edge")
        self.seen_edges.add(edge_key)
        return True, None

    def _reject(self, reason: str) -> str:
        self.rejection_breakdown[reason] += 1
        return reason
