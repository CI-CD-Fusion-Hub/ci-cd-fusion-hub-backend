from fastapi import APIRouter, Depends, Request

from schemas.response_sch import Response
from schemas.users_requests_sch import UpdateUsersRequest, CreateUsersRequest
from services.users_srv import UserService
from schemas.users_sch import CreateUser, UpdateUser, UserResponse, UsersResponse
from utils.check_session import auth_required, admin_access_required

router = APIRouter()


def create_user_service():
    return UserService()


@router.get("/users", tags=["users"])
@auth_required
@admin_access_required
async def get_all_users(request: Request, user_service: UserService = Depends(create_user_service)) -> UsersResponse:
    return await user_service.get_all_users()


@router.get("/users/{user_id}", tags=["users"])
@auth_required
async def get_user_by_id(request: Request, user_id: int,
                         user_service: UserService = Depends(create_user_service)) -> UserResponse:
    return await user_service.get_user_by_id(request, user_id)


@router.get("/user", tags=["users"])
@auth_required
async def get_user_by_id(request: Request,
                         user_service: UserService = Depends(create_user_service)) -> UserResponse:
    return await user_service.get_user_info_from_request(request)


@router.get("/user/requests", tags=["users"])
@auth_required
async def get_user_requests(request: Request,
                            user_service: UserService = Depends(create_user_service)) -> UserResponse:
    return await user_service.get_user_requests(request)


@router.put("/user/requests/{request_id}", tags=["users"])
@auth_required
async def update_user_requests(request: Request, request_id: int, users_request_data: UpdateUsersRequest,
                               user_service: UserService = Depends(create_user_service)) -> UserResponse:
    return await user_service.update_user_requests(request_id, users_request_data)


@router.post("/user/requests", tags=["users"])
@auth_required
async def create_user_requests(request: Request, users_request_data: CreateUsersRequest,
                               user_service: UserService = Depends(create_user_service)) -> UserResponse:
    return await user_service.create_user_requests(request, users_request_data)


@router.get("/user/unassigned_pipelines", tags=["users"])
@auth_required
async def get_user_unassigned_pipelines(request: Request,
                                        user_service: UserService = Depends(create_user_service)) -> UserResponse:
    return await user_service.get_user_unassigned_pipelines(request)


@router.post("/users", tags=["users"])
@auth_required
@admin_access_required
async def create_user(request: Request, user_data: CreateUser,
                      user_service: UserService = Depends(create_user_service)) -> UserResponse:
    return await user_service.create_user(user_data)


@router.put("/users/{user_id}", tags=["users"])
@auth_required
async def update_user(request: Request, user_id: int, updated_data: UpdateUser,
                      user_service: UserService = Depends(create_user_service)) -> UserResponse:
    return await user_service.update_user(request, user_id, updated_data)


@router.delete("/users/{user_id}", tags=["users"])
@auth_required
@admin_access_required
async def delete_user(request: Request, user_id: int,
                      user_service: UserService = Depends(create_user_service)) -> Response:
    return await user_service.delete_user(user_id)


@router.get("/users/{user_id}/unassigned_roles", tags=["users"])
@auth_required
@admin_access_required
async def get_user_unassigned_roles(request: Request, user_id: int,
                                    user_service: UserService = Depends(create_user_service)):
    return await user_service.fetch_user_unassigned_roles(user_id)
