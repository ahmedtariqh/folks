import uuid
from datetime import datetime
from typing import Optional, Any
from sqlalchemy import String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, utc_now

class AgentMessage(Base):
    __tablename__ = "agent_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id: Mapped[str] = mapped_column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    sender_type: Mapped[str] = mapped_column(String(20), default="USER") # "USER" or "AGENT"
    message: Mapped[str] = mapped_column(Text, nullable=False)
    message_type: Mapped[str] = mapped_column(String(50), default="CHAT") # "CHAT", "DELEGATION_DIRECTIVE", "STATUS_REPORT", "TASK_CREATED"
    metadata_payload: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    # Relationship
    agent = relationship("Agent", foreign_keys=[agent_id])
