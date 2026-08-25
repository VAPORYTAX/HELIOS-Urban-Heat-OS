from sqlalchemy import desc, select
from app.db.session import SessionLocal
from app.db.models_context import ContextPacket

db=SessionLocal()
try:
    cp=db.execute(
        select(ContextPacket)
        .where(ContextPacket.area_id=="phx-downtown")
        .order_by(desc(ContextPacket.created_at)).limit(1)
    ).scalar_one()
    packet=cp.packet_json
    kinds=[x.get("kind") for x in packet.get("evidence_refs",[])]
    forbidden={"optimizer","exposure_metric","hotspot"}
    present=sorted(forbidden.intersection(kinds))
    assert not present, f"Stale provider-transition evidence still present: {present}"
    assert packet["state"]["optimizer"] is None
    assert packet["state"]["optimizer_status"]["status"]=="stale_quarantined"
    assert packet["state"]["evidence_transition"]["status"]=="clean"
    provider_refs=[x for x in packet["evidence_refs"] if x.get("kind")=="provider_operational_metric"]
    assert len(provider_refs)==4, f"Expected 4 provider operational refs, got {len(provider_refs)}"
    print("PASS: stale optimizer/exposure/hotspot evidence removed")
    print("PASS: 4 provider-operational evidence refs authoritative")
    print("PASS: optimizer remains quarantined pending explicit rebuild")
finally:
    db.close()
