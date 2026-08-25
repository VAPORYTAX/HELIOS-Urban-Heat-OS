from sqlalchemy import desc,select
from app.db.session import SessionLocal
from app.db.models_provider_ops import ProviderOperationalMetric
from app.db.models_context import ContextPacket
from app.db.models_quality import QualitySnapshot

db=SessionLocal()
try:
    ops=db.execute(select(ProviderOperationalMetric).where(ProviderOperationalMetric.area_id=="phx-downtown")).scalars().all()
    op_latest={}
    for r in sorted(ops,key=lambda x:x.created_at,reverse=True): op_latest.setdefault(r.cell_id,r)

    cp=db.execute(
        select(ContextPacket).where(ContextPacket.area_id=="phx-downtown")
        .order_by(desc(ContextPacket.created_at)).limit(1)
    ).scalar_one()
    cells={x["cell_id"]:x for x in cp.packet_json["state"]["cells"]}
    assert len(cells)==4
    for cid,r in op_latest.items():
        assert abs(cells[cid]["teu"]-r.teu)<1e-9
        assert abs(cells[cid]["hazard_index"]-r.hazard_index)<1e-9
        assert cells[cid]["truth_category"]=="provider_derived"

    assert cp.packet_json["state"].get("optimizer") is None
    assert cp.packet_json["state"].get("optimizer_status",{}).get("status")=="stale_quarantined"

    q=db.execute(
        select(QualitySnapshot).where(QualitySnapshot.area_id=="phx-downtown")
        .order_by(desc(QualitySnapshot.created_at)).limit(1)
    ).scalar_one()
    assert q.requires_human_review is True

    print("PASS: ContextForge uses provider-derived metrics")
    print("PASS: stale optimizer quarantined")
    print("PASS: provider-aware quality snapshot is latest")
finally:
    db.close()
