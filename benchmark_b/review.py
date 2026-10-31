"""Create reviewer templates and import independent per-fact decisions."""
import json
from pathlib import Path


def template(questions,path):
    rows=[]
    for q in questions:
        rows.append(dict(question_id=q['question_id'],review_status='PENDING',reviewer=None,
            fact_decisions={f['fact_id']:None for f in q.get('atomic_annotations',[])},
            exception_decisions={f['annotation_id']:None for f in q.get('required_exceptions_annotations',[])},
            forbidden_claim_decisions={f['annotation_id']:None for f in q.get('forbidden_claims_annotations',[])},
            unsupported_claim_rate=None,abstention_accuracy=None,refusal_quality=None,notes=''))
    Path(path).write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def scores(q,review):
    if review.get('review_status')!='REVIEWED': return {}
    if not review.get('reviewer'): raise ValueError('Reviewed decisions require reviewer identity')
    decisions=review.get('fact_decisions',{})
    def average(ids,source):
        values=[source.get(x) for x in ids]
        if not values or any(v is None for v in values): return None
        if any(v not in (0,0.5,1) for v in values): raise ValueError('Fact decisions must be 0, 0.5 or 1')
        return sum(values)/len(values)
    facts=q.get('atomic_annotations',[])
    return dict(review_status='REVIEWED',atomic_fact_coverage=average([f['fact_id'] for f in facts],decisions),
        condition_coverage=average([f['fact_id'] for f in facts if f['role']=='REQUIRED_CONDITION'],decisions),
        subject_scope_accuracy=average([f['fact_id'] for f in facts if f['role']=='SUBJECT_SCOPE'],decisions),
        exception_coverage=average([f['annotation_id'] for f in q.get('required_exceptions_annotations',[])],review.get('exception_decisions',{})),
        forbidden_claim_rate=average([f['annotation_id'] for f in q.get('forbidden_claims_annotations',[])],review.get('forbidden_claim_decisions',{})),
        **{k:review.get(k) for k in ['unsupported_claim_rate','abstention_accuracy','refusal_quality','legal_correctness']})
