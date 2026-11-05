"""Turn retrieved UKG records into bounded, citable legal context."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .evidence_fusion import EvidenceCandidate, render_legal_locator


MODALITY_LABELS = {
    "ALLOW": "ĐƯỢC PHÉP",
    "REQUIRE": "BẮT BUỘC",
    "PROHIBIT": "BỊ CẤM",
}


class ContextAssembler:
    def __init__(self, max_chars: int = 16000, max_total_tokens: int = 10000) -> None:
        if isinstance(max_chars, bool) or not isinstance(max_chars, int) or max_chars < 1:
            raise ValueError("max_chars must be a positive integer.")
        if isinstance(max_total_tokens, bool) or not isinstance(max_total_tokens, int) or max_total_tokens < 1:
            raise ValueError("max_total_tokens must be a positive integer.")
        self.max_chars = max_chars
        self.max_total_tokens = max_total_tokens

    @staticmethod
    def _items(values: Any) -> list[str]:
        if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
            return []
        rendered = []
        for value in values:
            if isinstance(value, Mapping):
                text = value.get("text") or value.get("id")
            else:
                text = value
            if text:
                rendered.append(str(text))
        return list(dict.fromkeys(rendered))

    @staticmethod
    def _citation(record: Mapping[str, Any]) -> str:
        parts = []
        law_code = record.get("law_code")
        article_number = record.get("article_number")
        labels = record.get("anchor_labels") or []
        anchor_number = record.get("anchor_number")
        if law_code:
            parts.append(str(law_code))
        if article_number:
            parts.append(f"Điều {article_number}")
        elif "ARTICLE" in labels and anchor_number:
            parts.append(f"Điều {anchor_number}")
        if anchor_number and "CLAUSE" in labels:
            parts.append(f"khoản {anchor_number}")
        if anchor_number and "POINT" in labels:
            parts.append(f"điểm {anchor_number}")
        parts.append(f"node {record.get('anchor_id', 'unknown')}")
        return ", ".join(parts)

    def _bound(self, sections: list[str]) -> str:
        context = "\n\n".join(section for section in sections if section)
        if len(context) <= self.max_chars:
            return context
        marker = "\n[Ngữ cảnh đã được giới hạn.]"
        return context[: max(0, self.max_chars - len(marker))].rstrip() + marker

    def assemble_mode_a(self, records: Sequence[Mapping[str, Any]]) -> str:
        if not records:
            return "Không tìm thấy quy phạm liên quan trong đồ thị pháp lý."

        norms: dict[str, dict[str, Any]] = {}
        for record in records:
            norm_id = str(record.get("norm_id") or record.get("anchor_id") or len(norms))
            if norm_id not in norms:
                norms[norm_id] = {**record, "citations": []}
            citation = self._citation(record)
            if citation not in norms[norm_id]["citations"]:
                norms[norm_id]["citations"].append(citation)

        sections = []
        for index, (norm_id, norm) in enumerate(norms.items(), start=1):
            modality = str(norm.get("modality") or "UNSPECIFIED").upper()
            lines = [
                f"Quy tắc {index} ({norm_id}): {MODALITY_LABELS.get(modality, modality)}",
                f"Chủ thể: {', '.join(self._items(norm.get('subjects'))) or 'không xác định'}",
                f"Hành động: {', '.join(self._items(norm.get('actions'))) or 'không xác định'}",
            ]
            objects = self._items(norm.get("objects"))
            if objects:
                lines.append(f"Đối tượng: {', '.join(objects)}")

            groups = norm.get("condition_groups") or []
            if groups:
                for group in groups:
                    operator = str(group.get("operator") or "AND").upper()
                    values = self._items(group.get("conditions") or group.get("condition_ids"))
                    if values:
                        lines.append(f"Điều kiện ({operator}): {'; '.join(values)}")
            else:
                conditions = self._items(norm.get("conditions"))
                if conditions:
                    lines.append(f"Điều kiện: {'; '.join(conditions)}")

            exceptions = self._items(norm.get("exceptions"))
            if exceptions:
                lines.append(f"Ngoại lệ: {'; '.join(exceptions)}")
            consequences = self._items(norm.get("consequences"))
            if consequences:
                lines.append(f"Hệ quả: {'; '.join(consequences)}")
            evidence = norm.get("evidence") or norm.get("anchor_text")
            if evidence:
                lines.append(f"Nguyên văn: {evidence}")
            lines.append(f"Căn cứ: {'; '.join(norm['citations'])}")
            sections.append("\n".join(lines))
        return self._bound(sections)

    def assemble_mode_b(self, records: Sequence[Mapping[str, Any]]) -> str:
        if not records:
            return "Không tìm thấy đoạn đồ thị liên quan trong đồ thị pháp lý."

        physical_nodes: dict[str, dict[str, Any]] = {}
        for record in records:
            for node in record.get("nodes", []):
                labels = node.get("labels") or []
                properties = node.get("properties") or {}
                if "LegalNode" not in labels:
                    continue
                text = properties.get("text") or properties.get("title")
                if text:
                    physical_nodes[node["id"]] = {
                        "text": str(text),
                        "number": properties.get("number"),
                        "labels": labels,
                        "law_code": properties.get("law_code"),
                    }

        sections = []
        for node_id, node in physical_nodes.items():
            citation_parts = []
            if node.get("law_code"):
                citation_parts.append(str(node["law_code"]))
            if "ARTICLE" in node["labels"] and node.get("number"):
                citation_parts.append(f"Điều {node['number']}")
            elif node.get("number"):
                citation_parts.append(f"mục {node['number']}")
            citation_parts.append(f"node {node_id}")
            sections.append(
                f"Đoạn nguồn: {node['text']}\nCăn cứ: {', '.join(citation_parts)}"
            )
        if not sections:
            return "Đồ thị có node liên quan nhưng không có văn bản nguồn để trích dẫn."
        return self._bound(sections)

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Conservative language-independent estimate used only for a hard budget."""
        if not text:
            return 0
        return max(1, (len(text) + 2) // 3)

    @staticmethod
    def _render_fusion_candidate(candidate: EvidenceCandidate, index: int) -> str:
        locator = candidate.canonical_locator or "UNRESOLVED"
        roles = ", ".join(candidate.roles) if candidate.roles else candidate.source_type
        lines = [
            f"Bằng chứng {index} [{locator}]",
            f"Căn cứ: {render_legal_locator(candidate.canonical_locator)}",
            f"Loại evidence: {roles}",
            f"Nguồn truy hồi: {candidate.source_type}; provenance={candidate.provenance}",
        ]
        if candidate.relation_type:
            lines.append(
                "Dẫn chiếu: "
                f"{candidate.source_locator or 'UNRESOLVED'} "
                f"--{candidate.relation_type}--> "
                f"{candidate.target_locator or 'UNRESOLVED'}"
            )
        lines.append(f"Nguyên văn: {candidate.text}")
        return "\n".join(lines)

    def assemble_fusion(
        self,
        candidates: Sequence[EvidenceCandidate],
    ) -> tuple[str, list[EvidenceCandidate], dict[str, Any]]:
        """Render only candidates that fit the same 10k-token budget as LightRAG."""
        sections: list[str] = []
        included: list[EvidenceCandidate] = []
        consumed = 0
        for candidate in candidates:
            section = self._render_fusion_candidate(candidate, len(included) + 1)
            cost = self.estimate_tokens(section)
            if consumed + cost > self.max_total_tokens:
                continue
            sections.append(section)
            included.append(candidate)
            consumed += cost
        if not sections:
            context = "Không tìm thấy bằng chứng pháp lý đủ provenance để tạo ngữ cảnh."
        else:
            context = "\n\n".join(sections)
        return context, included, {
            "max_total_tokens": self.max_total_tokens,
            "estimated_tokens": consumed,
            "estimator": "ceil_unicode_chars_div_3",
            "candidate_count": len(candidates),
            "included_count": len(included),
            "within_budget": consumed <= self.max_total_tokens,
        }
