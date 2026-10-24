"""MongoDB collection names."""

from enum import Enum


class DatabaseEnum(str, Enum):
    """Keep collection names consistent across persistence models."""

    COLLECTION_PROJECT_NAME = "projects"
    COLLECTION_DATA_CHUNK_NAME = "chunks"
    COLLECTION_ASSET_NAME = "assets"
