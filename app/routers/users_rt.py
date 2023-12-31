from fastapi import APIRouter, Depends, Request

from app.schemas.response_sch import Response
from app.schemas.users_requests_sch import UpdateUsersRequest, CreateUsersRequest
from app.services.users_srv import UserService
from app.schemas.users_sch import CreateUser, UpdateUser, UserResponse, UsersResponse, UpdateUserProfile
from app.utils.check_session import auth_required, admin_access_required
from app.utils.enums import SessionAttributes

router = APIRouter()


def create_user_service():
    return UserService()


@router.get("/users", tags=["users"])
@auth_required
@admin_access_required
async def get_all_users(request: Request, user_service: UserService = Depends(create_user_service)) -> UsersResponse:
    return await user_service.get_all_users()


@router.post("/users", tags=["users"])
@auth_required
@admin_access_required
async def create_user(request: Request, user_data: CreateUser,
                      user_service: UserService = Depends(create_user_service)) -> UserResponse:
    return await user_service.create_user(request, user_data)


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


@router.post("/user/requests", tags=["users"])
@auth_required
async def create_user_requests(request: Request, users_request_data: CreateUsersRequest,
                               user_service: UserService = Depends(create_user_service)) -> UserResponse:
    return await user_service.create_user_requests(request, users_request_data)


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


@router.put("/user/profile", tags=["users"])
@auth_required
async def update_user_profile(request: Request, user_data: UpdateUserProfile,
                              user_service: UserService = Depends(create_user_service)) -> UserResponse:
    user_id = request.session.get(SessionAttributes.USER_ID.value)
    return await user_service.update_user(user_id, user_data)


@router.get("/user/unassigned_pipelines", tags=["users"])
@auth_required
async def get_user_unassigned_pipelines(request: Request,
                                        user_service: UserService = Depends(create_user_service)) -> UserResponse:
    return await user_service.get_user_unassigned_pipelines(request)


@router.put("/users/{user_id}", tags=["users"])
@auth_required
@admin_access_required
async def update_user(request: Request, user_id: int, updated_data: UpdateUser,
                      user_service: UserService = Depends(create_user_service)) -> UserResponse:
    return await user_service.update_user(user_id, updated_data)


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
