import json
from sqlalchemy import select
from app.db.session import SessionLocal
from app.db.models_thermal import ThermalCell
from app.exposure.service import compute_latest_exposure_for_cell

db = SessionLocal()
try:
    ids = db.execute(
        select(ThermalCell.id).where(ThermalCell.area_id == "phx-downtown")
    ).scalars().all()
    rows = []
    for cell_id in ids:
        result = compute_latest_exposure_for_cell(db, cell_id)
        if result:
            metric, driver = result
            rows.append({
                "cell_id": cell_id,
                "teu": metric.teu,
                "vulnerable_teu": metric.vulnerable_teu,
                "dominant_driver": driver.dominant_driver,
                "confidence": metric.confidence,
            })
    print(json.dumps({"computed_cells": len(rows), "results": rows}, indent=2))
finally:
    db.close()
