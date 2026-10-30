"""Durable per-request API ledger; provider charges and tariff estimates stay distinct."""
import json
import threading
import time
from pathlib import Path
from uuid import uuid4


class EventLog:
    def __init__(self,path,system,run_id=None):
        self.path=Path(path); self.system=system; self.run_id=run_id or str(uuid4()); self.lock=threading.Lock()

    def record(self,response=None,*,phase='index',operation='structured_extraction',attempt_no=1,node_id=None,started=None,error=None):
        raw=response.model_dump() if response is not None and hasattr(response,'model_dump') else response or {}
        usage=raw.get('usage') or {}
        if not isinstance(usage,dict): usage={}
        event=dict(run_id=self.run_id,system=self.system,phase=phase,operation=operation,attempt_no=attempt_no,node_id=node_id,
            generation_id=raw.get('id'),model=raw.get('model'),provider=raw.get('provider'),success=error is None,error_type=type(error).__name__ if error else None,
            prompt_tokens=usage.get('prompt_tokens'),completion_tokens=usage.get('completion_tokens'),total_tokens=usage.get('total_tokens'),
            provider_cost_usd=usage.get('cost'),cached_tokens=(usage.get('prompt_tokens_details') or {}).get('cached_tokens'),
            cache_status='PROVIDER_REPORTED' if 'cached_tokens' in (usage.get('prompt_tokens_details') or {}) else 'UNKNOWN',
            latency_ms=(time.perf_counter()-started)*1000 if started is not None else None)
        with self.lock:
            self.path.parent.mkdir(parents=True,exist_ok=True)
            with self.path.open('a',encoding='utf-8') as stream: stream.write(json.dumps(event,ensure_ascii=False)+'\n')
        return event

    def summary(self, *, phase='index', scope=None):
        rows=[json.loads(x) for x in self.path.read_text(encoding='utf-8').splitlines()] if self.path.exists() else []
        rows=[x for x in rows if x['run_id']==self.run_id and x['phase']==phase]
        return dict(run_id=self.run_id,scope=scope or ('indexing_llm_extraction' if phase=='index' else phase),calls=len(rows),missing_usage_calls=sum(x['prompt_tokens'] is None or x['completion_tokens'] is None for x in rows),
            prompt_tokens=sum(x['prompt_tokens'] or 0 for x in rows),completion_tokens=sum(x['completion_tokens'] or 0 for x in rows),
            known_provider_cost_usd=sum(x['provider_cost_usd'] or 0 for x in rows),missing_cost_calls=sum(x['provider_cost_usd'] is None for x in rows),complete=bool(rows) and all(x['provider_cost_usd'] is not None and x['prompt_tokens'] is not None and x['completion_tokens'] is not None for x in rows))
