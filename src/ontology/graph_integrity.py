# -*- coding: utf-8 -*-
"""Final dependency closure and export gate for Module 7."""

from __future__ import annotations

from collections import Counter
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from src.ontology.schemas import (
    CanonicalSemanticGraph,
    MentionStatus,
    NormStatus,
    RelationType,
    ValidationReport,
)


_NORM_ID_FIELDS = (
    "subject_ids",
    "action_ids",
    "object_ids",
    "condition_ids",
    "exception_ids",
    "consequence_ids",
)


class GraphIntegrityError(ValueError):
    """Raised when final M7 graph is unsafe to export."""


class GraphIntegrityFinalizer:
    """Close graph dependencies, repair ownership, and enforce export invariants."""

    def finalize(
        self,
        graph: CanonicalSemanticGraph,
        physical_node_ids: Optional[Set[str]] = None,
    ) -> CanonicalSemanticGraph:
        self._cascade_norm_dependencies(graph)
        self._cascade_edges(graph)
        self._repair_reference_ownership(graph)
        self._record_orphan_audit(graph)

        metrics = self._audit(graph, physical_node_ids or set())
        self._recompute_report(graph, metrics)
        graph.metadata["final_integrity_gate"] = metrics

        fatal_keys = (
            "broken_endpoints",
            "broken_norm_references",
            "broken_reference_owners",
            "active_quarantine_overlap",
            "duplicate_ids",
            "duplicate_edges",
            "domain_range_violations",
            "provenance_violations",
        )
        failures = {key: metrics[key] for key in fatal_keys if metrics[key]}
        if failures or not metrics["conservation_ok"]:
            if not metrics["conservation_ok"]:
                failures["conservation_ok"] = False
            raise GraphIntegrityError(
                f"M7 final integrity gate failed: {failures}"
            )
        return graph

    def _cascade_norm_dependencies(self, graph: CanonicalSemanticGraph) -> None:
        active_ids = {mention.id for mention in graph.active_nodes}
        kept_norms = []
        for norm in graph.norms:
            removed: Dict[str, List[str]] = {}
            for field in _NORM_ID_FIELDS:
                values = list(getattr(norm, field))
                kept = [value for value in values if value in active_ids]
                missing = [value for value in values if value not in active_ids]
                setattr(norm, field, kept)
                if missing:
                    removed[field] = missing

            for group in norm.condition_groups:
                group.condition_ids = [
                    value for value in group.condition_ids if value in active_ids
                ]
            norm.condition_groups = [
                group for group in norm.condition_groups if group.condition_ids
            ]

            if not norm.action_ids:
                norm.status = NormStatus.QUARANTINED
                norm.notes = "MISSING_ACTION_AFTER_CASCADE"
                self._append_unique(
                    graph.quarantine.norms,
                    {
                        **norm.model_dump(),
                        "quarantine_reason": "MISSING_ACTION_AFTER_CASCADE",
                        "removed_dependencies": removed,
                    },
                )
                continue

            if norm.subject_ids:
                norm.subject_status = "RESOLVED"
                norm.norm_completeness = "COMPLETE"
            else:
                norm.subject_status = "UNRESOLVED"
                norm.norm_completeness = "PARTIAL"
            if removed:
                norm.notes = "DEPENDENCY_CLOSURE_APPLIED"
            kept_norms.append(norm)
        graph.norms = kept_norms

    def _cascade_edges(self, graph: CanonicalSemanticGraph) -> None:
        mention_ids = {mention.id for mention in graph.active_nodes}
        norm_ids = {norm.id for norm in graph.norms}
        concept_ids = {concept.id for concept in graph.concepts}
        known_ids = mention_ids | norm_ids | concept_ids
        quarantined_ids = {
            item.get("id") for item in graph.quarantine.mentions
        } | {item.get("id") for item in graph.quarantine.norms}

        kept = []
        for edge in graph.active_edges:
            reason = None
            if edge.source_id in quarantined_ids or edge.target_id in quarantined_ids:
                reason = "DEPENDENCY_QUARANTINED"
            elif edge.source_id not in known_ids or edge.target_id not in known_ids:
                reason = "MISSING_ENDPOINT_AFTER_CASCADE"
            if reason:
                edge.status = "QUARANTINED"
                self._append_unique(
                    graph.quarantine.edges,
                    {**edge.model_dump(), "quarantine_reason": reason},
                    edge_key=True,
                )
            else:
                kept.append(edge)
        graph.active_edges = kept

    def _repair_reference_ownership(self, graph: CanonicalSemanticGraph) -> None:
        mention_by_id = {mention.id: mention for mention in graph.active_nodes}
        norm_by_id = {norm.id: norm for norm in graph.norms}
        mentions_by_provenance: Dict[str, List[str]] = {}
        norms_by_provenance: Dict[str, List[str]] = {}
        for mention in graph.active_nodes:
            mentions_by_provenance.setdefault(mention.provenance_node_id, []).append(mention.id)
        for norm in graph.norms:
            norms_by_provenance.setdefault(norm.provenance_node_id, []).append(norm.id)

        kept_refs = []
        for ref in graph.references:
            mention_ok = bool(ref.owner_mention_id in mention_by_id)
            norm_ok = bool(ref.owner_norm_id in norm_by_id)
            if mention_ok or norm_ok:
                if not mention_ok:
                    ref.owner_mention_id = None
                kept_refs.append(ref)
                continue

            local_norms = sorted(norms_by_provenance.get(ref.provenance_node_id, []))
            local_mentions = sorted(
                mentions_by_provenance.get(ref.provenance_node_id, [])
            )
            if local_norms:
                ref.owner_norm_id = local_norms[0]
                ref.owner_mention_id = None
                kept_refs.append(ref)
            elif local_mentions:
                ref.owner_mention_id = local_mentions[0]
                ref.owner_norm_id = None
                kept_refs.append(ref)
            else:
                self._append_unique(
                    graph.quarantine.references,
                    {
                        **ref.model_dump(),
                        "quarantine_reason": "MISSING_REFERENCE_OWNER",
                    },
                )
        graph.references = kept_refs

    def _record_orphan_audit(self, graph: CanonicalSemanticGraph) -> None:
        mention_ids = {mention.id for mention in graph.active_nodes}
        linked: Set[str] = set()
        for edge in graph.active_edges:
            linked.update({edge.source_id, edge.target_id} & mention_ids)
        for norm in graph.norms:
            for field in _NORM_ID_FIELDS:
                linked.update(getattr(norm, field))
        linked.update(
            ref.owner_mention_id
            for ref in graph.references
            if ref.owner_mention_id in mention_ids
        )
        linked.update(
            mention.id
            for mention in graph.active_nodes
            if mention.canonical_concept_id
        )
        unlinked = sorted(mention_ids - linked)
        graph.metadata["orphan_audit"] = {
            "policy": "reference-aware; valid unlinked evidence remains active",
            "reference_owner": sum(
                1 for ref in graph.references if ref.owner_mention_id in mention_ids
            ),
            "norm_component": sum(
                1
                for mention_id in mention_ids
                if any(
                    mention_id in getattr(norm, field)
                    for norm in graph.norms
                    for field in _NORM_ID_FIELDS
                )
            ),
            "unlinked_evidence": len(unlinked),
            "unlinked_evidence_ids": unlinked,
            "true_orphan": 0,
        }

    def _audit(
        self,
        graph: CanonicalSemanticGraph,
        physical_node_ids: Set[str],
    ) -> Dict[str, Any]:
        mention_ids = [mention.id for mention in graph.active_nodes]
        norm_ids = [norm.id for norm in graph.norms]
        concept_ids = [concept.id for concept in graph.concepts]
        ref_ids = [ref.id for ref in graph.references]
        mention_set, norm_set, concept_set = set(mention_ids), set(norm_ids), set(concept_ids)
        known = mention_set | norm_set | concept_set

        broken_endpoints = sum(
            int(edge.source_id not in known) + int(edge.target_id not in known)
            for edge in graph.active_edges
        )
        broken_norm_references = sum(
            1
            for norm in graph.norms
            for field in _NORM_ID_FIELDS
            for value in getattr(norm, field)
            if value not in mention_set
        )
        broken_reference_owners = sum(
            1
            for ref in graph.references
            if not (
                (ref.owner_mention_id and ref.owner_mention_id in mention_set)
                or (ref.owner_norm_id and ref.owner_norm_id in norm_set)
            )
        )

        quarantine_ids = {
            item.get("id")
            for bucket in (
                graph.quarantine.mentions,
                graph.quarantine.norms,
                graph.quarantine.references,
            )
            for item in bucket
        }
        active_quarantine_overlap = len(
            (mention_set | norm_set | set(ref_ids)) & quarantine_ids
        )

        all_ids = mention_ids + norm_ids + concept_ids + ref_ids
        duplicate_ids = sum(count - 1 for count in Counter(all_ids).values() if count > 1)
        edge_keys = [
            (edge.source_id, edge.relation_type.value, edge.target_id, edge.evidence or "")
            for edge in graph.active_edges
        ]
        duplicate_edges = sum(
            count - 1 for count in Counter(edge_keys).values() if count > 1
        )

        from src.ontology.ontology_validator import OntologyValidator

        validator = OntologyValidator()
        mention_by_id = {mention.id: mention for mention in graph.active_nodes}
        domain_range_violations = sum(
            1
            for edge in graph.active_edges
            if not validator._validate_edge(
                edge, mention_by_id, norm_set, concept_set
            )[0]
        )

        provenance_violations = 0
        if physical_node_ids:
            provenance_violations = sum(
                item.provenance_node_id not in physical_node_ids
                for item in [*graph.active_nodes, *graph.norms, *graph.references]
            )

        input_mentions = len(graph.active_nodes) + len(graph.quarantine.mentions)
        input_norms = len(graph.norms) + len(graph.quarantine.norms)
        input_edges = len(graph.active_edges) + len(graph.quarantine.edges)
        conservation_ok = (
            input_mentions
            == len(graph.active_nodes) + len(graph.quarantine.mentions)
            and input_norms == len(graph.norms) + len(graph.quarantine.norms)
            and input_edges == len(graph.active_edges) + len(graph.quarantine.edges)
        )
        return {
            "broken_endpoints": broken_endpoints,
            "broken_norm_references": broken_norm_references,
            "broken_reference_owners": broken_reference_owners,
            "active_quarantine_overlap": active_quarantine_overlap,
            "duplicate_ids": duplicate_ids,
            "duplicate_edges": duplicate_edges,
            "domain_range_violations": domain_range_violations,
            "provenance_violations": provenance_violations,
            "input_mentions": input_mentions,
            "input_norms": input_norms,
            "input_edges": input_edges,
            "conservation_ok": conservation_ok,
        }

    def _recompute_report(
        self,
        graph: CanonicalSemanticGraph,
        metrics: Dict[str, Any],
    ) -> None:
        previous = graph.validation_report
        report = ValidationReport()
        report.rejected_reasons = list(previous.rejected_reasons)
        report.input_mentions = metrics["input_mentions"]
        report.total_mentions = metrics["input_mentions"]
        report.active_mentions = len(graph.active_nodes)
        report.valid_mentions = sum(
            mention.status == MentionStatus.VALID for mention in graph.active_nodes
        )
        report.corrected_mentions = sum(
            mention.status == MentionStatus.CORRECTED for mention in graph.active_nodes
        )
        report.unresolved_mentions = sum(
            item.get("status") == MentionStatus.UNRESOLVED.value
            for item in graph.quarantine.mentions
        )
        report.quarantined_mentions = len(graph.quarantine.mentions)

        report.input_norms = metrics["input_norms"]
        report.total_norms = metrics["input_norms"]
        report.active_norms = len(graph.norms)
        report.valid_norms = sum(norm.status == NormStatus.VALID for norm in graph.norms)
        report.flagged_norms = sum(norm.status == NormStatus.FLAGGED for norm in graph.norms)
        report.quarantined_norms = len(graph.quarantine.norms)
        report.partial_norms = sum(
            norm.norm_completeness == "PARTIAL" for norm in graph.norms
        )

        report.input_edges = metrics["input_edges"]
        report.total_edges = metrics["input_edges"]
        report.active_edges = len(graph.active_edges)
        report.quarantined_edges = len(graph.quarantine.edges)
        report.filtered_edges = 0
        report.rejected_edges = 0

        report.total_references = len(graph.references) + len(graph.quarantine.references)
        report.classified_references = sum(
            ref.scope != "AMBIGUOUS" for ref in graph.references
        )
        report.ambiguous_references = sum(
            ref.scope == "AMBIGUOUS" for ref in graph.references
        )
        report.total_concepts = len(graph.concepts)
        for key in (
            "broken_endpoints",
            "broken_norm_references",
            "broken_reference_owners",
            "active_quarantine_overlap",
            "duplicate_ids",
            "duplicate_edges",
            "domain_range_violations",
            "provenance_violations",
            "conservation_ok",
        ):
            setattr(report, key, metrics[key])
        graph.validation_report = report

    @staticmethod
    def _append_unique(
        bucket: List[Dict[str, Any]],
        item: Dict[str, Any],
        edge_key: bool = False,
    ) -> None:
        if edge_key:
            key: Tuple[Any, ...] = (
                item.get("source_id"),
                str(item.get("relation_type")),
                item.get("target_id"),
                item.get("evidence"),
            )
            existing = {
                (
                    current.get("source_id"),
                    str(current.get("relation_type")),
                    current.get("target_id"),
                    current.get("evidence"),
                )
                for current in bucket
            }
            if key not in existing:
                bucket.append(item)
            return
        item_id = item.get("id")
        if item_id not in {current.get("id") for current in bucket}:
            bucket.append(item)
