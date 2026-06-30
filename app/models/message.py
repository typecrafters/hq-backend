from datetime import datetime
from sqlalchemy import BigInteger, DateTime, ForeignKey, Identity, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Message(Base):
    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    subject: Mapped[str] = mapped_column(String, default='General inquiry')
    content: Mapped[str] = mapped_column(String, nullable=False)
    mail_to: Mapped[str] = mapped_column(String, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    read_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    replied_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    replied_by: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id'), nullable=False)
    reply: Mapped[str] = mapped_column(Text, nullable=True)
