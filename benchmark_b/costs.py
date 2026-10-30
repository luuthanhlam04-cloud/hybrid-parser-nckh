"""Transparent token accounting for Benchmark B.

Only provider-reported usage is treated as an observed cost. Estimates are kept
separate so a local embedding model is never misrepresented as an API expense.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Price:
    input_per_million_usd: float = 0.15
    output_per_million_usd: float = 0.60


@dataclass
class CostLedger:
    model: str
    price: Price = field(default_factory=Price)
    _phases: dict[str, dict[str, float]] = field(default_factory=lambda: defaultdict(lambda: defaultdict(float)))

    def add_usage(self, phase: str, usage: Any) -> None:
        """Add OpenAI-compatible usage; missing usage is explicitly not invented."""
        if usage is None:
            self._phases[phase]["missing_usage_calls"] += 1
            return
        if hasattr(usage, "model_dump"):
            usage = usage.model_dump()
        if not isinstance(usage, dict):
            self._phases[phase]["missing_usage_calls"] += 1
            return
        prompt = usage.get("prompt_tokens", usage.get("input_tokens", 0)) or 0
        completion = usage.get("completion_tokens", usage.get("output_tokens", 0)) or 0
        total = usage.get("total_tokens", prompt + completion) or (prompt + completion)
        self._phases[phase]["prompt_tokens"] += float(prompt)
        self._phases[phase]["completion_tokens"] += float(completion)
        self._phases[phase]["total_tokens"] += float(total)
        self._phases[phase]["observed_calls"] += 1

    def to_dict(self) -> dict[str, Any]:
        phases: dict[str, Any] = {}
        for phase, usage in self._phases.items():
            input_cost = usage.get("prompt_tokens", 0) * self.price.input_per_million_usd / 1_000_000
            output_cost = usage.get("completion_tokens", 0) * self.price.output_per_million_usd / 1_000_000
            phases[phase] = {
                **{
                    key: int(value) if isinstance(value, float) and value.is_integer() else value
                    for key, value in usage.items()
                },
                "input_cost_usd": input_cost,
                "output_cost_usd": output_cost,
                "observed_cost_usd": input_cost + output_cost,
            }
        return {
            "model": self.model,
            "pricing": {
                "input_per_million_usd": self.price.input_per_million_usd,
                "output_per_million_usd": self.price.output_per_million_usd,
            },
            "phases": phases,
            "total_observed_cost_usd": sum(item["observed_cost_usd"] for item in phases.values()),
            "embedding_api_cost_usd": 0.0,
            "embedding_cost_note": "BGE-M3 is run locally; local compute is reported as duration, not API cost.",
        }
