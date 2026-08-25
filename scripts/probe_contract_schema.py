import json
import httpx
from app.intelligence.contracts import IntelligenceAnswer

schema=IntelligenceAnswer.model_json_schema()
print("=== AUTHORITATIVE recommended_actions SCHEMA ===")
print(json.dumps(schema.get("properties",{}).get("recommended_actions",{}),indent=2))

payload={
    "model":"helios-gemma4",
    "messages":[
        {"role":"system","content":"You are HELIOS. Follow the supplied response schema exactly. Do not invent evidence or numeric facts."},
        {"role":"user","content":"Return a review-required test response with no evidence references and no numeric claims."}
    ],
    "temperature":0.1,
    "response_format":{
        "type":"json_schema",
        "json_schema":{"name":"helios_intelligence_answer","strict":True,"schema":schema}
    }
}

with httpx.Client(timeout=180.0) as c:
    r=c.post("http://127.0.0.1:1235/v1/chat/completions",json=payload)
    print("HTTP",r.status_code)
    print(r.text[:10000])
    assert r.status_code==200,r.text
    obj=json.loads(r.json()["choices"][0]["message"]["content"])
    parsed=IntelligenceAnswer.model_validate(obj)
    assert parsed.requires_human_review is True
    print("PASS: Gemma output validates directly against IntelligenceAnswer")
