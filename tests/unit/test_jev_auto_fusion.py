import json
import inspect

import httpx
import pytest

from benchmark_b.events import EventLog
from src.retrieval.answerability_gate import AnswerabilityGate
from src.retrieval.context_assembler import ContextAssembler
from src.retrieval.evidence_fusion import (
    EvidenceCandidate,
    canonical_locator_from_node_id,
    rank_candidates,
    render_legal_locator,
)
from src.retrieval.jev_client import JevClient, JevError
from src.retrieval.question_router import QuestionRouter
from src.retrieval.routing_contracts import QuestionNeeds, RoutingDecision


def decisions_payload(keys, *, value=.8, cost=.00001):
    return {
        "id":"dec-1","model":"typesafe/jev-1.14-20261014","provider":"TypeSafe",
        "answers":{key:{"type":"noul","noul":value} for key in keys},
        "usage":{"input_tokens":100,"output_tokens":len(keys),"cost":cost},
    }


def test_jev_uses_decisions_endpoint_parses_noul_and_logs_cost(tmp_path):
    captured={}
    def respond(request):
        captured['url']=str(request.url)
        captured['authorization']=request.headers.get('authorization')
        body=json.loads(request.content)
        return httpx.Response(200,json=decisions_payload(body['questions'].keys()))
    log=EventLog(tmp_path/'jev.jsonl','hybrid','run-1')
    client=JevClient('secret-key',event_log=log,transport=httpx.MockTransport(respond),max_retries=1)
    result=client.decide(state={'query':'q'},questions={'route':{'type':'noul','instructions':'route?'}},operation='pre_retrieval_route',question_id='B001')
    client.close()
    assert captured['url']=='https://openrouter.ai/api/alpha/decisions'
    assert captured['authorization']=='Bearer secret-key'
    assert result.answers=={'route':.8}
    summary=log.summary(phase='jev')
    assert summary['prompt_tokens']==100 and summary['completion_tokens']==1
    assert summary['known_provider_cost_usd']==pytest.approx(.00001)
    assert 'secret-key' not in log.path.read_text(encoding='utf-8')


def test_jev_retries_at_most_three_and_raises(tmp_path):
    attempts={'count':0}
    def fail(request):
        attempts['count']+=1
        return httpx.Response(503,json={'error':'unavailable'})
    client=JevClient('secret',transport=httpx.MockTransport(fail),max_retries=3)
    with pytest.raises(JevError,match='after 3 attempts'):
        client.decide(state='x',questions={'x':{'type':'noul','instructions':'x?'}},operation='test')
    client.close()
    assert attempts['count']==3


def test_router_rule_signals_and_jev_failure_conservative_fallback():
    class Broken:
        model='typesafe/jev-1.14'
        def decide(self,**kwargs): raise TimeoutError('timeout')
    route=QuestionRouter(Broken()).route('Ai phải liệt kê các điều kiện và ngoại lệ theo Điều 46?')
    assert route.fallback_used is True
    assert route.status=='FAILED_FALLBACK_USED'
    assert {'requires_parent_context','requires_all_children','requires_reference_traversal','requires_exception'} <= set(route.activated_features)


def test_router_uncertainty_activates_conservative_expansion():
    class Stub:
        model='typesafe/jev-1.14'
        def decide(self,**kwargs):
            from src.retrieval.jev_client import JevDecisionResult
            values={key:.5 for key in kwargs['questions']}
            return JevDecisionResult(self.model,values,{},None,None)
    route=QuestionRouter(Stub()).route('Quy định này áp dụng thế nào?')
    assert set(route.uncertain_features)==set(QuestionNeeds().to_dict())
    assert set(route.activated_features)==set(QuestionNeeds().to_dict())


def test_locator_and_render_preserve_d_and_dd():
    assert canonical_locator_from_node_id('doc_dieu-45_khoan-6_diem-d_p1')=='LD2024:A45:K6:Dd'
    assert canonical_locator_from_node_id('doc_dieu-45_khoan-6_diem-dd_p2')=='LD2024:A45:K6:Dđ'
    assert render_legal_locator('LD2024:A45:K6:Dđ')=='điểm đ khoản 6 Điều 45 Luật Đất đai 2024'


def test_fusion_deduplicates_and_context_never_exceeds_budget():
    rows=[
        EvidenceCandidate('n1','LD2024:A46:K1:Da','Tài sản được tạo lập hợp pháp.','ANCHOR',vector_score=.9),
        EvidenceCandidate('n1','LD2024:A46:K1:Da','Tài sản được tạo lập hợp pháp.','NORM'),
        EvidenceCandidate('n2',None,'Không ánh xạ được.','PHYSICAL_FALLBACK',exact_provenance=False),
    ]
    ranked=rank_candidates('điều kiện tài sản hợp pháp',rows,limit=12)
    assert len(ranked)==2 and ranked[0].canonical_locator=='LD2024:A46:K1:Da'
    context,included,budget=ContextAssembler(max_total_tokens=40).assemble_fusion(ranked)
    assert budget['within_budget'] and budget['estimated_tokens']<=40
    assert all(item.canonical_locator or item.alignment_status=='UNRESOLVED' for item in included)


def test_answerability_gate_failure_keeps_evidence_and_marks_fallback():
    class Broken:
        def decide(self,**kwargs): raise RuntimeError('down')
    candidate=EvidenceCandidate('n1','LD2024:A46:K1','Điều kiện.','ANCHOR')
    route=RoutingDecision(QuestionNeeds(),source='RULES_PLUS_JEV')
    result=AnswerabilityGate(Broken()).assess('Điều kiện?', [candidate], route)
    assert result.kept_candidates==[candidate]
    assert result.fallback_used and result.status=='FAILED_FALLBACK_USED'


def test_m10_retrieval_code_has_no_gold_leakage():
    from src.retrieval.m10_pipeline import M10Pipeline
    source=inspect.getsource(M10Pipeline)
    for forbidden in ('gold_locations','reference_answer','required_atomic_facts','accepted_chain_sets'):
        assert forbidden not in source


def test_benchmark_measures_anchor_expanded_and_context_separately():
    from benchmark_b.evaluation import evaluate_record
    question={
        'question_id':'BXXX','benchmark_b_category':'TEST','answerability':'ANSWERABLE_IN_CHAPTER_III',
        'relevant_articles':['31/2024/qh15#46'],'gold_locations':[{'article':'46'}],
    }
    result={
        'system':'hybrid_ukg','answer':'Điều 46','retrieved_article_ids':['31/2024/qh15#45'],
        'anchor_article_ids':['31/2024/qh15#45'],
        'expanded_article_ids':['31/2024/qh15#45','31/2024/qh15#46'],
        'context_article_ids':['31/2024/qh15#46'],
    }
    metrics=evaluate_record(question,result)
    assert metrics['anchor_recall_at_5']==0
    assert metrics['expanded_evidence_recall']==1
    assert metrics['generation_context_recall']==1
