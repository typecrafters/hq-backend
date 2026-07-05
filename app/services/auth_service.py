import secrets
from datetime import timedelta

from app.config.settings import settings
from app.models.session import Session
from app.repositories.token_repository import TokenRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.user_repository import UserRepository
from app.services.crypto_service import CryptoService
from app.services.email_service import EmailService
from app.services.password_service import PasswordService


class AuthService:
    user_repo: UserRepository
    session_repo: SessionRepository
    token_repo: TokenRepository
    pw_service: type[PasswordService]
    crypto_service: type[CryptoService]
    email_service: type[EmailService]

    standard_age = timedelta(days=7)
    extended_age = timedelta(days=30)
    reset_token_age = timedelta(hours=1)

    def __init__(
        self,
        user_repo: UserRepository,
        session_repo: SessionRepository,
        token_repo: TokenRepository,
        pw_service: type[PasswordService],
        crypto_service: type[CryptoService],
        email_service: type[EmailService]
    ):
        self.user_repo = user_repo
        self.session_repo = session_repo
        self.token_repo = token_repo
        self.pw_service = pw_service
        self.crypto_service = crypto_service
        self.email_service = email_service

    def auth_user(self, email: str, password: str, max_age: timedelta) -> str | None:
        user = self.user_repo.get_by_email(email)
        if not user:
            return None

        if not self.pw_service.compare(user.password, password):
            return None

        pysessid = secrets.token_hex(32)
        self.session_repo.create(user, self.crypto_service.sha256hash(pysessid), max_age=max_age)
        return pysessid

    def request_password_reset(self, email: str) -> None:
        user = self.user_repo.get_by_email(email)
        if not user:
            return

        token = secrets.token_hex(32)
        self.token_repo.create(user, self.crypto_service.sha256hash(token), max_age=self.reset_token_age)

        reset_link = f'{settings.frontend_url}/password/reset?token={token}'
        self.email_service.send_password_reset_email(user.email, reset_link)

    def verify_reset_token(self, token: str) -> bool:
        reset_token = self.token_repo.get_valid_by_token_hash(self.crypto_service.sha256hash(token))
        return reset_token is not None

    def reset_password(self, token: str, new_password: str) -> bool:
        reset_token = self.token_repo.get_valid_by_token_hash(self.crypto_service.sha256hash(token))
        if reset_token is None:
            return False

        user = self.user_repo.get_by_id(reset_token.uid)
        if user is None:
            return False

        user.password = self.pw_service.hash(new_password)
        self.token_repo.mark_used(reset_token)
        self.session_repo.revoke_all_for_user(user.id)
        return True
    
    def get_session(self, pysessid: str) -> Session | None:
        return self.session_repo.get_by_pysessid(pysessid)
