from fastapi import APIRouter, Depends

from services.users_srv import UserService
from schemas.users_sch import CreateUser, UpdateUser

router = APIRouter()


def create_user_service():
    return UserService()


@router.get("/users", tags=["users"])
async def get_all_users(user_service: UserService = Depends(create_user_service)):
    return await user_service.get_all_users()


@router.get("/users/{user_id}", tags=["users"])
async def get_user_by_id(user_id: int, user_service: UserService = Depends(create_user_service)):
    return await user_service.get_user_by_id(user_id)


@router.post("/users", tags=["users"])
async def create_user(user_data: CreateUser, user_service: UserService = Depends(create_user_service)):
    return await user_service.create_user(user_data)


@router.put("/users/{user_id}", tags=["users"])
async def update_user(user_id: int, updated_data: UpdateUser, user_service: UserService = Depends(create_user_service)):
    return await user_service.update_user(user_id, updated_data)


@router.delete("/users/{user_id}", tags=["users"])
async def delete_user(user_id: int, user_service: UserService = Depends(create_user_service)):
    return await user_service.delete_user(user_id)


@router.get("/users/{user_id}/unassigned_roles", tags=["users"])
async def get_user_unassigned_roles(user_id: int, user_service: UserService = Depends(create_user_service)):
    return await user_service.fetch_user_unassigned_roles(user_id)
