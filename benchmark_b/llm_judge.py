"""Rubric-grounded LLM judge for Benchmark B answer quality.

The judge is deliberately separate from retrieval and answer generation.  It
uses only the signed gold rubric and the system answer, emits auditable JSON,
and records its own OpenRouter usage/cost ledger.
"""
from __future__ import annotations

import json
import os
import re
import time
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from .events import EventLog


DEFAULT_JUDGE_MODEL = "openai/gpt-4o-mini"


SYSTEM_PROMPT = """Bạn là bộ chấm Benchmark B về Luật Đất đai.
Chỉ dùng GOLD RUBRIC được cung cấp; không bổ sung kiến thức ngoài rubric.
Đánh giá nội dung câu trả lời, không đánh giá văn phong.

Quy tắc điểm:
- fact_decisions/exception_decisions: 1 = nêu đúng và đủ; 0.5 = đúng nhưng thiếu một phần quan trọng; 0 = thiếu hoặc sai.
- forbidden_claim_checks là phép kiểm tra SỰ HIỆN DIỆN CỦA KHẲNG ĐỊNH SAI, không phải điểm tuân thủ. is_present=true CHỈ KHI system_answer thực sự khẳng định hoặc tất yếu kéo theo TOÀN BỘ nội dung forbidden claim. Nếu câu trả lời không nói nội dung đó, nói mệnh đề hẹp hơn, hoặc chỉ thiếu ngoại lệ thì is_present=false. Khi không chắc chắn, chọn false và chấm sự thiếu sót ở fact/exception coverage.
- Khi is_present=true, evidence phải sao chép một đoạn liên tục 6–30 từ system_answer, không diễn giải. Khi false, evidence phải là null.
- Ví dụ: forbidden claim là "mọi X đều bắt buộc Y" nhưng answer chỉ nói "X được Y hoặc Z theo pháp luật" thì is_present=false.
- unsupported_claim_rate: tỷ lệ 0..1 của các khẳng định pháp lý đáng kể không được gold rubric hỗ trợ.
- legal_correctness: 0..1, tính đúng pháp lý tổng thể so với gold.
- Với INSUFFICIENT_CORPUS, correctly_abstained=true khi câu trả lời nói không đủ căn cứ/dữ liệu trong corpus và không bịa con số hay tiêu chí; refusal_quality là số 0..1: 1 = từ chối rõ, nêu phạm vi thiếu và không bịa; 0.5 = từ chối đúng nhưng giải thích thiếu; 0 = không từ chối hoặc bịa. Với câu trả lời được trong corpus, đặt cả hai là null.
- Với INSUFFICIENT_CORPUS, một câu chỉ nói "không đủ thông tin" mà không bịa vẫn là khẳng định đúng: unsupported_claim_rate=0 và legal_correctness không được bằng 0. Sự thiếu giải thích hoặc thiếu chỉ dẫn tra cứu phải làm giảm fact_decisions/refusal_quality, không được biến thành khẳng định sai.
- Không tự thưởng cho câu trả lời chỉ dẫn số Điều nhưng thiếu điều kiện/ngoại lệ mà rubric yêu cầu.
- Trả về đúng JSON theo schema, không kèm markdown.
"""


