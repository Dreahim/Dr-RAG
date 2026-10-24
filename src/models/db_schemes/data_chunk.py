"""Extracted text and provenance for one document chunk."""

from typing import Any

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field


class DataChunk(BaseModel):
    """Store a chunk with its project, source asset, and position."""

    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)

    id: ObjectId | None = Field(default=None, alias="_id")
    chunk_text: str = Field(min_length=1)
    chunk_metadata: dict[str, Any]
    chunk_order: int = Field(ge=1)
    chunk_project_id: ObjectId
    chunk_asset_id: ObjectId

    @classmethod
    def get_indexes(cls) -> list[dict]:
        """Support project chunk lookup and reset."""
        return [
            {
                "key": [("chunk_project_id", 1)],
                "name": "chunk_project_id_index_1",
                "unique": False,
            }
        ]
