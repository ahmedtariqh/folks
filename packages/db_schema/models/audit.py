import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, JSON, Text, Index
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, utc_now

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    correlation_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    agent_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    task_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    daemon_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False) # HEARTBEAT, LOCK_ACQUIRED, TOOL_CALL, STDOUT, REAPED_TO_DLQ
    level: Mapped[str] = mapped_column(String(20), default="INFO") # INFO, WARN, ERROR, DEBUG
    message: Mapped[str] = mapped_column(Text, default="")
    payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)

    __table_args__ = (
        Index("idx_audit_task_corr", "task_id", "correlation_id"),
    )
