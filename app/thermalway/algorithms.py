from __future__ import annotations
import heapq
from math import radians, sin, cos, sqrt, atan2


def haversine_m(a_lon,a_lat,b_lon,b_lat):
    R=6371000.0
    dlat=radians(b_lat-a_lat); dlon=radians(b_lon-a_lon)
    q=sin(dlat/2)**2 + cos(radians(a_lat))*cos(radians(b_lat))*sin(dlon/2)**2
    return 2*R*atan2(sqrt(q),sqrt(max(1e-16,1-q)))


def _reconstruct(prev,start,goal):
    if goal==start: return []
    if goal not in prev: raise RuntimeError('No route found')
    out=[]; u=goal
    while u!=start:
        pu,e,tec=prev[u]; out.append((pu,u,e,tec)); u=pu
    out.reverse(); return out


def dijkstra(adj,start,goal,blocked_edges=None):
    blocked_edges=blocked_edges or set()
    pq=[(0.0,start)]; dist={start:0.0}; prev={}
    while pq:
        d,u=heapq.heappop(pq)
        if d!=dist.get(u): continue
        if u==goal: break
        for v,c,e,tec in adj.get(u,[]):
            if e.id in blocked_edges: continue
            nd=d+c
            if nd<dist.get(v,float('inf')):
                dist[v]=nd; prev[v]=(u,e,tec); heapq.heappush(pq,(nd,v))
    if goal not in dist: raise RuntimeError('No connected route')
    return _reconstruct(prev,start,goal),dist[goal]


def astar(adj,start,goal,coords,max_speed_mps=1.25,blocked_edges=None):
    blocked_edges=blocked_edges or set()
    def h(n):
        lon,lat=coords[n]; glon,glat=coords[goal]
        return haversine_m(lon,lat,glon,glat)/max(max_speed_mps,1e-9)
    pq=[(h(start),0.0,start)]; g={start:0.0}; prev={}
    while pq:
        _,gu,u=heapq.heappop(pq)
        if gu!=g.get(u): continue
        if u==goal: break
        for v,c,e,tec in adj.get(u,[]):
            if e.id in blocked_edges: continue
            ng=gu+c
            if ng<g.get(v,float('inf')):
                g[v]=ng; prev[v]=(u,e,tec); heapq.heappush(pq,(ng+h(v),ng,v))
    if goal not in g: raise RuntimeError('No connected route')
    return _reconstruct(prev,start,goal),g[goal]


def yen_k_routes(adj,start,goal,coords,k=3):
    first,_=astar(adj,start,goal,coords,max_speed_mps=1.25)
    routes=[first]; seen={tuple(x[2].id for x in first)}
    for _ in range(1,k):
        candidates=[]
        for prior in routes:
            for step in prior:
                try:
                    cand,cost=astar(adj,start,goal,coords,max_speed_mps=1.25,blocked_edges={step[2].id})
                except RuntimeError:
                    continue
                sig=tuple(x[2].id for x in cand)
                if sig in seen: continue
                seen.add(sig); candidates.append((cost,cand))
        if not candidates: break
        candidates.sort(key=lambda x:x[0]); routes.append(candidates[0][1])
    return routes
