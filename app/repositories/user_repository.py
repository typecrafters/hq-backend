from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.repository import Repository

class UserRepository(Repository[User, int]):
    def __init__(self, db: Session):
        super().__init__(db, User)

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email).limit(1)
        return self.db.execute(stmt).scalar_one_or_none()
    