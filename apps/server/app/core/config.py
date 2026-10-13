import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Folks Multi-Agent Orchestrator"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./folks.db")
    
    # State Machine & Lock Parameters
    LOCK_DEFAULT_TTL_SECONDS: int = 60
    LOCK_SWEEPER_INTERVAL_SECONDS: int = 5
    DAEMON_HEARTBEAT_INTERVAL_SECONDS: int = 15
    
    # Server Host / Port
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS
    CORS_ORIGINS: list[str] = ["*"]

    model_config = SettingsConfigDict(case_sensitive=True)

settings = Settings()
