import json
from app.intelligence.router import choose_profile
from app.intelligence.gateway import readiness

print("READINESS", json.dumps(readiness(), indent=2))
print("FAST_PROFILE", json.dumps(choose_profile("portfolio_optimization","investment",False), indent=2))
print("DEEP_PROFILE", json.dumps(choose_profile("scenario_comparison","planning",None), indent=2))
