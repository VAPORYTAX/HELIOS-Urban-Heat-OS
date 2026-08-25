from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from geoalchemy2.shape import to_shape
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models_thermal import ThermalCell
from app.db.models_provider_ops import ProviderOperationalMetric

router = APIRouter(prefix="/spatial", tags=["spatial"])

@router.get("/cells")
def cells_geojson(area_id: str = Query("phx-downtown"), db: Session = Depends(get_db)):
    cells = db.execute(
        select(ThermalCell).where(ThermalCell.area_id == area_id)
    ).scalars().all()

    rows = db.execute(
        select(ProviderOperationalMetric)
        .where(ProviderOperationalMetric.area_id == area_id)
        .order_by(desc(ProviderOperationalMetric.created_at))
    ).scalars().all()

    latest = {}
    for row in rows:
        latest.setdefault(row.cell_id, row)

    features = []
    for cell in cells:
        m = latest.get(cell.id)
        props = {
            "cell_id": cell.id,
            "area_id": cell.area_id,
            "truth_category": "helios_real_cell_geometry_provider_operational_metrics",
        }
        if m is not None:
            props.update({
                "current_c": m.current_c,
                "hazard_index": m.hazard_index,
                "vulnerability_index": m.vulnerability_index,
                "teu": m.teu,
                "va_teu": getattr(m, "va_teu", getattr(m, "vulnerable_teu", None)),
                "confidence": m.confidence,
            })
        features.append({
            "type": "Feature",
            "id": cell.id,
            "geometry": to_shape(cell.geometry).__geo_interface__,
            "properties": props,
        })

    return {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "area_id": area_id,
            "feature_count": len(features),
            "geometry_source": "HELIOS PostGIS ThermalCell",
            "metric_source": "latest ProviderOperationalMetric per cell",
            "modelled_is_causal": False,
        },
    }
