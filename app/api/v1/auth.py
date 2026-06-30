from fastapi import APIRouter
from app.schemas.request.create_user import CreateUser

router = APIRouter(prefix='auth')


@router.post('/login')
def authenticate_user(user: CreateUser):
    pass

@router.post('/password/forgot')
def authenticate_user(user: CreateUser):
    pass