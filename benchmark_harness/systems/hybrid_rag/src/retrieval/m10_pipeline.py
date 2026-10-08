"""M10 orchestration and JSONL handoff records for M11 evaluation."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

from .answer_generator import AnswerGenerator
from .anchor_search import AnchorSearch
from .context_assembler import ContextAssembler
from .graph_query import GraphQuery


class M10Pipeline:
    def __init__(
        self,
        anchor_search: AnchorSearch,
        graph_query: GraphQuery,
        answer_generator: AnswerGenerator,
        context_assembler: ContextAssembler | None = None,
        log_path: str | Path | None = "outputs/evaluation/m10_answers.jsonl",
    ) -> None:
        self.anchor_search = anchor_search
        self.graph_query = graph_query
        self.answer_generator = answer_generator
        self.context_assembler = context_assembler or ContextAssembler()
        self.log_path = Path(log_path) if log_path is not None else None

    def answer(
        self,
        question: str,
        *,
        mode: Literal["A", "B"] = "A",
        top_k: int = 5,
        max_hops: int = 2,
        result_limit: int = 20,
    ) -> dict[str, Any]:
        if not isinstance(question, str) or not question.strip():
            raise ValueError("question must be a non-empty string.")
        mode = mode.upper()
        if mode not in {"A", "B"}:
            raise ValueError("mode must be 'A' or 'B'.")

        anchors = self.anchor_search.search(question, top_k=top_k)
        anchor_ids = [anchor["node_id"] for anchor in anchors]
        if mode == "A":
            records = self.graph_query.retrieve_mode_a(anchor_ids, limit=result_limit)
            context = self.context_assembler.assemble_mode_a(records)
        else:
            records = self.graph_query.retrieve_mode_b(
                anchor_ids,
                max_hops=max_hops,
                max_paths=result_limit,
            )
            context = self.context_assembler.assemble_mode_b(records)

        generation = self.answer_generator.generate(question.strip(), context)
        result = {
            "request_id": str(uuid4()),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "question": question.strip(),
            "mode": mode,
            "anchors": anchors,
            "retrieved_count": len(records),
            "context": context,
            "answer": generation["answer"],
            "model": generation["model"],
            "usage": generation.get("usage"),
        }
        if self.log_path is not None:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with self.log_path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(result, ensure_ascii=False) + "\n")
        return result