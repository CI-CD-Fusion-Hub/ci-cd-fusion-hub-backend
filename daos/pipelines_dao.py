from typing import List

from sqlalchemy import select, delete, update
from sqlalchemy.exc import IntegrityError

from exceptions.database_exception import DatabaseIntegrityException
from models import db_models as model

from utils import database


class PipelineDAO:
    def __init__(self):
        self.db = database.SessionLocal()

    async def get_all(self) -> List[model.Pipelines]:
        """Fetch all pipelines."""
        async with self.db:
            result = await self.db.execute(select(model.Pipelines))
            return result.scalars().all()

    async def get_by_application_type(self, app_type: str) -> List[model.Pipelines]:
        """Fetch all pipelines for a specific application type."""
        async with self.db:
            result = await self.db.execute(
                select(model.Pipelines).join(model.Applications).where(model.Applications.type == app_type)
            )
            return result.scalars().all()

    async def get_pipelines_by_ids(self, pipeline_ids: List[int]):
        """Fetch all pipelines by ids."""
        async with self.db:
            result = await self.db.execute(select(model.Pipelines).where(model.Pipelines.id.in_(pipeline_ids)))
            return result.scalars().all()

    async def get_by_id(self, pipeline_id: int) -> model.Pipelines:
        """Fetch a specific pipeline by its ID."""
        async with self.db:
            result = await self.db.execute(select(model.Pipelines).where(model.Pipelines.id == pipeline_id))
            return result.scalars().first()

    async def create(self, pipeline_data) -> model.Pipelines:
        """Create a new pipeline."""
        pipeline = model.Pipelines(**pipeline_data)
        try:
            async with self.db:
                self.db.add(pipeline)
                await self.db.commit()
                return pipeline
        except IntegrityError:
            await self.db.rollback()
            raise DatabaseIntegrityException("Pipeline with that name already exists.")

    async def create_bulk(self, pipelines_data: List[dict]) -> List[model.Pipelines]:
        """Create multiple pipelines."""
        pipelines = [model.Pipelines(**data) for data in pipelines_data]
        try:
            async with self.db:
                self.db.add_all(pipelines)
                await self.db.commit()
                return pipelines
        except IntegrityError:
            await self.db.rollback()
            raise DatabaseIntegrityException("One or more pipelines have conflicting data.")

    async def update(self, pipeline_id: int, updated_data):
        """Update an existing pipeline."""
        async with self.db:
            await self.db.execute(update(model.Pipelines).where(model.Pipelines.id == pipeline_id)
                                  .values(**updated_data))
            await self.db.commit()

    async def delete(self, pipeline_id: int):
        """Delete a pipeline."""
        async with self.db:
            await self.db.execute(delete(model.Pipelines).where(model.Pipelines.id == pipeline_id))
            await self.db.commit()
