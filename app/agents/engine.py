from __future__ import annotations

def clamp01(v: float) -> float:
    return max(0.0, min(1.0, float(v)))

def scout_agent(area_exposure: dict, thermal: dict) -> dict:
    return {
        "agent": "Scout",
        "finding_type": "situation",
        "severity": "high" if thermal.get("hotspot_count", 0) > 0 else "routine",
        "confidence": clamp01(min(area_exposure.get("mean_confidence") or 0, thermal.get("confidence") or 0)),
        "content": {
            "hotspot_count": thermal.get("hotspot_count", 0),
            "peak_temperature_c": thermal.get("peak_temperature_c"),
            "total_teu": area_exposure.get("total_teu", 0),
            "population_exposed": area_exposure.get("population_exposed", 0),
        },
    }

def diagnostician_agent(attribution_rows: list[dict]) -> dict:
    counts = {}
    confidences = []
    for row in attribution_rows:
        counts[row["dominant_driver"]] = counts.get(row["dominant_driver"], 0) + 1
        confidences.append(row["confidence"])
    dominant = max(counts, key=counts.get) if counts else "unknown"
    return {
        "agent": "Diagnostician",
        "finding_type": "drivers",
        "severity": "elevated" if counts else "unknown",
        "confidence": sum(confidences)/len(confidences) if confidences else 0,
        "content": {"dominant_driver": dominant, "driver_counts": counts},
    }

def exposure_agent(area_exposure: dict) -> dict:
    total = float(area_exposure.get("total_teu", 0))
    vulnerable = float(area_exposure.get("total_vulnerable_teu", 0))
    share = 0 if total <= 0 else vulnerable / total
    return {
        "agent": "Exposure",
        "finding_type": "burden",
        "severity": "high" if share >= 0.4 else "elevated",
        "confidence": clamp01(area_exposure.get("mean_confidence") or 0),
        "content": {
            "total_teu": total,
            "vulnerable_teu": vulnerable,
            "vulnerable_burden_ratio": share,
            "population_exposed": area_exposure.get("population_exposed", 0),
            "vulnerable_population_exposed": area_exposure.get("vulnerable_population_exposed", 0),
        },
    }

def planner_agent(optimizer: dict) -> dict:
    return {
        "agent": "Planner",
        "finding_type": "portfolio",
        "severity": "action",
        "confidence": clamp01(optimizer.get("confidence") or 0),
        "content": {
            "objective": optimizer.get("objective"),
            "selected_count": optimizer.get("selected_count", 0),
            "budget": optimizer.get("budget", 0),
            "total_cost": optimizer.get("total_cost", 0),
            "teu_reduction": optimizer.get("teu_reduction", 0),
            "teu_reduction_pct": optimizer.get("teu_reduction_pct", 0),
            "vulnerable_teu_reduction": optimizer.get("vulnerable_teu_reduction", 0),
            "actions": optimizer.get("actions", []),
        },
    }

def skeptic_agent(*, optimizer: dict, source_truth_categories: set[str], mode: str) -> dict:
    issues = []
    severity = "routine"

    if optimizer.get("confidence", 0) < 0.70:
        issues.append("Portfolio confidence is below 0.70.")
        severity = "review"

    if "fixture" in source_truth_categories:
        issues.append("One or more decision inputs are fixture data.")
        severity = "review"

    if mode == "operational" and source_truth_categories != {"provider", "observed", "derived"}:
        issues.append("Operational use requires real observed/provider inputs.")
        severity = "block"

    result = optimizer.get("teu_reduction_pct", 0)
    if result > 60:
        issues.append("Projected TEU reduction is unusually large and requires manual validation.")
        severity = "review" if severity != "block" else severity

    return {
        "agent": "Skeptic",
        "finding_type": "challenge",
        "severity": severity,
        "confidence": 0.95,
        "content": {
            "issues": issues,
            "passed": len(issues) == 0,
            "truth_categories": sorted(source_truth_categories),
        },
    }

def evidence_agent(evidence: list[dict]) -> dict:
    if not evidence:
        return {
            "agent": "Evidence",
            "finding_type": "evidence_quality",
            "severity": "review",
            "confidence": 0,
            "content": {"count": 0, "truth_categories": {}, "message": "No evidence records."},
        }
    categories = {}
    for e in evidence:
        categories[e["truth_category"]] = categories.get(e["truth_category"], 0) + 1
    confidence = sum(e["confidence"] for e in evidence) / len(evidence)
    return {
        "agent": "Evidence",
        "finding_type": "evidence_quality",
        "severity": "review" if "fixture" in categories else "routine",
        "confidence": clamp01(confidence),
        "content": {
            "count": len(evidence),
            "truth_categories": categories,
        },
    }

def executive_agent(findings: list[dict], min_confidence: float) -> dict:
    skeptic = next((x for x in findings if x["agent"] == "Skeptic"), None)
    planner = next((x for x in findings if x["agent"] == "Planner"), None)
    confidences = [x["confidence"] for x in findings if x["agent"] != "Skeptic"]
    confidence = min(confidences) if confidences else 0.0

    requires_review = (
        confidence < min_confidence
        or skeptic is None
        or skeptic["severity"] in {"review", "block"}
    )
    if skeptic and skeptic["severity"] == "block":
        decision_status = "blocked"
    elif requires_review:
        decision_status = "review_required"
    else:
        decision_status = "recommend"

    actions = planner["content"].get("actions", []) if planner else []
    return {
        "agent": "Executive",
        "finding_type": "decision",
        "severity": decision_status,
        "confidence": clamp01(confidence),
        "content": {
            "decision_status": decision_status,
            "requires_human_review": requires_review,
            "recommended_actions": actions,
            "headline": (
                "Portfolio requires human review before operational use."
                if requires_review
                else "Portfolio is recommended under the stated planning constraints."
            ),
        },
    }
