from __future__ import annotations
import heapq
from collections import defaultdict
from sqlalchemy import desc,select
from geoalchemy2.shape import to_shape
from app.db.models_thermalway import ThermalWayOSMNode,ThermalWayOSMEdge,ThermalWayRouteRun
from app.db.models_provider_ops import ProviderOperationalMetric
from app.db.models_thermal import ThermalCell
from app.thermalway.algorithms import dijkstra, astar
from app.thermalway.profile_rules import edge_allowed_for_profile, profile_edge_penalty

PROFILE_MULT={"standard":1.0,"child":1.15,"older_adult":1.30,"outdoor_worker":1.20,"mobility_limited":1.25}
WALK_MPS=1.25

def _nearest(nodes,lon,lat):
    return min(nodes,key=lambda n:(n[1]-lon)**2+(n[2]-lat)**2)[0]

def _edge_cell(edge_geom,cells):
    mid=edge_geom.interpolate(.5,normalized=True)
    for cid,g in cells:
        if g.contains(mid) or g.touches(mid):return cid
    return None

def _tec(edge,metric,profile):
    duration=edge.length_m/WALK_MPS
    if not metric:
        return duration*0.15
    heat=max(0.0,min(1.0,(metric.current_c-25.0)/20.0))
    vuln=1.0+metric.vulnerability_index*0.75
    prof=PROFILE_MULT.get(profile,1.0)
    uncertainty=1.0+(1.0-metric.confidence)*0.5
    shade=.75 if (edge.covered or "").lower() in {"yes","true","1"} else 1.0
    return heat*duration*vuln*prof*uncertainty*shade

def _cost(edge,metric,profile,mode):
    duration=edge.length_m/WALK_MPS
    tec=_tec(edge,metric,profile)
    if mode=="fastest":
        return duration,tec
    if mode=="thermal_safe":
        return duration+3.0*tec,tec
    raise ValueError(f"Unsupported route mode: {mode}")

def route(db,origin_lon,origin_lat,dest_lon,dest_lat,mode="thermal_safe",profile="standard",area_id="phx-downtown",algorithm="auto"):
    ns=db.execute(select(ThermalWayOSMNode)).scalars().all()
    es=db.execute(select(ThermalWayOSMEdge)).scalars().all()
    if not ns or not es:raise RuntimeError("ThermalWay OSM network not loaded")
    nodes=[(n.osm_node_id,to_shape(n.geometry).x,to_shape(n.geometry).y) for n in ns]
    start=_nearest(nodes,origin_lon,origin_lat);goal=_nearest(nodes,dest_lon,dest_lat)
    coords={n:(x,y) for n,x,y in nodes}
    cell_rows=db.execute(select(ThermalCell).where(ThermalCell.area_id==area_id)).scalars().all()
    cells=[(c.id,to_shape(c.geometry)) for c in cell_rows]
    ops=db.execute(select(ProviderOperationalMetric).where(ProviderOperationalMetric.area_id==area_id).order_by(desc(ProviderOperationalMetric.created_at))).scalars().all()
    metrics={}
    for m in ops:metrics.setdefault(m.cell_id,m)

    adj=defaultdict(list); edge_lookup={}
    for e in es:
        g=to_shape(e.geometry);cid=_edge_cell(g,cells);m=metrics.get(cid)
        if not edge_allowed_for_profile(e,profile):
            continue
        cost,tec=_cost(e,m,profile,mode)
        penalty=profile_edge_penalty(e,profile)
        cost*=penalty; tec*=penalty
        adj[e.u].append((e.v,cost,e,tec));adj[e.v].append((e.u,cost,e,tec))
        edge_lookup[e.id]=(cid,m)

    chosen=algorithm
    if chosen=="auto":
        chosen="astar" if mode=="fastest" else "dijkstra"
    if chosen=="astar":
        path,_=astar(adj,start,goal,coords,max_speed_mps=WALK_MPS)
    elif chosen=="dijkstra":
        path,_=dijkstra(adj,start,goal)
    else:
        raise ValueError(f"Unsupported routing algorithm: {chosen}")
    total_m=sum(step[2].length_m for step in path)
    total_tec=sum(step[3] for step in path)

    line=[];fingerprints=[]
    for pu,v,e,tec in path:
        a=coords[pu];b=coords[v]
        if not line:line.append([a[0],a[1]])
        line.append([b[0],b[1]])
        cid,m=edge_lookup[e.id]
        fingerprints.append({
            "edge_id":e.id,"cell_id":cid,"temperature_c":m.current_c if m else None,
            "vulnerability_index":m.vulnerability_index if m else None,
            "thermal_exposure_cost":tec,"length_m":e.length_m,
            "highway":e.highway,"name":e.name,"covered":e.covered
        })

    duration_min=(total_m/WALK_MPS)/60
    conf=min([m.confidence for m in metrics.values()] or [0.5])
    rr=ThermalWayRouteRun(
        area_id=area_id,mode=mode,traveler_profile=profile,
        origin_json={"requested":[origin_lon,origin_lat],"snapped_node":start,"snapped":[*coords[start]]},
        destination_json={"requested":[dest_lon,dest_lat],"snapped_node":goal,"snapped":[*coords[goal]]},
        route_json={"type":"LineString","coordinates":line,"fingerprint":fingerprints,"algorithm":chosen},
        distance_m=total_m,duration_min=duration_min,thermal_exposure_cost=total_tec,
        confidence=conf,truth_category="real_osm_provider_thermal_modelled_cost")
    db.add(rr);db.commit();db.refresh(rr)
    return rr

def compare(db,origin_lon,origin_lat,dest_lon,dest_lat,profile="standard",area_id="phx-downtown"):
    fast=route(db,origin_lon,origin_lat,dest_lon,dest_lat,"fastest",profile,area_id)
    safe=route(db,origin_lon,origin_lat,dest_lon,dest_lat,"thermal_safe",profile,area_id)
    return fast,safe
