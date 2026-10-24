"""Project document and its unique public identifier."""

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field


class Project(BaseModel):
    """Identify a project independently of its MongoDB ID."""

    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)

    id: ObjectId | None = Field(default=None, alias="_id")
    project_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]*$")

    @classmethod
    def get_indexes(cls) -> list[dict]:
        """Prevent duplicate public project identifiers."""
        return [
            {
                "key": [("project_id", 1)],
                "name": "project_id_index_1",
                "unique": True,
            }
        ]
