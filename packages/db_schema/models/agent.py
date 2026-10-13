import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Numeric, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, utc_now

class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(100), nullable=False)
    backstory: Mapped[str] = mapped_column(String(2000), default="")
    adapter_type: Mapped[str] = mapped_column(String(50), default="host_cli") # 'host_cli', 'claude_local', etc.
    model_name: Mapped[str] = mapped_column(String(100), default="claude-3-7-sonnet")
    project_tags: Mapped[List[str]] = mapped_column(JSON, default=list) # e.g. ["proj_backend", "proj_api"]
    monthly_budget_usd: Mapped[float] = mapped_column(Numeric(10, 2), default=50.0)
    current_spend_usd: Mapped[float] = mapped_column(Numeric(10, 4), default=0.0)
    status: Mapped[str] = mapped_column(String(50), default="IDLE") # IDLE, IN_PROGRESS, PAUSED_FOR_CONSULTATION, CONSULTANT_ACTIVE, PAUSED_BUDGET
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    team_memberships = relationship("TeamMembership", back_populates="agent", cascade="all, delete-orphan")
    assigned_tasks = relationship("Task", back_populates="assigned_agent", foreign_keys="Task.assigned_agent_id")