def _schema(question: dict[str, Any]) -> dict[str, Any]:
    fact_ids = [item["fact_id"] for item in question.get("atomic_annotations", [])]
    exception_ids = [item["annotation_id"] for item in question.get("required_exceptions_annotations", [])]
    forbidden_ids = [item["annotation_id"] for item in question.get("forbidden_claims_annotations", [])]
    return {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "question_id", "fact_decisions", "exception_decisions",
            "forbidden_claim_checks", "unsupported_claim_rate",
            "legal_correctness", "correctly_abstained", "refusal_quality", "rationale",
        ],
        "properties": {
            "question_id": {"type": "string", "enum": [question["question_id"]]},
            "fact_decisions": {
                "type": "object", "additionalProperties": False,
                "required": fact_ids,
                "properties": {key: {"type": "number", "enum": [0, 0.5, 1]} for key in fact_ids},
            },
            "exception_decisions": {
                "type": "object", "additionalProperties": False,
                "required": exception_ids,
                "properties": {key: {"type": "number", "enum": [0, 0.5, 1]} for key in exception_ids},
            },
            "forbidden_claim_checks": {
                "type": "object", "additionalProperties": False,
                "required": forbidden_ids,
                "properties": {
                    key: {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["is_present", "evidence"],
                        "properties": {
                            "is_present": {"type": "boolean"},
                            "evidence": {"type": ["string", "null"]},
                        },
                    }
                    for key in forbidden_ids
                },
            },
            "unsupported_claim_rate": {"type": "number", "minimum": 0, "maximum": 1},
            "legal_correctness": {"type": "number", "minimum": 0, "maximum": 1},
            "correctly_abstained": {"type": ["boolean", "null"]},
            "refusal_quality": {"type": ["number", "null"], "minimum": 0, "maximum": 1},
            "rationale": {"type": "string"},
        },
    }


def _rubric(question: dict[str, Any], answer: str) -> str:
    payload = {
        "question_id": question["question_id"],
        "question": question["question"],
        "answerability": question["answerability"],
        "reference_answer": question["reference_answer"],
        "atomic_facts": [
            {"fact_id": item["fact_id"], "role": item["role"], "text": item["text"]}
            for item in question.get("atomic_annotations", [])
        ],
        "required_exceptions": [
            {"annotation_id": item["annotation_id"], "text": item["text"]}
            for item in question.get("required_exceptions_annotations", [])
        ],
        "forbidden_claims": [
            {"annotation_id": item["annotation_id"], "text": item["text"]}
            for item in question.get("forbidden_claims_annotations", [])
        ],
        "system_answer": answer,
    }
    return "GOLD RUBRIC VÀ CÂU TRẢ LỜI:\n" + json.dumps(payload, ensure_ascii=False, indent=2)


def _normalise_quote(text: str) -> str:
    """Normalise presentation differences without allowing paraphrase matching."""
    value = unicodedata.normalize("NFKC", text).casefold()
    value = re.sub(r"[^\w]+", " ", value, flags=re.UNICODE)
    return " ".join(value.split())


def _align_answer_evidence(answer: str, *queries: str) -> str | None:
    """Return an actual answer span when the model paraphrases its evidence field."""
    candidates = [
        part.strip(" -\t")
        for part in re.split(r"(?<=[.!?;:])\s+|\n+", answer)
        if len(_normalise_quote(part).split()) >= 6
    ]
    normalised_queries = [_normalise_quote(query) for query in queries if query]
    best: tuple[float, str] | None = None
    for candidate in candidates:
        normalised_candidate = _normalise_quote(candidate)
        candidate_tokens = set(normalised_candidate.split())
        for query in normalised_queries:
            query_tokens = set(query.split())
            overlap = len(candidate_tokens & query_tokens) / max(1, min(len(candidate_tokens), len(query_tokens)))
            sequence = SequenceMatcher(None, normalised_candidate, query).ratio()
            score = max(overlap, sequence)
            if best is None or score > best[0]:
                best = (score, candidate)
    return best[1] if best is not None and best[0] >= 0.45 else None


