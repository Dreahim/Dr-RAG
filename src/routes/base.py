"""Application information endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends

from src.helpers.config import Settings, get_settings

router = APIRouter(prefix="/api/v1", tags=["api_v1"])


@router.get("/")
async def welcome(
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict[str, str]:
    """Return basic application information."""
    return {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
    }
