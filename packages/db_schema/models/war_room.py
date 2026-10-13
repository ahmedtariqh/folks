import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, utc_now

class WarRoom(Base):
    __tablename__ = "war_rooms"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id: Mapped[str] = mapped_column(String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    initiator_agent_id: Mapped[str] = mapped_column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE") # 'ACTIVE', 'CONCLUDED', 'CANCELLED'
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    concluded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    task = relationship("Task", back_populates="war_rooms")
    initiator = relationship("Agent", foreign_keys=[initiator_agent_id])
    participants = relationship("WarRoomParticipant", back_populates="war_room", cascade="all, delete-orphan")
    messages = relationship("WarRoomMessage", back_populates="war_room", cascade="all, delete-orphan")


class WarRoomParticipant(Base):
    __tablename__ = "war_room_participants"

    war_room_id: Mapped[str] = mapped_column(String(36), ForeignKey("war_rooms.id", ondelete="CASCADE"), primary_key=True)
    agent_id: Mapped[str] = mapped_column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), primary_key=True)
    role: Mapped[str] = mapped_column(String(50), default="CONSULTANT") # 'INITIATOR', 'CONSULTANT'
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    # Relationships
    war_room = relationship("WarRoom", back_populates="participants")
    agent = relationship("Agent")


class WarRoomMessage(Base):
    __tablename__ = "war_room_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    war_room_id: Mapped[str] = mapped_column(String(36), ForeignKey("war_rooms.id", ondelete="CASCADE"), nullable=False)
    sender_type: Mapped[str] = mapped_column(String(20), default="AGENT") # 'AGENT', 'OWNER', 'SYSTEM'
    agent_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    # Relationships
    war_room = relationship("WarRoom", back_populates="messages")
    agent = relationship("Agent")
