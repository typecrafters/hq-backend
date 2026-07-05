from typing import Annotated
from minio import Minio
from sqlalchemy.exc import SQLAlchemyError
from fastapi import Cookie, Depends, HTTPException
from app.config.settings import settings
from app.db.session import engine
from app.models.session import Session
from app.models.user import User
from app.repositories.token_repository import TokenRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.user_repository import UserRepository
from app.schemas.current import Current
from app.services.auth_service import AuthService
from app.services.crypto_service import CryptoService
from app.services.email_service import EmailService
from app.services.password_service import PasswordService
from app.services.user_service import UserService


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

def get_token_repository(db: RequiresDBSession) -> TokenRepository:
    return TokenRepository(db)

def get_role_repository(db: RequiresDBSession) -> RoleRepository:
    return RoleRepository(db)

RequiresRoleRepository = Annotated[RoleRepository, Depends(get_role_repository)]

RequiresTokenRepository = Annotated[TokenRepository, Depends(get_token_repository)]

def get_user_service(
    user_repo: RequiresUserRepository,
    role_repo: RequiresRoleRepository,
    pw_service: RequiresPasswordService
) -> UserService:
    return UserService(user_repo, role_repo, pw_service)

RequiresUserService = Annotated[UserService, Depends(get_user_service)]

def get_auth_service(
    user_repo: RequiresUserRepository,
    session_repo: RequiresSessionRepository,
    token_repo: RequiresTokenRepository,
    pw_service: RequiresPasswordService,
    crypto_service: RequiresCryptoService,
    email_service: RequiresEmailService,
) -> AuthService:
    return AuthService(user_repo, session_repo, token_repo, pw_service, crypto_service, email_service)

RequiresAuthService = Annotated[AuthService, Depends(get_auth_service)]


def get_current_user(auth_service: RequiresAuthService, user_service: RequiresUserService, pysessid: Annotated[str | None, Cookie()] = None):
    unauthorized = HTTPException(401, "Unauthorized.")

    if pysessid is None:
        raise unauthorized
    
    session = auth_service.get_session(pysessid)

    if session is None:
        raise unauthorized
    
    user = user_service.get_by_id(session.uid)

    if user is None:
        raise unauthorized
    
    return Current(session=session, user=user)


RequiresAuthentication = Annotated[User | None, Depends(get_current_user)]