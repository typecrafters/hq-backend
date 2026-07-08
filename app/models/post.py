import enum
from datetime import datetime, timezone
from sqlalchemy import BigInteger, Boolean, DateTime, Enum, ForeignKey, Identity, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class PostStatus(enum.Enum):
    Published = 'Published'
    Draft = 'Draft'
    Archived = 'Archived'


class Post(Base):
    __tablename__ = 'posts'

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    author: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id'), nullable=False)
    status: Mapped[PostStatus] = mapped_column(Enum(PostStatus), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    content: Mapped[dict] = mapped_column(JSONB, nullable=True)
    featured: Mapped[bool] = mapped_column(Boolean, default=False)
