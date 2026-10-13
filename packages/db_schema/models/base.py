import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import DeclarativeBase

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Base(DeclarativeBase):
    def __init__(self, **kwargs):
        if "id" not in kwargs and "id" in self.__table__.columns:
            kwargs["id"] = str(uuid.uuid4())
        for k, v in kwargs.items():
            setattr(self, k, v)
