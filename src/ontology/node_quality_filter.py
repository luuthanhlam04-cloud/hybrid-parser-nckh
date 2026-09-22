import re
from collections import Counter
from typing import Any, Dict, Iterable, Tuple


class NodeQualityFilter:
    """Filter malformed M6 nodes and extraction records before normalization."""

    _ENTITY_TYPES = {
        "SUBJECT",
        "ACTION",
        "OBJECT",
        "CONDITION",
        "EXCEPTION",
        "REFERENCE",
        "PENALTY",
    }
    _PLACEHOLDERS = {
        "",
        "n/a",
        "na",
        "none",
        "null",
        "unknown",
        "test",
        "...",
        "không có",
        "khong co",
    }

    def __init__(self) -> None:
        self.rejection_breakdown: Counter[str] = Counter()

    def filter_node(
        self, node: Any
    ) -> Tuple[str | None, list[Dict[str, Any]], list[Dict[str, Any]]]:
        if not isinstance(node, dict):
            self._reject("invalid_node")
            return None, [], []

        node_id = self._text(node.get("node_id"))
        extraction = node.get("extraction")
        if not node_id:
            self._reject("missing_node_id")
            return None, [], []
        if not isinstance(extraction, dict):
            self._reject("invalid_extraction")
            return None, [], []

        entities = self._filter_entities(extraction.get("entities", []))
        entity_ids = {entity["id"] for entity in entities}
        relations = self._filter_relations(
            extraction.get("relations", []), entity_ids
        )

        if not entities and not relations:
            self._reject("empty_after_filter")
            return None, [], []
        return node_id, entities, relations

    def _filter_entities(self, raw_entities: Any) -> list[Dict[str, Any]]:
        if not isinstance(raw_entities, list):
            self._reject("invalid_entities")
            return []

        valid: list[Dict[str, Any]] = []
        seen_ids: set[str] = set()
        for entity in raw_entities:
            if not isinstance(entity, dict):
                self._reject("invalid_entity")
                continue
            entity_id = self._text(entity.get("id"))
            text = self._text(entity.get("text"))
            entity_type = self._text(entity.get("entity_type")).upper()
            evidence = self._text(entity.get("evidence"))
            if not entity_id:
                self._reject("entity_missing_id")
                continue
            if entity_id in seen_ids:
                self._reject("duplicate_entity_id")
                continue
            if not text or self._is_placeholder(text):
                self._reject("entity_empty_text")
                continue
            if entity_type not in self._ENTITY_TYPES:
                self._reject("entity_invalid_type")
                continue
            if not self._valid_evidence(evidence):
                self._reject("entity_invalid_evidence")
                continue
            seen_ids.add(entity_id)
            valid.append(
                {
                    **entity,
                    "id": entity_id,
                    "text": text,
                    "entity_type": entity_type,
                    "evidence": evidence,
                }
            )
        return valid

    def _filter_relations(
        self, raw_relations: Any, entity_ids: set[str]
    ) -> list[Dict[str, Any]]:
        if not isinstance(raw_relations, list):
            self._reject("invalid_relations")
            return []

        valid: list[Dict[str, Any]] = []
        seen: set[tuple[str, str, str, str]] = set()
        for relation in raw_relations:
            if not isinstance(relation, dict):
                self._reject("invalid_relation")
                continue
            source = self._text(relation.get("source"))
            target = self._text(relation.get("target"))
            relation_type = self._text(relation.get("relation_type")).upper()
            evidence = self._text(relation.get("evidence"))
            if not source or not target:
                self._reject("relation_missing_endpoint")
                continue
            if source not in entity_ids or target not in entity_ids:
                self._reject("relation_orphan_endpoint")
                continue
            if not relation_type or not self._valid_evidence(evidence):
                self._reject("relation_invalid_content")
                continue
            key = (source, relation_type, target, evidence.casefold())
            if key in seen:
                self._reject("duplicate_relation")
                continue
            seen.add(key)
            valid.append(
                {
                    **relation,
                    "source": source,
                    "target": target,
                    "relation_type": relation_type,
                    "evidence": evidence,
                }
            )
        return valid

    def _valid_evidence(self, value: str) -> bool:
        return bool(value) and not self._is_placeholder(value) and any(
            character.isalnum() for character in value
        )

    def _is_placeholder(self, value: str) -> bool:
        normalized = re.sub(r"\s+", " ", value).strip().casefold()
        return normalized in self._PLACEHOLDERS

    @staticmethod
    def _text(value: Any) -> str:
        return value.strip() if isinstance(value, str) else ""

    def _reject(self, reason: str) -> None:
        self.rejection_breakdown[reason] += 1
