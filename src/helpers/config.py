"""Environment-backed application settings."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Configuration for the API and local file storage."""

    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", extra="ignore")

    APP_NAME: str = "Dr-RAG"
    APP_VERSION: str = "0.1.0"
    OPENAI_API_KEY: str = ""
    FILE_ALLOWED_TYPES: str = "text/plain,application/pdf"
    FILE_MAX_SIZE_MB: int = Field(default=10, gt=0)
    FILE_DEFAULT_CHUNK_SIZE: int = Field(default=512000, gt=0)
    FILE_STORAGE_DIR: Path = PROJECT_ROOT / "src" / "assets" / "files"
    MONGODB_URL: str = Field(min_length=1, repr=False)
    MONGODB_DB_NAME: str = Field(default="dr-rag", pattern=r"^[A-Za-z0-9_-]+$")

    @property
    def allowed_file_types(self) -> frozenset[str]:
        """Return the exact media types accepted by the upload route."""
        return frozenset(
            item.strip().lower()
            for item in self.FILE_ALLOWED_TYPES.split(",")
            if item.strip()
        )

    @property
    def max_file_size_bytes(self) -> int:
        """Return the configured upload limit in bytes."""
        return self.FILE_MAX_SIZE_MB * 1024 * 1024


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load settings once for use by FastAPI dependencies."""
    return Settings()
