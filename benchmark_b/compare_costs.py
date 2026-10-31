"""Compare audited extraction events, never QA/judge costs."""
import argparse
import json
from pathlib import Path

def summarize(path):
    rows=[json.loads(line) for line in Path(path).read_text(encoding='utf-8').splitlines()]
    rows=[r for r in rows if r['phase']=='index']
    if len({r['run_id'] for r in rows})!=1: raise ValueError('Select exactly one extraction run per file')
    complete=bool(rows) and all(r['prompt_tokens'] is not None and r['completion_tokens'] is not None and r['provider_cost_usd'] is not None for r in rows)
    return dict(complete=complete,calls=len(rows),prompt_tokens=sum(r['prompt_tokens'] or 0 for r in rows),completion_tokens=sum(r['completion_tokens'] or 0 for r in rows),known_cost_usd=sum(r['provider_cost_usd'] or 0 for r in rows),models=sorted({r['model'] for r in rows if r['model']}))

def compare(hybrid,lightrag):
    a,b=summarize(hybrid),summarize(lightrag)
    compatible=a['complete'] and b['complete'] and a['models']==b['models']
    tokens=lambda r:r['prompt_tokens']+r['completion_tokens']
    return dict(hybrid=a,lightrag=b,usage_complete_and_models_match=compatible,
        token_reduction_percent=100*(1-tokens(a)/tokens(b)) if compatible and tokens(b)>0 else None,
        billed_cost_reduction_percent=100*(1-a['known_cost_usd']/b['known_cost_usd']) if compatible and b['known_cost_usd']>0 else None,
        protocol_note='Verify source corpus, provider policy and fresh caches in run manifests before interpreting reductions.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--hybrid',required=True);p.add_argument('--lightrag',required=True)
    a=p.parse_args();print(json.dumps(compare(a.hybrid,a.lightrag),indent=2))
