from sqlalchemy import select
from app.db.session import SessionLocal
from app.db.models_provider_ops import ProviderOperationalMetric
db=SessionLocal()
try:
    rows=db.execute(select(ProviderOperationalMetric).where(ProviderOperationalMetric.area_id=="phx-downtown")).scalars().all()
    assert len(rows)==4
    assert all(r.truth_category=="provider_derived" for r in rows)
    assert all(0<=r.hazard_index<=1 for r in rows)
    assert all(r.teu>=0 and r.va_teu>=0 for r in rows)
    print("PASS: 4 provider-derived operational metric rows verified")
finally:db.close()
