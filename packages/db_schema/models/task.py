import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Integer, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, utc_now

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    project_tag: Mapped[str] = mapped_column(String(100), nullable=False) # Strict project boundary

    team_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
    assigned_agent_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True)

    # State Machine
    # BACKLOG, QUEUED, IN_PROGRESS, PAUSED_FOR_CONSULTATION, BLOCKED, AWAITING_REVIEW, DEAD_LETTER_QUEUE, DONE
    status: Mapped[str] = mapped_column(String(50), default="BACKLOG")
    priority: Mapped[str] = mapped_column(String(20), default="MEDIUM") # LOW, MEDIUM, HIGH, URGENT

    # Lock Management & Resilience
    lock_owner_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True) # Agent or Daemon ID
    lock_acquired_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    lock_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    lock_ttl_seconds: Mapped[int] = mapped_column(Integer, default=60)
    lock_suspended: Mapped[bool] = mapped_column(Boolean, default=False)
    lock_suspended_remaining_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Observability & Reaping
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    blocker_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    dlq_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    team = relationship("Team", back_populates="tasks")
    assigned_agent = relationship("Agent", back_populates="assigned_tasks", foreign_keys=[assigned_agent_id])
    review_gates = relationship("ReviewGate", back_populates="task", cascade="all, delete-orphan")
    war_rooms = relationship("WarRoom", back_populates="task", cascade="all, delete-orphan")
