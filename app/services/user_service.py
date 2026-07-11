from app.models.role import Role
from app.models.user import User
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.schemas.request.create_user import CreateUser
from app.schemas.response.role import RoleResponse
from app.schemas.response.user_with_role import UserWithRole
from app.services.static.file_service import FileService
from app.services.static.password_service import PasswordService


class UserService:
    user_repo: UserRepository
    role_repo: RoleRepository
    file_service: type[FileService]

    def __init__(self, user_repo: UserRepository, role_repo: RoleRepository, file_service: type[FileService]):
        self.user_repo = user_repo
        self.role_repo = role_repo
        self.file_service = file_service

    def get_by_id(self, id: int, with_picture: bool = False) -> User | None:
        user = self.user_repo.get_by_id(id)
        if with_picture:
            user.profile_picture_url = self.file_service.sign_download(user.profile_picture_url)

    def get_by_email(self, email: str, with_picture: bool = False) -> User | None:
        user = self.user_repo.get_by_email(email)
        if with_picture:
            user.profile_picture_url = self.file_service.sign_download(user.profile_picture_url)

    def list(self, page: int, limit: int, with_picture: bool = False) -> list[User]:
        limit = max(1, min(limit, 100))
        page = max(page - 1, 0)
        offset = page * limit

        users = self.user_repo.get_all(limit=limit, offset=offset)

        if with_picture:
            for user in users:
                user.profile_picture_url = self.file_service.sign_download(user.profile_picture_url)
        
        return users

    def create(self, data: CreateUser) -> User:
        role = self.role_repo.save(Role(
            name=f'{data.first_name}_{data.last_name}_role',
            permissions=[p.strip().lower() for p in data.permissions],
            can_login=True,
        ))

        if data.create_role:
            self.role_repo.save(Role(
                name=f'{data.first_name}_{data.last_name}#creation_pgroup',
                permissions=[p.strip().lower() for p in data.permissions],
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

    def load_by_id(self, id: int, with_picture: bool = False) -> UserWithRole | None:
        user = self.user_repo.get_by_id(id)
        if user is None:
            return None
        role = self.role_repo.get_by_id(user.role_id)
        if role is None:
            return None
        
        if with_picture:
            user.profile_picture_url = self.file_service.sign_download(user.profile_picture_url)

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
