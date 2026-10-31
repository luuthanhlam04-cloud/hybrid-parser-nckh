"""Normalize, deduplicate and rank evidence from all AUTO-FUSION branches."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import asdict, dataclass, field
from typing import Any, Iterable, Mapping, Sequence


NODE_LOCATOR = re.compile(
    r"_dieu-(?P<article>\d+)(?:_khoan-(?P<clause>\d+))?(?:_diem-(?P<point>[a-z]+))?",
    re.IGNORECASE,
)


def canonical_locator_from_node_id(node_id: str | None) -> str | None:
    if not node_id:
        return None
    match = NODE_LOCATOR.search(str(node_id))
    if not match:
        return None
    locator = f"LD2024:A{match.group('article')}"
    if match.group("clause"):
        locator += f":K{match.group('clause')}"
    if match.group("point"):
        point = match.group("point").lower()
        point = "đ" if point == "dd" else point
        locator += f":D{point}"
    return locator


def locator_to_article_id(locator: str | None) -> str | None:
    match = re.match(r"LD2024:A(\d+)", locator or "")
    return f"31/2024/qh15#{match.group(1)}" if match else None


def render_legal_locator(locator: str | None) -> str:
    if not locator:
        return "Căn cứ chưa ánh xạ được"
    match = re.fullmatch(r"LD2024:A(\d+)(?::K(\d+))?(?::D([a-zđ]))?", locator)
    if not match:
        return "Căn cứ chưa ánh xạ được"
    article, clause, point = match.groups()
    parts = []
    if point:
        parts.append(f"điểm {point}")
    if clause:
        parts.append(f"khoản {clause}")
    parts.append(f"Điều {article}")
    return " ".join(parts) + " Luật Đất đai 2024"


def _normalized(text: str) -> str:
    return " ".join(unicodedata.normalize("NFC", text).casefold().split())


@dataclass
class EvidenceCandidate:
    node_id: str
    canonical_locator: str | None
    text: str
    source_type: str
    vector_score: float | None = None
    graph_distance: int = 0
    relation_type: str | None = None
    roles: list[str] = field(default_factory=list)
    exact_provenance: bool = True
    parent_locator: str | None = None
    source_locator: str | None = None
    target_locator: str | None = None
    direction: str | None = None
    provenance: str = "NEO4J_OBSERVED"
    rank_score: float = 0.0

    @property
    def alignment_status(self) -> str:
        return "EXACT" if self.canonical_locator and self.exact_provenance else "UNRESOLVED"

    def to_dict(self) -> dict[str, Any]:
        row = asdict(self)
        row["alignment_status"] = self.alignment_status
        row["display_locator"] = render_legal_locator(self.canonical_locator)
        return row


def _roles_from_norm(record: Mapping[str, Any]) -> list[str]:
    roles = []
    for key, role in (
        ("subjects", "SUBJECT"),
        ("actions", "ACTION"),
        ("objects", "OBJECT"),
        ("conditions", "CONDITION"),
        ("exceptions", "EXCEPTION"),
        ("consequences", "CONSEQUENCE"),
    ):
        if record.get(key):
            roles.append(role)
    return roles or ["NORM"]


def _record_candidate(record: Mapping[str, Any], source_type: str) -> EvidenceCandidate | None:
    node_id = str(record.get("node_id") or record.get("anchor_id") or "")
    text = str(record.get("text") or record.get("evidence") or record.get("anchor_text") or "").strip()
    if not node_id or not text:
        return None
    locator = str(record.get("canonical_locator") or "") or canonical_locator_from_node_id(node_id)
    roles = list(record.get("roles") or (_roles_from_norm(record) if source_type == "NORM" else [source_type]))
    return EvidenceCandidate(
        node_id=node_id,
        canonical_locator=locator,
        text=text,
        source_type=source_type,
        vector_score=record.get("score"),
        graph_distance=int(record.get("graph_distance") or 0),
        relation_type=record.get("relation_type"),
        roles=roles,
        exact_provenance=bool(locator),
        parent_locator=record.get("parent_locator") or canonical_locator_from_node_id(str(record.get("parent_id") or "")),
        source_locator=record.get("source_locator"),
        target_locator=record.get("target_locator"),
        direction=record.get("direction"),
        provenance=str(record.get("provenance") or "NEO4J_OBSERVED"),
    )


def collect_candidates(
    *,
    anchors: Sequence[Mapping[str, Any]],
    norms: Sequence[Mapping[str, Any]],
    paths: Sequence[Mapping[str, Any]],
    parents: Sequence[Mapping[str, Any]],
    children: Sequence[Mapping[str, Any]],
    exceptions: Sequence[Mapping[str, Any]],
    physical: Sequence[Mapping[str, Any]],
) -> list[EvidenceCandidate]:
    candidates: list[EvidenceCandidate] = []
    for records, source_type in (
        (anchors, "ANCHOR"),
        (norms, "NORM"),
        (parents, "PARENT"),
        (children, "CHILD"),
        (exceptions, "EXCEPTION"),
        (physical, "PHYSICAL_FALLBACK"),
    ):
        for record in records:
            candidate = _record_candidate(record, source_type)
            if candidate:
                candidates.append(candidate)
    for path in paths:
        source = _record_candidate(
            {
                "node_id": path.get("source_id"),
                "text": path.get("source_text"),
                "canonical_locator": path.get("source_locator"),
                "relation_type": path.get("relation_type"),
                "source_locator": path.get("source_locator"),
                "target_locator": path.get("target_locator"),
                "direction": path.get("direction"),
                "graph_distance": path.get("hop", 1),
                "provenance": path.get("provenance"),
                "roles": ["REFERENCE_SOURCE"],
            },
            "REFERENCE_SOURCE",
        )
        target = _record_candidate(
            {
                "node_id": path.get("target_id"),
                "text": path.get("target_text"),
                "canonical_locator": path.get("target_locator"),
                "relation_type": path.get("relation_type"),
                "source_locator": path.get("source_locator"),
                "target_locator": path.get("target_locator"),
                "direction": path.get("direction"),
                "graph_distance": path.get("hop", 1),
                "provenance": path.get("provenance"),
                "roles": ["REFERENCE_TARGET"],
            },
            "REFERENCE_TARGET",
        )
        if source:
            candidates.append(source)
        if target:
            candidates.append(target)
    return candidates


def _query_tokens(question: str) -> set[str]:
    return {token for token in re.findall(r"[\wđĐ]+", _normalized(question)) if len(token) > 2}


def rank_candidates(question: str, candidates: Iterable[EvidenceCandidate], *, limit: int = 12) -> list[EvidenceCandidate]:
    query_tokens = _query_tokens(question)
    source_priority = {
        "NORM": 1.0,
        "REFERENCE_TARGET": 0.95,
        "ANCHOR": 0.9,
        "CHILD": 0.85,
        "PARENT": 0.8,
        "EXCEPTION": 0.9,
        "REFERENCE_SOURCE": 0.8,
        "PHYSICAL_FALLBACK": 0.75,
    }
    deduplicated: dict[tuple[str, str], EvidenceCandidate] = {}
    for candidate in candidates:
        key = (candidate.canonical_locator or "UNRESOLVED", _normalized(candidate.text))
        existing = deduplicated.get(key)
        if existing is None or source_priority.get(candidate.source_type, 0) > source_priority.get(existing.source_type, 0):
            deduplicated[key] = candidate
    for candidate in deduplicated.values():
        text_tokens = _query_tokens(candidate.text)
        overlap = len(query_tokens & text_tokens) / max(1, len(query_tokens))
        vector = max(0.0, min(1.0, float(candidate.vector_score or 0.0)))
        relation = 1.0 if candidate.relation_type else 0.0
        role_coverage = min(1.0, len(candidate.roles) / 4)
        specificity = 1.0 if candidate.canonical_locator and ":D" in candidate.canonical_locator else 0.75 if candidate.canonical_locator and ":K" in candidate.canonical_locator else 0.5
        provenance = 1.0 if candidate.exact_provenance else 0.0
        candidate.rank_score = round(
            0.35 * max(vector, overlap)
            + 0.20 * overlap
            + 0.15 * relation
            + 0.10 * role_coverage
            + 0.10 * specificity
            + 0.10 * provenance,
            6,
        )
    return sorted(
        deduplicated.values(),
        key=lambda item: (-item.rank_score, item.graph_distance, item.canonical_locator or "~", item.node_id),
    )[:limit]
