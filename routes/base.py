import os

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["api_v1"])


@router.get("/")
async def welcome() -> dict[str, str]:
    """Return basic application information."""
    return {
        "app_name": os.getenv("APP_NAME", "Dr-RAG"),
        "app_version": os.getenv("APP_VERSION", "0.1.0"),
    }
