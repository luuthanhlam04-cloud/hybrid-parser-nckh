"""HTTP-level instrumentation includes Instructor and SDK internal retries."""
import json
import time
from collections import Counter
import httpx


class MeteredTransport(httpx.BaseTransport):
    def __init__(self, events, inner=None):
        self.events=events; self.inner=inner or httpx.HTTPTransport(); self.node_id=None; self.attempts=Counter()

    def handle_request(self,request):
        started=time.perf_counter(); self.attempts[self.node_id]+=1
        metadata=dict(node_id=self.node_id,attempt_no=self.attempts[self.node_id],started=started)
        try:
            response=self.inner.handle_request(request); response.read()
        except Exception as exc:
            self.events.record(error=exc,**metadata); raise
        try: raw=response.json()
        except (ValueError,UnicodeDecodeError): raw={}
        error=RuntimeError(f'HTTP {response.status_code}') if response.is_error else None
        self.events.record(raw,error=error,**metadata)
        return response

    def close(self): self.inner.close()
