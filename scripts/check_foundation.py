import sys
import urllib.request
import json

URL = "http://127.0.0.1:8080/api/v1/health"

try:
    with urllib.request.urlopen(URL, timeout=5) as r:
        data = json.load(r)
except Exception as exc:
    print(f"FAIL: could not reach {URL}: {exc}")
    sys.exit(1)

print(json.dumps(data, indent=2))
if data.get("database") != "ok":
    print("FAIL: database health is not ok")
    sys.exit(2)

print("PASS: HELIOS foundation is healthy")
