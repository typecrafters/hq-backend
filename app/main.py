from app.api.v1 import v1_router
from fastapi import FastAPI

app = FastAPI()

app.include_router(v1_router)