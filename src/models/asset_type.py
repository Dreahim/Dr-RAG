"""Asset types stored in the project catalog."""

from enum import Enum


class AssetTypeEnum(str, Enum):
    """Identify the kinds of registered project assets."""

    FILE = "file"
