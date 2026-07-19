import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import api
from app.config.settings import settings
from app.db.session import create_db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list(),
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods_list(),
    allow_headers=settings.cors_headers_list(),
)

app.include_router(api.router)

if __name__ == "__main__":
    create_db()
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)