"""Metadata for an uploaded file."""

from datetime import UTC, datetime
from typing import Any

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field


class Asset(BaseModel):
    """Link a stored filename to its owning project."""

    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)

    id: ObjectId | None = Field(default=None, alias="_id")
    asset_project_id: ObjectId
    asset_type: str = Field(min_length=1)
    asset_name: str = Field(min_length=1)
    asset_size: int = Field(ge=0)
    asset_config: dict[str, Any] = Field(default_factory=dict)
    asset_pushed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def get_indexes(cls) -> list[dict]:
        """Support project lookup and unique filenames within a project."""
        return [
            {
                "key": [("asset_project_id", 1)],
                "name": "asset_project_id_index_1",
                "unique": False,
            },
            {
                "key": [("asset_project_id", 1), ("asset_name", 1)],
                "name": "asset_project_id_name_index_1",
                "unique": True,
            },
        ]
