import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, DateTime, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, utc_now

class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    domain_tag: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. 'security_standards', 'system_architecture'
    documents: Mapped[List[dict]] = mapped_column(JSON, default=list) # Rich documents, guidelines, benchmarks
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    advisors = relationship("AdvisorKnowledgeLink", back_populates="knowledge_base", cascade="all, delete-orphan")
