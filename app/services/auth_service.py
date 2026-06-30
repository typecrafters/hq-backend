import secrets
from datetime import timedelta

from app.repositories.session_repository import SessionRepository
from app.repositories.user_repository import UserRepository
from app.services.crypto_service import CryptoService
from app.services.password_service import PasswordService


class AuthService:
    user_repo: UserRepository
    session_repo: SessionRepository
    pw_service: type[PasswordService]
    crypto_service: type[CryptoService]

    standard_age = timedelta(days=7)
    extended_age = timedelta(days=30)

    def __init__(
        self, 
        user_repo: UserRepository, 
        session_repo: SessionRepository, 
        pw_service: type[PasswordService],
        crypto_service: type[CryptoService]
    ):
        self.user_repo = user_repo
        self.session_repo = session_repo
        self.pw_service = pw_service
        self.crypto_service = crypto_service

    def auth_user(self, email: str, password: str) -> str | None:
        user = self.user_repo.get_by_email(email)
        if not user:
            return None
        
        if not self.pw_service.compare(user.password, password):
            return None
        
        raw = secrets.token_hex(32)
        self.session_repo.create(user, self.crypto_service.sha256hash(raw), max_age=self.standard_age)
        return raw

