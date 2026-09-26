"""Optional W3C SHACL validation for a fused graph.

The core fusion pipeline does not require pyshacl. Calling ``validate`` makes
the dependency requirement explicit instead of silently skipping validation.
"""

from __future__ import annotations

from collections import defaultdict
import re
from pathlib import Path
from typing import Any, Dict, Tuple

STRUCTURAL_LABELS = {"CHAPTER", "SECTION", "ARTICLE", "CLAUSE", "POINT"}
VALID_HIERARCHY_PAIRS = {
    ("SECTION", "CHAPTER"),
    ("ARTICLE", "SECTION"),
    ("ARTICLE", "CHAPTER"),
    ("CLAUSE", "ARTICLE"),
    ("POINT", "CLAUSE"),
    ("POINT", "POINT"),
}
VALID_SEMANTIC_PAIRS = {
    "ALLOW": {("LEGAL_SUBJECT", "LEGAL_ACTION")},
    "PROHIBIT": {("LEGAL_SUBJECT", "LEGAL_ACTION")},
    "REQUIRE": {
        ("LEGAL_SUBJECT", "LEGAL_ACTION"),
        ("LEGAL_ACTION", "LEGAL_ACTION"),
    },
    "HAS_CONDITION": {
        ("LEGAL_SUBJECT", "CONDITION"),
        ("LEGAL_ACTION", "CONDITION"),
    },
    "HAS_EXCEPTION": {
        ("LEGAL_ACTION", "EXCEPTION"),
        ("CONDITION", "EXCEPTION"),
    },
    "HAS_CONSEQUENCE": {("LEGAL_ACTION", "LEGAL_CONSEQUENCE")},
    "REFERENCE_TO": {
        ("LEGAL_SUBJECT", "LEGAL_DOCUMENT_REF"),
        ("LEGAL_ACTION", "LEGAL_DOCUMENT_REF"),
        ("CONDITION", "LEGAL_DOCUMENT_REF"),
        ("EXCEPTION", "LEGAL_DOCUMENT_REF"),
        ("PENALTY", "LEGAL_DOCUMENT_REF"),
        ("LEGAL_DOCUMENT_REF", "LEGAL_DOCUMENT_REF"),
        ("LEGAL_OBJECT", "LEGAL_DOCUMENT_REF"),
    },
    "HAS_PENALTY": {("LEGAL_ACTION", "PENALTY")},
    "HAS_OBJECT": {
        ("LEGAL_ACTION", "LEGAL_OBJECT"),
        ("LEGAL_ACTION", "LEGAL_SUBJECT"),
        ("LEGAL_SUBJECT", "LEGAL_OBJECT"),
        ("LEGAL_SUBJECT", "LEGAL_SUBJECT"),
    },
    "DENOTES": {
        (ontology_class, ontology_class)
        for ontology_class in (
            "LEGAL_SUBJECT", "LEGAL_ACTION", "LEGAL_OBJECT",
            "LEGAL_CONSEQUENCE", "CONDITION", "EXCEPTION",
            "LEGAL_DOCUMENT_REF", "PENALTY",
        )
    },
}


def _hierarchy_cycle_nodes(graph: Dict[str, Any]) -> set[str]:
    adjacency: dict[str, set[str]] = defaultdict(set)
    for node in graph.get("nodes", []):
        node_id = str(node.get("id", ""))
        parent_id = node.get("properties", {}).get("parent_id")
        if node_id and parent_id:
            adjacency[node_id].add(str(parent_id))
    for edge in graph.get("edges", []):
        if edge.get("type") == "BELONG_TO":
            adjacency[str(edge.get("source", ""))].add(
                str(edge.get("target", ""))
            )

    visited: set[str] = set()
    cycle_nodes: set[str] = set()
    for start in adjacency:
        if start in visited:
            continue
        path: list[str] = []
        path_positions: dict[str, int] = {}
        stack: list[tuple[str, Any]] = [(start, iter(adjacency[start]))]
        path.append(start)
        path_positions[start] = 0
        while stack:
            current, targets = stack[-1]
            try:
                target = next(targets)
            except StopIteration:
                stack.pop()
                visited.add(current)
                path_positions.pop(current, None)
                path.pop()
                continue
            if target in path_positions:
                cycle_nodes.update(path[path_positions[target]:])
            elif target not in visited:
                path_positions[target] = len(path)
                path.append(target)
                stack.append((target, iter(adjacency.get(target, set()))))
    return cycle_nodes


