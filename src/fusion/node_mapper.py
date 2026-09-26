"""Node mapping and physical hierarchy helpers for Module 8."""

from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, Iterable, Optional


class NodeMapper:
    def __init__(self, physical_nodes: Iterable[Dict[str, Any]]) -> None:
        self.nodes = {node["id"]: node for node in physical_nodes if node.get("id")}
        self._parent = {
            node["id"]: node.get("properties", {}).get("parent_id")
            for node in self.nodes.values()
        }
        self._labels = {
            node["id"]: set(node.get("labels", [])) for node in self.nodes.values()
        }
        self._children: Dict[str, list[str]] = {}
        for child_id, parent_id in self._parent.items():
            if parent_id:
                self._children.setdefault(parent_id, []).append(child_id)
        self._law_titles: Dict[str, set[str]] = {}
        for node in self.nodes.values():
            properties = node.get("properties", {})
            law_code = properties.get("law_code")
            source_doc = properties.get("source_doc")
            if law_code and source_doc:
                title = self._normalize(source_doc.rsplit(".", 1)[0])
                title_tokens = {
                    token for token in re.split(r"[^a-z0-9]+", title)
                    if token and token not in {
                        "luat", "nghi", "dinh", "thong", "tu", "bo", "chuong",
                        "muc", "phan", "doc",
                    } and not token.isdigit()
                }
                if title_tokens:
                    self._law_titles.setdefault(str(law_code), set()).update(title_tokens)

    def exists(self, node_id: str) -> bool:
        return node_id in self.nodes

    def ancestor(self, node_id: str, label: str) -> Optional[str]:
        current = node_id
        visited = set()
        while current and current not in visited:
            visited.add(current)
            if label in self._labels.get(current, set()):
                return current
            current = self._parent.get(current)
        return None

    def resolve_anaphoric_reference(
        self, reference_text: str, source_node_id: str
    ) -> list[str]:
        lowered = reference_text.casefold()
        clause_in_article = re.search(
            r"khoản\s+(\d+)\s+điều\s+này", lowered
        )
        section_in_chapter = re.search(
            r"mục\s+(\d+)\s+chương\s+này", lowered
        )
        if clause_in_article:
            article_id = self.ancestor(source_node_id, "ARTICLE")
            clause_number = clause_in_article.group(1)
            return [
                child_id
                for child_id in self._children.get(article_id or "", [])
                if "CLAUSE" in self._labels.get(child_id, set())
                and str(self.nodes[child_id].get("properties", {}).get("number"))
                == clause_number
            ]
        if "khoản này" in lowered:
            target = self.ancestor(source_node_id, "CLAUSE")
        elif "điều này" in lowered:
            target = self.ancestor(source_node_id, "ARTICLE")
        elif section_in_chapter:
            chapter_id = self.ancestor(source_node_id, "CHAPTER")
            section_number = section_in_chapter.group(1)
            matches = [
                child_id
                for child_id in self._children.get(chapter_id or "", [])
                if "SECTION" in self._labels.get(child_id, set())
                and str(self.nodes[child_id].get("properties", {}).get("number"))
                == section_number
            ]
            return matches
        elif "mục này" in lowered:
            target = self.ancestor(source_node_id, "SECTION")
        elif "chương này" in lowered:
            target = self.ancestor(source_node_id, "CHAPTER")
        else:
            target = None
        return [target] if target else []

    def resolve_reference_hint(
        self, hint: Any, source_node_id: str
    ) -> list[str]:
        if not isinstance(hint, dict):
            return []
        article_hint = str(hint.get("article", "")).strip()
        clause_hint = str(hint.get("clause", "")).strip()
        section_hint = str(hint.get("section", "")).strip()
        source = self.nodes.get(source_node_id)
        law_code = source.get("properties", {}).get("law_code") if source else None
        if article_hint.casefold() == "same":
            article_ids = [
                article_id
                for article_id in [self.ancestor(source_node_id, "ARTICLE")]
                if article_id
            ]
        elif article_hint.isdigit():
            article_ids = self._find_nodes("ARTICLE", article_hint, law_code)
        else:
            article_ids = []
        if clause_hint and clause_hint.isdigit():
            matches = list(dict.fromkeys(
                child_id
                for article_id in article_ids
                for child_id in self._children.get(article_id, [])
                if "CLAUSE" in self._labels.get(child_id, set())
                and str(self.nodes[child_id].get("properties", {}).get("number"))
                == clause_hint
            ))
            return matches if len(matches) == 1 else []
        if article_ids:
            return article_ids
        if section_hint.isdigit():
            chapter_hint = str(hint.get("chapter", "")).strip()
            chapter_ids = (
                [self.ancestor(source_node_id, "CHAPTER")]
                if chapter_hint.casefold() == "same"
                else self._find_nodes("CHAPTER", chapter_hint, law_code)
                if chapter_hint
                else []
            )
            matches = list(dict.fromkeys(
                child_id
                for chapter_id in chapter_ids if chapter_id
                for child_id in self._children.get(chapter_id, [])
                if "SECTION" in self._labels.get(child_id, set())
                and str(self.nodes[child_id].get("properties", {}).get("number"))
                == section_hint
            ))
            return matches if len(matches) == 1 else []
        return []

    def resolve_reference_text(self, text: str, source_node_id: str) -> list[str]:
        """Resolve explicit Vietnamese legal citations within the current document."""
        source = self.nodes.get(source_node_id)
        if source is None:
            return []
        props = source.get("properties", {})
        law_code = props.get("law_code")
        if not self._is_local_statute_reference(text, law_code):
            return []
        clause_pattern = re.compile(
            r"khoản\s+(\d+)\s+điều\s+(\d+)", re.IGNORECASE
        )
        section_pattern = re.compile(
            r"mục\s+(\d+)\s+chương\s+([0-9ivxlcdm]+)", re.IGNORECASE
        )
        article_pattern = re.compile(r"điều\s+(\d+)", re.IGNORECASE)
        chapter_pattern = re.compile(r"chương\s+([0-9ivxlcdm]+)", re.IGNORECASE)
        resolved: list[str] = []
        compound_spans: list[tuple[int, int]] = []
        for match in clause_pattern.finditer(text):
            compound_spans.append(match.span())
            clause_number, article_number = match.groups()
            article_ids = self._find_nodes("ARTICLE", article_number, law_code)
            if len(article_ids) == 1:
                clauses = [
                    child_id
                    for child_id in self._children.get(article_ids[0], [])
                    if "CLAUSE" in self._labels.get(child_id, set())
                    and str(self.nodes[child_id].get("properties", {}).get("number"))
                    == clause_number
                ]
                if len(clauses) == 1:
                    resolved.extend(clauses)
        for match in section_pattern.finditer(text):
            compound_spans.append(match.span())
            section_number, chapter_number = match.groups()
            chapter_ids = self._find_nodes("CHAPTER", chapter_number, law_code)
            if len(chapter_ids) == 1:
                sections = [
                    child_id
                    for child_id in self._children.get(chapter_ids[0], [])
                    if "SECTION" in self._labels.get(child_id, set())
                    and str(self.nodes[child_id].get("properties", {}).get("number"))
                    == section_number
                ]
                if len(sections) == 1:
                    resolved.extend(sections)
        is_inside_compound = lambda span: any(
            start <= span[0] and span[1] <= end for start, end in compound_spans
        )
        for match in article_pattern.finditer(text):
            if not is_inside_compound(match.span()):
                article_ids = self._find_nodes("ARTICLE", match.group(1), law_code)
                if len(article_ids) == 1:
                    resolved.extend(article_ids)
        for match in chapter_pattern.finditer(text):
            if not is_inside_compound(match.span()):
                chapter_ids = self._find_nodes("CHAPTER", match.group(1), law_code)
                if len(chapter_ids) == 1:
                    resolved.extend(chapter_ids)
        return list(dict.fromkeys(resolved))

    def _is_local_statute_reference(self, text: str, law_code: Any) -> bool:
        normalized = self._normalize(text)
        cited_codes = re.findall(r"\b\d+/\d{4}/[a-z0-9]+\b", normalized)
        if cited_codes:
            return bool(law_code) and all(
                code == self._normalize(str(law_code)) for code in cited_codes
            )
        act_terms = ("luat ", "nghi dinh ", "thong tu ", "bo luat ")
        explicit_act = any(term in normalized for term in act_terms)
        if not explicit_act or any(
            local_reference in normalized
            for local_reference in (
                "luat nay", "nghi dinh nay", "thong tu nay", "bo luat nay"
            )
        ):
            return True
        known_title = self._law_titles.get(str(law_code), set())
        if not known_title:
            return False
        cited_title_tokens = {
            token for token in re.split(r"[^a-z0-9]+", normalized)
            if token and token not in {
                "dieu", "khoan", "muc", "chuong", "luat", "nghi", "dinh",
                "thong", "tu", "bo", "luat", "nay", "cua", "ve",
            } and not token.isdigit()
        }
        return bool(known_title & cited_title_tokens)

    @staticmethod
    def _normalize(text: str) -> str:
        decomposed = unicodedata.normalize("NFD", text.casefold())
        normalized = "".join(
            character for character in decomposed
            if unicodedata.category(character) != "Mn"
        )
        return normalized.replace("đ", "d")

    def _find_nodes(self, label: str, number: str, law_code: Any) -> list[str]:
        matches = []
        for node_id, node in self.nodes.items():
            properties = node.get("properties", {})
            if label not in self._labels.get(node_id, set()):
                continue
            if str(properties.get("number", "")).casefold() != number.casefold():
                continue
            if law_code and properties.get("law_code") != law_code:
                continue
            matches.append(node_id)
        return matches