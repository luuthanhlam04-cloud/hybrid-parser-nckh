"""Typed routing contracts for Jev-assisted AUTO-FUSION retrieval."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


FEATURES = (
    "requires_parent_context",
    "requires_all_children",
    "requires_reference_traversal",
    "requires_multi_hop",
    "requires_exception",
    "requires_subject_resolution",
    "requires_comparison",
)


@dataclass(frozen=True)
class QuestionNeeds:
    requires_parent_context: float = 0.0
    requires_all_children: float = 0.0
    requires_reference_traversal: float = 0.0
    requires_multi_hop: float = 0.0
    requires_exception: float = 0.0
    requires_subject_resolution: float = 0.0
    requires_comparison: float = 0.0

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"{name} must be numeric.")
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(f"{name} must be in [0, 1].")

    def to_dict(self) -> dict[str, float]:
        return {name: float(value) for name, value in asdict(self).items()}


@dataclass(frozen=True)
class RoutingDecision:
    profile: QuestionNeeds
    activated_features: list[str] = field(default_factory=list)
    uncertain_features: list[str] = field(default_factory=list)
    deterministic_signals: list[str] = field(default_factory=list)
    source: str = "RULES_ONLY_FALLBACK"
    model: str | None = None
    fallback_used: bool = False
    status: str = "OK"
    error: str | None = None

    def enabled(self, feature: str) -> bool:
        return feature in self.activated_features

    def to_dict(self) -> dict[str, Any]:
        return {
            "probabilities": self.profile.to_dict(),
            "activated_features": list(self.activated_features),
            "uncertain_features": list(self.uncertain_features),
            "deterministic_signals": list(self.deterministic_signals),
            "source": self.source,
            "jev_model": self.model,
            "fallback_used": self.fallback_used,
            "jev_status": self.status,
            "error": self.error,
        }
