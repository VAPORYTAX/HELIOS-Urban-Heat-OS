import json,urllib.request
def get(u):
 with urllib.request.urlopen(u,timeout=10) as r:return json.load(r)
c=get('http://127.0.0.1:8080/api/v1/thermal/current?area_id=phx-downtown'); h=get('http://127.0.0.1:8080/api/v1/thermal/hotspots?area_id=phx-downtown')
assert c['type']=='FeatureCollection' and len(c['features'])==4; assert h
t=[f['properties']['temperature_c'] for f in c['features']]; s=[f['properties']['severity_score'] for f in c['features']]
print(json.dumps({'thermal_cells':len(c['features']),'temperature_range_c':[min(t),max(t)],'severity_range':[min(s),max(s)],'hotspots':len(h),'latest_hotspot':h[0]},indent=2)); print('PASS: HELIOS thermal intelligence core is healthy')
