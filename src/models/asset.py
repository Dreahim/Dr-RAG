"""MongoDB operations for uploaded file metadata."""

from typing import Self

from bson import ObjectId
from pymongo.asynchronous.database import AsyncDatabase

from src.models.base_data import BaseDataModel
from src.models.database_enum import DatabaseEnum
from src.models.db_schemes import Asset


class AssetModel(BaseDataModel):
    """Find and register files belonging to a project."""

    def __init__(self, db_client: AsyncDatabase) -> None:
        super().__init__(db_client)
        self.collection = db_client[DatabaseEnum.COLLECTION_ASSET_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: AsyncDatabase) -> Self:
        """Create a model and ensure its collection indexes."""
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self) -> None:
        """Ensure the declared indexes without depending on collection creation."""
        for index in Asset.get_indexes():
            await self.collection.create_index(
                index["key"], name=index["name"], unique=index["unique"]
            )

    async def create_asset(self, asset: Asset) -> Asset:
        """Insert metadata for a successfully stored file."""
        result = await self.collection.insert_one(
            asset.model_dump(by_alias=True, exclude_none=True)
        )
        asset.id = result.inserted_id
        return asset

    async def get_all_project_assets(
        self, asset_project_id: ObjectId, asset_type: str
    ) -> list[Asset]:
        """Return the project's registered assets in insertion order."""
        cursor = self.collection.find(
            {"asset_project_id": asset_project_id, "asset_type": asset_type}
        ).sort("_id", 1)
        records = await cursor.to_list(length=None)
        return [Asset(**record) for record in records]

    async def get_asset_record(
        self, asset_project_id: ObjectId, asset_id: str
    ) -> Asset | None:
        """Look up the upload response's ID within its owning project."""
        record = await self.collection.find_one(
            {"_id": ObjectId(asset_id), "asset_project_id": asset_project_id}
        )
        return Asset(**record) if record else None
