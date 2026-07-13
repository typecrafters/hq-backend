from typing import Annotated

import jwt as pyjwt
from fastapi import Depends, Header, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import engine
from app.repositories.message_repository import MessageRepository
from app.repositories.post_repository import PostRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.token_repository import TokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.current_user import CurrentUser
from app.services.auth_service import AuthService
from app.services.static.crypto_service import CryptoService
from app.services.static.email_service import EmailService
from app.services.static.file_service import FileService
from app.services.static.jwt_service import JwtService
from app.services.static.password_service import PasswordService
from app.services.user_service import UserService

# Database session

def get_db_session():
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            print(e)
            session.rollback()
            raise

RequiresDBSession = Annotated[Session, Depends(get_db_session)]

# Repositories

def get_message_repository(db: RequiresDBSession) -> MessageRepository:
    return MessageRepository(db=db)

RequiresMessageRepository = Annotated[MessageRepository, Depends(get_message_repository)]

def get_post_repository(db: RequiresDBSession) -> PostRepository:
    return PostRepository(db=db)

RequiresPostRepository = Annotated[PostRepository, Depends(get_post_repository)]

def get_project_repository(db: RequiresDBSession) -> ProjectRepository:
    return ProjectRepository(db=db)

RequiresProjectRepository = Annotated[ProjectRepository, Depends(get_project_repository)]

def get_role_repository(db: RequiresDBSession) -> RoleRepository:
    return RoleRepository(db=db)

RequiresRoleRepository = Annotated[RoleRepository, Depends(get_role_repository)]

def get_token_repository(db: RequiresDBSession) -> TokenRepository:
    return TokenRepository(db=db)

RequiresTokenRepository = Annotated[TokenRepository, Depends(get_token_repository)]

def get_user_repository(db: RequiresDBSession) -> UserRepository:
    return UserRepository(db=db)

RequiresUserRepository = Annotated[UserRepository, Depends(get_user_repository)]


def get_session_repository(db: RequiresDBSession) -> SessionRepository:
    return SessionRepository(db=db)

RequiresSessionRepository = Annotated[SessionRepository, Depends(get_session_repository)]

# Static services
def crypto_service() -> type[CryptoService]:
    return CryptoService

RequiresCryptoService = Annotated[CryptoService, Depends(crypto_service)]

def email_service() -> type[EmailService]:
    return EmailService

RequiresEmailService = Annotated[EmailService, Depends(email_service)]

def file_service() -> type[FileService]:
    return FileService

RequiresFileService = Annotated[FileService, Depends(file_service)]

def password_service() -> type[PasswordService]:
    return PasswordService

RequiresPasswordService = Annotated[PasswordService, Depends(password_service)]

def jwt_service() -> type[JwtService]:
    return JwtService

RequiresJwtService = Annotated[JwtService, Depends(jwt_service)]


# Services

def get_user_service(user_repo: RequiresUserRepository, role_repo: RequiresRoleRepository) -> UserService:
    return UserService(user_repo, role_repo)

RequiresUserService = Annotated[UserService, Depends(get_user_service)]

def get_auth_service(
    session_repo: RequiresSessionRepository,
    user_service: RequiresUserService,
    pw_service: RequiresPasswordService,
    crypto_service: RequiresCryptoService,
    jwt_service: RequiresJwtService,
) -> AuthService:
    return AuthService(
        session_repo,
        user_service,
        pw_service,
        crypto_service,
        jwt_service,
    )

RequiresAuthService = Annotated[AuthService, Depends(get_auth_service)]


# JWT Bearer auth

def get_current_user(
    authorization: str | None = Header(default=None),
) -> CurrentUser:
    """Return the authenticated user extracted from a Bearer JWT token.

    The ``sub`` claim (RFC 7519) is stored as a string by ``JwtService.encode``
    but ``CurrentUser.id`` is ``int`` — this function converts via ``int()``.
    """
    unauthorized = HTTPException(status_code=401, detail="Unauthorized.")

    if not authorization:
        raise unauthorized

    try:
        scheme, token = authorization.split(" ", 1)
        if scheme.lower() != "bearer":
            raise unauthorized

        payload = JwtService.decode(token)

        return CurrentUser(
            id=int(payload["sub"]),
            email=payload.get("email"),
            permissions=payload.get("permissions", []),
        )
    except (ValueError, pyjwt.PyJWTError, KeyError, TypeError):
        raise unauthorized


RequiresCurrentUser = Annotated[CurrentUser, Depends(get_current_user)]
    
