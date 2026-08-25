import json,urllib.request
BASE="http://127.0.0.1:8080/api/v1"

def get(path):
    with urllib.request.urlopen(BASE+path,timeout=10) as r:
        return json.load(r)

runs=get("/agents/runs?area_id=phx-downtown")
assert runs,"no agent runs"
detail=get(f"/agents/runs/{runs[0]['id']}")
latest=get("/agents/recommendations/latest?area_id=phx-downtown")

agents={x["agent"] for x in detail["findings"]}
required={"Scout","Diagnostician","Exposure","Planner","Skeptic","Evidence","Executive"}
assert required.issubset(agents),agents
assert detail["evidence"],"no evidence"
assert latest["decision_status"] in {"recommend","review_required","blocked"}
assert latest["requires_human_review"] is True
assert "fixture" in latest["evidence_summary"]["truth_categories"]

print(json.dumps({
    "run_id":detail["id"],
    "agents":sorted(agents),
    "evidence_records":len(detail["evidence"]),
    "decision_status":latest["decision_status"],
    "headline":latest["headline"],
    "confidence":latest["confidence"],
    "requires_human_review":latest["requires_human_review"],
    "skeptic_findings":latest["skeptic_findings"],
    "evidence_summary":latest["evidence_summary"],
    "recommended_action_count":len(latest["recommended_actions"]["actions"]),
},indent=2))
print("PASS: HELIOS agentic decision and governance layer is healthy")
