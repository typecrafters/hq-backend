from fastapi import APIRouter
from app.api.v1 import users

v1_router = APIRouter('v1')

v1_router.include_router(users.router)