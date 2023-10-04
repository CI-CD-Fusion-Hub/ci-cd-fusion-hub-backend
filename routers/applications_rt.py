from fastapi import APIRouter, Depends

from schemas.applications_sch import CreateApplication, UpdateApplication
from services.applications_srv import ApplicationService

router = APIRouter()


def create_application_service():
    return ApplicationService()


@router.get("/applications", tags=["applications"])
async def get_all_applications(application_service: ApplicationService = Depends(create_application_service)):
    return await application_service.get_all_applications()


@router.get("/applications/{application_id}", tags=["applications"])
async def get_application(application_id: int,
                          application_service: ApplicationService = Depends(create_application_service)):
    return await application_service.get_application_by_id(application_id)


@router.post("/applications", tags=["applications"])
async def create_application(app_data: CreateApplication,
                             application_service: ApplicationService = Depends(create_application_service)):
    return await application_service.create_application(app_data)


@router.post("/applications/verify", tags=["applications"])
async def verify_application(app_data: CreateApplication,
                             application_service: ApplicationService = Depends(create_application_service)):
    return await application_service.verify_application(app_data)


@router.put("/applications/{application_id}", tags=["applications"])
async def update_application(application_id: int, app_data: UpdateApplication,
                             application_service: ApplicationService = Depends(create_application_service)):
    return await application_service.update_application(application_id, app_data)


@router.delete("/applications/{application_id}", tags=["applications"])
async def delete_application(application_id: int,
                             application_service: ApplicationService = Depends(create_application_service)):
    return await application_service.delete_application(application_id)
