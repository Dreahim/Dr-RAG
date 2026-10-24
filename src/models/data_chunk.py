"""MongoDB operations for extracted document chunks."""

from typing import Self

from bson import ObjectId
from pymongo import InsertOne
from pymongo.asynchronous.database import AsyncDatabase

from src.models.base_data import BaseDataModel
from src.models.database_enum import DatabaseEnum
from src.models.db_schemes import DataChunk


class DataChunkModel(BaseDataModel):
    """Store, retrieve, and reset a project's chunks."""

    def __init__(self, db_client: AsyncDatabase) -> None:
        super().__init__(db_client)
        self.collection = db_client[DatabaseEnum.COLLECTION_DATA_CHUNK_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: AsyncDatabase) -> Self:
        """Create a model and ensure its collection indexes."""
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self) -> None:
        """Ensure the project index on new and existing collections."""
        for index in DataChunk.get_indexes():
            await self.collection.create_index(
                index["key"], name=index["name"], unique=index["unique"]
            )

    async def create_data_chunk(self, data_chunk: DataChunk) -> DataChunk:
        """Insert one chunk and attach its database ID."""
        result = await self.collection.insert_one(
            data_chunk.model_dump(by_alias=True, exclude_none=True)
        )
        data_chunk.id = result.inserted_id
        return data_chunk

    async def get_data_chunk(self, chunk_id: str) -> DataChunk | None:
        """Find a chunk by its MongoDB ID."""
        record = await self.collection.find_one({"_id": ObjectId(chunk_id)})
        return DataChunk(**record) if record else None

    async def insert_many_chunks(
        self, data_chunks: list[DataChunk], batch_size: int = 100
    ) -> int:
        """Insert chunks in batches and report acknowledged insertions."""
        if batch_size < 1:
            raise ValueError("batch_size must be positive")
        inserted = 0
        for start in range(0, len(data_chunks), batch_size):
            batch = data_chunks[start : start + batch_size]
            operations = [
                InsertOne(chunk.model_dump(by_alias=True, exclude_none=True))
                for chunk in batch
            ]
            result = await self.collection.bulk_write(operations)
            inserted += result.inserted_count
        return inserted

    async def delete_chunks_by_project_id(self, project_id: ObjectId) -> int:
        """Delete every chunk belonging to the selected project."""
        result = await self.collection.delete_many({"chunk_project_id": project_id})
        return result.deleted_count
