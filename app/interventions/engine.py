from __future__ import annotations

def clamp01(v: float) -> float:
    return max(0.0, min(1.0, float(v)))

def suitability(intervention: dict, context, driver) -> dict:
    constraints = intervention["constraints"]
    failures = []
    reasons = []

    checks = {
        "min_road_fraction": context.road_fraction,
        "max_shade_fraction": context.shade_fraction,
        "max_vegetation_fraction": context.vegetation_fraction,
        "min_solar_exposure_index": context.solar_exposure_index,
        "min_building_fraction": context.building_fraction,
        "min_impervious_fraction": context.impervious_fraction,
        "min_vulnerability_index": context.vulnerability_index,
    }

    for key, threshold in constraints.items():
        value = checks.get(key)
        if value is None:
            failures.append(f"missing:{key}")
            continue
        if key.startswith("min_") and value < threshold:
            failures.append(f"{key}:{value:.3f}<{threshold:.3f}")
        elif key.startswith("max_") and value > threshold:
            failures.append(f"{key}:{value:.3f}>{threshold:.3f}")
        else:
            reasons.append(f"{key} satisfied")

    dominant = driver.dominant_driver if driver else None
    driver_bonus = 0.0
    mapping = {
        "tree_canopy": {"low_vegetation", "solar_exposure"},
        "shade_structure": {"solar_exposure", "road_hardscape", "low_vegetation"},
        "cool_roof": {"built_form", "nighttime_heat_retention"},
        "cool_pavement": {"impervious_surface", "road_hardscape"},
        "cooling_center": {"background_thermal_anomaly", "nighttime_heat_retention", "low_vegetation"},
    }
    if dominant in mapping.get(intervention["id"], set()):
        driver_bonus = 0.15
        reasons.append(f"matches dominant driver: {dominant}")

    base = 0.70 if not failures else 0.25
    score = clamp01(base + driver_bonus + 0.15 * context.data_quality)
    confidence = clamp01(0.65 * intervention["base_confidence"] + 0.35 * context.data_quality)

    return {
        "suitability_score": round(score, 6),
        "confidence": round(confidence, 6),
        "feasible": len(failures) == 0,
        "reasons": reasons,
        "constraint_failures": failures,
    }

def estimate_cost(intervention: dict, suitability_score: float) -> float:
    base = float(intervention["cost_model"]["base_cost"])
    # Slightly higher deployment cost when suitability is marginal.
    adjustment = 1.0 + max(0.0, 0.75 - suitability_score) * 0.25
    return round(base * adjustment, 2)
