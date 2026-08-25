import os,time,httpx
from pathlib import Path
BASE="https://api.fortyguard.com/v1"
def _env():
    p=Path(r"D:\HELIOS\.env"); out={}
    if p.exists():
        for raw in p.read_text(encoding="utf-8-sig").splitlines():
            line=raw.strip()
            if line and not line.startswith("#") and "=" in line:
                k,v=line.split("=",1); out[k.strip()]=v.strip().strip('"').strip("'")
    return out
def api_key():
    v=os.getenv("FORTYGUARD_API_KEY") or _env().get("FORTYGUARD_API_KEY")
    if not v: raise RuntimeError("FORTYGUARD_API_KEY missing")
    return v
def submit_heatmap(payload):
    with httpx.Client(timeout=45,follow_redirects=True) as c:
        r=c.post(BASE+"/heatmap",headers={"api-key":api_key(),"Content-Type":"application/json"},json=payload)
        r.raise_for_status(); body=r.json()
    aid=((body.get("data") or {}).get("activity_id"))
    if not aid: raise RuntimeError(f"No activity_id returned: {body}")
    return aid
def wait_result(aid,max_polls=60,interval=5):
    transient=(httpx.ConnectError,httpx.ReadError,httpx.RemoteProtocolError,httpx.ConnectTimeout,httpx.ReadTimeout)
    consecutive_errors=0
    poll=0
    while poll < max_polls:
        time.sleep(interval if poll else 0)
        try:
            with httpx.Client(timeout=45,follow_redirects=True) as c:
                r=c.get(BASE+f"/status/{aid}",headers={"api-key":api_key()})
                r.raise_for_status()
                body=r.json()
                data=body.get("data") or {}
            consecutive_errors=0
            poll += 1
            status=str(data.get("status","")).lower()
            print(f"POLL {poll:02d}: {data.get('status')}",flush=True)
            if status in {"completed","succeeded"}:
                return data.get("result") or {}
            if status in {"failed","error"}:
                raise RuntimeError(f"FortyGuard activity failed: {body}")
        except transient as exc:
            consecutive_errors += 1
            if consecutive_errors > 8:
                raise
            delay=min(30,2**min(consecutive_errors,4))
            print(f"TRANSIENT NETWORK ERROR {consecutive_errors}/8: {type(exc).__name__}; retrying in {delay}s",flush=True)
            time.sleep(delay)
    raise TimeoutError(f"FortyGuard activity {aid} did not complete")
