"""Validation of M4/M7 graph inputs before fusion."""

from __future__ import annotations

import math
from typing import Any, Dict, Iterable


class GraphContractError(ValueError):
    pass


PHYSICAL_EDGE_TYPES = {"BELONG_TO", "NEXT", "PREVIOUS"}
SEMANTIC_RELATION_TYPES = {
    "ALLOW", "REQUIRE", "PROHIBIT", "HAS_CONDITION", "HAS_EXCEPTION",
    "REFERENCE_TO", "HAS_PENALTY", "HAS_OBJECT", "HAS_CONSEQUENCE",
}
SEMANTIC_CLASSES = {
    "LEGAL_SUBJECT", "LEGAL_ACTION", "LEGAL_OBJECT", "LEGAL_CONSEQUENCE",
    "CONDITION", "EXCEPTION", "LEGAL_DOCUMENT_REF", "PENALTY",
}


def _require_list(data: Dict[str, Any], key: str, label: str) -> list[Any]:
    value = data.get(key)
    if not isinstance(value, list):
        raise GraphContractError(f"{label}.{key} must be a list")
    return value


def _unique_ids(items: Iterable[Dict[str, Any]], key: str, label: str) -> set[str]:
    found: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise GraphContractError(f"{label}[{index}] must be an object")
        value = item.get(key)
        if not isinstance(value, str) or not value.strip():
            raise GraphContractError(f"{label}[{index}].{key} must be a non-empty string")
        if value in found:
            raise GraphContractError(f"Duplicate {label} ID: {value}")
        found.add(value)
    return found


def validate_graph_inputs(
    physical: Dict[str, Any], semantic: Dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    physical_nodes = _require_list(physical, "nodes", "physical")
    physical_edges = _require_list(physical, "edges", "physical")
    entities = _require_list(semantic, "entities", "semantic")
    relations = _require_list(semantic, "relations", "semantic")

    physical_ids = _unique_ids(physical_nodes, "id", "physical.nodes")
    semantic_ids = _unique_ids(entities, "canonical_id", "semantic.entities")
    collisions = physical_ids & semantic_ids
    if collisions:
        raise GraphContractError(f"Physical/semantic node ID collision: {sorted(collisions)}")

    node_by_id = {node["id"]: node for node in physical_nodes}
    for index, node in enumerate(physical_nodes):
        if not isinstance(node.get("labels"), list) or not node["labels"]:
            raise GraphContractError(f"physical.nodes[{index}].labels must be a non-empty list")
        if not isinstance(node.get("properties", {}), dict):
            raise GraphContractError(f"physical.nodes[{index}].properties must be an object")
        parent_id = node.get("properties", {}).get("parent_id")
        if parent_id and parent_id not in physical_ids:
            raise GraphContractError(
                f"Physical node {node['id']} references missing parent {parent_id}"
            )
    for node_id in physical_ids:
        visited: set[str] = set()
        current = node_id
        while current:
            if current in visited:
                raise GraphContractError(f"Physical parent cycle detected at node {current}")
            visited.add(current)
            current = node_by_id[current].get("properties", {}).get("parent_id")

    for index, edge in enumerate(physical_edges):
        if not isinstance(edge, dict):
            raise GraphContractError(f"physical.edges[{index}] must be an object")
        for endpoint in ("source", "target"):
            if edge.get(endpoint) not in physical_ids:
                raise GraphContractError(
                    f"Physical edge {index} has missing {endpoint}: {edge.get(endpoint)}"
                )
        if edge.get("type") not in PHYSICAL_EDGE_TYPES:
            raise GraphContractError(
                f"Unsupported physical edge type at index {index}: {edge.get('type')}"
            )
        if not isinstance(edge.get("properties", {}), dict):
            raise GraphContractError(f"physical.edges[{index}].properties must be an object")
        if edge["type"] == "BELONG_TO":
            expected_parent = node_by_id[edge["source"]].get(
                "properties", {}
            ).get("parent_id")
            if expected_parent and expected_parent != edge["target"]:
                raise GraphContractError(
                    f"BELONG_TO edge for {edge['source']} disagrees with parent_id"
                )

    for index, entity in enumerate(entities):
        if not isinstance(entity.get("ontology_class"), str) or not entity["ontology_class"]:
            raise GraphContractError(
                f"semantic.entities[{index}].ontology_class must be a non-empty string"
            )
        if entity["ontology_class"] not in SEMANTIC_CLASSES:
            raise GraphContractError(
                f"Unsupported semantic ontology class at index {index}: "
                f"{entity['ontology_class']}"
            )

    for index, relation in enumerate(relations):
        if not isinstance(relation, dict):
            raise GraphContractError(f"semantic.relations[{index}] must be an object")
        if relation.get("relation_type") not in SEMANTIC_RELATION_TYPES:
            raise GraphContractError(
                f"Unsupported semantic relation type at index {index}: "
                f"{relation.get('relation_type')}"
            )
        relation_id = relation.get("relation_id")
        if not isinstance(relation_id, str) or not relation_id.strip():
            raise GraphContractError(
                f"semantic.relations[{index}].relation_id must be a non-empty string"
            )
    relation_ids = [relation["relation_id"] for relation in relations]
    if len(set(relation_ids)) != len(relation_ids):
        raise GraphContractError("Semantic relation IDs must be unique")
        if relation.get("source") not in semantic_ids or relation.get("target") not in semantic_ids:
            raise GraphContractError(
                f"Semantic relation {relation.get('relation_id')} has an unknown entity endpoint"
            )
        if not isinstance(relation.get("source_node_id"), str) or not relation["source_node_id"]:
            raise GraphContractError(
                f"Semantic relation {relation.get('relation_id')} has no source_node_id"
            )
        if not isinstance(relation.get("evidence"), str) or not relation["evidence"].strip():
            raise GraphContractError(
                f"Semantic relation {relation.get('relation_id')} has no evidence"
            )
        normalized_evidence = relation["evidence"].strip().casefold()
        if normalized_evidence in {"...", "unknown", "none", "null", "n/a", "na", "test"}:
            raise GraphContractError(
                f"Semantic relation {relation['relation_id']} has placeholder evidence"
            )
        for confidence_key in ("confidence", "confidence_m6", "similarity", "sim_vector"):
            confidence = relation.get(confidence_key)
            if confidence is None:
                continue
            if (
                isinstance(confidence, bool)
                or not isinstance(confidence, (int, float))
                or not math.isfinite(float(confidence))
                or not 0.0 <= float(confidence) <= 1.0
            ):
                raise GraphContractError(
                    f"{relation['relation_id']}.{confidence_key} must be finite and within [0, 1]"
                )

    return physical_nodes, physical_edges, entities, relations
