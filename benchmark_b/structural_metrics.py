"""Metrics with explicit applicability/observability and denominator accounting."""
import re


def metric(value=None, status='not_measured', reason=None):
    return dict(value=value, status=status, reason=reason)


def recall(gold, found):
    return len(set(gold)&set(found))/len(set(gold)) if gold else None


def citations(text):
    """Conservative explicit citations: never attach a remote clause to a nearby article."""
    found=set()
    patterns=[r'(?:điểm\s+([a-zđ])\s+)?(?:khoản\s+(\d+)\s+)?Điều\s+(\d+)',
              r'Điều\s+(\d+)\s*[,;]?\s*khoản\s+(\d+)(?:\s*[,;]?\s*điểm\s+([a-zđ]))?']
    for m in re.finditer(patterns[0],text,re.I):
        point,clause,article=m.groups(); found.add(f'LD2024:A{article}'+(f':K{clause}' if clause else '')+(f':D{point.lower()}' if point else ''))
    for m in re.finditer(patterns[1],text,re.I):
        article,clause,point=m.groups(); found.add(f'LD2024:A{article}:K{clause}'+(f':D{point.lower()}' if point else ''))
    return found


def evaluate(q, result):
    positive=q['answerability']=='ANSWERABLE_IN_CHAPTER_III'
    evidence=result.get('evidence')
    exact=[x for x in (evidence or []) if x['alignment_status']=='EXACT']
    observed=evidence is not None and (not evidence or len(exact)==len(evidence))
    found={loc for x in exact[:5] for loc in x['canonical_locators']}
    sets=q.get('acceptable_evidence_sets',[])
    gold=sets[0] if sets else []
    out={}
    def put(name,value=None,eligible=True,measured=True):
        out[name]=metric(value if measured and eligible else None,'scored' if measured and eligible else 'not_applicable' if not eligible else 'not_measured')
    put('exact_locator_recall_at_5',max((recall(s,found) for s in sets),default=None),positive and bool(sets),observed)
    context=result.get('context_evidence')
    context_found={loc for x in (context or []) for loc in x['canonical_locators'] if x['alignment_status']=='EXACT'}
    for role, locs in q.get('hierarchy_requirements',{}).items():
        put('hierarchy_'+role,recall(locs,context_found),positive and bool(locs),context is not None and all(x['alignment_status']=='EXACT' for x in context))
    chain_sets=q.get('accepted_chain_sets',[])
    paths=result.get('reference_paths')
    tuples=lambda path:[(s['source'],s['relation_type'],s['target']) for s in path['steps']]
    labels_reviewed=all(s.get('review_status') in {'REVIEWED','STRUCTURAL'} for group in chain_sets for p in group['required_paths'] for s in p['steps'])
    if chain_sets and paths is not None:
        actual=[tuples(p) for p in paths]; actual_edges={s for p in actual for s in p}
        candidates=[]
        for group in chain_sets:
            expected=[tuples(p) for p in group['required_paths']]; edges={s for p in expected for s in p}
            intersection=len(edges&actual_edges); precision=intersection/len(actual_edges) if actual_edges else 0
            r=intersection/len(edges) if edges else 0
            candidates.append(dict(chain_step_precision=precision,chain_step_recall=r,chain_step_f1=2*precision*r/(precision+r) if precision+r else 0,
                chain_exact_match=float(all(p in actual for p in expected) and all(p in expected for p in actual)),
                reference_target_recall=recall({s[2] for s in edges},{s[2] for s in actual_edges}),
                edge_label_accuracy=intersection/len({s for s in actual_edges if (s[0],s[2]) in {(e[0],e[2]) for e in edges}}) if any((s[0],s[2]) in {(e[0],e[2]) for e in edges} for s in actual_edges) else 0))
        best=max(candidates,key=lambda x:(x['chain_step_f1'],x['chain_exact_match']))
    else: best={}
    for name in ['chain_step_precision','chain_step_recall','chain_step_f1','chain_exact_match','reference_target_recall','edge_label_accuracy']:
        put(name,best.get(name),positive and bool(chain_sets),paths is not None and labels_reviewed)
    cited=citations(result.get('answer',''))
    for level,depth in [('article',0),('clause',1),('point',2)]:
        expected={':'.join(x.split(':')[:depth+2]) for x in gold if len(x.split(':'))>=depth+2}
        predicted={':'.join(x.split(':')[:depth+2]) for x in cited if len(x.split(':'))>=depth+2}
        put('citation_'+level+'_precision',len(predicted&expected)/len(predicted) if predicted else 0,positive and bool(expected))
        put('citation_'+level+'_recall',recall(expected,predicted),positive and bool(expected))
    review=result.get('human_review',{})
    unreviewed=any(f['role']=='UNREVIEWED' for f in q.get('atomic_annotations',[]))
    eligible={'atomic_fact_coverage':positive,'condition_coverage':positive and (unreviewed or any(f['role']=='REQUIRED_CONDITION' for f in q.get('atomic_annotations',[]))),
        'exception_coverage':positive and bool(q.get('required_exceptions',[])),
        'subject_scope_accuracy':positive and (unreviewed or any(f['role']=='SUBJECT_SCOPE' for f in q.get('atomic_annotations',[]))),
        'forbidden_claim_rate':positive and bool(q.get('forbidden_claims',[])),
        'unsupported_claim_rate':True,'legal_correctness':True,
        'abstention_accuracy':not positive,'refusal_quality':not positive}
    for name,applicable in eligible.items():
        value=review.get(name)
        if value is not None and (isinstance(value,bool) or not isinstance(value,(int,float)) or not 0<=value<=1): raise ValueError('Review scores must be numeric in [0,1]')
        put(name,value,applicable,value is not None and review.get('review_status')=='REVIEWED')
    return out


def aggregate(rows):
    names={name for row in rows for name in row}
    report={}
    for name in sorted(names):
        items=[(qid,row[name]) for qid,row in enumerate(rows) if name in row]
        scored=[m['value'] for _,m in items if m['status']=='scored' and m['value'] is not None]
        report[name]=dict(mean=sum(scored)/len(scored) if scored else None,n_eligible=sum(m['status']!='not_applicable' for _,m in items),n_scored=len(scored),n_not_measured=sum(m['status']=='not_measured' for _,m in items),n_not_applicable=sum(m['status']=='not_applicable' for _,m in items))
    return report
