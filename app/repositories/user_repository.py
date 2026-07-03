from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.repository import Repository

class UserRepository(Repository):
    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email).limit(1)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_id(self, uid: int) -> User | None:
        return self.db.get(User, uid)

    def create(
        self,
        first_name: str,
        last_name: str,
        title: str,
        email: str,
        password: str,
        show_on_page: bool,
        profile_picture_url: str,
        role_id: int,
    ) -> User:
        user = User(
            role_id=role_id,
            first_name=first_name,
            last_name=last_name,
            title=title,
            email=email,
            password=password,
            profile_picture_url=profile_picture_url,
            show_on_page=show_on_page,
        )

        self.db.add(user)
        self.db.flush()
        return user