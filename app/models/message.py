from datetime import datetime, timezone
from sqlalchemy import BigInteger, DateTime, ForeignKey, Identity, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Message(Base):
    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    subject: Mapped[str] = mapped_column(String, default='General inquiry')
    content: Mapped[str] = mapped_column(String, nullable=False)
    mail_to: Mapped[str] = mapped_column(String, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    read_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    replied_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    replied_by: Mapped[int | None] = mapped_column(BigInteger, ForeignKey('users.id'), nullable=True)
    reply: Mapped[str] = mapped_column(Text, nullable=True)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
