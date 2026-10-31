"""Minimal adapter contract used by the shared Benchmark B runner."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class BenchmarkSystem(ABC):
    name: str

    def __init__(self, output_dir: str | Path) -> None:
        self.output_dir = Path(output_dir)

    @abstractmethod
    def readiness(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def index(self, corpus: list[dict[str, Any]], *, fresh: bool = False) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def answer(self, question: dict[str, Any], *, top_k: int) -> dict[str, Any]:
        raise NotImplementedError
