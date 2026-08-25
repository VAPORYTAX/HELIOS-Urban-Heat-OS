from __future__ import annotations

def clamp01(v: float) -> float:
    return max(0.0, min(1.0, float(v)))

def va_teu(hazard_index: float, vulnerable_population: float, vulnerability_index: float) -> float:
    return max(0.0, hazard_index) * max(0.0, vulnerable_population) * (1.0 + clamp01(vulnerability_index))

def validate_metric_relationships(*, teu: float, va_teu_value: float, population: float,
                                  vulnerable_population: float, vulnerability_index: float) -> list[str]:
    issues = []
    if teu < 0:
        issues.append("TEU must not be negative")
    if va_teu_value < 0:
        issues.append("VA-TEU must not be negative")
    if population < 0 or vulnerable_population < 0:
        issues.append("Population values must not be negative")
    if vulnerable_population > population * 2:
        issues.append("Vulnerable population is implausibly above total population")
    if not 0 <= vulnerability_index <= 1:
        issues.append("Vulnerability index must be within [0,1]")
    return issues
