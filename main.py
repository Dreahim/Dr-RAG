from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI

from routes import base, users

load_dotenv(Path(__file__).with_name(".env"))

app = FastAPI()
app.include_router(base.router)
app.include_router(users.router)
