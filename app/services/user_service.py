from datetime import datetime, timedelta, timezone
import secrets

from app.config.settings import settings
from app.core.util import Duration
from app.models.role import Role
from app.models.token import Token
from app.models.user import User
from app.repositories.role_repository import RoleRepository
from app.repositories.token_repository import TokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.request.create_user import CreateUser
from app.schemas.response.role import RoleResponse
from app.schemas.response.user_with_role import UserWithRole
from app.services.static.crypto_service import CryptoService
from app.services.static.email_service import EmailService
from app.services.static.file_service import FileService
from app.services.static.password_service import PasswordService
from app.services.static.templating_service import TemplatingService


class UserService:
    VERIFICATION_TOKEN_LENGTH = 32
    EMAIL_TOKEN_AGE = timedelta(days=1)

    user_repo: UserRepository
    role_repo: RoleRepository
    token_repo: TokenRepository
    file_service: type[FileService]
    email_service: type[EmailService]
    templating_service: type[TemplatingService]
    crypto_service: type[CryptoService]

    def __init__(
        self,
        user_repo: UserRepository,
        role_repo: RoleRepository,
        token_repo: TokenRepository,
        file_service: type[FileService],
        email_service: type[EmailService],
        templating_service: type[TemplatingService],
        crypto_service: type[CryptoService]
    ):
        self.user_repo = user_repo
        self.role_repo = role_repo
        self.token_repo = token_repo
        self.file_service = file_service
        self.email_service = email_service
        self.templating_service = templating_service
        self.crypto_service = crypto_service

    def get_by_id(self, id: int, with_picture: bool = False) -> User | None:
        user = self.user_repo.get_by_id(id)
        if user is None:
            return None
        if with_picture:
            self.user_repo.db.expunge(user)
            user.profile_picture_url = self.file_service.sign_download(user.profile_picture_url)
        return user

    def get_by_email(self, email: str, with_picture: bool = False) -> User | None:
        user = self.user_repo.get_by_email(email)
        if user is None:
            return None
        if with_picture:
            self.user_repo.db.expunge(user)
            user.profile_picture_url = self.file_service.sign_download(user.profile_picture_url)
        return user

    def list(self, page: int, limit: int, with_picture: bool = False) -> list[User]:
        limit = max(1, min(limit, 100))
        page = max(page - 1, 0)
        offset = page * limit

        users = self.user_repo.get_all(limit=limit, offset=offset)

        if with_picture:
            for user in users:
                self.user_repo.db.expunge(user)
                user.profile_picture_url = self.file_service.sign_download(user.profile_picture_url)

        return users

    def create(self, data: CreateUser) -> User:
        if data.can_access_panel:
            role = self.role_repo.save(Role(
                name=f'{data.first_name.lower()}_{data.last_name.lower()}_role',
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
            profile_picture_url='system/placeholder.svg',
            show_on_page=data.show_on_page,
        )

        return self.user_repo.save(user)

    def create_email_verification_token(self, user: User):
        token = secrets.token_urlsafe(self.VERIFICATION_TOKEN_LENGTH)

        now = datetime.now(timezone.utc)

        self.token_repo.save(Token(
            token_hash=self.crypto_service.sha256hash(token),
            uid=user.id,
            issued_at=now,
            expires_at=now + self.EMAIL_TOKEN_AGE
        ))

        url = f"{settings.frontend_url}/auth/email/verify?token={token}"

        html = self.templating_service.render('verify-email.html.j2').using({
            'first_name': user.first_name,
            'url': url,
            'expires_in': Duration.readable(self.EMAIL_TOKEN_AGE)
        })

        self.email_service.send_html(user.email, 'Verify your email address', html)

    def load_by_id(self, id: int, with_picture: bool = False) -> UserWithRole | None:
        user = self.user_repo.get_by_id(id)
        if user is None:
            return None
        role = self.role_repo.get_by_id(user.role_id)
        if role is None:
            return None
        
        if with_picture:
            self.user_repo.db.expunge(user)
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
    
    def update(self, user: User) -> User | None:
        if self.user_repo.exists(user.id):
            return self.user_repo.save(user)
        
    def delete(self, id: int) -> bool:
        return self.user_repo.delete_by_id(id)