class ShaclValidator:
    def __init__(self, shapes_path: str | Path | None = None) -> None:
        self.shapes_path = Path(shapes_path or Path(__file__).with_name("shapes.ttl"))

    def validate(self, graph: Dict[str, Any]) -> Tuple[bool, str, str]:
        try:
            from pyshacl import validate
            from rdflib import Graph, Literal, RDF, URIRef
        except ImportError as exc:
            raise RuntimeError(
                "SHACL validation requires pyshacl and rdflib. "
                "Install dependencies from requirements.txt."
            ) from exc

        data_graph = Graph()
        namespace = "https://hybrid-parser.example/kg#"
        kg = namespace
        node_uris = {
            node["id"]: URIRef(f"{namespace}node/{node['id']}")
            for node in graph.get("nodes", [])
        }
        hierarchy_cycles = _hierarchy_cycle_nodes(graph)
        node_labels = {
            node["id"]: set(node.get("labels", []))
            for node in graph.get("nodes", [])
            if node.get("node_kind") == "PHYSICAL"
        }
        ontology_classes = {
            node["id"]: node.get("properties", {}).get("ontology_class")
            for node in graph.get("nodes", [])
            if node.get("node_kind") == "SEMANTIC"
        }
        for node in graph.get("nodes", []):
            node_uri = node_uris[node["id"]]
            node_kind = node.get("node_kind")
            data_graph.add((node_uri, RDF.type, URIRef(f"{kg}GraphNode")))
            if node_kind == "PHYSICAL":
                data_graph.add((
                    node_uri, RDF.type, URIRef(f"{kg}PhysicalNode")
                ))
            elif node_kind == "SEMANTIC":
                data_graph.add((
                    node_uri, RDF.type, URIRef(f"{kg}SemanticNode")
                ))
            data_graph.add((
                node_uri, URIRef(f"{kg}nodeId"), Literal(str(node["id"]))
            ))
            data_graph.add((
                node_uri,
                URIRef(f"{kg}hasHierarchyCycle"),
                Literal(str(node["id"]) in hierarchy_cycles),
            ))
            article_number = node.get("properties", {}).get("number")
            article_number_valid = (
                "ARTICLE" not in node.get("labels", [])
                or bool(re.fullmatch(r"[1-9][0-9]*", str(article_number or "")))
            )
            data_graph.add((
                node_uri,
                URIRef(f"{kg}articleNumberValid"),
                Literal(article_number_valid),
            ))
            if node_kind == "SEMANTIC":
                ontology_class = node.get("properties", {}).get("ontology_class")
                if ontology_class:
                    data_graph.add((
                        node_uri, URIRef(f"{kg}ontologyClass"),
                        Literal(str(ontology_class)),
                    ))
            elif node_kind == "PHYSICAL":
                for label in node.get("labels", []):
                    data_graph.add((
                        node_uri, URIRef(f"{kg}label"), Literal(str(label)),
                    ))
                properties = node.get("properties", {})
                number = properties.get("number")
                if number is not None:
                    data_graph.add((
                        node_uri, URIRef(f"{kg}number"), Literal(str(number)),
                    ))
                parent_id = properties.get("parent_id")
                if parent_id in node_uris:
                    data_graph.add((
                        node_uri, URIRef(f"{kg}parent"), node_uris[parent_id],
                    ))

        for index, edge in enumerate(graph.get("edges", [])):
            edge_uri = URIRef(f"{namespace}edge/{index}")
            is_physical = edge.get("type") in {"BELONG_TO", "NEXT", "PREVIOUS"}
            data_graph.add((edge_uri, RDF.type, URIRef(f"{kg}Edge")))
            data_graph.add((
                edge_uri, RDF.type,
                URIRef(f"{kg}{'PhysicalEdge' if is_physical else 'Edge'}"),
            ))
            if not is_physical and edge.get("type") not in {"MENTIONS", "RESOLVES_TO"}:
                data_graph.add((edge_uri, RDF.type, URIRef(f"{kg}SemanticRelation")))
            data_graph.add((
                edge_uri, URIRef(f"{kg}edgeType"), Literal(str(edge.get("type", ""))),
            ))
            structure_valid = bool(
                edge.get("type")
                and edge.get("source") in node_uris
                and edge.get("target") in node_uris
            )
            data_graph.add((
                edge_uri, URIRef(f"{kg}edgeStructureValid"),
                Literal(structure_valid),
            ))
            if edge.get("source") in node_uris:
                data_graph.add((
                    edge_uri, URIRef(f"{kg}source"), node_uris[edge["source"]],
                ))
            if edge.get("target") in node_uris:
                data_graph.add((
                    edge_uri, URIRef(f"{kg}target"), node_uris[edge["target"]],
                ))
            if edge.get("type") == "BELONG_TO":
                source_uri = node_uris.get(edge.get("source"))
                if source_uri is not None:
                    data_graph.add((
                        source_uri, URIRef(f"{kg}belongsToSource"), edge_uri,
                    ))
            edge_type = str(edge.get("type", ""))
            source_label = next(iter(
                node_labels.get(str(edge.get("source")), set())
                & STRUCTURAL_LABELS
            ), None)
            target_label = next(iter(
                node_labels.get(str(edge.get("target")), set())
                & STRUCTURAL_LABELS
            ), None)
            hierarchy_valid = not (
                edge_type == "BELONG_TO"
                and source_label is not None
                and target_label is not None
                and (source_label, target_label) not in VALID_HIERARCHY_PAIRS
            )
            sequence_valid = not (
                edge_type in {"NEXT", "PREVIOUS"}
                and source_label is not None
                and target_label is not None
                and source_label != target_label
            )
            data_graph.add((
                edge_uri, URIRef(f"{kg}hierarchyValid"), Literal(hierarchy_valid),
            ))
            data_graph.add((
                edge_uri, URIRef(f"{kg}sequenceLevelValid"), Literal(sequence_valid),
            ))
            source_class = ontology_classes.get(str(edge.get("source")))
            target_class = ontology_classes.get(str(edge.get("target")))
            domain_range_valid = True
            if source_class and target_class:
                domain_range_valid = (
                    (source_class, target_class)
                    in VALID_SEMANTIC_PAIRS.get(edge_type, set())
                )
            data_graph.add((
                edge_uri, URIRef(f"{kg}domainRangeValid"),
                Literal(domain_range_valid),
            ))
        shapes_graph = Graph()
        shapes_graph.parse(self.shapes_path, format="turtle")
        conforms, report_graph, report_text = validate(
            data_graph, shacl_graph=shapes_graph, inference="none"
        )
        if hasattr(report_graph, "serialize"):
            report_turtle = report_graph.serialize(format="turtle")
        else:
            report_turtle = str(report_graph)
        return bool(conforms), report_text, report_turtle
