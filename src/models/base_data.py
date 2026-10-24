"""Shared database handle for persistence models."""

from pymongo.asynchronous.database import AsyncDatabase


class BaseDataModel:
    """Keep the application database available to each model."""

    def __init__(self, db_client: AsyncDatabase) -> None:
        self.db_client = db_client
