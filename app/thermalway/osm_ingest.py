from __future__ import annotations
from datetime import datetime,timezone
import httpx
from shapely.geometry import LineString,Point
from geoalchemy2.shape import from_shape,to_shape
from sqlalchemy import delete,select
from app.db.models_thermal import ThermalCell
from app.db.models_thermalway import ThermalWayOSMNode,ThermalWayOSMEdge

OVERPASS_URL="https://overpass-api.de/api/interpreter"
ALLOWED={
 "footway","pedestrian","path","living_street","residential","service",
 "unclassified","tertiary","tertiary_link","secondary","secondary_link",
 "primary","primary_link","cycleway","steps"
}
BLOCK_ACCESS={"private","no"}
BLOCK_FOOT={"no","private"}

def _haversine(a,b):
    from math import radians,sin,cos,sqrt,atan2
    lat1,lon1=a;lat2,lon2=b
    R=6371000.0
    dlat=radians(lat2-lat1);dlon=radians(lon2-lon1)
    q=sin(dlat/2)**2+cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    return 2*R*atan2(sqrt(q),sqrt(1-q))

def _walkable(tags):
    h=tags.get("highway")
    if h not in ALLOWED:return False
    if tags.get("access") in BLOCK_ACCESS:return False
    if tags.get("foot") in BLOCK_FOOT:return False
    return True

def ingest_osm_network(db,area_id="phx-downtown"):
    cells=db.execute(select(ThermalCell).where(ThermalCell.area_id==area_id)).scalars().all()
    if not cells:raise RuntimeError("No thermal cells")
    bounds=[to_shape(c.geometry).bounds for c in cells]
    west=min(x[0] for x in bounds);south=min(x[1] for x in bounds)
    east=max(x[2] for x in bounds);north=max(x[3] for x in bounds)
    pad=.003
    bbox=f"{south-pad},{west-pad},{north+pad},{east+pad}"
    query=f'[out:json][timeout:60];way["highway"]({bbox});out body geom;'
    with httpx.Client(timeout=90,headers={"User-Agent":"HELIOS-ThermalWay/1.0"}) as client:
        r=client.post(OVERPASS_URL,content=query.encode("utf-8"))
        r.raise_for_status()
        data=r.json()
    ways=[x for x in data.get("elements",[]) if x.get("type")=="way" and _walkable(x.get("tags") or {})]
    if not ways:raise RuntimeError("Overpass returned no walkable OSM ways for HELIOS AOI")

    db.execute(delete(ThermalWayOSMEdge));db.execute(delete(ThermalWayOSMNode))
    node_coords={}
    edges=[]
    stamp=datetime.now(timezone.utc)
    for way in ways:
        ids=way.get("nodes") or [];geom=way.get("geometry") or [];tags=way.get("tags") or {}
        if len(ids)!=len(geom) or len(ids)<2:continue
        for nid,g in zip(ids,geom):
            node_coords[int(nid)]=(float(g["lon"]),float(g["lat"]))
        for i in range(len(ids)-1):
            u=int(ids[i]);v=int(ids[i+1]);a=node_coords[u];b=node_coords[v]
            if a==b:continue
            line=LineString([a,b])
            length=_haversine((a[1],a[0]),(b[1],b[0]))
            edge=ThermalWayOSMEdge(
                id=f"{way['id']}:{i}",osm_way_id=int(way["id"]),u=u,v=v,
                geometry=from_shape(line,srid=4326),length_m=length,
                highway=tags.get("highway"),name=tags.get("name"),foot=tags.get("foot"),
                sidewalk=tags.get("sidewalk"),covered=tags.get("covered"),access=tags.get("access"),
                tags_json=tags,source="OpenStreetMap/Overpass",source_timestamp=stamp)
            db.add(edge);edges.append(edge)
    used={e.u for e in edges}|{e.v for e in edges}
    for nid in used:
        lon,lat=node_coords[nid]
        db.add(ThermalWayOSMNode(osm_node_id=nid,geometry=from_shape(Point(lon,lat),srid=4326)))
    db.commit()
    return {"ways":len(ways),"nodes":len(used),"edges":len(edges),"bbox":bbox,"source_timestamp":stamp.isoformat()}
