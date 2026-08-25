import json
from app.db.session import SessionLocal
from app.thermalway.accessibility import build_accessibility,build_critical_journeys
from app.thermalway.pareto import pareto_routes
db=SessionLocal()
try:
    a=build_accessibility(db); j=build_critical_journeys(db)
    p=pareto_routes(db,-112.0775,33.4465,-112.0665,33.4545,"older_adult",k=5)
    print(json.dumps({"accessibility":[{"cell":x.cell_id,"score":x.accessibility_score,"minutes":x.best_duration_min,"tec":x.best_tec} for x in a],"critical_journeys":len(j),"pareto_count":len(p["pareto_front"]),"pareto":p["pareto_front"]},indent=2,default=str))
    print("PASS: Thermal Accessibility + Critical Journeys + Pareto built")
finally: db.close()
