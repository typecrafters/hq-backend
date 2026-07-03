from typing import Annotated
from minio import Minio
from sqlalchemy.exc import SQLAlchemyError
from fastapi import Depends
from app.config.settings import settings
from app.db.session import engine
from app.models.session import Session
from app.repositories.password_reset_token_repository import PasswordResetTokenRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.crypto_service import CryptoService
from app.services.email_service import EmailService
from app.services.password_service import PasswordService


def get_s3_client() -> Minio:
    return Minio(
        settings.s3_endpoint,
        access_key=settings.s3_access_key,
        secret_key=settings.s3_secret_key,
        secure=settings.s3_secure
    )

RequiresS3 = Annotated[Minio, Depends(get_s3_client)]


def password_service() -> type[PasswordService]:
    return PasswordService

RequiresPasswordService = Annotated[type[PasswordService], Depends(password_service)]


def crypto_service() -> type[CryptoService]:
    return CryptoService

RequiresCryptoService = Annotated[type[PasswordService], Depends(crypto_service)]

def email_service() -> type[EmailService]:
    return EmailService

RequiresEmailService = Annotated[type[EmailService], Depends(email_service)]

def get_db_session():
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            print(e)
            session.rollback()

RequiresDBSession = Annotated[Session, Depends(get_db_session)]

def get_user_repository(db: RequiresDBSession) -> UserRepository:
    return UserRepository(db)

RequiresUserRepository = Annotated[UserRepository, Depends(get_user_repository)]

def get_session_repository(db: RequiresDBSession) -> SessionRepository:
    return SessionRepository(db)

RequiresSessionRepository = Annotated[SessionRepository, Depends(get_session_repository)]

def get_password_reset_token_repository(db: RequiresDBSession) -> PasswordResetTokenRepository:
    return PasswordResetTokenRepository(db)

RequiresPasswordResetTokenRepository = Annotated[PasswordResetTokenRepository, Depends(get_password_reset_token_repository)]

def get_auth_service(
    user_repo: RequiresUserRepository,
    session_repo: RequiresSessionRepository,
    reset_token_repo: RequiresPasswordResetTokenRepository,
    pw_service: RequiresPasswordService,
    crypto_service: RequiresCryptoService,
    email_service: RequiresEmailService,
) -> AuthService:
    return AuthService(user_repo, session_repo, reset_token_repo, pw_service, crypto_service, email_service)

RequiresAuthService = Annotated[AuthService, Depends(get_auth_service)]