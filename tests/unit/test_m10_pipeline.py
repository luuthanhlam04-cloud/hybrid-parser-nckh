import json

from src.retrieval import M10Pipeline


class FakeAnchorSearch:
    def __init__(self, anchors):
        self.anchors = anchors

    def search(self, question, *, top_k=5):
        assert question == "Có bắt buộc công chứng không?"
        assert top_k == 3
        return self.anchors


class FakeGraphQuery:
    def __init__(self, records_a=None, records_b=None):
        self.records_a = records_a or []
        self.records_b = records_b or []

    def retrieve_mode_a(self, anchor_ids, *, limit=20):
        assert anchor_ids == ["anchor-1"]
        return self.records_a

    def retrieve_mode_b(self, anchor_ids, *, max_hops=2, max_paths=100):
        assert anchor_ids == ["anchor-1"]
        return self.records_b


class FakeAnswerGenerator:
    def __init__(self):
        self.calls = []

    def generate(self, question, context):
        self.calls.append((question, context))
        return {"answer": "Dựa trên ngữ cảnh.", "model": "fake-model", "usage": {"tokens": 11}}


class FakeContextAssembler:
    def assemble_mode_a(self, records):
        return "MODE_A_CONTEXT"

    def assemble_mode_b(self, records):
        return "MODE_B_CONTEXT"


def test_public_retrieval_api_exposes_pipeline():
    assert M10Pipeline is not None


def test_m10_pipeline_builds_answer_and_logs_jsonl(tmp_path):
    log_path = tmp_path / "m10_answers.jsonl"
    pipeline = M10Pipeline(
        anchor_search=FakeAnchorSearch([{"node_id": "anchor-1", "score": 0.95}]),
        graph_query=FakeGraphQuery(records_a=[{"norm_id": "norm-1", "modality": "REQUIRE"}]),
        answer_generator=FakeAnswerGenerator(),
        context_assembler=FakeContextAssembler(),
        log_path=log_path,
    )

    result = pipeline.answer(
        "Có bắt buộc công chứng không?",
        mode="A",
        top_k=3,
        max_hops=2,
        result_limit=7,
    )

    assert result["mode"] == "A"
    assert result["answer"] == "Dựa trên ngữ cảnh."
    assert result["context"] == "MODE_A_CONTEXT"
    assert result["anchors"][0]["node_id"] == "anchor-1"
    assert result["retrieved_count"] == 1
    assert log_path.exists()
    payload = json.loads(log_path.read_text(encoding="utf-8").strip())
    assert payload["question"] == "Có bắt buộc công chứng không?"
    assert payload["mode"] == "A"


def test_m10_pipeline_auto_mode_fallbacks_when_empty(tmp_path):
    log_path = tmp_path / "m10_answers_fallback.jsonl"
    pipeline = M10Pipeline(
        anchor_search=FakeAnchorSearch([{"node_id": "anchor-1", "score": 0.95}]),
        graph_query=FakeGraphQuery(records_a=[], records_b=[{"neighbor": "data"}]),
        answer_generator=FakeAnswerGenerator(),
        context_assembler=FakeContextAssembler(),
        log_path=log_path,
    )

    result = pipeline.answer(
        "Có bắt buộc công chứng không?",
        mode="AUTO",
        top_k=3,
        max_hops=2,
        result_limit=7,
    )

    assert result["mode"] == "B (Fallback)"
    assert result["context"] == "MODE_B_CONTEXT"
    assert result["retrieved_count"] == 1
