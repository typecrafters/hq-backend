from datetime import datetime, timezone
from sqlalchemy import BigInteger, DateTime, Identity, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class LegalPage(Base):
    __tablename__ = 'legal_pages'

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content_markdown: Mapped[str] = mapped_column(Text, nullable=False, default='')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
