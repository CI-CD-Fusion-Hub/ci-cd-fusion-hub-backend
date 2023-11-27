from fastapi import APIRouter, Depends, Request

from app.schemas.pipelines_sch import PipelinesResponse, PipelineResponse
from app.services.pipelines_srv import PipelinesService
from app.utils.check_session import auth_required

router = APIRouter()


def create_pipeline_service():
    return PipelinesService()


@router.get("/pipelines", tags=["pipelines"])
@auth_required
async def get_all_pipelines(request: Request,
                            pipeline_service: PipelinesService = Depends(create_pipeline_service)) -> PipelinesResponse:
    return await pipeline_service.get_all_pipelines(request)


@router.get("/pipelines/{pipeline_id}", tags=["pipelines"])
@auth_required
async def get_pipeline(request: Request, pipeline_id: int,
                       pipeline_service: PipelinesService = Depends(create_pipeline_service)) -> PipelineResponse:
    return await pipeline_service.get_pipeline_by_id(request, pipeline_id)
