"""M10 orchestration with Jev-assisted, provenance-preserving AUTO-FUSION."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

from .answer_generator import AnswerGenerator
from .answer_path_builder import AnswerPathBuilder
from .anchor_search import AnchorSearch
from .answerability_gate import AnswerabilityGate, GateResult
from .context_assembler import ContextAssembler
from .context_pruning import ContextPruner
from .evidence_fusion import canonical_locator_from_node_id, collect_candidates, rank_candidates
from .graph_query import GraphQuery
from .question_router import QuestionRouter


RetrievalMode = Literal["A", "B", "AUTO", "AUTO_FUSION"]


class M10Pipeline:
    def __init__(
        self,
        anchor_search: AnchorSearch,
        graph_query: GraphQuery,
        answer_generator: AnswerGenerator,
        context_assembler: ContextAssembler | None = None,
        log_path: str | Path | None = "outputs/evaluation/m10_answers.jsonl",
        *,
        jev_client: Any | None = None,
        question_router: QuestionRouter | None = None,
        answerability_gate: AnswerabilityGate | None = None,
        context_pruner: ContextPruner | None = None,
        answer_path_builder: AnswerPathBuilder | None = None,
    ) -> None:
        self.anchor_search = anchor_search
        self.graph_query = graph_query
        self.answer_generator = answer_generator
        self.context_assembler = context_assembler or ContextAssembler()
        self.log_path = Path(log_path) if log_path is not None else None
        self.jev_client = jev_client
        self.question_router = question_router or QuestionRouter(jev_client)
        self.answerability_gate = answerability_gate or AnswerabilityGate(jev_client)
        self.context_pruner = context_pruner or ContextPruner()
        self.answer_path_builder = answer_path_builder or AnswerPathBuilder(jev_client)

    @staticmethod
    def _reference_paths(
        records: list[dict[str, Any]],
        included: list[Any],
    ) -> list[dict[str, Any]]:
        """Compose only explicit legal-reference edges that reached generation context."""
        selected={candidate.canonical_locator for candidate in included if candidate.canonical_locator}
        edges=[]
        for record in records:
            source=record.get("source_locator");target=record.get("target_locator")
            if source in selected and target in selected:
                edges.append({
                    "source":source,"relation_type":record.get("relation_type"),"target":target,
                    "direction":record.get("direction","OUTGOING"),"hop":record.get("hop",1),
                    "provenance":record.get("provenance","EXPLICIT_TEXT_REFERENCE"),"review_status":"STRUCTURAL",
                })
        unique=[]
        for edge in edges:
            if (edge["source"],edge["relation_type"],edge["target"]) not in {
                (item["source"],item["relation_type"],item["target"]) for item in unique
            }:
                unique.append(edge)
        adjacency={}
        for edge in unique:
            adjacency.setdefault(edge["source"],[]).append(edge)
        targets={edge["target"] for edge in unique}
        roots=[source for source in adjacency if source not in targets] or list(adjacency)
        output=[]
        def walk(node,steps,seen):
            next_edges=[edge for edge in adjacency.get(node,[]) if edge["target"] not in seen]
            if not next_edges or len(steps)>=5:
                if steps: output.append({"steps":steps})
                return
            for edge in next_edges:
                walk(edge["target"],steps+[edge],seen|{edge["target"]})
        for root in roots:
            walk(root,[],{root})
        return output

    @staticmethod
    def _hierarchy_context_edges(hierarchy_records: list[dict[str, Any]], included: list[Any]) -> list[dict[str, Any]]:
        """Keep hierarchy evidence auditable without contaminating legal-reference metrics."""
        selected = {candidate.canonical_locator for candidate in included if candidate.canonical_locator}
        edges = []
        for record in hierarchy_records:
            child = canonical_locator_from_node_id(str(record.get("node_id") or ""))
            parent = canonical_locator_from_node_id(str(record.get("parent_id") or ""))
            if parent in selected and child in selected:
                edge = {
                    "source": parent, "relation_type": "PARENT_CHILD_CONTEXT", "target": child,
                    "direction": "OUTGOING", "provenance": "NEO4J_BELONG_TO_INVERTED",
                }
                if edge not in edges:
                    edges.append(edge)
        return edges

    @staticmethod
    def _parent_ids(records: list[dict[str, Any]]) -> list[str]:
        ids = []
        for record in records:
            labels = set(record.get("labels") or [])
            if labels & {"ARTICLE", "CLAUSE"} and record.get("node_id"):
                ids.append(str(record["node_id"]))
        return list(dict.fromkeys(ids))

    def _auto_fusion(
        self,
        question: str,
        anchors: list[dict[str, Any]],
        *,
        question_id: str | None,
        result_limit: int,
    ) -> dict[str, Any]:
        anchor_ids = [str(anchor["node_id"]) for anchor in anchors]
        route = self.question_router.route(question, question_id=question_id)

        auxiliary=[]
        if route.enabled("requires_reference_traversal") and hasattr(self.anchor_search,"search_lexical_auxiliary"):
            auxiliary=self.anchor_search.search_lexical_auxiliary(question,top_k=10)
        path_anchor_ids=list(dict.fromkeys(anchor_ids+[str(item["node_id"]) for item in auxiliary]))

        # Mode A always runs. Typed reference traversal also always runs at one hop.
        norms = self.graph_query.retrieve_mode_a(anchor_ids, limit=result_limit)
        path_hops = 2 if route.enabled("requires_multi_hop") else 1
        # Auxiliary lexical anchors may identify the governing right only after the
        # initial vector anchors. Keep the candidate pool bounded but large enough
        # to include those branches before semantic path planning.
        candidate_paths = self.graph_query.retrieve_typed_paths(path_anchor_ids, max_hops=path_hops, max_paths=result_limit * 12)
        path_pruning = self.context_pruner.prune_paths(question, candidate_paths, path_anchor_ids)
        paths = path_pruning.selected
        physical = self.graph_query.retrieve_physical_evidence(anchor_ids)

        needs_parents = any(
            route.enabled(feature)
            for feature in ("requires_parent_context", "requires_subject_resolution", "requires_all_children")
        )
        parents = self.graph_query.retrieve_parents(anchor_ids, limit=result_limit * 2) if needs_parents else []
        # The semantic path planner evaluates complete branches.  It needs bounded
        # hierarchy below every observed explicit-reference target, not only below
        # edges retained by the earlier evidence pruner.
        reference_target_ids=[str(path["target_id"]) for path in candidate_paths if not str(path.get("target_id","")).startswith("external:")]
        child_sources = anchor_ids + self._parent_ids(parents) + reference_target_ids
        candidate_children = (
            self.graph_query.retrieve_hierarchy_descendants(child_sources, max_depth=2, limit=result_limit * 6)
            if route.enabled("requires_all_children") or route.enabled("requires_reference_traversal")
            else []
        )
        relevant_parent_locators = {
            str(path.get("target_locator")) for path in paths if path.get("target_locator")
        }
        relevant_parent_locators.update(
            locator for node_id in anchor_ids
            if (locator := canonical_locator_from_node_id(node_id))
        )
        child_pruning = self.context_pruner.select_children(
            question, candidate_children, route, relevant_parent_locators=relevant_parent_locators
        )
        children = child_pruning.selected
        exceptions = (
            self.graph_query.retrieve_exception_records(child_sources, limit=result_limit * 3)
            if route.enabled("requires_exception")
            else []
        )

        all_candidates: list[Any] = []
        def build_candidates() -> list[Any]:
            nonlocal all_candidates
            all_candidates = collect_candidates(
                anchors=anchors,
                norms=norms,
                paths=paths,
                parents=parents,
                children=children,
                exceptions=exceptions,
                physical=physical,
            )
            return rank_candidates(
                question,
                all_candidates,
                limit=12,
            )

        candidates = build_candidates()
        initial_gate = self.answerability_gate.assess(
            question,
            candidates,
            route,
            question_id=question_id,
            operation="evidence_relevance_gate",
        )
        expansion_performed: list[str] = []
        final_gate: GateResult = initial_gate

        # One bounded targeted-expansion round. No loop and no more than three Jev calls/question.
        if initial_gate.status == "OK" and initial_gate.missing_facets:
            missing = set(initial_gate.missing_facets)
            if missing & {"subject", "overall_sufficiency"}:
                extra = self.graph_query.retrieve_parents(anchor_ids, limit=result_limit * 2)
                parents.extend(record for record in extra if record not in parents)
                expansion_performed.append("PARENT_CONTEXT")
            if missing & {"conditions", "overall_sufficiency"}:
                target_ids=[str(path["target_id"]) for path in paths if not str(path.get("target_id","")).startswith("external:")]
                sources = anchor_ids + self._parent_ids(parents) + target_ids
                extra = self.graph_query.retrieve_hierarchy_descendants(sources, max_depth=2, limit=result_limit * 6)
                candidate_children.extend(record for record in extra if record not in candidate_children)
                relevant_parent_locators.update(
                    str(path.get("target_locator")) for path in paths if path.get("target_locator")
                )
                child_pruning = self.context_pruner.select_children(
                    question, candidate_children, route, relevant_parent_locators=relevant_parent_locators
                )
                children = child_pruning.selected
                expansion_performed.append("FACET_FILTERED_DIRECT_CHILDREN")
            if missing & {"reference_target", "overall_sufficiency"}:
                extra = self.graph_query.retrieve_typed_paths(path_anchor_ids, max_hops=2, max_paths=result_limit * 12)
                candidate_paths.extend(record for record in extra if record not in candidate_paths)
                path_pruning = self.context_pruner.prune_paths(question, candidate_paths, path_anchor_ids)
                paths = path_pruning.selected
                expansion_performed.append("MINIMAL_TYPED_REFERENCE_PATHS")
            if missing & {"exception", "overall_sufficiency"}:
                sources = anchor_ids + self._parent_ids(parents)
                extra = self.graph_query.retrieve_exception_records(sources, limit=result_limit * 3)
                exceptions.extend(record for record in extra if record not in exceptions)
                expansion_performed.append("EXCEPTION_CONTEXT")
            candidates = build_candidates()
            final_gate = self.answerability_gate.assess(
                question,
                candidates,
                route,
                question_id=question_id,
                operation="post_expansion_sufficiency",
            )

        selected = list(final_gate.kept_candidates or candidates)
        preferred_locators = {candidate.canonical_locator for candidate in selected if candidate.canonical_locator}
        answer_path_result = self.answer_path_builder.build(
            question,
            anchors,
            candidate_paths,
            candidate_children,
            route,
            preferred_locators=preferred_locators,
            question_id=question_id,
        )
        path_evidence = collect_candidates(
            anchors=[], norms=[], paths=candidate_paths, parents=[], children=candidate_children,
            exceptions=[], physical=[],
        )
        primary_locators=[candidate.canonical_locator for candidate in all_candidates if candidate.source_type=="ANCHOR"][:2]
        primary_parent_locators=set()
        for locator in primary_locators:
            if locator:
                primary_parent_locators.add(locator)
                primary_parent_locators.add(locator.rsplit(":",1)[0] if ":" in locator else locator)
        forced=[]
        if route.enabled("requires_all_children"):
            forced.extend(candidate for candidate in all_candidates if candidate.source_type=="CHILD" and candidate.parent_locator in primary_parent_locators)
        if route.enabled("requires_reference_traversal"):
            reference_target_locators={path.get("target_locator") for path in paths if path.get("target_locator")}
            forced.extend(candidate for candidate in all_candidates if candidate.source_type=="CHILD" and candidate.parent_locator in reference_target_locators)
            primary_articles={locator.split(":K",1)[0].split(":D",1)[0] for locator in primary_locators if locator}
            forced.extend(candidate for candidate in all_candidates if candidate.source_type in {"REFERENCE_SOURCE","REFERENCE_TARGET"} and (
                (candidate.source_locator or "").split(":K",1)[0].split(":D",1)[0] in primary_articles
            ))
            auxiliary_ids={str(item["node_id"]) for item in auxiliary}
            auxiliary_path_keys={(path.get("source_locator"),path.get("target_locator")) for path in paths if str(path.get("source_id")) in auxiliary_ids}
            forced.extend(candidate for candidate in all_candidates if candidate.source_type in {"REFERENCE_SOURCE","REFERENCE_TARGET"} and (
                (candidate.source_locator,candidate.target_locator) in auxiliary_path_keys
            ))
        seen={(candidate.canonical_locator,candidate.text) for candidate in selected}
        for candidate in forced:
            key=(candidate.canonical_locator,candidate.text)
            if key not in seen:
                selected.append(candidate);seen.add(key)
        for candidate in path_evidence:
            if candidate.canonical_locator not in answer_path_result.selected_node_locators:
                continue
            key = (candidate.canonical_locator, candidate.text)
            if key not in seen:
                selected.append(candidate)
                seen.add(key)
        context, included, budget = self.context_assembler.assemble_fusion(selected)
        retrieval_records = norms + paths + parents + children + exceptions + physical
        return {
            "mode": "AUTO_FUSION",
            "retrieval_records": retrieval_records,
            "retrieved_count": len(retrieval_records),
            "context": context,
            "routing_trace": {**route.to_dict(),"auxiliary_reference_anchor_count":len(auxiliary)},
            "anchor_records": anchors,
            "auxiliary_reference_anchors": auxiliary,
            "expanded_evidence": [candidate.to_dict() for candidate in candidates],
            "context_evidence": [candidate.to_dict() for candidate in included],
            "reference_paths": answer_path_result.paths,
            "answer_paths": answer_path_result.paths,
            "explicit_reference_edges": [
                step for path in answer_path_result.paths for step in path["steps"]
                if step["relation_type"] != "PARENT_CHILD_CONTEXT"
            ],
            "selected_hierarchy_steps": [
                step for path in answer_path_result.paths for step in path["steps"]
                if step["relation_type"] == "PARENT_CHILD_CONTEXT"
            ],
            "hierarchy_context_edges": self._hierarchy_context_edges(children,included),
            "candidate_reference_paths": candidate_paths,
            "path_pruning_trace": path_pruning.audit,
            "answer_path_trace": answer_path_result.trace,
            "child_pruning_trace": child_pruning.audit,
            "answerability_trace": {
                "initial": initial_gate.to_dict(),
                "expansion_performed": expansion_performed,
                "final": final_gate.to_dict(),
            },
            "context_budget": budget,
            "retrieval_stage_counts": {
                "anchors": len(anchors),
                "norms": len(norms),
                "candidate_typed_paths": len(candidate_paths),
                "typed_paths": len(paths),
                "parents": len(parents),
                "candidate_children": len(candidate_children),
                "children": len(children),
                "exceptions": len(exceptions),
                "physical": len(physical),
                "expanded_candidates": len(candidates),
                "context_candidates": len(included),
            },
        }

    def answer(
        self,
        question: str,
        *,
        mode: RetrievalMode = "AUTO_FUSION",
        top_k: int = 5,
        max_hops: int = 2,
        result_limit: int = 20,
        question_id: str | None = None,
    ) -> dict[str, Any]:
        if not isinstance(question, str) or not question.strip():
            raise ValueError("question must be a non-empty string.")
        normalized_mode = mode.upper()
        if normalized_mode not in {"A", "B", "AUTO", "AUTO_FUSION"}:
            raise ValueError("mode must be 'A', 'B', 'AUTO', or 'AUTO_FUSION'.")
        if normalized_mode == "AUTO":
            normalized_mode = "AUTO_FUSION"

        question = question.strip()
        anchors = self.anchor_search.search(question, top_k=top_k)
        anchor_ids = [anchor["node_id"] for anchor in anchors]

        if normalized_mode == "A":
            records = self.graph_query.retrieve_mode_a(anchor_ids, limit=result_limit)
            stage = {
                "mode": "A",
                "retrieval_records": records,
                "retrieved_count": len(records),
                "context": self.context_assembler.assemble_mode_a(records),
            }
        elif normalized_mode == "B":
            records = self.graph_query.retrieve_mode_b(anchor_ids, max_hops=max_hops, max_paths=result_limit)
            stage = {
                "mode": "B",
                "retrieval_records": records,
                "retrieved_count": len(records),
                "context": self.context_assembler.assemble_mode_b(records),
            }
        else:
            stage = self._auto_fusion(question, anchors, question_id=question_id, result_limit=result_limit)

        generation = self.answer_generator.generate(question, stage["context"])
        result = {
            "request_id": str(uuid4()),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "question_id": question_id,
            "question": question,
            "anchors": anchors,
            **stage,
            "answer": generation["answer"],
            "model": generation["model"],
            "usage": generation.get("usage"),
        }
        if self.log_path is not None:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with self.log_path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(result, ensure_ascii=False) + "\n")
        return result

    def close(self) -> None:
        if self.jev_client is not None and hasattr(self.jev_client, "close"):
            self.jev_client.close()
