"""Question-aware pruning for typed reference paths and hierarchy children."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .evidence_fusion import canonical_locator_from_node_id
from .routing_contracts import RoutingDecision


STOPWORDS = {
    "cua", "cho", "voi", "theo", "trong", "duoc", "nhung", "cac", "khi",
    "nay", "la", "va", "co", "gi", "nao", "phai", "ve", "doi", "tai",
}


def _fold(text: str) -> str:
    value = unicodedata.normalize("NFD", str(text).casefold())
    return "".join(char for char in value if unicodedata.category(char) != "Mn").replace("đ", "d")


def _tokens(text: str) -> set[str]:
    return {
        token for token in re.findall(r"[a-z0-9]+", _fold(text))
        if len(token) > 2 and token not in STOPWORDS
    }


ACTION_PHRASES = (
    "chuyển đổi", "chuyển nhượng", "cho thuê lại", "cho thuê", "thế chấp",
    "góp vốn", "tặng cho", "thừa kế", "bán tài sản", "đăng ký", "khấu trừ",
)
FACET_PHRASES = {
    "CONDITION": ("điều kiện", "đáp ứng", "khi có đủ", "phải"),
    "EXCEPTION": ("ngoại lệ", "trừ trường hợp", "không áp dụng", "chỉ được"),
    "SUBJECT": ("ai", "chủ thể", "đối tượng", "tổ chức", "cá nhân", "người"),
    "RECIPIENT": ("tại ai", "cho ai", "bên nhận", "tổ chức tín dụng", "ngân hàng"),
}


def requested_facets(question: str) -> set[str]:
    folded = _fold(question)
    facets = {
        facet for facet, phrases in FACET_PHRASES.items()
        if any(_fold(phrase) in folded for phrase in phrases)
    }
    if re.search(r"bao gom|liet ke|nhung gi|cac dieu kien", folded):
        facets.add("LIST")
    return facets


@dataclass(frozen=True)
class PruningResult:
    selected: list[dict[str, Any]]
    audit: list[dict[str, Any]]


class ContextPruner:
    def __init__(self, *, max_paths: int = 3, max_children_per_parent: int = 5) -> None:
        self.max_paths = max_paths
        self.max_children_per_parent = max_children_per_parent

    @staticmethod
    def _locator_article(locator: str | None) -> str | None:
        match = re.match(r"LD2024:A\d+", locator or "")
        return match.group(0) if match else None

    def prune_paths(
        self,
        question: str,
        paths: Sequence[Mapping[str, Any]],
        anchor_ids: Sequence[str],
    ) -> PruningResult:
        """Keep a small connected, query-relevant subgraph; retain all decisions for audit."""
        query_tokens = _tokens(question)
        anchor_locators = {canonical_locator_from_node_id(node_id) for node_id in anchor_ids}
        anchor_articles = {self._locator_article(locator) for locator in anchor_locators if locator}
        scored: list[tuple[float, int, dict[str, Any]]] = []
        for index, raw in enumerate(paths):
            row = dict(raw)
            source = str(row.get("source_locator") or "")
            target = str(row.get("target_locator") or "")
            text_tokens = _tokens(f"{row.get('source_text', '')} {row.get('target_text', '')}")
            overlap = len(query_tokens & text_tokens) / max(1, len(query_tokens))
            source_seed = source in anchor_locators or self._locator_article(source) in anchor_articles
            target_seed = target in anchor_locators or self._locator_article(target) in anchor_articles
            hop = max(1, int(row.get("hop") or 1))
            score = 0.55 * overlap + 0.30 * float(source_seed) + 0.10 * float(target_seed) + 0.05 / hop
            scored.append((round(score, 6), index, row))

        scored.sort(key=lambda item: (-item[0], int(item[2].get("hop") or 1), item[1]))
        selected: list[dict[str, Any]] = []
        selected_keys: set[tuple[str, str, str]] = set()
        reached = {locator for locator in anchor_locators if locator}
        remaining = list(scored)
        while remaining and len(selected) < self.max_paths:
            def connected_to_reached(item: tuple[float, int, dict[str, Any]]) -> bool:
                source = str(item[2].get("source_locator") or "")
                return any(source == locator or source.startswith(f"{locator}:") or locator.startswith(f"{source}:") for locator in reached)

            connected = [item for item in remaining if connected_to_reached(item)]
            score, index, row = (connected or remaining)[0]
            key = (str(row.get("source_locator")), str(row.get("relation_type")), str(row.get("target_locator")))
            remaining.remove((score, index, row))
            if key in selected_keys:
                continue
            selected.append(row)
            selected_keys.add(key)
            reached.add(row.get("target_locator"))

        audit = []
        for score, _, row in scored:
            key = (str(row.get("source_locator")), str(row.get("relation_type")), str(row.get("target_locator")))
            audit.append({
                "source": row.get("source_locator"),
                "relation_type": row.get("relation_type"),
                "target": row.get("target_locator"),
                "score": score,
                "selected": key in selected_keys,
                "reason": "MINIMAL_CONNECTED_PATH" if key in selected_keys else "LOWER_RANK_OR_REDUNDANT_PATH",
            })
        return PruningResult(selected, audit)

    def select_children(
        self,
        question: str,
        children: Sequence[Mapping[str, Any]],
        route: RoutingDecision,
        *,
        relevant_parent_locators: set[str],
    ) -> PruningResult:
        query_tokens = _tokens(question)
        folded_question = _fold(question)
        actions = {_fold(action) for action in ACTION_PHRASES if _fold(action) in folded_question}
        facets = requested_facets(question)
        rows: list[tuple[float, int, str, dict[str, Any], list[str]]] = []
        for index, raw in enumerate(children):
            row = dict(raw)
            text = str(row.get("text") or row.get("evidence") or row.get("anchor_text") or "")
            folded_text = _fold(text)
            parent = str(row.get("parent_locator") or canonical_locator_from_node_id(str(row.get("parent_id") or "")) or "")
            overlap = len(query_tokens & _tokens(text)) / max(1, len(query_tokens))
            action_match = 1.0 if actions and any(action in folded_text for action in actions) else 0.0
            condition_match = 1.0 if "CONDITION" in facets and any(term in folded_text for term in ("dieu kien", "phai", "da ", "co ")) else 0.0
            exception_match = 1.0 if "EXCEPTION" in facets and any(term in folded_text for term in ("tru ", "khong duoc", "chi duoc")) else 0.0
            parent_match = 1.0 if parent in relevant_parent_locators else 0.0
            reasons = []
            if action_match: reasons.append("ACTION_MATCH")
            if condition_match: reasons.append("CONDITION_MATCH")
            if exception_match: reasons.append("EXCEPTION_MATCH")
            if overlap: reasons.append("LEXICAL_MATCH")
            if parent_match: reasons.append("RELEVANT_PARENT")
            score = 0.40 * action_match + 0.25 * overlap + 0.15 * condition_match + 0.10 * exception_match + 0.10 * parent_match
            rows.append((round(score, 6), index, parent, row, reasons))

        selected_keys: set[tuple[str, str]] = set()
        selected: list[dict[str, Any]] = []
        grouped: dict[str, list[tuple[float, int, str, dict[str, Any], list[str]]]] = {}
        for item in rows:
            grouped.setdefault(item[2], []).append(item)
        for parent, items in grouped.items():
            items.sort(key=lambda item: (-item[0], item[1]))
            if parent not in relevant_parent_locators:
                continue
            # Complete-list questions may retain all point children, but only under relevant parents.
            threshold = 0.10 if route.enabled("requires_all_children") and "LIST" in facets else 0.25
            kept = [item for item in items if item[0] >= threshold][: self.max_children_per_parent]
            if not kept and items:
                kept = items[:1]
            for _, _, _, row, _ in kept:
                key = (str(row.get("node_id")), parent)
                if key not in selected_keys:
                    selected.append(row)
                    selected_keys.add(key)

        audit = []
        for score, _, parent, row, reasons in sorted(rows, key=lambda item: (-item[0], item[1])):
            key = (str(row.get("node_id")), parent)
            is_selected = key in selected_keys
            audit.append({
                "node_id": row.get("node_id"),
                "locator": canonical_locator_from_node_id(str(row.get("node_id") or "")),
                "parent_locator": parent or None,
                "score": score,
                "selected": is_selected,
                "reason": reasons if is_selected else ["UNRELATED_BRANCH_OR_BELOW_THRESHOLD"],
            })
        return PruningResult(selected, audit)
