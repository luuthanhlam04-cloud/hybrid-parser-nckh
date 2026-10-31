"""Build a common article-level corpus from the physical graph.

Both systems receive the same legal text.  This is deliberately article-level:
the LightRAG baseline is given the same scope as the Hybrid Parser/UKG, while the
Hybrid system remains free to use its finer clause/point graph internally.
"""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


DEFAULT_GRAPH = Path("outputs/physical_graphs/physical_graph.json")
DEFAULT_CORPUS_DIR = Path("outputs/benchmark_b/corpus")
DEFAULT_CLEAN_TEXT = Path("outputs/clean_texts/clean_Luat_dat_dai_chuong_3.txt")


def build_clean_text_corpus(text_path: str | Path = DEFAULT_CLEAN_TEXT) -> list[dict[str, Any]]:
    """Return the cleaned TXT as one source document for the LightRAG baseline."""
    source = Path(text_path)
    text = source.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError(f"Clean text input is empty: {source}")
    return [{
        "article_id": "clean_Luat_dat_dai_chuong_3.txt",
        "text": text,
        "evidence_ids": [],
        "source_path": str(source),
    }]


def _node_kind(node: dict[str, Any]) -> str:
    labels = node.get("labels", [])
    return next((label for label in labels if label != "LegalNode"), "UNKNOWN")


def _sort_key(node: dict[str, Any]) -> tuple[int, str]:
    properties = node.get("properties", {})
    return (int(properties.get("start_idx") or 0), str(node.get("id", "")))


def build_article_corpus(graph_path: str | Path = DEFAULT_GRAPH) -> list[dict[str, Any]]:
    """Return one deterministic document per ARTICLE and retain physical evidence IDs."""
    with Path(graph_path).open(encoding="utf-8") as stream:
        graph = json.load(stream)
    nodes = graph.get("nodes", [])
    by_id = {node["id"]: node for node in nodes}
    children: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for node in nodes:
        parent_id = node.get("properties", {}).get("parent_id")
        if parent_id:
            children[parent_id].append(node)
    for node_list in children.values():
        node_list.sort(key=_sort_key)

    documents: list[dict[str, Any]] = []
    for article in sorted((node for node in nodes if _node_kind(node) == "ARTICLE"), key=_sort_key):
        article_properties = article["properties"]
        article_number = str(article_properties["number"])
        law_code = article_properties.get("law_code", "31/2024/QH15")
        article_id = f"{law_code.lower()}#{article_number}"
        evidence_ids: list[str] = []
        spans = []
        lines = [
            f"[ARTICLE_ID: {article_id}]",
            f"Điều {article_number}. {article_properties.get('title') or ''}".strip(),
        ]
        # Điều 47 is represented as an ARTICLE with direct text (no clause child).
        # Preserve that source node instead of silently emitting an empty document.
        article_text = (article_properties.get("text") or "").strip()
        if article_text:
            start = len('\n'.join(lines)) + 1
            lines.append(article_text)
            evidence_ids.append(article["id"])
            spans.append(dict(physical_node_id=article['id'],start=start,end=start+len(article_text)))
        stack = list(reversed(children.get(article["id"], [])))
        while stack:
            node = stack.pop()
            props = node.get("properties", {})
            kind = _node_kind(node)
            marker = props.get("marker")
            number = props.get("number")
            text = (props.get("text") or "").strip()
            if text:
                prefix = ""
                if kind == "CLAUSE" and number is not None:
                    prefix = f"{number}. "
                elif kind == "POINT" and marker:
                    prefix = f"{marker}) "
                start = len('\n'.join(lines)) + 1
                lines.append(prefix + text)
                spans.append(dict(physical_node_id=node['id'],start=start,end=start+len(prefix+text)))
                evidence_ids.append(node["id"])
            stack.extend(reversed(children.get(node["id"], [])))
        documents.append(
            {
                "article_id": article_id,
                "article_number": article_number,
                "physical_article_node_id": article["id"],
                "physical_evidence_node_ids": evidence_ids,
                "source_spans": spans,
                "text": "\n".join(lines),
            }
        )
    if len(documents) != 23:
        raise ValueError(f"Expected 23 ARTICLE nodes, found {len(documents)}.")
    return documents


def write_article_corpus(
    graph_path: str | Path = DEFAULT_GRAPH,
    output_dir: str | Path = DEFAULT_CORPUS_DIR,
) -> dict[str, Any]:
    """Persist the shared corpus and a manifest used to prove input equality."""
    documents = build_article_corpus(graph_path)
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    corpus_path = target / "chapter_iii_articles.json"
    encoded = json.dumps(documents, ensure_ascii=False, indent=2)
    corpus_path.write_text(encoded + "\n", encoding="utf-8")
    manifest = {
        "corpus_path": str(corpus_path),
        "article_count": len(documents),
        "article_ids": [document["article_id"] for document in documents],
        "sha256": hashlib.sha256(encoded.encode("utf-8")).hexdigest(),
        "source_physical_graph": str(graph_path),
        "document_strategy": "one_document_per_article",
    }
    (target / "corpus_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest
