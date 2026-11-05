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

    def retrieve_typed_paths(self, anchor_ids, *, max_hops=1, max_paths=100):
        assert anchor_ids == ["anchor-1"]
        return self.records_b

    def retrieve_physical_evidence(self, anchor_ids):
        return [{"node_id":"doc_dieu-27_khoan-3_diem-a_p1","text":"Phải công chứng.","score":.95}]

    def retrieve_parents(self, anchor_ids, *, limit=30):
        return []

    def retrieve_all_direct_children(self, anchor_ids, *, limit=80):
        return []

    def retrieve_hierarchy_descendants(self, anchor_ids, *, max_depth=2, limit=120):
        return []

    def retrieve_exception_records(self, anchor_ids, *, limit=40):
        return []


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

    def assemble_fusion(self, candidates):
        return "AUTO_FUSION_CONTEXT", list(candidates), {"within_budget":True,"estimated_tokens":5,"max_total_tokens":10000}


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


def test_m10_pipeline_auto_fusion_runs_a_and_typed_b_even_when_a_has_records(tmp_path):
    log_path = tmp_path / "m10_answers_fallback.jsonl"
    pipeline = M10Pipeline(
        anchor_search=FakeAnchorSearch([{"node_id": "anchor-1", "score": 0.95}]),
        graph_query=FakeGraphQuery(
            records_a=[{"anchor_id":"doc_dieu-27_khoan-3_diem-a_p1","evidence":"Phải công chứng.","norm_id":"n1"}],
            records_b=[{
                "source_id":"doc_dieu-27_khoan-3_diem-a_p1","source_locator":"LD2024:A27:K3:Da","source_text":"Phải công chứng theo Điều 46.",
                "relation_type":"DIRECT_REFERENCE","target_id":"doc_dieu-46_p1","target_locator":"LD2024:A46","target_text":"Điều kiện bán tài sản.",
                "hop":1,"direction":"OUTGOING","provenance":"EXPLICIT_TEXT_REFERENCE"
            }],
        ),
        answer_generator=FakeAnswerGenerator(),
        context_assembler=FakeContextAssembler(),
        log_path=log_path,
    )

    result = pipeline.answer(
        "Có bắt buộc công chứng không?",
        mode="AUTO_FUSION",
        top_k=3,
        max_hops=2,
        result_limit=7,
    )

    assert result["mode"] == "AUTO_FUSION"
    assert result["context"] == "AUTO_FUSION_CONTEXT"
    assert any(r.get("norm_id")=="n1" for r in result["retrieval_records"])
    assert result["reference_paths"][0]["steps"][0] == {
        "source":"LD2024:A27:K3:Da","relation_type":"DIRECT_REFERENCE","target":"LD2024:A46",
        "direction":"OUTGOING","hop":1,"provenance":"EXPLICIT_TEXT_REFERENCE","review_status":"STRUCTURAL"
    }
