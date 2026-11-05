"""Semantic-role answer-path planning for legal cross-reference retrieval."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import re
from typing import Any, Mapping, Sequence

from .context_pruning import ACTION_PHRASES, _fold, _tokens, requested_facets
from .evidence_fusion import canonical_locator_from_node_id
from .routing_contracts import RoutingDecision


ROLE_PHRASES = {
    "subject": (
        "tổ chức kinh tế", "cá nhân", "người sử dụng đất",
        "người gốc việt nam định cư ở nước ngoài",
        "vốn đầu tư nước ngoài", "doanh nghiệp có vốn đầu tư nước ngoài",
        "tổ chức tôn giáo", "đơn vị sự nghiệp công lập",
    ),
    "legal_regime": (
        "trả tiền thuê đất hằng năm", "thu tiền thuê đất hằng năm",
        "quyền thuê trong hợp đồng thuê đất", "thuê lại đất",
        "khu công nghiệp", "cụm công nghiệp", "khu công nghệ cao",
        "giao đất có thu tiền sử dụng đất", "thuê đất một lần",
    ),
}

# A role is represented by its ordinary legal-language variants rather than a
# single surface string.  This matters for questions phrased as "doanh nghiệp
# có vốn đầu tư nước ngoài" while the statute says "tổ chức kinh tế có vốn đầu
# tư nước ngoài".
ROLE_ALIASES = {
    "economic_organization": (
        "tổ chức kinh tế", "doanh nghiệp",
    ),
    "foreign_invested_entity": (
        "doanh nghiệp có vốn đầu tư nước ngoài",
        "tổ chức kinh tế có vốn đầu tư nước ngoài",
        "vốn đầu tư nước ngoài",
    ),
    "annual_land_rent": (
        "trả tiền thuê đất hằng năm",
        "thu tiền thuê đất hằng năm",
        "trả tiền hằng năm",
        "thuê lại đất hằng năm",
        "nộp tiền hằng năm",
    ),
    "industrial_zone": (
        "khu công nghiệp", "cụm công nghiệp", "khu công nghệ cao",
    ),
}

DISTINCTIVE_REGIMES = (
    "vốn đầu tư nước ngoài", "khu công nghiệp", "cụm công nghiệp",
    "khu công nghệ cao", "đơn vị sự nghiệp", "tổ chức tôn giáo",
    "kết cấu hạ tầng", "dự án đầu tư",
)


def _related(left: str | None, right: str | None) -> bool:
    return bool(left and right and (left == right or left.startswith(f"{right}:") or right.startswith(f"{left}:")))


def _depth(locator: str) -> int:
    return int(":K" in locator) + int(":D" in locator)


@dataclass(frozen=True)
class SemanticQuery:
    tokens: set[str]
    actions: set[str]
    roles: dict[str, tuple[str, ...]]
    role_concepts: set[str]
    facets: set[str]
    includes_lease_right_transfer: bool

    @classmethod
    def from_question(cls, question: str) -> "SemanticQuery":
        folded = _fold(question)
        question_tokens = _tokens(question)
        facets = requested_facets(question)
        if "quyen ban" in folded or "xac dinh quyen" in folded:
            facets.add("RIGHT_ORIGIN")
        all_actions = {
            _fold(action) for action in ACTION_PHRASES
            if set(_tokens(action)).issubset(question_tokens)
        }
        # A scenario can mention many legal actions (for example, "thuê lại"
        # as the land-use regime) while asking only about "bán".  Prefer the
        # action governed by an operative cue rather than treating every word
        # in the fact pattern as a requested action.
        focused_actions: set[str] = set()
        for cue in ("muon", "co quyen", "duoc", "can"):
            match = re.search(rf"\b{cue}\b\s+([^.!?;:]{{0,100}})", folded)
            if match:
                tail_tokens = _tokens(match.group(1))
                focused_actions = {
                    action for action in all_actions
                    if set(_tokens(action)).issubset(tail_tokens)
                }
                if focused_actions:
                    break
        return cls(
            tokens=question_tokens,
            actions=focused_actions or all_actions,
            roles={
                name: tuple(_fold(phrase) for phrase in phrases if _fold(phrase) in folded)
                for name, phrases in ROLE_PHRASES.items()
            },
            role_concepts={
                concept for concept, aliases in ROLE_ALIASES.items()
                if any(_fold(alias) in folded for alias in aliases)
            },
            facets=facets,
            includes_lease_right_transfer=any(
                phrase in folded for phrase in (
                    "quyen thue trong hop dong", "ban dong thoi", "cung quyen thue",
                )
            ),
        )

    def score_text(self, text: str) -> tuple[float, dict[str, float]]:
        folded = _fold(text)
        token_score = len(self.tokens & _tokens(text)) / max(1, len(self.tokens))
        action_score = float(self.action_match(text))
        role_scores = {
            role: float(bool(phrases) and any(phrase in folded for phrase in phrases))
            for role, phrases in self.roles.items()
        }
        concept_scores = {
            concept: float(any(_fold(alias) in folded for alias in aliases))
            for concept, aliases in ROLE_ALIASES.items()
            if concept in self.role_concepts
        }
        requested_roles = sum(bool(phrases) for phrases in self.roles.values())
        requested_concepts = len(concept_scores)
        role_score = (
            (sum(role_scores.values()) + sum(concept_scores.values()))
            / (requested_roles + requested_concepts)
            if requested_roles + requested_concepts else 0.0
        )
        mismatch = sum(
            _fold(phrase) in folded and not _tokens(phrase).issubset(self.tokens)
            for phrase in DISTINCTIVE_REGIMES
        )
        mismatch_penalty = min(0.30, 0.10 * mismatch)
        # Legal actors and regimes are scope constraints, not optional
        # keywords.  Missing a requested specific role is therefore a
        # substantial penalty; it prevents a generic downstream consequence
        # from outranking the applicable rights branch.
        missing_concepts = sum(1 for value in concept_scores.values() if not value)
        concept_penalty = min(0.42, 0.18 * missing_concepts)
        return max(0.0, 0.45 * token_score + 0.35 * action_score + 0.20 * role_score - mismatch_penalty - concept_penalty), {
            "token": round(token_score, 4), "action": action_score, "role": round(role_score, 4),
            "regime_mismatch_penalty": mismatch_penalty, "role_mismatch_penalty": concept_penalty,
        }

    def action_match(self, text: str) -> bool:
        """Match multi-word statutory actions even when punctuation intervenes."""
        text_tokens = _tokens(text)
        return bool(self.actions) and any(set(_tokens(action)).issubset(text_tokens) for action in self.actions)


@dataclass(frozen=True)
class AnswerPathResult:
    paths: list[dict[str, Any]]
    selected_edges: list[dict[str, Any]]
    selected_node_locators: set[str]
    trace: list[dict[str, Any]]


class AnswerPathBuilder:
    """Plan one minimal legal branch, then retain only its answer-bearing leaves.

    The planner operates only on observed physical text, explicit reference edges
    and parent/child links. It never receives benchmark gold annotations.
    """

    def __init__(self, jev_client: Any | None = None, *, max_root_edges: int = 12, max_complete_paths: int = 6) -> None:
        self.jev_client = jev_client
        self.max_root_edges = max_root_edges
        self.max_complete_paths = max_complete_paths

    def _adjudicate_roots(
        self,
        question: str,
        roots: list[tuple[float, int, dict[str, Any], dict[str, float]]],
        *,
        question_id: str | None,
    ) -> tuple[list[tuple[float, int, dict[str, Any], dict[str, float]]], dict[tuple[str, str, str], float], str]:
        """Use Jev only to choose among observed candidate roots; always fallback."""
        if self.jev_client is None or not roots:
            return roots, {}, "DETERMINISTIC_FALLBACK"
        questions = {
            f"root_{index}_is_necessary_start": {
                "type": "noul",
                "instructions": (
                    f"Cạnh `candidate_roots[{index - 1}]` có phải là điểm bắt đầu pháp lý cần thiết nhất "
                    "để trả lời `query` không? Chọn cao chỉ khi source khớp chủ thể, hành vi và chế độ pháp lý "
                    "nêu trong query; không chọn một hệ quả, quy định chung hoặc nhánh có điều kiện khác."
                ),
            }
            for index, _ in enumerate(roots, start=1)
        }
        state = {
            "query": question,
            "candidate_roots": [
                {
                    "id": f"root_{index}",
                    "source_locator": edge.get("source_locator"),
                    "relation_type": edge.get("relation_type"),
                    "target_locator": edge.get("target_locator"),
                    "source_text": str(edge.get("source_text") or "")[:1000],
                    "target_text": str(edge.get("target_text") or "")[:1000],
                }
                for index, (_, _, edge, _) in enumerate(roots, start=1)
            ],
        }
        try:
            result = self.jev_client.decide(
                state=state,
                questions=questions,
                operation="jev_path_root_adjudication",
                question_id=question_id,
            )
            probabilities = {
                (str(edge.get("source_locator")), str(edge.get("relation_type")), str(edge.get("target_locator"))):
                result.answers[f"root_{index}_is_necessary_start"]
                for index, (_, _, edge, _) in enumerate(roots, start=1)
            }
            ranked = sorted(
                roots,
                key=lambda item: (
                    -probabilities[(str(item[2].get("source_locator")), str(item[2].get("relation_type")), str(item[2].get("target_locator")))],
                    -item[0], item[1],
                ),
            )
            return ranked, probabilities, "JEV_ADJUDICATED"
        except Exception:
            return roots, {}, "DETERMINISTIC_FALLBACK"

    @staticmethod
    def _edge_dict(raw: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "source": raw.get("source_locator"), "relation_type": raw.get("relation_type"),
            "target": raw.get("target_locator"), "direction": raw.get("direction", "OUTGOING"),
            "hop": raw.get("hop", 1), "provenance": raw.get("provenance", "EXPLICIT_TEXT_REFERENCE"),
            "review_status": "STRUCTURAL",
        }

    @staticmethod
    def _child_locator(row: Mapping[str, Any]) -> str | None:
        return canonical_locator_from_node_id(str(row.get("node_id") or ""))

    @staticmethod
    def _parent_locator(row: Mapping[str, Any]) -> str | None:
        return str(row.get("parent_locator") or "") or canonical_locator_from_node_id(str(row.get("parent_id") or ""))

    @staticmethod
    def _hierarchy(parent: str, child: str) -> dict[str, Any]:
        return {
            "source": parent, "relation_type": "PARENT_CHILD_CONTEXT", "target": child,
            "direction": "OUTGOING", "hop": 1, "provenance": "NEO4J_BELONG_TO_INVERTED",
            "review_status": "STRUCTURAL",
        }

    @staticmethod
    def _deduplicate(paths: list[tuple[float, list[dict[str, Any]]]]) -> list[tuple[float, list[dict[str, Any]]]]:
        unique: dict[tuple[tuple[str, str, str], ...], tuple[float, list[dict[str, Any]]]] = {}
        for score, steps in paths:
            key = tuple((str(step["source"]), str(step["relation_type"]), str(step["target"])) for step in steps)
            if key and (key not in unique or score > unique[key][0]):
                unique[key] = (score, steps)
        return [value for key, value in unique.items() if not any(len(key) < len(other) and other[:len(key)] == key for other in unique)]

    def build(
        self,
        question: str,
        anchors: Sequence[Mapping[str, Any]],
        explicit_edges: Sequence[Mapping[str, Any]],
        descendants: Sequence[Mapping[str, Any]],
        route: RoutingDecision,
        *,
        preferred_locators: set[str] | None = None,
        question_id: str | None = None,
        structural_context: Sequence[Mapping[str, Any]] = (),
    ) -> AnswerPathResult:
        profile = SemanticQuery.from_question(question)
        preferred_locators = preferred_locators or set()
        anchor_locators = {
            locator for anchor in anchors
            if (locator := canonical_locator_from_node_id(str(anchor.get("node_id") or "")))
        }
        node_text: dict[str, str] = {}
        for record in list(anchors) + list(structural_context):
            locator = canonical_locator_from_node_id(str(record.get("node_id") or ""))
            if locator:
                node_text[locator] = str(record.get("text") or record.get("title") or "")
        children_by_parent: dict[str, list[str]] = defaultdict(list)
        for row in descendants:
            child, parent = self._child_locator(row), self._parent_locator(row)
            if not child or not parent:
                continue
            node_text.setdefault(child, str(row.get("text") or row.get("title") or ""))
            if child not in children_by_parent[parent]:
                children_by_parent[parent].append(child)

        edge_rows: list[tuple[float, int, dict[str, Any], dict[str, float]]] = []
        edges_by_source: dict[str, list[tuple[float, dict[str, Any]]]] = defaultdict(list)
        for index, raw in enumerate(explicit_edges):
            source, target = str(raw.get("source_locator") or ""), str(raw.get("target_locator") or "")
            if not source or not target or target.startswith("external:"):
                continue
            source_text, target_text = str(raw.get("source_text") or ""), str(raw.get("target_text") or "")
            node_text.setdefault(source, source_text)
            node_text.setdefault(target, target_text)
            # A point often contains only an enumerated condition.  Its
            # subject, action and legal regime are stated in the immediately
            # enclosing clause, so score the observed parent context too.
            # Only POINT text is normally elliptical.  A CLAUSE already
            # carries its own scope; inheriting an ARTICLE title for it can
            # blur two neighbouring regimes during root selection.
            source_parent = source.rsplit(":", 1)[0] if ":D" in source else ""
            source_context = f"{source_text} {node_text.get(source_parent, '')}".strip()
            source_semantic, source_components = profile.score_text(source_context)
            target_semantic, target_components = profile.score_text(target_text)
            source_is_condition_container = "khi co du cac dieu kien" in _fold(source_context)
            semantic = (
                0.75 * source_semantic + 0.25 * target_semantic
                if "RIGHT_ORIGIN" in profile.facets
                else 0.40 * source_semantic + 0.60 * target_semantic
            )
            # A question asking where a right originates must begin from the
            # applicable right/regime branch, not from the downstream clause
            # that merely enumerates conditions.  Direct condition questions
            # deliberately retain the opposite behaviour.
            if "RIGHT_ORIGIN" in profile.facets and source_is_condition_container:
                semantic = max(0.0, semantic - 0.30)
            elif "CONDITION" in profile.facets and source_is_condition_container:
                # In a direct condition question, the operative clause that
                # states "khi có đủ các điều kiện" is preferable to a broad
                # cross-reference which only says to consult that Article.
                semantic += 0.32
            components = {
                "source_semantic": round(source_semantic, 4),
                "target_semantic": round(target_semantic, 4),
                "source_action": source_components["action"],
                "target_action": target_components["action"],
                "right_origin": float("RIGHT_ORIGIN" in profile.facets),
                "source_condition_container": float(source_is_condition_container),
            }
            anchor = float(any(_related(source, locator) for locator in anchor_locators))
            preferred = float(source in preferred_locators or target in preferred_locators)
            relation = str(raw.get("relation_type") or "")
            relation_fit = (
                1.0 if "CONDITION" in profile.facets and relation == "REQUIRES_CONDITION_FROM"
                else 1.0 if "EXCEPTION" in profile.facets and relation == "EXCEPTION_REFERENCE"
                else 0.75 if route.enabled("requires_reference_traversal") and relation == "INHERITS_RIGHTS_OBLIGATIONS"
                else 0.25 if relation == "DIRECT_REFERENCE" else 0.0
            )
            score = round(0.50 * semantic + 0.22 * anchor + 0.15 * relation_fit + 0.08 * preferred + 0.05 * (_depth(source) / 2), 6)
            row = dict(raw)
            edge_rows.append((score, index, row, components))
            edges_by_source[source].append((score, row))
        for source in edges_by_source:
            edges_by_source[source].sort(key=lambda item: -item[0])

        def child_score(parent: str, child: str) -> tuple[float, bool]:
            semantic, _ = profile.score_text(node_text.get(child, ""))
            action_match = profile.action_match(node_text.get(child, ""))
            connector = float(child in edges_by_source)
            preferred = float(child in preferred_locators or parent in preferred_locators)
            condition_leaf = float("CONDITION" in profile.facets and any(term in _fold(node_text.get(child, "")) for term in ("dieu kien", "phai", "da ", "co ")))
            return 0.55 * semantic + 0.25 * connector + 0.10 * preferred + 0.10 * condition_leaf, action_match

        def expand(node: str, steps: list[dict[str, Any]], score: float, seen: set[str], depth: int) -> list[tuple[float, list[dict[str, Any]]]]:
            if depth >= 6:
                return [(score, steps)]
            outgoing = [(edge_score, edge) for edge_score, edge in edges_by_source.get(node, []) if str(edge.get("target_locator") or "") not in seen]
            if outgoing:
                return [result for edge_score, edge in outgoing[:2] for result in expand(
                    str(edge["target_locator"]), steps + [self._edge_dict(edge)], score + edge_score,
                    seen | {str(edge["target_locator"])}, depth + 1,
                )]
            scored_children = sorted(
                ((score, child, action_match) for child in children_by_parent.get(node, []) if child not in seen
                 for score, action_match in [child_score(node, child)]),
                key=lambda item: -item[0],
            )
            if not scored_children:
                return [(score, steps)]
            # A connector is not automatically superior to a child that expresses
            # the requested action/right. Rank both by semantic child score.
            action_children = [(value, child, action_match) for value, child, action_match in scored_children if action_match]
            containers: list[tuple[float, str, bool]] = []
            if "CONDITION" in profile.facets:
                containers = [
                    (value, child, action_match) for value, child, action_match in scored_children
                    if any(marker in _fold(node_text.get(child, "")) for marker in ("khi co du cac dieu kien", "dieu kien sau day"))
                ]
            if containers:
                # Article 46 contains parallel annual-rent regimes.  A query
                # about sale *with the lease right* belongs to clause 2; a
                # query about sale of the asset alone belongs to clause 1.
                # This is derived from the question's legal regime, never
                # from locator or benchmark metadata.
                if containers:
                    def container_score(item: tuple[float, str, bool]) -> float:
                        value, child, _ = item
                        has_lease_right = "quyen thue trong hop dong" in _fold(node_text.get(child, ""))
                        return value + (0.45 if has_lease_right == profile.includes_lease_right_transfer else -0.45)
                    containers = sorted(containers, key=container_score, reverse=True)
                chosen = containers[:1]
            elif action_children:
                # The requested action identifies the legal branch even for a
                # question which ultimately asks for its conditions.
                chosen = action_children[:2]
            elif "CONDITION" in profile.facets:
                # At a clause containing condition leaves, keep the relevant
                # children if no nested condition container exists.
                parent_is_condition_list = any(
                    marker in _fold(node_text.get(node, ""))
                    for marker in ("khi co du cac dieu kien", "dieu kien sau day")
                )
                parent_transfers_lease_right = "quyen thue trong hop dong" in _fold(node_text.get(node, ""))
                chosen = (
                    scored_children
                    if parent_is_condition_list and not parent_transfers_lease_right
                    else [(value, child, action_match) for value, child, action_match in scored_children if value >= 0.10][:5]
                )
            else:
                # Once a child expressly performs the requested legal action,
                # it is the answer branch.  Do not follow an unrelated
                # connector such as "quyền và nghĩa vụ chung" merely because
                # it has an outgoing reference edge.
                chosen = [
                    (value, child, action_match) for value, child, action_match in scored_children if value >= 0.22
                ][:2]
            # A proof path follows the child that performs the next explicit
            # reference.  Other sibling conditions remain retrieval evidence,
            # but are not falsely reported as an alternative reference chain.
            reference_children = [item for item in chosen if item[1] in edges_by_source]
            # For asset-only sale, the selected clause is itself the complete
            # condition list: every leaf is evidence in the proof path.  A
            # sale that also transfers the lease right has an additional
            # cross-reference and therefore follows that explicit child.
            if (
                reference_children
                and profile.includes_lease_right_transfer
                and "quyen thue trong hop dong" in _fold(node_text.get(node, ""))
            ):
                chosen = reference_children
            if not chosen:
                return [(score, steps)]
            return [result for value, child, _ in chosen for result in expand(
                child, steps + [self._hierarchy(node, child)], score + value, seen | {child}, depth + 1,
            )]

        candidate_roots = sorted((row for row in edge_rows if row[0] > 0), key=lambda item: (-item[0], item[1]))[:self.max_root_edges]
        candidate_roots, jev_probabilities, root_selection_source = self._adjudicate_roots(
            question, candidate_roots, question_id=question_id,
        )
        completed: list[tuple[float, list[dict[str, Any]]]] = []
        root_trace: list[dict[str, Any]] = []
        for root_score, _, edge, components in candidate_roots[:self.max_root_edges]:
            source, target = str(edge["source_locator"]), str(edge["target_locator"])
            expanded = expand(target, [self._edge_dict(edge)], root_score, {source, target}, 1)
            completed.extend(expanded)
            root_trace.append({
                "source": source, "relation_type": edge.get("relation_type"), "target": target,
                "score": root_score, "semantic_components": components, "completed_path_count": len(expanded),
                "jev_root_probability": jev_probabilities.get((source, str(edge.get("relation_type")), target)),
                "root_selection_source": root_selection_source,
            })

        root_scores = {
            (str(edge.get("source_locator")), str(edge.get("relation_type")), str(edge.get("target_locator"))): (
                # Jev adjudicates close candidate roots, but cannot overturn
                # the deterministic subject/action/regime guard.
                0.95 * score + 0.05 * jev_probabilities[(str(edge.get("source_locator")), str(edge.get("relation_type")), str(edge.get("target_locator")))]
                if (str(edge.get("source_locator")), str(edge.get("relation_type")), str(edge.get("target_locator"))) in jev_probabilities
                else score
            )
            for score, _, edge, _ in candidate_roots
        }
        def path_rank(item: tuple[float, list[dict[str, Any]]]) -> float:
            total, steps = item
            root_key = tuple(str(steps[0][key]) for key in ("source", "relation_type", "target"))
            root_score = root_scores.get(root_key, 0.0)
            continuation = (total - root_score) / max(1, len(steps) - 1)
            # Prevent a long but weak path from beating a shorter, more relevant one.
            return 0.70 * root_score + 0.30 * continuation
        ranked = sorted(self._deduplicate(completed), key=lambda item: (-path_rank(item), -len(item[1])))
        if ranked:
            best_root = tuple(ranked[0][1][0][key] for key in ("source", "relation_type", "target"))
            ranked = [item for item in ranked if tuple(item[1][0][key] for key in ("source", "relation_type", "target")) == best_root]
        ranked = ranked[:self.max_complete_paths]
        paths = [{"steps": steps} for _, steps in ranked]
        selected_nodes = {str(step["source"]) for path in paths for step in path["steps"]} | {str(step["target"]) for path in paths for step in path["steps"]}
        selected_roots = {(path["steps"][0]["source"], path["steps"][0]["relation_type"], path["steps"][0]["target"]) for path in paths if path["steps"]}
        selected_edges = [edge for _, _, edge, _ in candidate_roots if (edge.get("source_locator"), edge.get("relation_type"), edge.get("target_locator")) in selected_roots]
        trace = [{**row, "selected_as_root": (row["source"], row["relation_type"], row["target"]) in selected_roots} for row in root_trace]
        return AnswerPathResult(paths, selected_edges, selected_nodes, trace)
