from app.api.v1 import v1_router
from fastapi import FastAPI

app = FastAPI()

app.include_router(v1_router)

if __name__ == "__main__":
    # Run the applicatio using Uvicorn (An ASGI web server)
    import uvicorn

    # app.main refers to the file name (main.py) and app refers to the FastAPI instance created in that file.
    # app is the FastAPI instance that we created earlier in the code.
    # reload=True enables automatic reloading of the application when code changes are detected, which is useful during development.
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)