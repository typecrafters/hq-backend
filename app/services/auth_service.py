from datetime import datetime, timedelta, timezone
import secrets 
from app.config.settings import settings
from app.core.util import Duration
from app.models.session import Session
from app.models.token import Token
from app.models.user import User
from app.repositories.session_repository import SessionRepository
from app.repositories.token_repository import TokenRepository
from app.services.static.crypto_service import CryptoService
from app.services.static.templating_service import TemplatingService
from app.services.static.email_service import EmailService
from app.services.static.password_service import PasswordService
from app.services.user_service import UserService


class AuthService:
    VERIFICATION_TOKEN_LENGTH = 32
    PYSESSID_LENGTH: int = 32
    DEFAULT_AGE = timedelta(days=7)
    EXTENDED_AGE = timedelta(days = 90)

    EMAIL_TOKEN_AGE = timedelta(days=1)
    PASSWORD_TOKEN_AGE = timedelta(hours=1)

    session_repo: SessionRepository
    token_repo: TokenRepository

    user_service: UserService

    email_service: type[EmailService]
    templating_service: type[TemplatingService]
    pw_service: type[PasswordService]
    crypto_service: type[CryptoService]

    def __init__(
        self,
        session_repo: SessionRepository,
        token_repo: TokenRepository,
        user_service: UserService,
        email_service: type[EmailService],
        templating_service: type[TemplatingService],
        pw_service: type[PasswordService],
        crypto_service: type[CryptoService]
    ):
        self.session_repo = session_repo
        self.token_repo = token_repo
        self.user_service = user_service
        self.email_service = email_service
        self.templating_service = templating_service
        self.pw_service = pw_service
        self.crypto_service = crypto_service

    def authenticate(self, email: str, password: str, ip_address: str, user_agent: str, remember_me: bool) -> str | None:        
        user = self.user_service.get_by_email(email)

        if user is None:
            print('No user with this email')
            return None

        if not self.pw_service.compare(user.password, password):
            print('Passwords do not match')
            return None
        
        pysessid = secrets.token_hex(self.PYSESSID_LENGTH)
        now = datetime.now(timezone.utc)
        exp = now + (self.EXTENDED_AGE if remember_me else self.DEFAULT_AGE)

        session = Session(
            id=self.crypto_service.sha256hash(pysessid),
            uid=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            issued_at=now,
            expires_at=exp
        )

        self.session_repo.save(session)

        return pysessid
    
    def create_email_verification(self, user: User):
        token = secrets.token_urlsafe(self.VERIFICATION_TOKEN_LENGTH)

        now = datetime.now(timezone.utc)

        self.token_repo.save(Token(
            token_hash=self.crypto_service.sha256hash(token),
            uid=user.id,
            issued_at=now,
            expires_at=now + self.PASSWORD_TOKEN_AGE
        ))
        
        url = f"{settings.frontend_url}/auth/password/verify?token={token}"

        html = self.templating_service.render('reset-password.html.j2').using({
            'first_name': user.first_name,
            'url': url,
            'expires_in': Duration.readable(self.PASSWORD_TOKEN_AGE)
        })

        self.email_service.send_html(user.email, 'Verify your email address', html)

    def verify_token(self, token: str, consume: bool = False) -> Token | None:
        token_hash = self.crypto_service.sha256hash(token)

        saved_token = self.token_repo.get_by('token_hash', token_hash)

        if not saved_token:
            return None
        
        now = datetime.now(timezone.utc)

        if saved_token.used_at is not None or saved_token.expires_at <= now:
            return None
        
        if consume:
            saved_token.used_at = now
            self.token_repo.save(saved_token)

        return saved_token

    def update_password(self, uid: int, password: str) -> None:
        password_hash = self.pw_service.hash(password)

        user = self.user_service.get_by_id(uid)

        if not user:
            return
        
        user.password = password_hash
        self.user_service.update(user)


    def get_session(self, pysessid: str) -> Session | None:
        return self.session_repo.get_by_id(pysessid)