from datetime import datetime, timezone
from sqlalchemy import BigInteger, Identity, String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    role_id: Mapped[int] = mapped_column(BigInteger)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, index=True, unique=True, nullable=False)
    password: Mapped[str | None] = mapped_column(String, nullable=True)
    profile_picture_url: Mapped[str | None] = mapped_column(String, nullable=True)
    show_on_page: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))