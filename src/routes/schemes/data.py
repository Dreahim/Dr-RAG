"""Request fields for processing an uploaded file."""

from typing import Self

from pydantic import BaseModel, Field, model_validator


class ProcessRequest(BaseModel):
    """Select assets and configure splitting and project-wide reset."""

    file_id: str | None = Field(default=None, pattern=r"^[0-9a-fA-F]{24}$")
    chunk_size: int = Field(default=100, gt=0)
    overlap_size: int = Field(default=20, ge=0)
    do_reset: int = Field(default=0, ge=0, le=1)

    @model_validator(mode="after")
    def validate_overlap(self) -> Self:
        """Reject invalid splitting settings before any database changes."""
        if self.overlap_size >= self.chunk_size:
            raise ValueError("overlap_size must be smaller than chunk_size")
        return self
