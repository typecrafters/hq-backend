from typing import Any
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import BigInteger, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Session(Base):
    __tablename__ = 'sessions'
    
    pysessid: Mapped[str] = mapped_column(String, primary_key=True)
    uid: Mapped[int] = mapped_column(BigInteger, nullable=False)
    ip_address: Mapped[str] = mapped_column(String, nullable=True)
    user_agent: Mapped[str] = mapped_column(String, nullable=True)
    issued_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    revoked_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    data: Mapped[dict[str, Any]] = mapped_column(JSONB, default={})
