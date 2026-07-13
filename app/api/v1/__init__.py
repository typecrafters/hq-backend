from fastapi import APIRouter
from app.api.v1 import auth, uploads, users, messages

router = APIRouter(prefix='/v1')

router.include_router(auth.router)
router.include_router(uploads.router)
router.include_router(users.router)
router.include_router(messages.router)