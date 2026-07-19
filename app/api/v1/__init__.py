from fastapi import APIRouter
from app.api.v1 import auth, messages, projects, roles, uploads, users

router = APIRouter(prefix='/v1')

router.include_router(auth.router)
router.include_router(messages.router)
router.include_router(projects.router)
router.include_router(roles.router)
router.include_router(uploads.router)
router.include_router(users.router)