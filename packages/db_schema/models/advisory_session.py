import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, utc_now

class AdvisorySession(Base):
    __tablename__ = "advisory_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)
    requesting_agent_id: Mapped[str] = mapped_column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    advisor_id: Mapped[str] = mapped_column(String(36), ForeignKey("advisors.id", ondelete="CASCADE"), nullable=False)
    
    # Request Info
    request_type: Mapped[str] = mapped_column(String(50), default="ARCHITECTURE_ADVICE") # 'ARCHITECTURE_ADVICE', 'SECURITY_REVIEW', 'STRATEGIC_DIRECTION', 'PRE_GATE_AUDIT'
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Intense Reasoning & Knowledge Base Evidence
    knowledge_references: Mapped[List[dict]] = mapped_column(JSON, default=list) # Cited KB articles/benchmarks
    reasoning_trace: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # Deep thinking / chain-of-thought
    verdict: Mapped[str] = mapped_column(String(50), default="PENDING") # 'APPROVED', 'RECOMMENDATIONS_PROVIDED', 'RISK_FLAGGED', 'REJECTED'
    advice_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    correlation_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PENDING") # 'PENDING', 'COMPLETED', 'FAILED'
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    advisor = relationship("Advisor", back_populates="advisory_sessions")
    requesting_agent = relationship("Agent")
    task = relationship("Task")
