import copy
import json
import httpx
import pytest
from benchmark_b.prepare import make_mapping, verify_mapping, MAP, V2
from benchmark_b.dataset import load_questions
from benchmark_b.alignment import align
from benchmark_b.structural_metrics import evaluate, aggregate, citations
from benchmark_b.events import EventLog
from benchmark_b.transport import MeteredTransport


def question():
    return dict(question_id='X',answerability='ANSWERABLE_IN_CHAPTER_III',acceptable_evidence_sets=[['LD2024:A46:K1:Da']],hierarchy_requirements={},accepted_chain_sets=[],atomic_annotations=[],required_exceptions=[],forbidden_claims=[])


def test_all_gold_mapping_and_d_dd():
    m=json.loads(MAP.read_text(encoding='utf-8')); qs=load_questions(V2)
    verify_mapping(m,qs)
    assert sum(len(q['gold_locations']) for q in qs)==148
    assert len(m['mappings'])==217
    assert m['mappings']['LD2024:A45:K6:Dd']['physical_node_id']!=m['mappings']['LD2024:A45:K6:Dđ']['physical_node_id']
    assert m['mappings']['LD2024:A47']['text']
    bad=copy.deepcopy(m); bad['mappings']['LD2024:A47']['text']='corrupt'
    with pytest.raises(ValueError): verify_mapping(bad,qs)


def test_evidence_requires_source_text_not_id():
    m=make_mapping(); row=m['mappings']['LD2024:A46:K1:Da']
    assert align(row['physical_node_id'],'generic paraphrase',1,m)['alignment_status']=='UNRESOLVED'
    assert 'LD2024:A46:K1:Da' in align('chunk-x',row['text'],1,m)['canonical_locators']


@pytest.mark.parametrize('status,expected',[('EXACT','scored'),('ARTICLE_ONLY','not_measured'),('UNRESOLVED','not_measured')])
def test_observability(status,expected):
    r=evaluate(question(),dict(answer='',evidence=[dict(alignment_status=status,canonical_locators=['LD2024:A46:K1:Da'])]))
    assert r['exact_locator_recall_at_5']['status']==expected
    assert r['chain_exact_match']['status']=='not_applicable'


def test_negative_excludes_content_metrics():
    q=question(); q['answerability']='INSUFFICIENT_CORPUS'
    r=evaluate(q,dict(answer='',evidence=[]))
    assert r['exact_locator_recall_at_5']['status']=='not_applicable'
    assert r['atomic_fact_coverage']['status']=='not_applicable'
    assert r['abstention_accuracy']['status']=='not_measured'


def test_branches_required_alternatives_and_order():
    q=question(); a=dict(source='A',target='B',relation_type='DIRECT_REFERENCE',review_status='REVIEWED'); b=dict(source='B',target='C',relation_type='DIRECT_REFERENCE',review_status='REVIEWED')
    q['accepted_chain_sets']=[dict(required_paths=[dict(steps=[a,b])])]
    result=dict(answer='',evidence=[],reference_paths=[dict(steps=[a,b])])
    assert evaluate(q,result)['chain_exact_match']['value']==1
    result['reference_paths']=[dict(steps=[b,a])]
    assert evaluate(q,result)['chain_exact_match']['value']==0
    q['accepted_chain_sets'].append(dict(required_paths=[dict(steps=[b,a])]))
    assert evaluate(q,result)['chain_exact_match']['value']==1


def test_chain_matching_normalises_duplicate_runtime_steps():
    q=question(); a=dict(source='A',target='B',relation_type='DIRECT_REFERENCE',review_status='REVIEWED'); b=dict(source='B',target='C',relation_type='DIRECT_REFERENCE',review_status='REVIEWED')
    q['accepted_chain_sets']=[dict(required_paths=[dict(steps=[a,b])])]
    result=dict(answer='',evidence=[],reference_paths=[dict(steps=[a,a,b])])
    assert evaluate(q,result)['chain_exact_match']['value']==1


def test_denominators_and_explicit_citations():
    rows=[evaluate(question(),dict(answer='',evidence=[]))]
    report=aggregate(rows)
    assert report['chain_exact_match']['n_not_applicable']==1
    assert 'LD2024:A46:K2:Db' in citations('điểm b khoản 2 Điều 46')
    assert 'LD2024:A46:K2:Db' in citations('Điều 46 khoản 2 điểm b')


