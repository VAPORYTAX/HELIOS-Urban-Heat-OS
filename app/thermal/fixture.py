from datetime import datetime,timedelta,timezone
from math import sin,pi
def fixture_grid():
    x0,y0=-112.0785,33.4455; dx,dy=.0065,.005; out=[]; idx=0
    for r in range(2):
      for c in range(2):
        idx+=1; x=x0+c*dx; y=y0+r*dy; ring=[[x,y],[x+dx,y],[x+dx,y+dy],[x,y+dy],[x,y]]
        out.append({'id':f'phx-cell-{idx:02d}','area_id':'phx-downtown','grid_key':f'phx-r{r}c{c}','resolution_m':100,'geometry':{'type':'Polygon','coordinates':[ring]}})
    return out
def fixture_observations(days=14):
    start=datetime(2026,8,1,12,tzinfo=timezone.utc); out=[]; cells=fixture_grid()
    for d in range(days):
      for hour in (12,15,18):
       t=start+timedelta(days=d,hours=hour-12)
       for i,c in enumerate(cells):
        temp=34+{12:4.5,15:7,18:3}[hour]+[0,1.8,3.6,.9][i]+.9*sin((d/max(days,1))*2*pi)+(4.5 if d>=days-2 and i in (1,2) else 0)
        out.append({'cell_id':c['id'],'observed_at':t.isoformat(),'temperature_c':round(temp,2),'apparent_temperature_c':round(temp+1.4,2),'humidity_pct':28+i*2,'heat_index_c':round(temp+.8,2),'source_type':'fixture','source_name':'helios-deterministic-fixture-v1','quality_label':'fixture','metadata':{'fixture':True,'day_index':d,'hour':hour}})
    return out
