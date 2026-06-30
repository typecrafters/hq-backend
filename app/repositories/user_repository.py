from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.repository import Repository

class UserRepository(Repository):
    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email).limit(1)
        return self.db.execute(stmt).scalar_one_or_none()