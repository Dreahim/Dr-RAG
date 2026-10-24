"""MongoDB operations for projects."""

from typing import Self

from pymongo import ReturnDocument
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.errors import DuplicateKeyError

from src.models.base_data import BaseDataModel
from src.models.database_enum import DatabaseEnum
from src.models.db_schemes import Project


class ProjectModel(BaseDataModel):
    """Create and retrieve project records."""

    def __init__(self, db_client: AsyncDatabase) -> None:
        super().__init__(db_client)
        self.collection = db_client[DatabaseEnum.COLLECTION_PROJECT_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: AsyncDatabase) -> Self:
        """Create a model and ensure its collection indexes."""
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self) -> None:
        """Ensure indexes even if the collection already exists."""
        for index in Project.get_indexes():
            await self.collection.create_index(
                index["key"], name=index["name"], unique=index["unique"]
            )

    async def create_project(self, project: Project) -> Project:
        """Insert a project and attach its database ID."""
        result = await self.collection.insert_one(
            project.model_dump(by_alias=True, exclude_none=True)
        )
        project.id = result.inserted_id
        return project

    async def get_project(self, project_id: str) -> Project | None:
        """Find an existing project without creating one."""
        record = await self.collection.find_one({"project_id": project_id})
        return Project(**record) if record else None

    async def get_project_or_create_one(self, project_id: str) -> Project:
        """Use an upsert so concurrent uploads share one project."""
        project = Project(project_id=project_id)
        try:
            record = await self.collection.find_one_and_update(
                {"project_id": project_id},
                {"$setOnInsert": project.model_dump(by_alias=True, exclude_none=True)},
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )
        except DuplicateKeyError:
            record = await self.collection.find_one({"project_id": project_id})
            if record is None:
                raise
        return Project(**record)

    async def get_all_projects(
        self, page: int = 1, page_size: int = 10
    ) -> tuple[list[Project], int]:
        """Return a stable page of projects and the total page count."""
        if page < 1 or page_size < 1:
            raise ValueError("page and page_size must be positive")
        total_documents = await self.collection.count_documents({})
        total_pages = (total_documents + page_size - 1) // page_size
        cursor = (
            self.collection.find()
            .sort("_id", 1)
            .skip((page - 1) * page_size)
            .limit(page_size)
        )
        records = await cursor.to_list(length=page_size)
        return [Project(**record) for record in records], total_pages
