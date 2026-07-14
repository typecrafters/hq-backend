from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.message import Message
from app.repositories.repository import Repository

class MessageRepository(Repository[Message, int]):
    def __init__(self, db: Session):
        super().__init__(db, Message)

    def get_all(self, limit: int | None = None, offset: int | None = None, unread: bool | None = None) -> list[Message]:
        stmt = select(self.entity).where(self.entity.archived_at.is_(None))
        if unread is not None:
            if unread:
                stmt = stmt.where(self.entity.read_at.is_(None))
            else:
                stmt = stmt.where(self.entity.read_at.is_not(None))
        stmt = stmt.limit(limit).offset(offset)
        return list(self.db.execute(stmt).scalars().all())

    def count_all(self, unread: bool | None = None) -> int:
        stmt = select(func.count()).select_from(self.entity).where(self.entity.archived_at.is_(None))
        if unread is not None:
            if unread:
                stmt = stmt.where(self.entity.read_at.is_(None))
            else:
                stmt = stmt.where(self.entity.read_at.is_not(None))
        return self.db.execute(stmt).scalar() or 0
