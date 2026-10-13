import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from .base import Base, utc_now

class Team(Base):
    __tablename__ = "teams"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    mission: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default="") # Company / Team Core Mission
    project_tag: Mapped[str] = mapped_column(String(100), nullable=False) # Bound project scope
    lead_agent_id: Mapped[str] = mapped_column(String(36), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


    # Relationships
    lead_agent = relationship("Agent", foreign_keys=[lead_agent_id])
    members = relationship("TeamMembership", back_populates="team", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="team")


class TeamMembership(Base):
    __tablename__ = "team_memberships"

    team_id: Mapped[str] = mapped_column(String(36), ForeignKey("teams.id", ondelete="CASCADE"), primary_key=True)
    agent_id: Mapped[str] = mapped_column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), primary_key=True)
    team_role: Mapped[str] = mapped_column(String(100), default="Member") # 'Lead', 'Specialist', 'Reviewer'
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    # Relationships
    team = relationship("Team", back_populates="members")
    agent = relationship("Agent", back_populates="team_memberships")
