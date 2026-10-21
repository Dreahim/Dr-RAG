"""Shared controller configuration."""

from uuid import uuid4

from src.helpers.config import Settings


class BaseController:
    """Keep the application settings shared across file controllers."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.files_dir = settings.FILE_STORAGE_DIR

    @staticmethod
    def get_unique_string(length: int = 12) -> str:
        """Return a short random prefix for a stored filename."""
        return uuid4().hex[:length]
