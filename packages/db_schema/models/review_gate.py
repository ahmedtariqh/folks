import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, utc_now

class ReviewGate(Base):
    __tablename__ = "review_gates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id: Mapped[str] = mapped_column(String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    agent_id: Mapped[str] = mapped_column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    diff_patch: Mapped[str] = mapped_column(Text, nullable=False) # Git diff
    test_results: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # Test runner results
    status: Mapped[str] = mapped_column(String(50), default="PENDING") # 'PENDING', 'APPROVED', 'REJECTED'
    owner_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    task = relationship("Task", back_populates="review_gates")
    agent = relationship("Agent")
