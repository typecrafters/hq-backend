from app.models.role import Role
from app.models.user import User
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.schemas.request.create_user import CreateUser
from app.schemas.response.role import RoleResponse
from app.schemas.response.user_with_role import UserWithRole
from app.services.static.password_service import PasswordService

class UserService:
    user_repo: UserRepository
    role_repo: RoleRepository

    def __init__(self, user_repo: UserRepository, role_repo: RoleRepository):
        self.user_repo = user_repo
        self.role_repo = role_repo


    def get_by_id(self, id: int) -> User | None:
        return self.user_repo.get_by_id(id)

    def get_by_email(self, email: str) -> User | None:
        return self.user_repo.get_by_email(email)

    def list(self, page: int, limit: int) -> list[User]:
        limit = max(1, min(limit, 100))
        page = max(page - 1, 0)
        offset = page * limit

        return self.user_repo.get_all(limit=limit, offset=offset)

    def create(self, data: CreateUser) -> User:
        role = self.role_repo.save(Role(
            name=f'{data.first_name}_{data.last_name}_role',
            permissions=data.permissions,
            can_login=True,
        ))

        if data.create_role:
            self.role_repo.save(Role(
                name=f'{data.first_name}_{data.last_name}#creation_pgroup',
                permissions=data.permissions,
                can_login=False,
            ))

        user = User(
            role_id=role.id,
            first_name=data.first_name,
            last_name=data.last_name,
            title=data.title,
            email=data.email,
            password=PasswordService.hash(data.password),
            profile_picture_url=data.profile_picture_url,
            show_on_page=data.show_on_page,
        )

        return self.user_repo.save(user)

    def load_by_id(self, id: int) -> UserWithRole | None:
        user = self.user_repo.get_by_id(id)
        if user is None:
            return None
        role = self.role_repo.get_by_id(user.role_id)
        if role is None:
            return None

        return UserWithRole(
            id=user.id,
            role=RoleResponse.model_validate(role),
            first_name=user.first_name,
            last_name=user.last_name,
            title=user.title,
            email=user.email,
            password_set=user.password is not None,
            profile_picture_url=user.profile_picture_url,
            show_on_page=user.show_on_page,
            created_at=user.created_at,
        )