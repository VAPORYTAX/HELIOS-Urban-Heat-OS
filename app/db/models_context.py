from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import JSON, Boolean, DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
def utcnow(): return datetime.now(timezone.utc)
class PromptRegistry(Base):
    __tablename__="prompt_registry"
    __table_args__=(UniqueConstraint("name","version",name="uq_prompt_name_version"),)
    id: Mapped[str]=mapped_column(String(64),primary_key=True)
    name: Mapped[str]=mapped_column(String(128),nullable=False)
    version: Mapped[str]=mapped_column(String(32),nullable=False)
    role: Mapped[str]=mapped_column(String(64),nullable=False)
    template_text: Mapped[str]=mapped_column(Text,nullable=False)
    active: Mapped[bool]=mapped_column(Boolean,nullable=False,default=True)
    metadata_json: Mapped[dict]=mapped_column(JSON,nullable=False,default=dict)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)
class ContextPacket(Base):
    __tablename__="context_packets"
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid4()))
    area_id: Mapped[str]=mapped_column(String(64),nullable=False)
    task_type: Mapped[str]=mapped_column(String(64),nullable=False)
    mode: Mapped[str]=mapped_column(String(32),nullable=False)
    user_intent: Mapped[str]=mapped_column(Text,nullable=False)
    context_hash: Mapped[str]=mapped_column(String(64),nullable=False,unique=True)
    prompt_bundle_version: Mapped[str]=mapped_column(String(64),nullable=False)
    token_budget: Mapped[int]=mapped_column(Integer,nullable=False)
    estimated_tokens: Mapped[int]=mapped_column(Integer,nullable=False)
    status: Mapped[str]=mapped_column(String(32),nullable=False)
    packet_json: Mapped[dict]=mapped_column(JSON,nullable=False)
    evidence_json: Mapped[dict]=mapped_column(JSON,nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)
