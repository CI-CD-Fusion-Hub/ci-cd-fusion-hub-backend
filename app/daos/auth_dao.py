from sqlalchemy import select, delete, update
from sqlalchemy.exc import IntegrityError

from app.models import db_models as model
from app.schemas.auth_sch import CreateAuthMethod
from app.utils import database


class AuthDAO:
    def __init__(self):
        self.db = database.SessionLocal()

    async def get_all(self) -> model.Auth:
        """Fetch all auth methods."""
        async with self.db:
            result = await self.db.execute(select(model.Auth))
            return result.scalars().first()

    async def get_by_id(self, auth_id: int) -> model.Auth:
        """Fetch a specific auth method by its ID."""
        async with self.db:
            result = await self.db.execute(select(model.Auth).where(model.Auth.id == auth_id))
            return result.scalars().first()

    async def create(self, auth_data: CreateAuthMethod) -> model.Auth:
        """Create an auth method."""
        auth = model.Auth(
            type=auth_data.type,
            properties=auth_data.properties
        )
        try:
            async with self.db:
                self.db.add(auth)
                await self.db.commit()
                return auth
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Auth method with that type already exists.")

    async def update(self, auth_id: int, auth_data) -> model.Auth:
        """Update an existing auth method."""
        async with self.db:
            await self.db.execute(update(model.Auth).where(model.Auth.id == auth_id).values(**auth_data))
            await self.db.commit()

        return await self.get_by_id(auth_id)

    async def delete_all(self):
        """Delete all an auth method."""
        async with self.db:
            await self.db.execute(delete(model.Auth))
            await self.db.commit()
