"""Parameterized Neo4j queries and explicit-text reference traversal for M10."""

from __future__ import annotations

import re
from collections import defaultdict, deque
from collections.abc import Sequence
from typing import Any

from .evidence_fusion import canonical_locator_from_node_id


class GraphQuery:
    """Retrieve norm records, physical hierarchy and auditable reference paths."""

    MODE_A_QUERY = """
        UNWIND $anchor_ids AS anchor_id
        MATCH (anchor:UKG_NODE:LegalNode {id: anchor_id})
        OPTIONAL MATCH (anchor)-[:MENTIONS]->(direct_norm:UKG_NODE:GLOBAL_NORM)
        OPTIONAL MATCH (anchor)<-[:BELONG_TO*1..3]-(descendant:UKG_NODE:LegalNode)-[:MENTIONS]->(child_norm:UKG_NODE:GLOBAL_NORM)
        WITH anchor, coalesce(direct_norm, child_norm) AS norm, coalesce(descendant, anchor) AS source_node
        WHERE norm IS NOT NULL
        CALL (norm) {
            OPTIONAL MATCH (norm)-[:HAS_SUBJECT]->(entity:UKG_NODE)
            RETURN collect(DISTINCT CASE WHEN entity IS NULL THEN null ELSE {id: entity.id, text: coalesce(entity.canonical_text, entity.name, entity.id)} END) AS subjects
        }
        CALL (norm) {
            OPTIONAL MATCH (norm)-[:HAS_ACTION]->(entity:UKG_NODE)
            RETURN collect(DISTINCT CASE WHEN entity IS NULL THEN null ELSE {id: entity.id, text: coalesce(entity.canonical_text, entity.name, entity.id)} END) AS actions
        }
        CALL (norm) {
            OPTIONAL MATCH (norm)-[:HAS_OBJECT]->(entity:UKG_NODE)
            RETURN collect(DISTINCT CASE WHEN entity IS NULL THEN null ELSE {id: entity.id, text: coalesce(entity.canonical_text, entity.name, entity.id)} END) AS objects
        }
        CALL (norm) {
            OPTIONAL MATCH (norm)-[:HAS_CONDITION]->(entity:UKG_NODE)
            RETURN collect(DISTINCT CASE WHEN entity IS NULL THEN null ELSE {id: entity.id, text: coalesce(entity.canonical_text, entity.name, entity.id)} END) AS conditions
        }
        CALL (norm) {
            OPTIONAL MATCH (norm)-[:HAS_EXCEPTION]->(entity:UKG_NODE)
            RETURN collect(DISTINCT CASE WHEN entity IS NULL THEN null ELSE {id: entity.id, text: coalesce(entity.canonical_text, entity.name, entity.id)} END) AS exceptions
        }
        CALL (norm) {
            OPTIONAL MATCH (norm)-[:HAS_CONSEQUENCE]->(entity:UKG_NODE)
            RETURN collect(DISTINCT CASE WHEN entity IS NULL THEN null ELSE {id: entity.id, text: coalesce(entity.canonical_text, entity.name, entity.id)} END) AS consequences
        }
        OPTIONAL MATCH (source_node)-[:BELONG_TO*0..3]->(article:UKG_NODE:ARTICLE)
        RETURN DISTINCT source_node.id AS anchor_id, source_node.text AS anchor_text,
               source_node.number AS anchor_number, labels(source_node) AS anchor_labels,
               source_node.title AS anchor_title, source_node.law_code AS law_code,
               article.number AS article_number, norm.id AS norm_id, norm.modality AS modality,
               norm.status AS status, norm.evidence AS evidence,
               subjects, actions, objects, conditions, exceptions, consequences
        ORDER BY anchor_id, norm_id
        LIMIT $limit
    """

    MODE_B_QUERY_TEMPLATE = """
        UNWIND $anchor_ids AS anchor_id
        MATCH (anchor:UKG_NODE:LegalNode {id: anchor_id})
        MATCH path=(anchor)-[*1..{max_hops}]-(neighbor:UKG_NODE)
        WHERE neighbor <> anchor
        RETURN DISTINCT anchor.id AS anchor_id,
               [node IN nodes(path) | {id: node.id, node_kind: node.node_kind, labels: labels(node), properties: properties(node)}] AS nodes,
               [rel IN relationships(path) | {type: type(rel), source_id: startNode(rel).id, target_id: endNode(rel).id, properties: properties(rel)}] AS relationships
        LIMIT $max_paths
    """

    PHYSICAL_QUERY = """
        MATCH (node:UKG_NODE:LegalNode)
        RETURN node.id AS node_id, node.text AS text, node.title AS title,
               node.number AS number, node.parent_id AS parent_id,
               node.law_code AS law_code, labels(node) AS labels
        ORDER BY node.id
    """

    PARENT_QUERY = """
        UNWIND $anchor_ids AS anchor_id
        MATCH (anchor:UKG_NODE:LegalNode {id: anchor_id})-[:BELONG_TO*1..3]->(node:UKG_NODE:LegalNode)
        RETURN DISTINCT node.id AS node_id, coalesce(node.text, node.title) AS text,
               node.title AS title, node.number AS number, node.parent_id AS parent_id,
               node.law_code AS law_code, labels(node) AS labels,
               1 AS graph_distance, 'PARENT' AS source_type
        LIMIT $limit
    """

    CHILD_QUERY = """
        UNWIND $anchor_ids AS anchor_id
        MATCH (node:UKG_NODE:LegalNode)-[:BELONG_TO]->(anchor:UKG_NODE:LegalNode {id: anchor_id})
        RETURN DISTINCT node.id AS node_id, coalesce(node.text, node.title) AS text,
               node.title AS title, node.number AS number, node.parent_id AS parent_id,
               node.law_code AS law_code, labels(node) AS labels,
               node.position AS position, 1 AS graph_distance, 'CHILD' AS source_type
        ORDER BY position, node_id
        LIMIT $limit
    """

    DESCENDANT_QUERY_TEMPLATE = """
        UNWIND $anchor_ids AS anchor_id
        MATCH (node:UKG_NODE:LegalNode)-[:BELONG_TO*1..{max_depth}]->(anchor:UKG_NODE:LegalNode {id: anchor_id})
        RETURN DISTINCT node.id AS node_id, coalesce(node.text, node.title) AS text,
               node.title AS title, node.number AS number, node.parent_id AS parent_id,
               node.law_code AS law_code, labels(node) AS labels,
               node.position AS position, 'CHILD' AS source_type
        ORDER BY node_id
        LIMIT $limit
    """

    PHYSICAL_ANCHOR_QUERY = """
        UNWIND $anchor_ids AS anchor_id
        MATCH (node:UKG_NODE:LegalNode {id: anchor_id})
        RETURN node.id AS node_id, coalesce(node.text, node.title) AS text,
               node.title AS title, node.number AS number, node.parent_id AS parent_id,
               node.law_code AS law_code, labels(node) AS labels,
               0 AS graph_distance, 'PHYSICAL_FALLBACK' AS source_type
    """

    def __init__(self, driver: Any, database: str | None = None) -> None:
        self.driver = driver
        self.database = database

    @staticmethod
    def _validate_anchor_ids(anchor_ids: Sequence[str]) -> list[str]:
        if isinstance(anchor_ids, (str, bytes)):
            raise ValueError("anchor_ids must be a sequence of node IDs, not a string.")
        normalized: list[str] = []
        for anchor_id in anchor_ids:
            if not isinstance(anchor_id, str) or not anchor_id.strip():
                raise ValueError("Every anchor ID must be a non-empty string.")
            if anchor_id not in normalized:
                normalized.append(anchor_id)
        return normalized

    @staticmethod
    def _positive_int(value: int, name: str) -> None:
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ValueError(f"{name} must be a positive integer.")

    def _run(self, query: str, **parameters: Any) -> list[dict[str, Any]]:
        with self.driver.session(database=self.database) as session:
            return [dict(record) for record in session.run(query, **parameters)]

    def retrieve_mode_a(self, anchor_ids: Sequence[str], *, limit: int = 20) -> list[dict[str, Any]]:
        anchors = self._validate_anchor_ids(anchor_ids)
        self._positive_int(limit, "limit")
        return self._run(self.MODE_A_QUERY, anchor_ids=anchors, limit=limit) if anchors else []

    def retrieve_mode_b(self, anchor_ids: Sequence[str], *, max_hops: int = 2, max_paths: int = 100) -> list[dict[str, Any]]:
        anchors = self._validate_anchor_ids(anchor_ids)
        self._positive_int(max_hops, "max_hops")
        self._positive_int(max_paths, "max_paths")
        if max_hops > 3:
            raise ValueError("max_hops cannot exceed 3.")
        if not anchors:
            return []
        query = self.MODE_B_QUERY_TEMPLATE.replace("{max_hops}", str(max_hops))
        return self._run(query, anchor_ids=anchors, max_paths=max_paths)

    def retrieve_parents(self, anchor_ids: Sequence[str], *, limit: int = 30) -> list[dict[str, Any]]:
        anchors = self._validate_anchor_ids(anchor_ids)
        self._positive_int(limit, "limit")
        return self._run(self.PARENT_QUERY, anchor_ids=anchors, limit=limit) if anchors else []

    def retrieve_all_direct_children(self, anchor_ids: Sequence[str], *, limit: int = 80) -> list[dict[str, Any]]:
        anchors = self._validate_anchor_ids(anchor_ids)
        self._positive_int(limit, "limit")
        return self._run(self.CHILD_QUERY, anchor_ids=anchors, limit=limit) if anchors else []

    def retrieve_hierarchy_descendants(
        self, anchor_ids: Sequence[str], *, max_depth: int = 2, limit: int = 120,
    ) -> list[dict[str, Any]]:
        """Read a bounded legal hierarchy branch for answer-path reconstruction."""
        anchors = self._validate_anchor_ids(anchor_ids)
        self._positive_int(max_depth, "max_depth")
        self._positive_int(limit, "limit")
        if max_depth > 2:
            raise ValueError("max_depth cannot exceed 2 for answer-path reconstruction.")
        if not anchors:
            return []
        query = self.DESCENDANT_QUERY_TEMPLATE.replace("{max_depth}", str(max_depth))
        return self._run(query, anchor_ids=anchors, limit=limit)

    def retrieve_physical_evidence(self, anchor_ids: Sequence[str]) -> list[dict[str, Any]]:
        anchors = self._validate_anchor_ids(anchor_ids)
        return self._run(self.PHYSICAL_ANCHOR_QUERY, anchor_ids=anchors) if anchors else []

    def retrieve_exception_records(self, anchor_ids: Sequence[str], *, limit: int = 40) -> list[dict[str, Any]]:
        records = self.retrieve_all_direct_children(anchor_ids, limit=limit)
        markers = ("trừ trường hợp", "không được", "chỉ được", "ngoại lệ", "hạn chế")
        return [record for record in records if any(marker in str(record.get("text", "")).casefold() for marker in markers)]

    @staticmethod
    def _locator_parts(locator: str | None) -> tuple[str | None, str | None, str | None]:
        match = re.fullmatch(r"LD2024:A(\d+)(?::K(\d+))?(?::D([a-zđ]))?", locator or "")
        return match.groups() if match else (None, None, None)

    @staticmethod
    def _relation_type(text: str, target_article: str) -> str:
        lowered = text.casefold()
        if target_article and not 26 <= int(target_article) <= 48:
            return "EXTERNAL_REFERENCE"
        if "trừ trường hợp" in lowered or "ngoại lệ" in lowered:
            return "EXCEPTION_REFERENCE"
        if "điều kiện quy định tại" in lowered or "phải đáp ứng" in lowered:
            return "REQUIRES_CONDITION_FROM"
        if "quyền và nghĩa vụ" in lowered or "tương ứng" in lowered:
            return "INHERITS_RIGHTS_OBLIGATIONS"
        return "DIRECT_REFERENCE"

    @classmethod
    def _extract_reference_locators(cls, text: str, source_locator: str | None) -> list[tuple[str, str]]:
        """Extract only explicit legal references; never infer a missing target."""
        article, source_clause, _ = cls._locator_parts(source_locator)
        found: list[tuple[str, str]] = []

        def add(target: str) -> None:
            target_article = cls._locator_parts(target)[0]
            if target_article:
                pair = (target, cls._relation_type(text, target_article))
                if pair not in found and target != source_locator:
                    found.append(pair)

        occupied: list[tuple[int, int]] = []
        for match in re.finditer(r"điểm\s+([a-zđ])\s+khoản\s+(\d+)\s+Điều\s+(\d+)", text, re.IGNORECASE):
            point, clause, target_article = match.groups()
            add(f"LD2024:A{target_article}:K{clause}:D{point.casefold()}")
            occupied.append(match.span())
        for match in re.finditer(r"khoản\s+(\d+(?:\s*(?:,|và)\s*khoản\s+\d+)*)\s+Điều\s+(\d+)", text, re.IGNORECASE):
            if any(start <= match.start() < end for start, end in occupied):
                continue
            clauses, target_article = match.groups()
            for clause in re.findall(r"\d+", clauses):
                add(f"LD2024:A{target_article}:K{clause}")
            occupied.append(match.span())
        for match in re.finditer(r"Điều\s+(\d+(?:\s*(?:,|và)\s*Điều\s+\d+)*)", text, re.IGNORECASE):
            if any(start <= match.start() < end for start, end in occupied):
                continue
            for target_article in re.findall(r"\d+", match.group(1)):
                add(f"LD2024:A{target_article}")
        if article:
            for match in re.finditer(r"điểm\s+([a-zđ])\s+khoản\s+(\d+)\s+Điều\s+này", text, re.IGNORECASE):
                add(f"LD2024:A{article}:K{match.group(2)}:D{match.group(1).casefold()}")
            for match in re.finditer(r"khoản\s+(\d+)\s+Điều\s+này", text, re.IGNORECASE):
                add(f"LD2024:A{article}:K{match.group(1)}")
            if source_clause:
                for match in re.finditer(r"điểm\s+([a-zđ])\s+khoản\s+này", text, re.IGNORECASE):
                    add(f"LD2024:A{article}:K{source_clause}:D{match.group(1).casefold()}")
        return found

    def retrieve_typed_paths(self, anchor_ids: Sequence[str], *, max_hops: int = 1, max_paths: int = 100) -> list[dict[str, Any]]:
        """Resolve explicit references against physical nodes without mutating M8/M9."""
        anchors = self._validate_anchor_ids(anchor_ids)
        self._positive_int(max_hops, "max_hops")
        self._positive_int(max_paths, "max_paths")
        if max_hops > 2:
            raise ValueError("Typed reference traversal is bounded to two hops.")
        if not anchors:
            return []
        nodes = self._run(self.PHYSICAL_QUERY)
        by_id = {str(node["node_id"]): node for node in nodes}
        by_locator = {locator: node for node in nodes if (locator := canonical_locator_from_node_id(str(node.get("node_id", ""))))}
        children: dict[str, list[str]] = defaultdict(list)
        for node in nodes:
            if node.get("parent_id"):
                children[str(node["parent_id"])].append(str(node["node_id"]))

        initial: list[str] = []
        for anchor_id in anchors:
            if anchor_id in by_id:
                initial.append(anchor_id)
                initial.extend(children.get(anchor_id, []))
        queue = deque((node_id, 1) for node_id in dict.fromkeys(initial))
        visited: set[tuple[str, int]] = set()
        paths: list[dict[str, Any]] = []
        while queue and len(paths) < max_paths:
            source_id, hop = queue.popleft()
            if (source_id, hop) in visited or hop > max_hops:
                continue
            visited.add((source_id, hop))
            source = by_id.get(source_id)
            if not source:
                continue
            source_text = str(source.get("text") or source.get("title") or "").strip()
            source_locator = canonical_locator_from_node_id(source_id)
            if not source_text or not source_locator:
                continue
            for target_locator, relation_type in self._extract_reference_locators(source_text, source_locator):
                target = by_locator.get(target_locator)
                target_id = str(target["node_id"]) if target else f"external:{target_locator}"
                target_text = str((target or {}).get("text") or (target or {}).get("title") or "").strip()
                record = {
                    "source_id": source_id,
                    "source_locator": source_locator,
                    "source_text": source_text,
                    "relation_type": relation_type,
                    "target_id": target_id,
                    "target_locator": target_locator,
                    "target_text": target_text,
                    "hop": hop,
                    "direction": "OUTGOING",
                    "provenance": "EXPLICIT_TEXT_REFERENCE",
                    "relationships": [{
                        "source_id": source_id,
                        "source_locator": source_locator,
                        "type": relation_type,
                        "target_id": target_id,
                        "target_locator": target_locator,
                        "direction": "OUTGOING",
                        "provenance": "EXPLICIT_TEXT_REFERENCE",
                    }],
                }
                if not any(row["source_locator"] == source_locator and row["relation_type"] == relation_type and row["target_locator"] == target_locator for row in paths):
                    paths.append(record)
                if target and hop < max_hops:
                    queue.append((target_id, hop + 1))
                    for child_id in children.get(target_id, []):
                        queue.append((child_id, hop + 1))
        return paths[:max_paths]
