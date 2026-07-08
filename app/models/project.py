import enum
from datetime import datetime, timezone
from sqlalchemy import ARRAY as Array, BigInteger, DateTime, Enum, ForeignKey, Identity, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class ProjectStatus(enum.Enum):
    Development = 'Development'
    Planned = 'Planned'
    Review = 'Review'
    Archived = 'Archived'
    Cancelled = 'Cancelled'


class Project(Base):
    __tablename__ = 'projects'

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    project_name: Mapped[str] = mapped_column(String, nullable=False)
    project_lead: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id'), nullable=False)
    status: Mapped[ProjectStatus] = mapped_column(Enum(ProjectStatus), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    tags: Mapped[list[str]] = mapped_column(Array(String), default=list)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    summary: Mapped[str] = mapped_column(String, nullable=False)