def test_transport_logs_every_http_retry_and_missing_usage(tmp_path):
    log=EventLog(tmp_path/'events.jsonl','hybrid')
    def respond(request): return httpx.Response(200,json={'id':'x','model':'test','usage':{'prompt_tokens':10,'completion_tokens':4,'cost':0.01}})
    transport=MeteredTransport(log,httpx.MockTransport(respond)); transport.node_id='n1'
    with httpx.Client(transport=transport) as client:
        client.post('https://example.org'); client.post('https://example.org')
    rows=[json.loads(x) for x in log.path.read_text().splitlines()]
    assert [x['attempt_no'] for x in rows]==[1,2]
    assert log.summary()['known_provider_cost_usd']==pytest.approx(.02)
    log.record({})
    assert log.summary()['complete'] is False
    assert log.summary()['missing_usage_calls']==1


def test_review_requires_identity_and_fact_decisions():
    from benchmark_b.review import scores
    q=question();q['atomic_annotations']=[dict(fact_id='F',role='REQUIRED_CONDITION')]
    with pytest.raises(ValueError): scores(q,dict(review_status='REVIEWED'))
    review=dict(review_status='REVIEWED',reviewer='reviewer-A',fact_decisions={'F':.5})
    assert scores(q,review)['condition_coverage']==.5
    assert evaluate(q,dict(answer='',human_review=scores(q,review)))['condition_coverage']['value']==.5


def test_lightrag_single_query_returns_real_chunks(monkeypatch,tmp_path):
    import sys,types
    from benchmark_b.systems.lightrag_adapter import LightRAGSystem
    from benchmark_b.contracts import EvidenceItem
    row=make_mapping()['mappings']['LD2024:A46:K1:Da']
    captured={}
    class Params:
        def __init__(self,**kwargs): captured.update(kwargs)
    monkeypatch.setitem(sys.modules,'lightrag',types.SimpleNamespace(QueryParam=Params))
    class Rag:
        async def aquery_llm(self,question,param):
            return dict(data=dict(chunks=[dict(chunk_id='c1',content=row['text'],file_path='31/2024/qh15#46')]),llm_response=dict(content='answer from stub'))
    system=LightRAGSystem(tmp_path)
    monkeypatch.setattr(system,'_initialize',lambda:Rag())
    result=system.answer(dict(question_id='X',question='test'),top_k=5)
    EvidenceItem(**result['evidence'][0])
    assert result['evidence'][0]['canonical_locators']==['LD2024:A46:K1:Da']
    assert result['reference_paths'] is None
    assert captured == dict(mode='hybrid',top_k=5,chunk_top_k=5,max_total_tokens=10000,
        max_entity_tokens=2000,max_relation_tokens=2000,enable_rerank=False,stream=False)
    assert result['retrieval_config']['chunk_top_k']==5
    system.close()


def test_gold_audit_candidate_preserves_provenance_and_completeness(monkeypatch,tmp_path):
    import benchmark_b.review_gold as audit
    target=tmp_path/'candidate.json'
    signoff_csv=tmp_path/'signoff.csv'
    monkeypatch.setattr(audit,'OUTPUT',target)
    monkeypatch.setattr(audit,'SIGNOFF_CSV',signoff_csv)
    report=audit.build()
    payload=json.loads(target.read_text(encoding='utf-8'))
    assert report['questions']==50
    assert payload['metadata']['status']=='AI_ASSISTED_VERIFIED_PENDING_HUMAN_SIGNOFF'
    assert payload['metadata']['review_provenance']['human_signoff'] is None
    assert {q['question_id']:q['category'] for q in payload['questions']}['B041']=='single_hop'
    assert all(f['role']!='UNREVIEWED' and f['evidence_any_of']
        for q in payload['questions'] if q['answerability']=='ANSWERABLE_IN_CHAPTER_III'
        for f in q['atomic_annotations'])
    assert all(not q['gold_locations'] and q['supporting_anchor_locators']
        and all(not f['evidence_any_of'] for f in q['atomic_annotations'])
        for q in payload['questions'] if q['question_id'] in {'B048','B049','B050'})
    assert set(audit.QUESTION_REVISIONS) == audit.ROUND1_REVISED_IDS
    import benchmark_b.signoff_gold as finalizer
    monkeypatch.setattr(finalizer,'CANDIDATE',target)
    monkeypatch.setattr(finalizer,'SIGNOFF_CSV',signoff_csv)
    monkeypatch.setattr(finalizer,'FINAL',tmp_path/'final.json')
    with pytest.raises(ValueError,match='incomplete'):
        finalizer.signoff('Test Reviewer','2026-10-31')


