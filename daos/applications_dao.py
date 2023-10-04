from typing import List

from sqlalchemy import select, delete, update
from sqlalchemy.exc import IntegrityError

from exceptions.database_exception import DatabaseIntegrityException
from models import db_models as model

from utils import database


class ApplicationDAO:
    def __init__(self):
        self.db = database.SessionLocal()

    async def get_all(self) -> List[model.Applications]:
        """Fetch all applications."""
        async with self.db:
            result = await self.db.execute(select(model.Applications))
            return result.scalars().all()

    async def get_by_id(self, application_id: int) -> model.Applications:
        """Fetch a specific application by its ID."""
        async with self.db:
            result = await self.db.execute(select(model.Applications).where(model.Applications.id == application_id))
            return result.scalars().first()

    async def create(self, app_data) -> model.Applications:
        """Create a new application."""
        application = model.Applications(**app_data)
        try:
            async with self.db:
                self.db.add(application)
                await self.db.commit()
                return application
        except IntegrityError:
            await self.db.rollback()
            raise DatabaseIntegrityException("Application with that name already exists.")

    async def update(self, application_id: int, updated_data) -> model.Applications:
        """Update an existing application."""
        async with self.db:
            await self.db.execute(update(model.Applications).where(model.Applications.id == application_id)
                                  .values(**updated_data))
            await self.db.commit()

        return await self.get_by_id(application_id)

    async def delete(self, application_id: int):
        """Delete an application."""
        async with self.db:
            await self.db.execute(delete(model.Applications).where(model.Applications.id == application_id))
            await self.db.commit()
