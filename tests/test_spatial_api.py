from app.api.spatial import router

def test_spatial_router_contract():
    paths = {getattr(r, "path", "") for r in router.routes}
    assert "/spatial/cells" in paths
