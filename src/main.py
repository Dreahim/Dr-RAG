"""FastAPI application entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pymongo import AsyncMongoClient

from src.helpers.config import get_settings
from src.models.asset import AssetModel
from src.models.data_chunk import DataChunkModel
from src.models.project import ProjectModel
from src.routes import base, data


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Verify the database, ensure indexes, and close the shared client."""
    settings = get_settings()
    client = AsyncMongoClient(
        settings.MONGODB_URL,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        tz_aware=True,
    )
    try:
        await client.admin.command("ping")
        app.state.db_client = client[settings.MONGODB_DB_NAME]
        await ProjectModel.create_instance(app.state.db_client)
        await AssetModel.create_instance(app.state.db_client)
        await DataChunkModel.create_instance(app.state.db_client)
        yield
    finally:
        await client.close()


app = FastAPI(lifespan=lifespan)
app.include_router(base.router)
app.include_router(data.router)
