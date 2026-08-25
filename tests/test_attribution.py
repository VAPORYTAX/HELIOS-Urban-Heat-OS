from app.attribution.engine import attribute_drivers

def test_driver_scores_sum_to_one():
    out = attribute_drivers(
        vegetation_fraction=0.1,
        impervious_fraction=0.8,
        building_fraction=0.4,
        shade_fraction=0.1,
        road_fraction=0.4,
        solar_exposure_index=0.9,
        nighttime_retention_index=0.8,
        anomaly_c=5,
        persistence_hours=10,
        context_quality=0.9,
        thermal_confidence=0.8,
    )
    assert abs(sum(out["driver_scores"].values()) - 1.0) < 1e-5

def test_low_vegetation_can_dominate():
    out = attribute_drivers(
        vegetation_fraction=0.0,
        impervious_fraction=0.2,
        building_fraction=0.1,
        shade_fraction=0.8,
        road_fraction=0.1,
        solar_exposure_index=0.2,
        nighttime_retention_index=0.1,
        anomaly_c=0,
        persistence_hours=0,
        context_quality=1,
        thermal_confidence=1,
    )
    assert out["dominant_driver"] == "low_vegetation"

def test_attribution_marks_noncausal_interpretation():
    out = attribute_drivers(
        vegetation_fraction=0.2,
        impervious_fraction=0.6,
        building_fraction=0.3,
        shade_fraction=0.2,
        road_fraction=0.3,
        solar_exposure_index=0.6,
        nighttime_retention_index=0.4,
        anomaly_c=2,
        persistence_hours=4,
        context_quality=0.8,
        thermal_confidence=0.8,
    )
    assert "not causal proof" in out["evidence"]["interpretation"].lower()