def test_lightrag_close_cancels_sdk_workers(tmp_path):
    import asyncio
    from benchmark_b.systems.lightrag_adapter import LightRAGSystem
    system = LightRAGSystem(tmp_path)
    async def start_worker():
        return asyncio.create_task(asyncio.Queue().get())
    worker = system._run(start_worker())
    system.close()
    assert worker.cancelled()
    assert system._loop.is_closed()


def test_hybrid_alignment_paths_are_observed_not_invented():
    from benchmark_b.alignment import hybrid_evidence,hybrid_paths
    from benchmark_b.contracts import EvidenceItem
    m=make_mapping();a=m['mappings']['LD2024:A46:K2:Da'];b=m['mappings']['LD2024:A46:K1']
    raw=dict(context=a['text'],retrieval_records=[dict(anchor_id=a['physical_node_id'],evidence=a['text'],relationships=[dict(type='REFERS_TO',source_id=a['physical_node_id'],target_id=b['physical_node_id'])])])
    evidence,context=hybrid_evidence(raw,m)
    EvidenceItem(**evidence[0])
    assert hybrid_paths(raw['retrieval_records'],m)[0]['steps'][0]['target']=='LD2024:A46:K1'


def test_cost_comparison_never_mixes_query(tmp_path):
    from benchmark_b.compare_costs import compare
    a=EventLog(tmp_path/'a','a');b=EventLog(tmp_path/'b','b')
    a.record(dict(model='m',usage=dict(prompt_tokens=10,completion_tokens=10,cost=.01)))
    a.record(dict(model='m',usage=dict(prompt_tokens=900,completion_tokens=900,cost=100)),phase='query')
    b.record(dict(model='m',usage=dict(prompt_tokens=20,completion_tokens=20,cost=.02)))
    result=compare(a.path,b.path)
    assert result['token_reduction_percent']==50
    assert result['billed_cost_reduction_percent']==50


def test_llm_judge_contract_and_negative_abstention():
    from benchmark_b.llm_judge import _schema, _validate
    positive=question();positive.update(question_id='B001',atomic_annotations=[dict(fact_id='F1')],
        required_exceptions_annotations=[dict(annotation_id='E1')],
        forbidden_claims_annotations=[dict(annotation_id='X1')])
    raw=dict(question_id='B001',fact_decisions={'F1':1},exception_decisions={'E1':.5},
        forbidden_claim_checks={'X1':{'is_present':False,'evidence':None}},unsupported_claim_rate=0,legal_correctness=1,
        correctly_abstained=None,refusal_quality=None,rationale='grounded')
    reviewed=_validate(positive,raw,model='openai/gpt-4o-mini',answer='sample answer')
    assert reviewed['reviewer_type']=='LLM_JUDGE'
    assert reviewed['prompt_version']=='benchmark-b-judge-v6-negative-consistency'
    assert set(_schema(positive)['properties']['fact_decisions']['properties'])=={'F1'}
    negative=copy.deepcopy(positive);negative['question_id']='B048';negative['answerability']='INSUFFICIENT_CORPUS'
    raw.update(question_id='B048',correctly_abstained=True,refusal_quality=1,
        forbidden_claim_checks={'X1':{'is_present':False,'evidence':None}})
    assert _validate(negative,raw,model='openai/gpt-4o-mini',answer='sample answer')['abstention_accuracy']==1


