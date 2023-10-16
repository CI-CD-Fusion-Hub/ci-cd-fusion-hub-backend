from typing import List

from sqlalchemy import select, delete, update, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

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

    async def get_by_email(self, email: str) -> model.Users:
        """Fetch a specific user by its Email."""
        async with self.db:
            result = await self.db.execute(select(model.Users).where(model.Users.email == email))
            return result.scalars().first()

    async def get_detailed_user_info(self, user_id: int):
        """Fetch a user with their roles and pipeline access."""
        async with self.db:
            stmt = (
                select(model.Users)
                .options(
                    joinedload(model.Users.roles)
                    .joinedload(model.AccessRoleMembers.role)
                    .joinedload(model.AccessRoles.pipelines)
                    .joinedload(model.AccessRolePipelines.pipeline)
                )
                .where(model.Users.id == user_id)
            )
            result = await self.db.execute(stmt)
            return result.scalars().first()

    async def create(self, user_data) -> model.Users:
        """Create a new user."""
        user = model.Users(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            password=user_data.password,
            status=user_data.status
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

    async def get_user_unassigned_roles(self, user_id: int):
        """Fetch all roles that are not assigned to a specific user."""
        async with self.db:
            stmt = (
                select(model.AccessRoles)
                .outerjoin(
                    model.AccessRoleMembers,
                    and_(
                        model.AccessRoles.id == model.AccessRoleMembers.role_id,
                        model.AccessRoleMembers.user_id == user_id
                    )
                )
                .where(model.AccessRoleMembers.user_id.is_(None))
            )
            result = await self.db.execute(stmt)
            return result.scalars().all()
