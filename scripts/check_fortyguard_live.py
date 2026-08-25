import json,urllib.request
BASE="http://127.0.0.1:8080/api/v1"
def get(p):
    with urllib.request.urlopen(BASE+p,timeout=10) as r:return json.load(r)
runs=get("/fortyguard/ingest/runs?area_id=phx-downtown")
assert runs and runs[0]["status"]=="complete" and runs[0]["cells_updated"]>=1
print(json.dumps({"latest_ingest":runs[0]},indent=2))
print("PASS: FortyGuard provider observations are stored in HELIOS")
