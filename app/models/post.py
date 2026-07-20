import enum
from datetime import datetime, timezone
from sqlalchemy import BigInteger, Boolean, DateTime, Enum, ForeignKey, Identity, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class PostStatus(enum.Enum):
    Published = 'Published'
    Draft = 'Draft'
    Archived = 'Archived'


class Post(Base):
    __tablename__ = 'posts'

    __table_args__ = (
        UniqueConstraint('slug', 'lang', name='uq_posts_slug_lang'),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    lang: Mapped[str] = mapped_column(String(5), nullable=False, default="en")
    author: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id'), nullable=False)
    status: Mapped[PostStatus] = mapped_column(Enum(PostStatus), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    content: Mapped[dict] = mapped_column(JSONB, nullable=True)
    featured: Mapped[bool] = mapped_column(Boolean, default=False)