def test_llm_judge_forbidden_claim_requires_exact_answer_quote():
    from benchmark_b.llm_judge import _validate
    item=question();item.update(question_id='B001',atomic_annotations=[],
        required_exceptions_annotations=[],forbidden_claims_annotations=[dict(annotation_id='X1')])
    raw=dict(question_id='B001',fact_decisions={},exception_decisions={},
        forbidden_claim_checks={'X1':{'is_present':True,'evidence':'not in answer'}},
        unsupported_claim_rate=0,legal_correctness=1,correctly_abstained=None,
        refusal_quality=None,rationale='grounded')
    with pytest.raises(ValueError,match='alignable to the answer'):
        _validate(item,raw,model='openai/gpt-4o-mini',answer='sample answer')


def test_llm_judge_quote_matching_normalises_unicode_spacing_and_punctuation():
    from benchmark_b.llm_judge import _validate
    item=question();item.update(question_id='B001',atomic_annotations=[],
        required_exceptions_annotations=[],forbidden_claims_annotations=[dict(annotation_id='X1')])
    raw=dict(question_id='B001',fact_decisions={},exception_decisions={},
        forbidden_claim_checks={'X1':{'is_present':True,'evidence':'Mọi văn bản đều bắt buộc công chứng'}},
        unsupported_claim_rate=.5,legal_correctness=.5,correctly_abstained=None,
        refusal_quality=None,rationale='forbidden claim present')
    answer='Mọi  văn bản đều bắt buộc: công chứng.'
    reviewed=_validate(item,raw,model='openai/gpt-4o-mini',answer=answer)
    assert reviewed['forbidden_claim_decisions']=={'X1':1}


def test_llm_judge_can_align_paraphrased_evidence_to_actual_answer_span():
    from benchmark_b.llm_judge import _validate
    item=question();item.update(question_id='B041',atomic_annotations=[],
        required_exceptions_annotations=[],forbidden_claims_annotations=[dict(
            annotation_id='X1',text='Mặc nhiên có quyền cho thuê lại quyền sử dụng đất')])
    raw=dict(question_id='B041',fact_decisions={},exception_decisions={},
        forbidden_claim_checks={'X1':{'is_present':True,'evidence':'có thể cho thuê lại đất'}},
        unsupported_claim_rate=.5,legal_correctness=.5,correctly_abstained=None,
        refusal_quality=None,rationale='forbidden claim present')
    answer='Tổ chức có thể cho thuê quyền sử dụng đất, bao gồm cả việc cho thuê lại quyền sử dụng đất theo hình thức trả tiền hằng năm.'
    reviewed=_validate(item,raw,model='openai/gpt-4o-mini',answer=answer)
    assert reviewed['forbidden_claim_evidence_status']=={'X1':'AUTO_ALIGNED_TO_ANSWER'}


def test_llm_judge_rejects_internally_inconsistent_correct_abstention():
    from benchmark_b.llm_judge import _validate
    item=question();item.update(question_id='B048',answerability='INSUFFICIENT_CORPUS',
        atomic_annotations=[],required_exceptions_annotations=[],
        forbidden_claims_annotations=[dict(annotation_id='X1',text='Tự bịa con số')])
    raw=dict(question_id='B048',fact_decisions={},exception_decisions={},
        forbidden_claim_checks={'X1':{'is_present':False,'evidence':None}},
        unsupported_claim_rate=1,legal_correctness=0,correctly_abstained=True,
        refusal_quality=1,rationale='Từ chối đúng và không bịa')
    with pytest.raises(ValueError,match='cannot be wholly incorrect'):
        _validate(item,raw,model='openai/gpt-4o-mini',answer='Tôi không đủ thông tin.')


def test_event_summary_can_isolate_judge_phase(tmp_path):
    from benchmark_b.events import EventLog
    log=EventLog(tmp_path/'events.jsonl','judge','run')
    log.record({'usage':{'prompt_tokens':10,'completion_tokens':2,'cost':.001}},phase='judge')
    log.record({'usage':{'prompt_tokens':99,'completion_tokens':99,'cost':9}},phase='query')
    summary=log.summary(phase='judge',scope='answer_quality_llm_judge')
    assert summary['calls']==1 and summary['prompt_tokens']==10
    assert summary['known_provider_cost_usd']==pytest.approx(.001)
