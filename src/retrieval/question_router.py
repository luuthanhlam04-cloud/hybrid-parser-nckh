"""Rule signals plus Jev probabilities for conservative retrieval routing."""

from __future__ import annotations

import os
import re
from typing import Any

from .routing_contracts import FEATURES, QuestionNeeds, RoutingDecision


ROUTE_QUESTIONS = {
    "requires_parent_context": {
        "type": "noul",
        "instructions": "Câu hỏi trong `query` có cần nội dung ở điều hoặc khoản cha để xác định đúng chủ thể hay phạm vi áp dụng không?",
        "criteria": {"true": "Nội dung cấp con có thể thiếu chủ thể hoặc phạm vi.", "false": "Một quy định độc lập đủ để trả lời."},
    },
    "requires_all_children": {
        "type": "noul",
        "instructions": "Câu hỏi trong `query` có yêu cầu liệt kê đầy đủ nhiều điều kiện, quyền, nghĩa vụ hoặc trường hợp không?",
        "criteria": {"true": "Cần tổng hợp danh sách nhiều thành phần.", "false": "Chỉ cần một kết luận hoặc thành phần."},
    },
    "requires_reference_traversal": {
        "type": "noul",
        "instructions": "Câu hỏi trong `query` có khả năng cần theo dẫn chiếu sang quy định khác để trả lời đầy đủ không?",
    },
    "requires_multi_hop": {
        "type": "noul",
        "instructions": "Câu hỏi trong `query` có khả năng cần tổng hợp từ nhiều hơn một bước dẫn chiếu pháp lý không?",
    },
    "requires_exception": {
        "type": "noul",
        "instructions": "Câu hỏi trong `query` có yêu cầu hoặc có nguy cơ cần nêu ngoại lệ, giới hạn hay trường hợp bị cấm không?",
    },
    "requires_subject_resolution": {
        "type": "noul",
        "instructions": "Cần xác định hoặc phân biệt chính xác chủ thể pháp lý để trả lời câu hỏi trong `query` không?",
    },
    "requires_comparison": {
        "type": "noul",
        "instructions": "Câu hỏi trong `query` có yêu cầu so sánh hai hay nhiều trường hợp pháp lý không?",
    },
}


class QuestionRouter:
    def __init__(self, jev_client: Any | None = None) -> None:
        self.jev_client = jev_client
        self.activate_threshold = float(os.getenv("JEV_ROUTE_ACTIVATE_THRESHOLD", "0.60"))
        self.uncertain_threshold = float(os.getenv("JEV_ROUTE_UNCERTAIN_THRESHOLD", "0.40"))
        self.reference_threshold = float(os.getenv("JEV_REFERENCE_ROUTE_THRESHOLD", "0.35"))

    @staticmethod
    def deterministic_signals(question: str) -> list[str]:
        text = question.casefold()
        signals: list[str] = []
        patterns = {
            "LIST_REQUEST": r"các điều kiện|bao gồm những gì|nội dung chính|các trường hợp|những quyền|nghĩa vụ nào|liệt kê",
            "REFERENCE_REQUEST": r"theo điều|quy định tại|ngoài điều kiện|quyền và nghĩa vụ tương ứng|dẫn chiếu",
            "EXCEPTION_REQUEST": r"trừ trường hợp|ngoại lệ|không được|chỉ được|bị cấm|hạn chế",
            "SUBJECT_REQUEST": r"\bai\b|đối tượng nào|tổ chức nào|cá nhân nào|chủ thể|có được phép",
            "COMPARISON_REQUEST": r"so sánh|khác nhau|phân biệt|tương ứng",
            "MULTI_HOP_REQUEST": r"đồng thời|và các điều kiện|quyền và nghĩa vụ chung|theo các điều",
        }
        for name, pattern in patterns.items():
            if re.search(pattern, text):
                signals.append(name)
        return signals

    @staticmethod
    def _rule_features(signals: list[str]) -> set[str]:
        active: set[str] = set()
        if "LIST_REQUEST" in signals:
            active.add("requires_all_children")
        if "REFERENCE_REQUEST" in signals:
            active.add("requires_reference_traversal")
        if "EXCEPTION_REQUEST" in signals:
            active.add("requires_exception")
        if "SUBJECT_REQUEST" in signals:
            active.update({"requires_subject_resolution", "requires_parent_context"})
        if "COMPARISON_REQUEST" in signals:
            active.add("requires_comparison")
        if "MULTI_HOP_REQUEST" in signals:
            active.update({"requires_reference_traversal", "requires_multi_hop"})
        return active

    def _policy(self, profile: QuestionNeeds, signals: list[str], *, fallback: bool) -> tuple[list[str], list[str]]:
        rule_features = self._rule_features(signals)
        activated: list[str] = []
        uncertain: list[str] = []
        probabilities = profile.to_dict()
        for feature in FEATURES:
            probability = probabilities[feature]
            threshold = self.reference_threshold if feature == "requires_reference_traversal" else self.activate_threshold
            if self.uncertain_threshold <= probability < self.activate_threshold:
                uncertain.append(feature)
            if feature in rule_features or probability >= threshold:
                activated.append(feature)
            elif probability >= self.uncertain_threshold:
                activated.append(feature)
        if fallback:
            for feature in ("requires_parent_context", "requires_reference_traversal", "requires_subject_resolution"):
                if feature not in activated:
                    activated.append(feature)
            if "LIST_REQUEST" in signals and "requires_all_children" not in activated:
                activated.append("requires_all_children")
            if "EXCEPTION_REQUEST" in signals and "requires_exception" not in activated:
                activated.append("requires_exception")
        return activated, uncertain

    def route(self, question: str, *, question_id: str | None = None) -> RoutingDecision:
        signals = self.deterministic_signals(question)
        if self.jev_client is None:
            profile = QuestionNeeds()
            activated, uncertain = self._policy(profile, signals, fallback=True)
            return RoutingDecision(profile, activated, uncertain, signals, "CONSERVATIVE_FUSION_FALLBACK", None, True, "NOT_CONFIGURED")
        try:
            result = self.jev_client.decide(
                state={"query": question, "rule_signals": signals},
                questions=ROUTE_QUESTIONS,
                operation="pre_retrieval_route",
                question_id=question_id,
            )
            profile = QuestionNeeds(**result.answers)
            activated, uncertain = self._policy(profile, signals, fallback=False)
            return RoutingDecision(profile, activated, uncertain, signals, "RULES_PLUS_JEV", result.model, False, "OK")
        except Exception as exc:  # Jev must never become a single point of failure.
            profile = QuestionNeeds()
            activated, uncertain = self._policy(profile, signals, fallback=True)
            return RoutingDecision(
                profile,
                activated,
                uncertain,
                signals,
                "CONSERVATIVE_FUSION_FALLBACK",
                getattr(self.jev_client, "model", None),
                True,
                "FAILED_FALLBACK_USED",
                f"{type(exc).__name__}: {exc}",
            )
