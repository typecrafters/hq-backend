from fastapi import APIRouter
from app.schemas.request.create_user import CreateUser

router = APIRouter(prefix='/users')

@router.get('/')
def list_users(page: int, limit: int):
    return {'page': page, 'limit': limit}

@router.post('/')
def save_user(user: CreateUser):
    pass