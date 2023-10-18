from fastapi import APIRouter, Depends, Request

from schemas.response_sch import Response
from schemas.users_sch import LoginUser, UserResponse
from services.users_srv import UserService

router = APIRouter()


def create_user_service():
    return UserService()


@router.post("/login", tags=["auth"])
async def login_user(request: Request, credentials: LoginUser,
                     user_service: UserService = Depends(create_user_service)) -> UserResponse:
    return await user_service.login(request, credentials)


@router.post("/logout", tags=["auth"])
async def login_user(request: Request, user_service: UserService = Depends(create_user_service)) -> Response:
    return await user_service.logout(request)
