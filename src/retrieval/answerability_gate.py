"""Jev evidence relevance and context sufficiency gate."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Sequence

from .evidence_fusion import EvidenceCandidate
from .routing_contracts import RoutingDecision


@dataclass(frozen=True)
class GateResult:
    kept_candidates: list[EvidenceCandidate]
    relevance: dict[str, float]
    sufficiency: dict[str, float]
    missing_facets: list[str]
    model: str | None
    status: str
    fallback_used: bool
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_relevance": dict(self.relevance),
            "sufficiency": dict(self.sufficiency),
            "missing_facets": list(self.missing_facets),
            "jev_model": self.model,
            "status": self.status,
            "fallback_used": self.fallback_used,
            "error": self.error,
        }


class AnswerabilityGate:
    def __init__(self, jev_client: Any | None = None) -> None:
        self.jev_client = jev_client
        self.keep_threshold = float(os.getenv("JEV_EVIDENCE_KEEP_THRESHOLD", "0.45"))
        self.sufficiency_threshold = float(os.getenv("JEV_ANSWERABILITY_THRESHOLD", "0.70"))

    @staticmethod
    def _questions(candidates: Sequence[EvidenceCandidate]) -> dict[str, dict[str, Any]]:
        questions: dict[str, dict[str, Any]] = {}
        for index, _ in enumerate(candidates, start=1):
            questions[f"e{index}_directly_supports_answer"] = {
                "type": "noul",
                "instructions": f"Nội dung trong `candidates[{index - 1}].text` có trực tiếp cung cấp quy tắc, điều kiện, ngoại lệ hoặc chủ thể cần thiết để trả lời `query` không?",
                "criteria": {"true": "Hỗ trợ trực tiếp câu trả lời.", "false": "Chỉ cùng chủ đề hoặc không liên quan trực tiếp."},
            }
        questions.update(
            {
                "context_has_subject": {"type": "noul", "instructions": "Tập `candidates` có đủ căn cứ để xác định đúng chủ thể áp dụng cho `query` không?"},
                "context_has_all_conditions": {"type": "noul", "instructions": "Tập `candidates` có đủ các điều kiện, quyền hoặc nghĩa vụ mà `query` yêu cầu liệt kê không?"},
                "context_has_required_exception": {"type": "noul", "instructions": "Nếu `route_requirements.requires_exception` là true, tập `candidates` đã chứa ngoại lệ hoặc giới hạn cần thiết chưa? Nếu false, trả true."},
                "context_has_reference_target": {"type": "noul", "instructions": "Nếu `route_requirements.requires_reference_traversal` là true, tập `candidates` đã chứa cả quy định nguồn và đích chưa? Nếu false, trả true."},
                "context_is_sufficient": {"type": "noul", "instructions": "Chỉ dựa trên tập `candidates`, có đủ căn cứ để trả lời `query` chính xác, đầy đủ và không suy đoán không?"},
            }
        )
        return questions

    @staticmethod
    def _fallback(candidates: Sequence[EvidenceCandidate], error: Exception | None = None) -> GateResult:
        kept = list(candidates)
        sufficiency = {
            "context_has_subject": 0.5,
            "context_has_all_conditions": 0.5,
            "context_has_required_exception": 0.5,
            "context_has_reference_target": 0.5,
            "context_is_sufficient": 0.5,
        }
        return GateResult(
            kept,
            {f"E{index}": 1.0 for index in range(1, len(kept) + 1)},
            sufficiency,
            ["sufficiency_unverified"],
            None,
            "FAILED_FALLBACK_USED" if error else "NOT_CONFIGURED",
            True,
            f"{type(error).__name__}: {error}" if error else None,
        )

    def assess(
        self,
        question: str,
        candidates: Sequence[EvidenceCandidate],
        route: RoutingDecision,
        *,
        question_id: str | None = None,
        operation: str = "evidence_relevance_gate",
    ) -> GateResult:
        if not candidates:
            return GateResult([], {}, {"context_is_sufficient": 0.0}, ["no_evidence"], None, "NO_EVIDENCE", False)
        if self.jev_client is None:
            return self._fallback(candidates)
        state_candidates = [
            {
                "id": f"E{index}",
                "locator": candidate.canonical_locator or "UNRESOLVED",
                "source_type": candidate.source_type,
                "text": candidate.text[:1200],
            }
            for index, candidate in enumerate(candidates, start=1)
        ]
        try:
            result = self.jev_client.decide(
                state={
                    "query": question,
                    "route_requirements": {feature: route.enabled(feature) for feature in route.profile.to_dict()},
                    "candidates": state_candidates,
                },
                questions=self._questions(candidates),
                operation=operation,
                question_id=question_id,
            )
            relevance = {
                f"E{index}": result.answers[f"e{index}_directly_supports_answer"]
                for index in range(1, len(candidates) + 1)
            }
            kept = [candidate for index, candidate in enumerate(candidates, start=1) if relevance[f"E{index}"] >= self.keep_threshold]
            if not kept:
                kept = [candidates[max(range(len(candidates)), key=lambda index: relevance[f"E{index + 1}"])]]
            sufficiency = {key: value for key, value in result.answers.items() if key.startswith("context_")}
            missing = []
            facet_map = {
                "context_has_subject": "subject",
                "context_has_all_conditions": "conditions",
                "context_has_required_exception": "exception",
                "context_has_reference_target": "reference_target",
                "context_is_sufficient": "overall_sufficiency",
            }
            for key, facet in facet_map.items():
                if sufficiency.get(key, 0.0) < self.sufficiency_threshold:
                    missing.append(facet)
            return GateResult(kept, relevance, sufficiency, missing, result.model, "OK", False)
        except Exception as exc:
            return self._fallback(candidates, exc)
