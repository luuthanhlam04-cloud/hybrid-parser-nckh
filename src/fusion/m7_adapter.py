"""Adapt both legacy M7 and concept/norm-based M7 outputs for fusion."""

from __future__ import annotations

from typing import Any, Dict


SEMANTIC_CLASS_MAP = {
    "LegalSubject": "LEGAL_SUBJECT",
    "LegalAction": "LEGAL_ACTION",
    "LegalObject": "LEGAL_OBJECT",
    "LegalConsequence": "LEGAL_CONSEQUENCE",
    "Condition": "CONDITION",
    "Exception": "EXCEPTION",
    "Reference": "LEGAL_DOCUMENT_REF",
}


def _value(value: Any) -> str:
    return str(getattr(value, "value", value))


class M7GraphAdapter:
    """Normalize M7 v1.3 and v1.2 graph contracts to a fusion input contract."""

    @classmethod
    def adapt(cls, graph: Dict[str, Any]) -> Dict[str, Any]:
        if "entities" in graph and "relations" in graph:
            return {
                "entities": graph["entities"],
                "relations": graph["relations"],
                "mention_nodes": [],
                "denotes_edges": [],
            }
        if not any(key in graph for key in ("active_nodes", "concepts", "norms")):
            raise ValueError(
                "Unsupported M7 graph: expected entities/relations or "
                "active_nodes/concepts/norms"
            )

        mentions = {
            mention["id"]: mention
            for mention in graph.get("active_nodes", [])
            if mention.get("id")
        }
        concepts = {
            concept["id"]: concept
            for concept in graph.get("concepts", [])
            if concept.get("id")
        }
        entity_by_id: Dict[str, Dict[str, Any]] = {}
        for concept_id, concept in concepts.items():
            semantic_type = _value(concept.get("concept_type", ""))
            entity_by_id[concept_id] = {
                "canonical_id": concept_id,
                "ontology_class": SEMANTIC_CLASS_MAP.get(
                    semantic_type, semantic_type.upper()
                ),
                "canonical_text": concept.get("preferred_name", concept_id),
                "aliases": list(concept.get("alt_labels", [])),
                "fusion_kind": "CANONICAL_CONCEPT",
            }

        mention_to_concept: Dict[str, str] = {}
        mention_nodes = []
        denotes_edges = []
        for mention_id, mention in mentions.items():
            semantic_type = _value(mention.get("semantic_type", ""))
            concept_id = mention.get("canonical_concept_id")
            ontology_class = SEMANTIC_CLASS_MAP.get(
                semantic_type, semantic_type.upper()
            )
            if concept_id and concept_id in concepts:
                mention_to_concept[mention_id] = concept_id
                denotes_edges.append({
                    "source": mention_id,
                    "target": concept_id,
                    "type": "DENOTES",
                    "properties": {
                        "evidence": mention.get("evidence", ""),
                        "source_node_id": mention.get("provenance_node_id"),
                        "provenance": "M7",
                    },
                    "provenance": ["M7"],
                })
            entity_by_id[mention_id] = {
                "canonical_id": mention_id,
                "ontology_class": ontology_class,
                "canonical_text": mention.get("raw_text", mention_id),
                "aliases": [],
                "fusion_kind": "LOCAL_MENTION",
                "mention_type": _value(mention.get("mention_type", "")),
                "semantic_type": semantic_type,
                "subtype": mention.get("subtype"),
                "status": _value(mention.get("status", "VALID")),
                "type_hierarchy": list(mention.get("type_hierarchy", [])),
                "source_node_id": mention.get("provenance_node_id"),
                "evidence": mention.get("evidence", ""),
            }
            mention_nodes.append(mention)

        def canonical_endpoint(endpoint_id: str) -> str:
            return mention_to_concept.get(endpoint_id, endpoint_id)

        relations = []
        rejected_relations = []
        for edge_index, edge in enumerate(graph.get("active_edges", [])):
            relation_type = _value(edge.get("relation_type", ""))
            source_id = edge.get("source_id")
            target_id = edge.get("target_id")
            if not source_id or not target_id:
                continue
            source_mention = mentions.get(source_id)
            target_mention = mentions.get(target_id)
            source_node_id = (
                (source_mention or target_mention or {}).get("provenance_node_id")
            )
            if relation_type == "DENOTES":
                continue
            if relation_type in {"HAS_SUBJECT", "HAS_ACTION"}:
                continue
            edge_status = _value(edge.get("status", "VALID")).upper()
            if edge_status not in {"VALID", "ASSERTED"}:
                rejected_relations.append({
                    "relation_id": f"M7EDGE_{edge_index:06d}_{relation_type}",
                    "reason": "M7_EDGE_NOT_ACTIVE",
                    "status": edge_status,
                })
                continue
            source_id = canonical_endpoint(source_id)
            target_id = canonical_endpoint(target_id)
            if source_id not in entity_by_id or target_id not in entity_by_id:
                continue
            relations.append({
                "relation_id": edge.get(
                    "id", f"M7EDGE_{edge_index:06d}_{relation_type}"
                ),
                "relation_type": relation_type,
                "source_node_id": source_node_id,
                "source": source_id,
                "target": target_id,
                "evidence": edge.get("evidence")
                or (source_mention or target_mention or {}).get("evidence", ""),
                "rule_id": edge.get("rule_id"),
                "assertion_status": edge.get("status", "ASSERTED"),
            })

        for norm in graph.get("norms", []):
            modality = _value(norm.get("modality", ""))
            provenance = norm.get("provenance_node_id")
            norm_id = norm.get("id", "UNKNOWN_NORM")
            norm_status = _value(norm.get("status", "VALID")).upper()
            if norm_status != "VALID":
                rejected_relations.append({
                    "relation_id": norm_id,
                    "reason": "M7_NORM_NOT_ACTIVE",
                    "status": norm_status,
                })
                continue
            for subject_index, subject_id in enumerate(norm.get("subject_ids", [])):
                for action_index, action_id in enumerate(norm.get("action_ids", [])):
                    subject = canonical_endpoint(subject_id)
                    action = canonical_endpoint(action_id)
                    if subject not in entity_by_id or action not in entity_by_id:
                        continue
                    condition_ids = list(norm.get("condition_ids", []))
                    for condition_group in norm.get("condition_groups", []):
                        condition_ids.extend(condition_group.get("condition_ids", []))
                    condition_ids = list(dict.fromkeys(condition_ids))
                    relations.append({
                        "relation_id": f"{norm_id}:norm:{subject_index}:{action_index}",
                        "norm_id": norm_id,
                        "relation_type": modality,
                        "source_node_id": provenance,
                        "source": subject,
                        "target": action,
                        "evidence": norm.get("evidence", ""),
                        "condition_ids": [
                            canonical_endpoint(item)
                            for item in condition_ids
                        ],
                        "exception_ids": [
                            canonical_endpoint(item)
                            for item in norm.get("exception_ids", [])
                        ],
                        "condition_groups": norm.get("condition_groups", []),
                        "norm_status": norm_status,
                    })
                    for index, condition_id in enumerate(condition_ids):
                        condition = canonical_endpoint(condition_id)
                        if condition in entity_by_id:
                            relations.append({
                                "relation_id": (
                                    f"{norm_id}:condition:{subject_index}:"
                                    f"{action_index}:{index}"
                                ),
                                "relation_type": "HAS_CONDITION",
                                "source_node_id": provenance,
                                "source": action,
                                "target": condition,
                                "evidence": norm.get("evidence", ""),
                            })
                    for index, exception_id in enumerate(norm.get("exception_ids", [])):
                        exception = canonical_endpoint(exception_id)
                        if exception in entity_by_id:
                            relations.append({
                                "relation_id": (
                                    f"{norm_id}:exception:{subject_index}:"
                                    f"{action_index}:{index}"
                                ),
                                "relation_type": "HAS_EXCEPTION",
                                "source_node_id": provenance,
                                "source": action,
                                "target": exception,
                                "evidence": norm.get("evidence", ""),
                            })
                    for index, object_id in enumerate(norm.get("object_ids", [])):
                        object_entity = canonical_endpoint(object_id)
                        if object_entity in entity_by_id:
                            relations.append({
                                "relation_id": (
                                    f"{norm_id}:object:{subject_index}:"
                                    f"{action_index}:{index}"
                                ),
                                "relation_type": "HAS_OBJECT",
                                "source_node_id": provenance,
                                "source": action,
                                "target": object_entity,
                                "evidence": norm.get("evidence", ""),
                            })
                    for index, consequence_id in enumerate(
                        norm.get("consequence_ids", [])
                    ):
                        consequence = canonical_endpoint(consequence_id)
                        if consequence in entity_by_id:
                            relations.append({
                                "relation_id": (
                                    f"{norm_id}:consequence:{subject_index}:"
                                    f"{action_index}:{index}"
                                ),
                                "relation_type": "HAS_CONSEQUENCE",
                                "source_node_id": provenance,
                                "source": action,
                                "target": consequence,
                                "evidence": norm.get("evidence", ""),
                            })

        norms_by_id = {norm.get("id"): norm for norm in graph.get("norms", [])}
        for reference in graph.get("references", []):
            reference_id = reference.get("id")
            if not reference_id:
                continue
            entity_by_id[reference_id] = {
                "canonical_id": reference_id,
                "ontology_class": "LEGAL_DOCUMENT_REF",
                "canonical_text": reference.get("raw_text", reference_id),
                "aliases": [],
                "fusion_kind": "REFERENCE",
            }
            owner_norm = norms_by_id.get(reference.get("owner_norm_id"), {})
            owner_id = reference.get("owner_mention_id")
            if not owner_id and owner_norm.get("subject_ids"):
                owner_id = owner_norm["subject_ids"][0]
            if not owner_id and owner_norm.get("action_ids"):
                owner_id = owner_norm["action_ids"][0]
            if not owner_id:
                continue
            owner_id = canonical_endpoint(owner_id)
            if owner_id not in entity_by_id:
                continue
            relations.append({
                "relation_id": reference_id,
                "relation_type": "REFERENCE_TO",
                "source_node_id": reference.get("provenance_node_id"),
                "source": owner_id,
                "target": reference_id,
                "evidence": reference.get("evidence", ""),
                "reference_scope": reference.get("scope"),
                "target_hint": reference.get("target_hint"),
            })

        return {
            "entities": list(entity_by_id.values()),
            "relations": relations,
            "mention_nodes": mention_nodes,
            "denotes_edges": denotes_edges,
            "rejected_relations": rejected_relations,
        }
