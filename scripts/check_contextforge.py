import json,urllib.request
BASE="http://127.0.0.1:8080/api/v1"
def get(path):
    with urllib.request.urlopen(BASE+path,timeout=10) as r:return json.load(r)
packets=get("/context/packets?area_id=phx-downtown"); prompts=get("/context/prompts")
assert packets
detail=get(f"/context/packets/{packets[0]['id']}")
assert detail["status"]=="ready"
assert len(detail["context_hash"])==64
assert detail["estimated_tokens"]<=detail["token_budget"]
assert len(prompts)>=5
assert detail["packet"]["truth_policy"]["fixture_requires_review"] is True
assert detail["packet"]["state"]["quality"]["requires_human_review"] is True
assert detail["packet"]["evidence_refs"]
print(json.dumps({"packet_id":detail["id"],"context_hash":detail["context_hash"],"task_type":detail["task_type"],
                  "mode":detail["mode"],"estimated_tokens":detail["estimated_tokens"],"token_budget":detail["token_budget"],
                  "prompt_count":len(prompts),"evidence_refs":len(detail["packet"]["evidence_refs"]),
                  "quality_gate":detail["packet"]["state"]["quality"]},indent=2))
print("PASS: HELIOS ContextForge is healthy")
