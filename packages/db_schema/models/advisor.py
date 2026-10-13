import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, utc_now

class Advisor(Base):
    __tablename__ = "advisors"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. 'SECURITY_COMPLIANCE', 'ENTERPRISE_ARCHITECTURE'
    reasoning_model: Mapped[str] = mapped_column(String(100), default="claude-3-7-sonnet-thought") # Deep reasoning model
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE") # 'ACTIVE', 'INACTIVE'
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    knowledge_links = relationship("AdvisorKnowledgeLink", back_populates="advisor", cascade="all, delete-orphan")
    advisory_sessions = relationship("AdvisorySession", back_populates="advisor")


class AdvisorKnowledgeLink(Base):
    __tablename__ = "advisor_knowledge_links"

    advisor_id: Mapped[str] = mapped_column(String(36), ForeignKey("advisors.id", ondelete="CASCADE"), primary_key=True)
    knowledge_base_id: Mapped[str] = mapped_column(String(36), ForeignKey("knowledge_bases.id", ondelete="CASCADE"), primary_key=True)
    linked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    # Relationships
    advisor = relationship("Advisor", back_populates="knowledge_links")
    knowledge_base = relationship("KnowledgeBase", back_populates="advisors")
