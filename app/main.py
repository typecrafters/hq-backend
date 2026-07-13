import uvicorn
from fastapi import FastAPI
from app import api
from app.db.session import create_db

app = FastAPI()

app.include_router(api.router)

if __name__ == "__main__":
    create_db()
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)