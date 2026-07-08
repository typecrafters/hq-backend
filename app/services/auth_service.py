from datetime import datetime, timedelta, timezone
import secrets
from app.config.settings import settings  
from app.models.session import Session
from app.repositories.session_repository import SessionRepository
from app.services.static.crypto_service import CryptoService
from app.services.static.email_service import EmailService
from app.services.static.password_service import PasswordService
from app.services.user_service import UserService


class AuthService:
    VERIFICATION_TOKEN_LENGTH = 32
    PYSESSID_LENGTH: int = 32
    DEFAULT_AGE = timedelta(days=7)
    EXTENDED_AGE = timedelta(days = 90)

    session_repo: SessionRepository
    
    user_service: UserService

    email_service: type[EmailService]
    pw_service: type[PasswordService]
    crypto_service: type[CryptoService]

    def __init__(
        self, 
        session_repo: SessionRepository, 
        user_service: UserService, 
        email_service: type[EmailService],
        pw_service: type[PasswordService],
        crypto_service: type[CryptoService]
    ):
        self.session_repo = session_repo
        self.user_service = user_service
        self.email_service = email_service
        self.pw_service = pw_service
        self.crypto_service = crypto_service

    def authenticate(self, email: str, password: str, remember_me: bool) -> str | None:        
        user = self.user_service.get_by_email(email)

        if user is None:
            return None

        if not self.pw_service.compare(user.password, password):
            return None
        
        pysessid = secrets.token_hex(self.PYSESSID_LENGTH)
        now = datetime.now(timezone.utc)
        exp = now + (self.EXTENDED_AGE if remember_me else self.DEFAULT_AGE)

        session = Session(
            id=self.crypto_service.sha256hash(pysessid),
            uid=user.id,
            ip_address='', # TODO provide
            user_agent='', # TODO provide
            issued_at=now,
            expires_at=exp
        )

        self.session_repo.save(session)

        return pysessid
    
    def create_email_verification(self):
        token = secrets.token_hex(self.VERIFICATION_TOKEN_LENGTH)
        
        pass
    
    def get_session(self, pysessid: str) -> Session | None:
        return self.session_repo.get_by_id(pysessid)