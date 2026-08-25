from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.db.models import ProvenanceRecord

def record_provider_provenance(
    db: Session,
    *,
    entity_type: str,
    entity_id: str,
    operation: str,
    activity_id: str | None,
    metadata: dict | None = None,
) -> ProvenanceRecord:
    row = ProvenanceRecord(
        entity_type=entity_type,
        entity_id=entity_id,
        source="FortyGuard Temperature API",
        source_operation=operation,
        source_activity_id=activity_id,
        retrieved_at=datetime.now(timezone.utc),
        quality_label="provider",
        metadata_json=metadata or {},
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
