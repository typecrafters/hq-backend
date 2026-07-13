from fastapi import APIRouter
from app.dependencies import RequiresCurrentUser, RequiresUserService
from app.schemas.current_user import CurrentUser
from app.schemas.request.create_user import CreateUser

router = APIRouter(prefix='/users')

@router.get('/')
def list_users(
    page: int,
    limit: int,
    user_service: RequiresUserService,
    current_user: RequiresCurrentUser,
):
    return user_service.list(page, limit)

@router.post('/')
def save_user(
    user: CreateUser,
    user_service: RequiresUserService,
    current_user: RequiresCurrentUser,
):
    return user_service.create(user)