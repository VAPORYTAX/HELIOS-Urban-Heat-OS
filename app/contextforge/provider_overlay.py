from __future__ import annotations
from sqlalchemy import desc, select
from app.db.models_provider_ops import ProviderOperationalMetric

STALE_PROVIDER_TRANSITION_KINDS = {"optimizer", "exposure_metric", "hotspot"}

def reconcile_provider_state(db, packet: dict, area_id: str) -> dict:
    rows=db.execute(
        select(ProviderOperationalMetric)
        .where(ProviderOperationalMetric.area_id==area_id)
        .order_by(desc(ProviderOperationalMetric.created_at))
    ).scalars().all()

    latest={}
    for r in rows:
        latest.setdefault(r.cell_id,r)
    if not latest:
        return packet

    newest=max(r.created_at for r in latest.values())
    packet.setdefault("state",{})
    packet["state"]["cells"]=[
        {
            "cell_id":r.cell_id,
            "current_c":r.current_c,
            "baseline_mean_c":r.baseline_mean_c,
            "anomaly_c":r.anomaly_c,
            "z_score":r.z_score,
            "persistence_hours":r.persistence_hours,
            "exceedance_hours":r.exceedance_hours,
            "hazard_index":r.hazard_index,
            "severity":r.severity,
            "population":r.population,
            "vulnerability_index":r.vulnerability_index,
            "teu":r.teu,
            "va_teu":r.va_teu,
            "confidence":r.confidence,
            "truth_category":r.truth_category,
            "model_version":r.model_version,
        }
        for r in sorted(latest.values(),key=lambda x:x.teu,reverse=True)
    ]
    packet["state"]["provider_operational"]={
        "active":True,
        "model_version":next(iter(latest.values())).model_version,
        "truth_category":"provider_derived",
        "latest_created_at":newest.isoformat(),
    }

    if packet["state"].get("optimizer"):
        packet["state"]["optimizer"]=None
    packet["state"]["optimizer_status"]={
        "status":"stale_quarantined",
        "reason":"Optimizer predates provider-derived operational metric rebuild.",
        "requires_rebuild":True,
    }

    # During the provider transition, old downstream model evidence must not survive
    # in the AI context merely because the visible state was replaced.
    refs=[
        x for x in packet.setdefault("evidence_refs",[])
        if x.get("kind") not in STALE_PROVIDER_TRANSITION_KINDS
    ]
    existing={x.get("ref") for x in refs}
    for r in latest.values():
        if r.id not in existing:
            refs.insert(0,{
                "kind":"provider_operational_metric",
                "ref":r.id,
                "truth_category":"provider_derived",
                "confidence":r.confidence,
                "utility_score":min(1.0,0.98*r.confidence),
            })
    packet["evidence_refs"]=refs
    packet["state"]["evidence_transition"]={
        "stale_kinds_removed":sorted(STALE_PROVIDER_TRANSITION_KINDS),
        "status":"clean",
        "reason":"Legacy downstream outputs must be rebuilt from provider-derived operational metrics.",
    }
    return packet
