import json, urllib.request

BASE="http://127.0.0.1:8080/api/v1"
def get(path):
    with urllib.request.urlopen(BASE+path, timeout=10) as r:
        return json.load(r)

ready=get("/intelligence/readiness")
runs=get("/intelligence/runs?area_id=phx-downtown")
assert runs
detail=get(f"/intelligence/runs/{runs[0]['id']}")
assert detail["validation"]["valid"] is True
assert detail["answer"]["requires_human_review"] is True
assert detail["answer"]["decision_status"] != "recommend"
assert detail["answer"]["headline"]
assert isinstance(detail["answer"]["recommended_actions"], list)

print(json.dumps({
    "gemma_readiness":ready,
    "run_id":detail["id"],
    "model":detail["model"],
    "thinking_enabled":detail["thinking_enabled"],
    "status":detail["status"],
    "fallback_used":detail["fallback_used"],
    "validation_valid":detail["validation"]["valid"],
    "decision_status":detail["answer"]["decision_status"],
    "requires_human_review":detail["answer"]["requires_human_review"],
    "recommended_action_count":len(detail["answer"]["recommended_actions"]),
},indent=2))
print("PASS: HELIOS Gemma intelligence gateway is healthy")
