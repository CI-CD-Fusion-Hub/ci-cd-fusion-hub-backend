from fastapi import APIRouter, Depends, Request

from app.schemas.users_requests_sch import UpdateUsersRequest
from app.services.users_requests_srv import UsersRequestsService
from app.utils.check_session import auth_required, admin_access_required

router = APIRouter()


def create_users_requests_service():
    return UsersRequestsService()


@router.get("/users_requests", tags=["users-requests"])
@auth_required
@admin_access_required
async def get_all_users_requests(request: Request,
                                 users_requests_service: UsersRequestsService = Depends(create_users_requests_service)):
    return await users_requests_service.get_all_users_requests()


@router.get("/users_requests/{users_request_id}", tags=["users-requests"])
@auth_required
@admin_access_required
async def get_users_request_by_id(request: Request, users_request_id: int,
                                  users_requests_service: UsersRequestsService = Depends(create_users_requests_service)):
    return await users_requests_service.get_by_id(users_request_id)


@router.put("/users_requests/{users_request_id}", tags=["users-requests"])
@auth_required
@admin_access_required
async def update_users_request(request: Request, users_request_id: int, users_request_data: UpdateUsersRequest,
                               users_requests_service: UsersRequestsService = Depends(create_users_requests_service)):
    return await users_requests_service.update_users_request(users_request_id, users_request_data)


@router.delete("/users_requests/{users_request_id}", tags=["users-requests"])
@auth_required
@admin_access_required
async def delete_users_request(request: Request, users_request_id: int,
                               users_requests_service: UsersRequestsService = Depends(create_users_requests_service)):
    return await users_requests_service.delete_users_request(users_request_id)