def _validate(
    question: dict[str, Any], raw: dict[str, Any], *, model: str, answer: str
) -> dict[str, Any]:
    if raw.get("question_id") != question["question_id"]:
        raise ValueError("Judge returned a mismatched question_id")
    expected = {
        "fact_decisions": {item["fact_id"] for item in question.get("atomic_annotations", [])},
        "exception_decisions": {item["annotation_id"] for item in question.get("required_exceptions_annotations", [])},
        "forbidden_claim_checks": {item["annotation_id"] for item in question.get("forbidden_claims_annotations", [])},
    }
    forbidden_text = {
        item["annotation_id"]: str(item.get("text") or "")
        for item in question.get("forbidden_claims_annotations", [])
    }
    for field, keys in expected.items():
        if set(raw.get(field, {})) != keys:
            raise ValueError(f"Judge returned invalid keys for {field}")
    for field in ("fact_decisions", "exception_decisions"):
        if any(value not in (0, 0.5, 1) for value in raw[field].values()):
            raise ValueError(f"Judge returned invalid score in {field}")
    forbidden_decisions: dict[str, int] = {}
    forbidden_evidence: dict[str, str | None] = {}
    forbidden_evidence_status: dict[str, str] = {}
    for key, check in raw["forbidden_claim_checks"].items():
        if not isinstance(check, dict) or not isinstance(check.get("is_present"), bool):
            raise ValueError("Judge returned invalid forbidden-claim check")
        present = check["is_present"]
        evidence = check.get("evidence")
        if present:
            normalised_evidence = _normalise_quote(evidence) if isinstance(evidence, str) else ""
            exact = (
                bool(normalised_evidence)
                and len(normalised_evidence.split()) >= 6
                and normalised_evidence in _normalise_quote(answer)
            )
            if not exact:
                aligned = _align_answer_evidence(
                    answer,
                    evidence if isinstance(evidence, str) else "",
                    forbidden_text.get(key, ""),
                )
                if aligned is None:
                    raise ValueError("Present forbidden claim requires evidence alignable to the answer")
                evidence = aligned
                forbidden_evidence_status[key] = "AUTO_ALIGNED_TO_ANSWER"
            else:
                forbidden_evidence_status[key] = "EXACT_NORMALISED_QUOTE"
            if (
                not normalised_evidence
                and forbidden_evidence_status[key] == "EXACT_NORMALISED_QUOTE"
            ):
                raise ValueError("Present forbidden claim requires an exact quote from the answer")
        elif evidence is not None:
            raise ValueError("Absent forbidden claim requires null evidence")
        else:
            forbidden_evidence_status[key] = "NOT_APPLICABLE"
        forbidden_decisions[key] = int(present)
        forbidden_evidence[key] = evidence.strip() if isinstance(evidence, str) else None
    for field in ("unsupported_claim_rate", "legal_correctness"):
        if not isinstance(raw.get(field), (int, float)) or not 0 <= raw[field] <= 1:
            raise ValueError(f"Judge returned invalid {field}")
    negative = question["answerability"] == "INSUFFICIENT_CORPUS"
    abstained = raw.get("correctly_abstained")
    if negative and not isinstance(abstained, bool):
        raise ValueError("Negative question requires boolean correctly_abstained")
    if not negative and abstained is not None:
        raise ValueError("Positive question requires null correctly_abstained")
    refusal = raw.get("refusal_quality")
    if negative and (not isinstance(refusal, (int, float)) or not 0 <= refusal <= 1):
        raise ValueError("Negative question requires numeric refusal_quality")
    if not negative and refusal is not None:
        raise ValueError("Positive question requires null refusal_quality")
    if negative and abstained and raw["legal_correctness"] >= 0.8 and raw["unsupported_claim_rate"] <= 0.2 and refusal < 0.5:
        raise ValueError("Correct, grounded abstention requires refusal_quality >= 0.5")
    if negative and abstained and not any(forbidden_decisions.values()):
        if raw["legal_correctness"] < 0.5 or raw["unsupported_claim_rate"] > 0.2:
            raise ValueError("Correct abstention without a forbidden claim cannot be wholly incorrect or unsupported")
    raw.pop("forbidden_claim_checks")
    raw["forbidden_claim_decisions"] = forbidden_decisions
    raw["forbidden_claim_evidence"] = forbidden_evidence
    raw["forbidden_claim_evidence_status"] = forbidden_evidence_status
    raw["abstention_accuracy"] = int(raw.pop("correctly_abstained")) if negative else None
    raw.update({
        "review_status": "REVIEWED",
        "reviewer": f"LLM_JUDGE:{model}",
        "reviewer_type": "LLM_JUDGE",
        "judge_model": model,
        "prompt_version": "benchmark-b-judge-v6-negative-consistency",
    })
    return raw


