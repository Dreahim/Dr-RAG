"""Request fields for processing an uploaded file."""

from pydantic import BaseModel, Field


class ProcessRequest(BaseModel):
    file_id: str = Field(min_length=1, max_length=255)
    chunk_size: int = Field(default=100, gt=0)
    overlap_size: int = Field(default=20, ge=0)
    do_research: bool = False
