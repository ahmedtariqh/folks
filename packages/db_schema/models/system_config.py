import uuid
from datetime import datetime
from typing import Optional, Any
from sqlalchemy import String, DateTime, Text, Boolean, Integer, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, utc_now

class LLMProviderConfig(Base):
    __tablename__ = "llm_provider_configs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    provider_type: Mapped[str] = mapped_column(String(50), default="custom") # 'custom', 'ollama', 'anthropic', 'openai', 'openrouter', 'gemini'
    provider_name: Mapped[str] = mapped_column(String(100), default="Custom LLM Provider")
    base_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    api_key: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    default_model: Mapped[str] = mapped_column(String(100), default="claude-3-7-sonnet")
    advisor_reasoning_model: Mapped[str] = mapped_column(String(100), default="claude-3-7-sonnet-thought")
    temperature: Mapped[float] = mapped_column(Float, default=0.7)
    max_tokens: Mapped[int] = mapped_column(Integer, default=4096)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


class SystemSetting(Base):
    __tablename__ = "system_settings"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
