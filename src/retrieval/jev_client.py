"""Small validated client for OpenRouter's Decisions API (Jev)."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Mapping

import httpx
from dotenv import load_dotenv


DEFAULT_JEV_MODEL = "typesafe/jev-1.14"
DEFAULT_JEV_URL = "https://openrouter.ai/api/alpha/decisions"


class JevError(RuntimeError):
    """Raised when a Decisions request or response is unusable."""


@dataclass(frozen=True)
class JevDecisionResult:
    model: str
    answers: dict[str, float]
    usage: dict[str, Any]
    generation_id: str | None
    provider: str | None


class JevClient:
    def __init__(
        self,
        api_key: str,
        *,
        model: str = DEFAULT_JEV_MODEL,
        api_url: str = DEFAULT_JEV_URL,
        timeout_seconds: float = 15.0,
        max_retries: int = 3,
        event_log: Any | None = None,
        transport: httpx.BaseTransport | None = None,
        enabled: bool = True,
    ) -> None:
        if enabled and not api_key:
            raise ValueError("An OpenRouter API key is required when Jev is enabled.")
        if max_retries < 1 or max_retries > 3:
            raise ValueError("JEV_MAX_RETRIES must be between 1 and 3.")
        self.api_key = api_key
        self.model = model
        self.api_url = api_url
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.event_log = event_log
        self.enabled = enabled
        self._client = httpx.Client(timeout=timeout_seconds, transport=transport)

    @classmethod
    def from_environment(cls, *, event_log: Any | None = None) -> "JevClient":
        load_dotenv()
        enabled = os.getenv("JEV_ENABLED", "true").strip().lower() not in {"0", "false", "no", "off"}
        key = os.getenv("OPENROUTER_API_KEY") or os.getenv("LLM_API_KEY") or ""
        return cls(
            key,
            model=os.getenv("JEV_MODEL", DEFAULT_JEV_MODEL),
            api_url=os.getenv("JEV_API_URL", DEFAULT_JEV_URL),
            timeout_seconds=float(os.getenv("JEV_TIMEOUT_SECONDS", "15")),
            max_retries=int(os.getenv("JEV_MAX_RETRIES", "3")),
            event_log=event_log,
            enabled=enabled,
        )

    @staticmethod
    def _validate_questions(questions: Mapping[str, Mapping[str, Any]]) -> None:
        if not questions:
            raise ValueError("Jev questions must not be empty.")
        for question_id, question in questions.items():
            if question.get("type") != "noul":
                raise ValueError(f"Only noul questions are supported here: {question_id}")
            if not str(question.get("instructions", "")).strip():
                raise ValueError(f"Jev question {question_id} has no instructions.")

    @staticmethod
    def _parse(payload: Mapping[str, Any], expected: set[str]) -> JevDecisionResult:
        raw_answers = payload.get("answers")
        if not isinstance(raw_answers, Mapping):
            raise JevError("Decisions response has no answers object.")
        if set(raw_answers) != expected:
            missing = sorted(expected - set(raw_answers))
            extra = sorted(set(raw_answers) - expected)
            raise JevError(f"Decisions answer keys mismatch; missing={missing}, extra={extra}.")
        answers: dict[str, float] = {}
        for key in expected:
            answer = raw_answers[key]
            if not isinstance(answer, Mapping) or answer.get("type") != "noul":
                raise JevError(f"Answer {key} is not a noul decision.")
            probability = answer.get("noul")
            if isinstance(probability, bool) or not isinstance(probability, (int, float)) or not 0 <= probability <= 1:
                raise JevError(f"Answer {key} has an invalid noul probability.")
            answers[key] = float(probability)
        usage = payload.get("usage")
        if not isinstance(usage, Mapping):
            raise JevError("Decisions response has no usage object.")
        return JevDecisionResult(
            model=str(payload.get("model") or DEFAULT_JEV_MODEL),
            answers=answers,
            usage=dict(usage),
            generation_id=str(payload["id"]) if payload.get("id") else None,
            provider=str(payload["provider"]) if payload.get("provider") else None,
        )

    def _record(
        self,
        payload: Mapping[str, Any] | None,
        *,
        operation: str,
        question_id: str | None,
        attempt_no: int,
        started: float,
        error: Exception | None,
    ) -> None:
        if self.event_log is None:
            return
        body = dict(payload or {})
        self.event_log.record(
            body,
            phase="jev",
            operation=operation,
            attempt_no=attempt_no,
            node_id=question_id,
            started=started,
            error=error,
        )

    def decide(
        self,
        *,
        state: Any,
        questions: Mapping[str, Mapping[str, Any]],
        operation: str,
        question_id: str | None = None,
    ) -> JevDecisionResult:
        if not self.enabled:
            raise JevError("Jev is disabled by configuration.")
        self._validate_questions(questions)
        body = {"model": self.model, "state": state, "questions": dict(questions)}
        last_error: Exception | None = None
        for attempt_no in range(1, self.max_retries + 1):
            started = time.perf_counter()
            payload: dict[str, Any] | None = None
            try:
                response = self._client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=body,
                )
                response.raise_for_status()
                payload = response.json()
                parsed = self._parse(payload, set(questions))
                self._record(payload, operation=operation, question_id=question_id, attempt_no=attempt_no, started=started, error=None)
                return parsed
            except (httpx.HTTPError, ValueError, TypeError, JevError) as exc:
                last_error = exc
                self._record(payload, operation=operation, question_id=question_id, attempt_no=attempt_no, started=started, error=exc)
        raise JevError(f"Jev failed after {self.max_retries} attempts: {last_error}") from last_error

    def close(self) -> None:
        self._client.close()
