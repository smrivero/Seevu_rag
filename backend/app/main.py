from fastapi import FastAPI

from app import health


def create_app() -> FastAPI:
    application = FastAPI()
    application.include_router(health.router)
    return application


app = create_app()
