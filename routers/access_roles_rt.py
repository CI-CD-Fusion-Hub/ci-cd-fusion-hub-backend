from typing import List

from fastapi import APIRouter, Depends

from schemas.access_roles_sch import CreateAccessRole, UpdateAccessRole, AddMembersToAccessRole, AddPipelineToAccessRole
from services.access_roles_srv import AccessRolesService

router = APIRouter()


def create_access_roles_service():
    return AccessRolesService()


@router.get("/access_roles", tags=["access_roles"])
async def get_all_access_roles(access_roles_service: AccessRolesService = Depends(create_access_roles_service)):
    return await access_roles_service.get_all_access_roles()


@router.get("/access_roles/{access_role_id}", tags=["access_roles"])
async def get_access_role(access_role_id: int,
                          access_roles_service: AccessRolesService = Depends(create_access_roles_service)):
    return await access_roles_service.get_access_roles_by_id(access_role_id)


@router.post("/access_roles", tags=["access_roles"])
async def create_role(access_role_data: CreateAccessRole,
                      access_roles_service: AccessRolesService = Depends(create_access_roles_service)):
    return await access_roles_service.create_access_role(access_role_data)


@router.put("/access_roles/{access_role_id}", tags=["access_roles"])
async def update_role(access_role_id: int, access_role_data: UpdateAccessRole,
                      access_roles_service: AccessRolesService = Depends(create_access_roles_service)):
    return await access_roles_service.update_access_role(access_role_id, access_role_data)


@router.delete("/access_roles/{access_role_id}", tags=["access_roles"])
async def delete_role(access_role_id: int,
                      access_roles_service: AccessRolesService = Depends(create_access_roles_service)):
    return await access_roles_service.delete_access_role(access_role_id)


@router.get("/access_roles/{access_role_id}/unassigned_users", tags=["access_roles"])
async def get_unassigned_users_for_role(access_role_id: int, access_roles_service: AccessRolesService = Depends(
                                        create_access_roles_service)):
    return await access_roles_service.get_unassigned_users_for_role(access_role_id)


@router.post("/access_roles/{access_role_id}/users", tags=["access_roles"])
async def add_member_to_access_role(access_role_id: int, members: List[AddMembersToAccessRole],
                                    access_roles_service: AccessRolesService = Depends(create_access_roles_service)):
    return await access_roles_service.add_members_to_role(access_role_id, [member.user_id for member in members])


@router.delete("/access_roles/{access_role_id}/users/{user_id}", tags=["access_roles"])
async def delete_members_from_role(access_role_id: int, user_id: int,
                                   access_roles_service: AccessRolesService = Depends(create_access_roles_service)):
    return await access_roles_service.delete_members_from_role(access_role_id, user_id)


@router.get("/access_roles/{access_role_id}/unassigned_pipelines", tags=["access_roles"])
async def get_unassigned_pipelines_for_role(access_role_id: int, access_roles_service: AccessRolesService = Depends(
                                        create_access_roles_service)):
    return await access_roles_service.get_unassigned_pipelines_for_role(access_role_id)


@router.post("/access_roles/{access_role_id}/pipelines", tags=["access_roles"])
async def add_pipeline_to_access_role(access_role_id: int, pipelines: List[AddPipelineToAccessRole],
                                      access_roles_service: AccessRolesService = Depends(create_access_roles_service)):
    return await access_roles_service.add_pipeline_to_role(access_role_id,
                                                           [pipeline.pipeline_id for pipeline in pipelines])


@router.delete("/access_roles/{access_role_id}/pipelines/{pipeline_id}", tags=["access_roles"])
async def delete_pipeline_from_role(access_role_id: int, pipeline_id: int,
                                    access_roles_service: AccessRolesService = Depends(create_access_roles_service)):
    return await access_roles_service.delete_pipeline_from_role(access_role_id, pipeline_id)
