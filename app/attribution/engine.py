from __future__ import annotations

def clamp01(v: float) -> float:
    return max(0.0, min(1.0, float(v)))

def normalize_scores(raw: dict[str, float]) -> dict[str, float]:
    total = sum(max(0.0, v) for v in raw.values())
    if total <= 1e-12:
        n = len(raw)
        return {k: round(1.0 / n, 6) for k in raw} if n else {}
    return {k: round(max(0.0, v) / total, 6) for k, v in raw.items()}

def attribute_drivers(
    *,
    vegetation_fraction: float | None,
    impervious_fraction: float | None,
    building_fraction: float | None,
    shade_fraction: float | None,
    road_fraction: float | None,
    solar_exposure_index: float | None,
    nighttime_retention_index: float | None,
    anomaly_c: float | None,
    persistence_hours: float,
    context_quality: float,
    thermal_confidence: float,
):
    vegetation = clamp01(vegetation_fraction or 0.0)
    impervious = clamp01(impervious_fraction or 0.0)
    building = clamp01(building_fraction or 0.0)
    shade = clamp01(shade_fraction or 0.0)
    road = clamp01(road_fraction or 0.0)
    solar = clamp01(solar_exposure_index or 0.0)
    retention = clamp01(nighttime_retention_index or 0.0)
    anomaly = clamp01(max(0.0, anomaly_c or 0.0) / 8.0)
    persistence = clamp01(persistence_hours / 12.0)

    raw = {
        "low_vegetation": (1.0 - vegetation) * 0.90,
        "impervious_surface": impervious * 1.00,
        "solar_exposure": solar * (1.0 - shade) * 0.95,
        "road_hardscape": road * 0.75,
        "built_form": building * 0.55,
        "nighttime_heat_retention": retention * (0.55 + 0.45 * persistence),
        "background_thermal_anomaly": anomaly * 0.65,
    }
    scores = normalize_scores(raw)
    dominant = max(scores, key=scores.get)
    confidence = clamp01(0.55 * context_quality + 0.45 * thermal_confidence)

    evidence = {
        "inputs": {
            "vegetation_fraction": vegetation_fraction,
            "impervious_fraction": impervious_fraction,
            "building_fraction": building_fraction,
            "shade_fraction": shade_fraction,
            "road_fraction": road_fraction,
            "solar_exposure_index": solar_exposure_index,
            "nighttime_retention_index": nighttime_retention_index,
            "anomaly_c": anomaly_c,
            "persistence_hours": persistence_hours,
        },
        "interpretation": "Deterministic diagnostic attribution; not causal proof.",
    }
    return {
        "dominant_driver": dominant,
        "driver_scores": scores,
        "confidence": round(confidence, 6),
        "method_version": "helios-driver-attribution-v1",
        "evidence": evidence,
    }
