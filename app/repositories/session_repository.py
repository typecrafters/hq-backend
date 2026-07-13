from datetime import datetime, timezone

from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from app.models.session import Session as SessionModel
from app.repositories.repository import Repository

class SessionRepository(Repository[SessionModel, str]):
    def __init__(self, db: Session):
        super().__init__(db, SessionModel)

    def delete_all_expired(self) -> None:
        self.db.execute(delete(SessionModel).where(SessionModel.expires_at <= datetime.now(timezone.utc)))
    
    def get_all_by_uid(self, uid: int) -> list[SessionModel]:
        stmt = select(SessionModel).where(SessionModel.uid == uid)
        return list(self.db.execute(stmt).scalars().all())
    
    def for_user_by_hash(self, uid: int, hash: str) -> SessionModel | None:
        stmt = select(SessionModel).where(SessionModel.uid == uid, SessionModel.id == hash)
        return self.db.execute(stmt).scalar_one_or_none()