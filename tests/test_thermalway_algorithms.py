from collections import defaultdict
from types import SimpleNamespace
from app.thermalway.algorithms import dijkstra,astar,yen_k_routes

def _g():
    a=SimpleNamespace(id='a'); b=SimpleNamespace(id='b'); c=SimpleNamespace(id='c')
    g=defaultdict(list)
    g[1]=[(2,1.0,a,1.0),(3,5.0,c,5.0)]
    g[2]=[(3,1.0,b,1.0)]
    return g,{1:(0.0,0.0),2:(0.001,0.0),3:(0.002,0.0)}

def test_dijkstra():
    g,c=_g(); p,cost=dijkstra(g,1,3)
    assert [x[2].id for x in p]==['a','b'] and cost==2.0

def test_astar():
    g,c=_g(); p,_=astar(g,1,3,c,max_speed_mps=1000)
    assert [x[2].id for x in p]==['a','b']

def test_yen():
    g,c=_g(); assert len(yen_k_routes(g,1,3,c,k=2))>=2
