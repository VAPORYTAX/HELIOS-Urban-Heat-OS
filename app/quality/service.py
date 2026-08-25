from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.models_demographics import CellDemographic
from app.db.models_exposure import ExposureMetric, UrbanContextCell
from app.db.models_quality import QualitySnapshot, SystemAuditEvent
from app.db.models_thermal import ThermalCell, ThermalObservation
from app.quality.freshness import thermal_freshness
from app.quality.metrics import validate_metric_relationships

def audit(db: Session, *, event_type: str, severity: str, message: str,
          area_id: str | None = None, entity_type: str | None = None,
          entity_id: str | None = None, details: dict | None = None):
    row = SystemAuditEvent(
        event_type=event_type,
        severity=severity,
        area_id=area_id,
        entity_type=entity_type,
        entity_id=entity_id,
        message=message,
        details_json=details or {},
    )
    db.add(row)
    return row

def run_quality_snapshot(db: Session, area_id: str, fortyguard_live: bool = False):
    cells = db.execute(select(ThermalCell).where(ThermalCell.area_id == area_id)).scalars().all()
    checks = []
    scores = []

    if not cells:
        checks.append({"check": "cells_present", "status": "fail", "score": 0.0})
        scores.append(0.0)
    else:
        checks.append({"check": "cells_present", "status": "pass", "score": 1.0, "count": len(cells)})
        scores.append(1.0)

    for cell in cells:
        obs = db.execute(
            select(ThermalObservation)
            .where(ThermalObservation.cell_id == cell.id)
            .order_by(desc(ThermalObservation.observed_at))
            .limit(1)
        ).scalar_one_or_none()

        fresh = thermal_freshness(obs.observed_at if obs else None, fortyguard_live)
        checks.append({"check": "thermal_freshness", "cell_id": cell.id, **fresh})
        scores.append(fresh["score"])

        ctx = db.execute(select(UrbanContextCell).where(UrbanContextCell.cell_id == cell.id)).scalar_one_or_none()
        demo = db.execute(select(CellDemographic).where(CellDemographic.cell_id == cell.id)).scalar_one_or_none()
        metric = db.execute(
            select(ExposureMetric)
            .where(ExposureMetric.cell_id == cell.id)
            .order_by(desc(ExposureMetric.observed_at))
            .limit(1)
        ).scalar_one_or_none()

        if ctx and demo and metric:
            issues = validate_metric_relationships(
                teu=metric.teu,
                va_teu_value=metric.vulnerable_teu,
                population=ctx.population,
                vulnerable_population=ctx.vulnerable_population,
                vulnerability_index=ctx.vulnerability_index,
            )
            score = 1.0 if not issues else 0.5
            checks.append({
                "check": "metric_invariants",
                "cell_id": cell.id,
                "status": "pass" if not issues else "review",
                "score": score,
                "issues": issues,
            })
            scores.append(score)
        else:
            checks.append({
                "check": "required_cell_layers",
                "cell_id": cell.id,
                "status": "fail",
                "score": 0.0,
            })
            scores.append(0.0)

    health = sum(scores) / len(scores) if scores else 0.0
    review = (
        health < 0.80
        or any(c.get("status") in {"fail", "expired"} for c in checks)
        or any(c.get("status") == "fixture_or_nonlive" for c in checks)
    )
    status = "healthy" if health >= 0.90 and not review else "review_required" if health >= 0.60 else "degraded"

    snapshot = QualitySnapshot(
        area_id=area_id,
        status=status,
        health_score=health,
        requires_human_review=review,
        checks_json={"checks": checks},
    )
    db.add(snapshot)

    if review:
        audit(
            db,
            event_type="quality_gate",
            severity="warning" if health >= 0.60 else "error",
            area_id=area_id,
            message="HELIOS quality gate requires review.",
            details={"health_score": health, "status": status},
        )

    db.commit()
    db.refresh(snapshot)
    return snapshot
