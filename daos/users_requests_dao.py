from typing import List

from sqlalchemy import select, delete, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, selectinload

from exceptions.database_exception import DatabaseIntegrityException
from models import db_models as model
from schemas.users_requests_sch import CreateUsersRequest
from utils import database


class UserRequestsDAO:
    def __init__(self):
        self.db = database.SessionLocal()

    async def get_all(self) -> List[model.UserRequestsAccess]:
        """Fetch all users requests."""
        async with self.db:
            query = select(model.UserRequestsAccess).options(selectinload(model.UserRequestsAccess.pipelines))
            result = await self.db.execute(query)
            return result.scalars().all()

    async def get_detailed_users_request_info(self, users_request_id: int):
        """Fetch a user with their roles and pipeline access."""
        async with self.db:
            stmt = (
                select(model.UserRequestsAccess)
                .options(
                    joinedload(model.UserRequestsAccess.pipelines)
                    .joinedload(model.UserRequestPipelineAssociation.pipeline)
                )
                .where(model.UserRequestsAccess.id == users_request_id)
            )
            result = await self.db.execute(stmt)
            return result.scalars().first()

    async def create(self, users_request_data: CreateUsersRequest) -> model.UserRequestsAccess:
        """Create a new user."""
        user = model.UserRequestsAccess(
            user_id=users_request_data.user_id,
            message=users_request_data.message,
            status="pending"
        )
        try:
            async with self.db:
                self.db.add(user)
                await self.db.commit()
                return user
        except IntegrityError as e:
            await self.db.rollback()
            raise e

    async def add_pipelines_to_request(self, users_request_id: int, pipeline_ids):
        """Add pipelines to request."""
        request_pipelines = [
            (model.UserRequestPipelineAssociation(
                user_request_id=users_request_id,
                pipeline_id=pipeline_id
            )) for pipeline_id in pipeline_ids]
        try:
            async with self.db:
                self.db.add_all(request_pipelines)
                await self.db.commit()
                return request_pipelines
        except IntegrityError:
            await self.db.rollback()
            raise DatabaseIntegrityException("One or more pipelines have conflicting data.")

    async def get_by_id(self, users_request_id: int) -> model.UserRequestsAccess:
        """Fetch a specific user request by its ID."""
        async with self.db:
            result = await self.db.execute(select(model.UserRequestsAccess)
                                           .where(model.UserRequestsAccess.id == users_request_id))
            return result.scalars().first()

    async def update(self, users_request_id: int, data_to_update):
        """Update an existing user request."""
        async with self.db:
            await self.db.execute(update(model.UserRequestsAccess)
                                  .where(model.UserRequestsAccess.id == users_request_id).values(**data_to_update))
            await self.db.commit()

        return await self.get_by_id(users_request_id)

    async def remove_pipelines_from_request(self, user_request_id: int, pipeline_ids):
        """Remove pipelines from user request."""
        async with self.db:
            await self.db.execute(
                delete(model.UserRequestPipelineAssociation)
                .where(model.UserRequestPipelineAssociation.user_request_id == user_request_id)
                .where(model.UserRequestPipelineAssociation.pipeline_id.in_(pipeline_ids))
            )

            await self.db.commit()

    async def delete(self, users_request_id: int):
        """Delete an user request."""
        async with self.db:
            await self.db.execute(delete(model.UserRequestsAccess)
                                  .where(model.UserRequestsAccess.id == users_request_id))
            await self.db.commit()
