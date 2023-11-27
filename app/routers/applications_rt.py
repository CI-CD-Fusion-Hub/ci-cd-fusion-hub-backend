from fastapi import APIRouter, Depends, Request

from app.schemas.applications_sch import CreateApplication, UpdateApplication, ApplicationsResponse, ApplicationResponse
from app.schemas.response_sch import Response
from app.services.applications_srv import ApplicationService
from app.utils.check_session import auth_required, admin_access_required

router = APIRouter()


def create_application_service():
    return ApplicationService()


@router.get("/applications", tags=["applications"])
@auth_required
@admin_access_required
async def get_all_applications(request: Request,
                               application_service: ApplicationService = Depends(
                                   create_application_service)) -> ApplicationsResponse:
    return await application_service.get_all_applications()


@router.get("/applications/{application_id}", tags=["applications"])
@auth_required
@admin_access_required
async def get_application(request: Request, application_id: int,
                          application_service: ApplicationService = Depends(
                              create_application_service)) -> ApplicationResponse:
    return await application_service.get_application_by_id(application_id)


@router.post("/applications", tags=["applications"])
@auth_required
@admin_access_required
async def create_application(request: Request, app_data: CreateApplication,
                             application_service: ApplicationService = Depends(
                                 create_application_service)) -> ApplicationResponse:
    return await application_service.create_application(app_data)


@router.post("/applications/verify", tags=["applications"])
@auth_required
@admin_access_required
async def verify_application(request: Request, app_data: CreateApplication,
                             application_service: ApplicationService = Depends(create_application_service)) -> Response:
    return await application_service.verify_application(app_data)


@router.put("/applications/{application_id}", tags=["applications"])
@auth_required
@admin_access_required
async def update_application(request: Request, application_id: int, app_data: UpdateApplication,
                             application_service: ApplicationService = Depends(
                                 create_application_service)) -> ApplicationResponse:
    return await application_service.update_application(application_id, app_data)


@router.delete("/applications/{application_id}", tags=["applications"])
@auth_required
@admin_access_required
async def delete_application(request: Request, application_id: int,
                             application_service: ApplicationService = Depends(create_application_service)) -> Response:
    return await application_service.delete_application(application_id)
