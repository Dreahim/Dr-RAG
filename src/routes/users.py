"""Placeholder users endpoint."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/users")
async def get_users() -> dict[str, str]:
    """Return the placeholder response for the users route."""
    return {"message": "Fetching all users..."}
