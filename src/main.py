"""FastAPI application entry point."""

from fastapi import FastAPI

from src.routes import base, data, users

app = FastAPI()
app.include_router(base.router)
app.include_router(users.router)
app.include_router(data.router)
