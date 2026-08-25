from shapely.geometry import box
from types import SimpleNamespace
from unittest.mock import patch
from app.fortyguard_live.service import map_tiles
class G:
    def __init__(self,geom): self.geom=geom
def fake(g): return g.geom
def test_map():
    cells=[SimpleNamespace(id="c1",geometry=G(box(0,0,1,1)))]
    features=[{"geometry":{"type":"Polygon","coordinates":[[[0,0],[1,0],[1,1],[0,1],[0,0]]]},
               "properties":{"tile_id":1,"average_temperature":35.0}}]
    with patch("app.fortyguard_live.service.to_shape",fake):
        rows=map_tiles(features,cells)
    assert rows[0]["cell_id"]=="c1" and rows[0]["temperature_c"]==35.0
