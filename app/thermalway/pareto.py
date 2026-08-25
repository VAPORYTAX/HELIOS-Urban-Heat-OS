from app.thermalway.alternatives import k_thermal_alternatives
def pareto_routes(db,origin_lon,origin_lat,dest_lon,dest_lat,profile="standard",area_id="phx-downtown",k=5):
    routes=k_thermal_alternatives(db,origin_lon,origin_lat,dest_lon,dest_lat,profile,area_id,k)
    front=[]
    for r in routes:
        dominated=any(
            q is not r and q["duration_min"]<=r["duration_min"] and
            q["thermal_exposure_cost"]<=r["thermal_exposure_cost"] and
            (q["duration_min"]<r["duration_min"] or q["thermal_exposure_cost"]<r["thermal_exposure_cost"])
            for q in routes)
        if not dominated: front.append(r)
    front.sort(key=lambda x:(x["thermal_exposure_cost"],x["duration_min"]))
    for i,r in enumerate(front,1): r["pareto_rank"]=i
    return {"alternatives":routes,"pareto_front":front}