class LLMJudge:
    def __init__(self, output_dir: str | Path, *, model: str = DEFAULT_JUDGE_MODEL, run_id: str | None = None):
        load_dotenv()
        key = (
            os.getenv("OPENROUTER_JUDGE_BENCHMARK_KEY")
            or os.getenv("OPENROUTER_LIGHTRAG_BENCHMARK_KEY")
            or os.getenv("OPENROUTER_API_KEY")
            or os.getenv("LLM_API_KEY")
        )
        if not key:
            raise RuntimeError("LLM judge requires an OpenRouter API key in .env")
        self.model = model
        self.output_dir = Path(output_dir)
        self.events = EventLog(self.output_dir / "judge_api_events.jsonl", "benchmark_b_llm_judge", run_id)
        self.client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=key, max_retries=0)

    def close(self) -> None:
        self.client.close()

    def judge_one(self, question: dict[str, Any], answer: str) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(1, 4):
            started = time.perf_counter()
            response = None
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    temperature=0,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": _rubric(question, answer)},
                    ],
                    response_format={
                        "type": "json_schema",
                        "json_schema": {
                            "name": "benchmark_b_judgement",
                            "strict": True,
                            "schema": _schema(question),
                        },
                    },
                )
                self.events.record(
                    response, phase="judge", operation="answer_quality_judge",
                    attempt_no=attempt, node_id=question["question_id"], started=started,
                )
                content = response.choices[0].message.content
                if not content:
                    raise ValueError("Judge returned empty content")
                return _validate(question, json.loads(content), model=self.model, answer=answer)
            except Exception as exc:
                last_error = exc
                if response is None:
                    self.events.record(
                        phase="judge", operation="answer_quality_judge",
                        attempt_no=attempt, node_id=question["question_id"],
                        started=started, error=exc,
                    )
                if attempt == 3:
                    raise RuntimeError(
                        f"LLM judge failed for {question['question_id']} after 3 attempts"
                    ) from exc
        raise RuntimeError("Unreachable judge retry state") from last_error

    def judge_all(
        self,
        questions: list[dict[str, Any]],
        results: list[dict[str, Any]],
        *,
        force_question_ids: set[str] | None = None,
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        if [q["question_id"] for q in questions] != [r["question_id"] for r in results]:
            raise ValueError("Question/result order mismatch before LLM judging")
        target = self.output_dir / "judge_decisions.jsonl"
        existing: dict[str, dict[str, Any]] = {}
        if target.is_file():
            for line in target.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                decision = json.loads(line)
                question_id = decision.get("question_id")
                if question_id in existing:
                    raise ValueError(f"Duplicate existing judge decision: {question_id}")
                existing[question_id] = decision
        expected_ids = {question["question_id"] for question in questions}
        if set(existing) - expected_ids:
            raise ValueError("Existing judge decisions contain unknown question IDs")
        force_question_ids = force_question_ids or set()
        if force_question_ids - expected_ids:
            raise ValueError("Forced rejudge contains unknown question IDs")
        decisions: list[dict[str, Any]] = []
        reused = 0
        for question, result in zip(questions, results, strict=True):
            if question["question_id"] in existing and question["question_id"] not in force_question_ids:
                decisions.append(existing[question["question_id"]])
                reused += 1
                continue
            decision = self.judge_one(question, str(result.get("answer") or ""))
            existing[question["question_id"]] = decision
            decisions.append(decision)
            ordered = [existing[q["question_id"]] for q in questions if q["question_id"] in existing]
            target.write_text(
                "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in ordered),
                encoding="utf-8",
            )
        summary = self.events.summary(phase="judge", scope="answer_quality_llm_judge")
        summary.update({
            "model": self.model,
            "questions_judged": len(decisions),
            "prompt_version": "benchmark-b-judge-v6-negative-consistency",
            "prompt_versions_present": sorted({decision["prompt_version"] for decision in decisions}),
            "human_review_used": False,
            "questions_reused": reused,
            "questions_called_this_resume": len(decisions) - reused,
        })
        (self.output_dir / "judge_summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        return decisions, summary
