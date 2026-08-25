import json
from app.intelligence.gateway import chat_native_fast

raw,latency=chat_native_fast(
    model_key="google/gemma-4-12b-qat",
    messages=[
        {"role":"system","content":"Return only compact JSON."},
        {"role":"user","content":'Return exactly {"status":"ready","transport":"native_fast"}'}
    ],
    timeout=60.0,
    max_output_tokens=120,
    temperature=0.0,
)
print("LATENCY_MS",latency)
print(json.dumps(raw,indent=2))
assert raw.get("status")=="ready"
assert raw.get("transport")=="native_fast"
print("PASS: native FAST gateway smoke")
