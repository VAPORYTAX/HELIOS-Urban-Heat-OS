from datetime import datetime, timedelta, timezone
from app.quality.freshness import thermal_freshness

def test_fixture_thermal_is_review_gated():
    now = datetime.now(timezone.utc)
    r = thermal_freshness(now, provider_live=False)
    assert r["status"] == "fixture_or_nonlive"
    assert r["score"] < 1

def test_live_fresh_thermal_scores_high():
    now = datetime.now(timezone.utc)
    r = thermal_freshness(now - timedelta(hours=1), provider_live=True)
    assert r["status"] == "fresh"
    assert r["score"] == 1.0
