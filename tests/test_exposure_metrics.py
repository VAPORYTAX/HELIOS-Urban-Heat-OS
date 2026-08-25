from app.exposure.metrics import compute_exposure_index, compute_hazard_index, compute_teu

def test_hazard_bounded():
    h = compute_hazard_index(
        severity_score=80,
        persistence_hours=12,
        apparent_temperature_c=47,
    )
    assert 0 <= h <= 1

def test_exposure_index_bounded():
    x = compute_exposure_index(population_density_km2=18000, facility_weight_sum=12)
    assert x == 1.0

def test_teu_increases_with_population():
    low = compute_teu(
        hazard_index=0.7,
        population=100,
        vulnerable_population=20,
        vulnerability_index=0.5,
        facility_exposure_score=1,
        confidence=0.8,
    )
    high = compute_teu(
        hazard_index=0.7,
        population=500,
        vulnerable_population=20,
        vulnerability_index=0.5,
        facility_exposure_score=1,
        confidence=0.8,
    )
    assert high.teu > low.teu

def test_vulnerability_amplifies_vulnerable_teu():
    x = compute_teu(
        hazard_index=0.8,
        population=100,
        vulnerable_population=40,
        vulnerability_index=0.75,
        facility_exposure_score=1,
        confidence=0.9,
    )
    assert x.vulnerable_teu > x.vulnerable_population_exposed
