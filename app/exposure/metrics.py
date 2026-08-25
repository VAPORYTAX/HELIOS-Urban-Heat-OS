from __future__ import annotations
from dataclasses import dataclass

def clamp01(v: float) -> float:
    return max(0.0, min(1.0, float(v)))

@dataclass(frozen=True)
class ExposureResult:
    hazard_index: float
    exposure_index: float
    vulnerability_index: float
    teu: float
    vulnerable_teu: float
    population_exposed: float
    vulnerable_population_exposed: float
    facility_exposure_score: float
    confidence: float
    components: dict

def compute_hazard_index(
    *,
    severity_score: float,
    persistence_hours: float,
    apparent_temperature_c: float | None,
) -> float:
    severity = clamp01(severity_score / 100.0)
    persistence = clamp01(persistence_hours / 12.0)
    apparent = 0.0 if apparent_temperature_c is None else clamp01((apparent_temperature_c - 30.0) / 20.0)
    return clamp01(0.65 * severity + 0.20 * persistence + 0.15 * apparent)

def compute_exposure_index(*, population_density_km2: float, facility_weight_sum: float) -> float:
    pop = clamp01(population_density_km2 / 15000.0)
    facilities = clamp01(facility_weight_sum / 8.0)
    return clamp01(0.80 * pop + 0.20 * facilities)

def compute_teu(
    *,
    hazard_index: float,
    population: float,
    vulnerable_population: float,
    vulnerability_index: float,
    facility_exposure_score: float,
    confidence: float,
) -> ExposureResult:
    pop = max(0.0, float(population))
    vulnerable = max(0.0, min(pop, float(vulnerable_population)))
    vuln = clamp01(vulnerability_index)
    hazard = clamp01(hazard_index)
    facility = max(0.0, float(facility_exposure_score))

    # TEU is an operational burden metric: hazard × people, confidence-tracked.
    # Vulnerable TEU adds vulnerability amplification only for vulnerable persons.
    teu = hazard * pop
    vulnerable_teu = hazard * vulnerable * (1.0 + vuln)
    population_exposed = hazard * pop
    vulnerable_population_exposed = hazard * vulnerable

    return ExposureResult(
        hazard_index=round(hazard, 6),
        exposure_index=0.0,  # populated by service once density/facilities are available
        vulnerability_index=round(vuln, 6),
        teu=round(teu, 6),
        vulnerable_teu=round(vulnerable_teu, 6),
        population_exposed=round(population_exposed, 6),
        vulnerable_population_exposed=round(vulnerable_population_exposed, 6),
        facility_exposure_score=round(facility, 6),
        confidence=round(clamp01(confidence), 6),
        components={
            "formula": "hazard_index * population",
            "vulnerable_formula": "hazard_index * vulnerable_population * (1 + vulnerability_index)",
        },
    )
