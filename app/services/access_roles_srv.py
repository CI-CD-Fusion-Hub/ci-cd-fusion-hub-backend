from typing import List
from fastapi import Request

from app.daos.access_roles_dao import AccessRolesDAO
from app.exceptions.access_roles_exception import AccessRoleNotFoundException
from app.schemas.access_roles_sch import AccessRoleOut, CreateAccessRole, UpdateAccessRole, AccessRoleBaseOut
from app.schemas.pipelines_sch import PipelineOut
from app.utils.enums import SessionAttributes, AccessLevel
from app.utils.logger import Logger
from app.utils.response import ok

LOGGER = Logger().start_logger()


class AccessRolesService:
    def __init__(self):
        self.access_roles_dao = AccessRolesDAO()

    async def get_all_access_roles(self, request: Request):
        user_access_level = request.session.get(SessionAttributes.USER_ACCESS_LEVEL.value)
        user_roles = request.session.get(SessionAttributes.USER_ROLES.value)

        if user_access_level != AccessLevel.ADMIN.value:
            LOGGER.info("Fetching access roles based on user roles for non-admin user.")
            access_roles = await self.access_roles_dao.get_access_roles_by_ids(user_roles)
        else:
            LOGGER.info("Fetching all access roles for admin user.")
            access_roles = await self.access_roles_dao.get_all()

        if not access_roles:
            LOGGER.warning("No access roles found.")

        return ok(
            message="Successfully provided all access_roles.",
            data=[AccessRoleBaseOut.model_validate(access_role.as_dict()) for access_role in access_roles]
        )

    async def get_access_roles_by_id(self, request: Request, access_role_id: int):
        user_access_level = request.session.get(SessionAttributes.USER_ACCESS_LEVEL.value)
        user_roles = request.session.get(SessionAttributes.USER_ROLES.value)

        if user_access_level != AccessLevel.ADMIN.value and access_role_id not in user_roles:
            LOGGER.warning(f"Non-admin user with insufficient rights attempted to access role ID {access_role_id}.")
            raise AccessRoleNotFoundException(f"Access role with ID {access_role_id} does not exist.")

        access_role = await self.access_roles_dao.get_detailed_role_info(access_role_id)
        if not access_role:
            LOGGER.warning(f"Access role with ID {access_role_id} not found.")
            raise AccessRoleNotFoundException(f"Access role with ID {access_role_id} does not exist.")

        role_data = AccessRoleOut.model_validate(access_role.as_dict())
        role_data.members = [member.user.as_dict() for member in access_role.users]
        role_data.pipelines = [PipelineOut.model_validate(pipeline.pipeline.as_dict())
                               for pipeline in access_role.pipelines]

        LOGGER.info(f"Access role details for ID {access_role_id} successfully retrieved.")
        return ok(message="Successfully provided access role.", data=role_data)

    async def create_access_role(self, access_role_data: CreateAccessRole):
        access_role = await self.access_roles_dao.create(access_role_data.model_dump())
        LOGGER.info("Successfully created a new access role.")

        return ok(message="Successfully created access role.",
                  data=AccessRoleOut.model_validate(access_role.as_dict()))

    async def update_access_role(self, access_role_id: int, access_role_data: UpdateAccessRole):
        access_role = await self.access_roles_dao.get_by_id(access_role_id)
        if not access_role:
            LOGGER.warning(f"Attempted to update a non-existent access role with ID {access_role_id}.")
            raise AccessRoleNotFoundException(f"Access role with ID {access_role_id} does not exist.")

        data_to_update = access_role_data.model_dump()
        data_to_update = {k: v for k, v in data_to_update.items() if v is not None}

        access_role = await self.access_roles_dao.update(access_role_id, data_to_update)

        LOGGER.info(f"Access role with ID {access_role_id} successfully updated.")
        return ok(message="Successfully updated access role.", data=AccessRoleOut.model_validate(access_role.as_dict()))

    async def delete_access_role(self, access_role_id: int):
        if not await self.access_roles_dao.get_by_id(access_role_id):
            LOGGER.warning(f"Attempted to delete a non-existent access role with ID {access_role_id}.")
            raise AccessRoleNotFoundException(f"Access role with ID {access_role_id} does not exist.")
        await self.access_roles_dao.delete(access_role_id)
        LOGGER.info(f"Access role with ID {access_role_id} has been successfully deleted.")

        return ok(message="Access role has been successfully deleted.")

    async def get_unassigned_users_for_role(self, access_role_id: int):
        unassigned_users = await self.access_roles_dao.get_unassigned_users_for_role(access_role_id)
        if not unassigned_users:
            LOGGER.info(f"No unassigned users found for access role ID {access_role_id}.")

        return ok(message="Successfully provided unassigned users for access role.",
                  data=[{"id": user.id, "email": user.email} for user in unassigned_users])

    async def add_members_to_role(self, access_role_id: int, user_ids: List[int]):
        await self.access_roles_dao.add_members_to_role(access_role_id, user_ids)
        LOGGER.info(f"Added {len(user_ids)} members to access role with ID {access_role_id}.")

        return ok(message="Successfully added members to access role.")

    async def delete_members_from_role(self, access_role_id: int, user_id: int):
        await self.access_roles_dao.delete_members_from_role(access_role_id, user_id)
        LOGGER.info(f"Successfully deleted user ID {user_id} from access role ID {access_role_id}.")

        return ok(message="Successfully deleted member from access role.")

    async def get_unassigned_pipelines_for_role(self, access_role_id: int):
        unassigned_pipelines = await self.access_roles_dao.get_unassigned_pipelines_for_role(access_role_id)
        if not unassigned_pipelines:
            LOGGER.info(f"No unassigned pipelines found for access role ID {access_role_id}.")

        return ok(message="Successfully provided unassigned pipelines for access role.",
                  data=[{"id": pipeline.id, "name": pipeline.name} for pipeline in unassigned_pipelines])

    async def add_pipeline_to_role(self, access_role_id: int, pipeline_ids: List[int]):
        await self.access_roles_dao.add_pipeline_to_role(access_role_id, pipeline_ids)
        LOGGER.info(f"Successfully added {len(pipeline_ids)} pipelines to access role ID {access_role_id}.")

        return ok(message="Successfully added pipelines to access role.")

    async def delete_pipeline_from_role(self, access_role_id: int, pipeline_id: int):
        await self.access_roles_dao.delete_pipeline_from_role(access_role_id, pipeline_id)
        LOGGER.info(f"Successfully deleted pipeline ID {pipeline_id} from access role ID {access_role_id}.")

        return ok(message="Successfully deleted pipeline from access role.")
