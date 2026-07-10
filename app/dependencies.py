from typing import Annotated
from fastapi import Cookie, Depends, HTTPException
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
from app.schemas.current import Current
from app.schemas.response.session import Session as AppSession
from app.services.auth_service import AuthService
from app.services.message_service import MessageService
from app.services.static.crypto_service import CryptoService
from app.services.static.email_service import EmailService
from app.services.static.file_service import FileService
from app.services.static.password_service import PasswordService
from app.services.static.templating_service import TemplatingService
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

RequiresEmailService = Annotated[type[EmailService], Depends(email_service)]

def file_service() -> type[FileService]:
    return FileService

RequiresFileService = Annotated[FileService, Depends(file_service)]

def password_service() -> type[PasswordService]:
    return PasswordService

RequiresPasswordService = Annotated[PasswordService, Depends(password_service)]

def templating_service() -> type[TemplatingService]:
    return TemplatingService

RequiresTemplatingService = Annotated[type[TemplatingService], Depends(templating_service)]


# Services

def get_user_service(user_repo: RequiresUserRepository, role_repo: RequiresRoleRepository) -> UserService:
    return UserService(user_repo, role_repo)

RequiresUserService = Annotated[UserService, Depends(get_user_service)]

def get_auth_service(
    session_repo: RequiresSessionRepository, 
    user_service: RequiresUserService, 
    pw_service: RequiresPasswordService,
    crypto_service: RequiresCryptoService
) -> AuthService:
    return AuthService(
        session_repo, 
        user_service, 
        pw_service,
        crypto_service
    )

RequiresAuthService = Annotated[AuthService, Depends(get_auth_service)]

def get_message_service(
    msg_repo: RequiresMessageRepository,
    email_service: RequiresEmailService,
    templating_service: RequiresTemplatingService
) -> MessageService:
    return MessageService(msg_repo, email_service, templating_service)

RequiresMessageService = Annotated[MessageService, Depends(get_message_service)]


# Session 
def get_current(session_repo: RequiresSessionRepository, user_service: RequiresUserService, crypto_service: RequiresCryptoService, pysessid: str | None = Cookie(default=None)) -> Current:
    unauthorized = HTTPException(401, 'Unauthorized.')

    if not pysessid:
        raise unauthorized
    
    sessid_hash = crypto_service.sha256hash(pysessid)

    session = session_repo.get_by_id(sessid_hash)

    if not session:
        raise unauthorized
    
    user = user_service.load_by_id(session.uid)

    if user is None:
        raise unauthorized
    
    return Current(session=AppSession.model_validate(session), user=user)


RequiresAuth = Annotated[Current, Depends(get_current)]
    
