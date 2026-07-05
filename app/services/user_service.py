from app.models.user import User
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.schemas.request.create_user import CreateUser
from app.schemas.response.protected_user import ProtectedUser
from app.services.password_service import PasswordService


class UserService:
    user_repo: UserRepository
    role_repo: RoleRepository
    pw_service: type[PasswordService]

    def __init__(self, user_repo: UserRepository, role_repo: RoleRepository, pw_service: type[PasswordService]):
        self.user_repo = user_repo
        self.role_repo = role_repo
        self.pw_service = pw_service

    def create(self, dto: CreateUser) -> User:
        role = self.role_repo.create_role(dto.title, dto.permissions, can_login=dto.can_access_panel)

        user = self.user_repo.create(
            first_name=dto.first_name,
            last_name=dto.last_name,
            title=dto.title,
            email=dto.email,
            password=self.pw_service.hash(dto.password),
            show_on_page=dto.show_on_page,
            profile_picture_url=dto.profile_picture_url,
            role_id=role.id,
        )

        if dto.create_role:
            self.role_repo.create_role(f'{dto.title} (No Login)', dto.permissions, can_login=False)

        return user
    
    def list(self, page: int, limit: int) -> list[User]:
        limit = max(min(limit, 100), 0)
        offset = max(page - 1, 0) * limit

    def get_by_id(self, id: int) -> User | None:
        pass