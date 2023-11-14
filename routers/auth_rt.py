from fastapi import APIRouter, Depends, Request
from fastapi import status as Status

from exceptions.custom_http_expeption import CustomHTTPException
from schemas.auth_sch import LoginUser, CreateAuthMethod
from schemas.response_sch import Response
from schemas.users_sch import UserResponse
from services.auth_srv import AuthService
from utils.check_session import admin_access_required, auth_required, auth_method_required
from utils.enums import SessionAttributes, AuthMethods

router = APIRouter()


def create_auth_service():
    return AuthService()


@router.get("/login", tags=["auth"])
@auth_method_required
async def login_user(request: Request, auth_service: AuthService = Depends(create_auth_service)) -> UserResponse:
    auth_method = request.session.get(SessionAttributes.AUTH_METHOD.value)
    if auth_method == AuthMethods.ADDS.value:
        return await auth_service.azure_login(request)
    if auth_method == AuthMethods.CAS.value:
        return await auth_service.cas_login(request)
    else:
        raise CustomHTTPException(
            detail="Invalid authentication method",
            status_code=Status.HTTP_400_BAD_REQUEST
        )


@router.get("/login/az/callback", tags=["auth"])
async def azure_callback(request: Request, code: str = None, state: str = None,
                         auth_service: AuthService = Depends(create_auth_service)):
    return await auth_service.az_callback(request, code, state)


@router.post("/login", tags=["auth"])
@auth_method_required
async def login_user(request: Request, credentials: LoginUser,
                     auth_service: AuthService = Depends(create_auth_service)):
    auth_method = request.session.get(SessionAttributes.AUTH_METHOD.value)
    if auth_method == AuthMethods.LOCAL.value:
        return await auth_service.login(request, credentials)
    else:
        raise CustomHTTPException(
            detail="Invalid authentication method.",
            status_code=Status.HTTP_400_BAD_REQUEST
        )


@router.get("/login/method", tags=["auth"])
async def get_login_auth_method(request: Request,
                                auth_service: AuthService = Depends(create_auth_service)):
    return await auth_service.get_login_auth_method()


@router.post("/logout", tags=["auth"])
async def login_user(request: Request, auth_service: AuthService = Depends(create_auth_service)) -> Response:
    return await auth_service.logout(request)


@auth_required
@admin_access_required
@router.post("/auth_method", tags=["auth"])
async def add_auth_method(request: Request, auth_data: CreateAuthMethod,
                          auth_service: AuthService = Depends(create_auth_service)):
    return await auth_service.add_auth_method(auth_data)


@auth_required
@admin_access_required
@router.get("/auth_method", tags=["auth"])
async def get_auth_method(request: Request,
                          auth_service: AuthService = Depends(create_auth_service)):
    return await auth_service.get_auth_method()

