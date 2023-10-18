from typing import List

from sqlalchemy import select, delete, update, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from exceptions.database_exception import DatabaseIntegrityException
from models import db_models as model
from utils import database


class AccessRolesDAO:
    def __init__(self):
        self.db = database.SessionLocal()

    async def get_all(self) -> List[model.AccessRoles]:
        """Fetch all access roles."""
        async with self.db:
            result = await self.db.execute(select(model.AccessRoles))
            return result.scalars().all()

    async def get_access_roles_by_ids(self, ids: List[int]) -> List[model.AccessRoles]:
        """Fetch all access roles by ids."""
        async with self.db:
            result = await self.db.execute(select(model.AccessRoles).where(model.AccessRoles.id.in_(ids)))
            return result.scalars().all()

    async def get_by_id(self, access_role_id: int) -> model.AccessRoles:
        """Fetch a specific access role by its ID."""
        async with self.db:
            result = await self.db.execute(select(model.AccessRoles).where(model.AccessRoles.id == access_role_id))
            return result.scalars().first()

    async def create(self, access_role_data) -> model.AccessRoles:
        """Create a new access role."""
        access_role = model.AccessRoles(**access_role_data)
        try:
            async with self.db:
                self.db.add(access_role)
                await self.db.commit()
                return access_role
        except IntegrityError:
            await self.db.rollback()
            raise DatabaseIntegrityException("Access Role with that name or email already exists.")

    async def update(self, access_role_id: int, updated_data) -> model.AccessRoles:
        """Update an existing access role."""
        async with self.db:
            await self.db.execute(update(model.AccessRoles).where(model.AccessRoles.id == access_role_id)
                                  .values(**updated_data))
            await self.db.commit()

        return await self.get_by_id(access_role_id)

    async def delete(self, access_role_id: int):
        """Delete an access role."""
        await self.delete_all_members_for_role(access_role_id)
        async with self.db:
            await self.db.execute(delete(model.AccessRoles).where(model.AccessRoles.id == access_role_id))
            await self.db.commit()

    async def delete_all_members_for_role(self, access_role_id: int):
        """Delete all members associated with a specific role."""
        async with self.db:
            await self.db.execute(delete(model.AccessRoleMembers)
                                  .where(model.AccessRoleMembers.role_id == access_role_id))
            await self.db.commit()

    async def add_members_to_role(self, access_role_id: int, user_ids: List[int]):
        """Add a list of members to a specific role."""
        members = [model.AccessRoleMembers(user_id=user_id, role_id=access_role_id) for user_id in user_ids]
        try:
            async with self.db:
                self.db.add_all(members)
                await self.db.commit()
        except IntegrityError as e:
            if "access_role_members_user_id_fkey" in str(e):
                raise DatabaseIntegrityException("Some of the provided users does not exist.")
            raise

    async def delete_members_from_role(self, access_role_id: int, user_id: int):
        """Delete a specific member from a specific role."""
        async with self.db:
            await self.db.execute(delete(model.AccessRoleMembers)
                                  .where(model.AccessRoleMembers.role_id == access_role_id)
                                  .where(model.AccessRoleMembers.user_id == user_id))
            await self.db.commit()

    async def get_unassigned_users_for_role(self, access_role_id: int) -> List[model.Users]:
        """Fetch all users that are not assigned to a specific role."""
        async with self.db:
            stmt = (
                select(model.Users.id, model.Users.email)
                .outerjoin(
                    model.AccessRoleMembers,
                    and_(
                        model.Users.id == model.AccessRoleMembers.user_id,
                        model.AccessRoleMembers.role_id == access_role_id
                    )
                )
                .where(model.AccessRoleMembers.role_id.is_(None))
            )
            result = await self.db.execute(stmt)
            return result.fetchall()

    async def get_detailed_role_info(self, access_role_id: int) -> model.AccessRoles:
        """Fetch a specific access role along with its associated members."""
        async with self.db:
            result = await self.db.execute(
                select(model.AccessRoles)
                .options(
                    joinedload(model.AccessRoles.users).joinedload(model.AccessRoleMembers.user),
                    joinedload(model.AccessRoles.pipelines).joinedload(model.AccessRolePipelines.pipeline)
                    .joinedload(model.Pipelines.application),

                )
                .where(model.AccessRoles.id == access_role_id)
            )
            return result.scalars().first()

    async def get_unassigned_pipelines_for_role(self, access_role_id: int) -> List[model.Pipelines]:
        """Fetch all pipelines that are not assigned to a specific role."""
        async with self.db:
            stmt = (
                select(model.Pipelines.id, model.Pipelines.name)
                .outerjoin(
                    model.AccessRolePipelines,
                    and_(
                        model.Pipelines.id == model.AccessRolePipelines.pipeline_id,
                        model.AccessRolePipelines.access_role_id == access_role_id
                    )
                )
                .where(model.AccessRolePipelines.access_role_id.is_(None))
            )
            result = await self.db.execute(stmt)
            return result.fetchall()

    async def add_pipeline_to_role(self, access_role_id: int, pipeline_ids: List[int]):
        """Add a list of pipelines to a specific role."""
        pipelines = [model.AccessRolePipelines(pipeline_id=pipeline_id, access_role_id=access_role_id) for pipeline_id
                     in pipeline_ids]
        try:
            async with self.db:
                self.db.add_all(pipelines)
                await self.db.commit()
        except IntegrityError as e:
            if "access_role_pipelines_pipeline_id_fkey" in str(e):
                raise DatabaseIntegrityException("Some of the provided pipelines does not exist.")
            if "access_role_pipelines_pkey" in str(e):
                raise DatabaseIntegrityException("Some of the provided pipelines are already assigned to access role.")
            raise

    async def delete_pipeline_from_role(self, access_role_id: int, pipeline_id: int):
        """Delete a specific pipeline from a specific role."""
        async with self.db:
            await self.db.execute(delete(model.AccessRolePipelines)
                                  .where(model.AccessRolePipelines.access_role_id == access_role_id)
                                  .where(model.AccessRolePipelines.pipeline_id == pipeline_id))
            await self.db.commit()




