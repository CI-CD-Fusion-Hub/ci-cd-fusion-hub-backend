from fastapi import APIRouter, Depends, Request

from schemas.pipelines_sch import PipelinesResponse
from schemas.response_sch import Response
from services.pipelines_srv import PipelinesService
from utils.check_session import auth_required

router = APIRouter()


def create_pipeline_service():
    return PipelinesService()


@router.get("/pipelines/github", tags=["github_pipelines"])
@auth_required
async def get_all_gitlab_pipeline(request: Request,
                                  pipeline_service: PipelinesService = Depends(
                                      create_pipeline_service)) -> PipelinesResponse:
    return await pipeline_service.get_all_github_pipelines(request)


@router.get("/pipelines/github/{pipeline_id}/builds", tags=["github_pipelines"])
@auth_required
async def get_gitlab_pipeline_builds(request: Request, pipeline_id: int,
                                     pipeline_service: PipelinesService = Depends(create_pipeline_service)) -> Response:
    return await pipeline_service.get_github_pipeline_builds(request, pipeline_id)

