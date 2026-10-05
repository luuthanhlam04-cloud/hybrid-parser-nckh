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
    def __init__(self, records):
        self.records = records

    def retrieve_mode_a(self, anchor_ids, *, limit=20):
        assert anchor_ids == ["anchor-1"]
        assert limit == 7
        return self.records

    def retrieve_mode_b(self, anchor_ids, *, max_hops=2, max_paths=100):
        assert anchor_ids == ["anchor-1"]
        assert max_hops == 2
        assert max_paths == 9
        return self.records


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
        graph_query=FakeGraphQuery([{"norm_id": "norm-1", "modality": "REQUIRE"}]),
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
