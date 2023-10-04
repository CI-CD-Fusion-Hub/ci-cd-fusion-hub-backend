from typing import List

from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, delete, update
from models import db_models as model
from utils import database


class UserDAO:
    def __init__(self):
        self.db = database.SessionLocal()

    async def get_all(self) -> List[model.Users]:
        """Fetch all users."""
        async with self.db:
            result = await self.db.execute(select(model.Users))
            return result.scalars().all()

    async def get_by_id(self, user_id: int) -> model.Users:
        """Fetch a specific user by its ID."""
        async with self.db:
            result = await self.db.execute(select(model.Users).where(model.Users.id == user_id))
            return result.scalars().first()

    async def create(self, user_data) -> model.Users:
        """Create a new user."""
        user = model.Users(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            password=user_data.password,
            status="active"
        )
        try:
            async with self.db:
                self.db.add(user)
                await self.db.commit()
                return user
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("User with that name or email already exists.")

    async def update(self, user_id: int, updated_data) -> model.Users:
        """Update an existing user."""
        async with self.db:
            await self.db.execute(update(model.Users).where(model.Users.id == user_id).values(**updated_data))
            await self.db.commit()

        return await self.get_by_id(user_id)

    async def delete(self, user_id: int):
        """Delete an user."""
        async with self.db:
            await self.db.execute(delete(model.Users).where(model.Users.id == user_id))
            await self.db.commit()
