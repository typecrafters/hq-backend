from datetime import datetime, timedelta
from sqlalchemy import select, update
from app.models.session import Session
from app.models.user import User
from app.repositories.repository import Repository


class SessionRepository(Repository):
    def get_by_pysessid(self, pysessid: str) -> Session | None:
        stmt = select(Session).where(Session.pysessid == pysessid).limit(1)
        return self.db.execute(stmt).scalar_one_or_none()
    
    def create(self, user: User, pysessid: str, max_age: timedelta) -> None:
        now = datetime.now()

        session = Session(
            pysessid=pysessid,
            uid=user.id,
            ip_address='',
            user_agent='',
            issued_at=now,
            expires_at=now + max_age,
        )

        self.db.add(session)

    def revoke_all_for_user(self, uid: int) -> None:
        stmt = (
            update(Session)
            .where(Session.uid == uid, Session.revoked_at.is_(None))
            .values(revoked_at=datetime.now())
        )
        self.db.execute(stmt)