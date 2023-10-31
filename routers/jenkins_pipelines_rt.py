from fastapi import APIRouter, Depends, Request

from schemas.pipelines_sch import PipelinesResponse, JenkinsStartPipelineParams
from schemas.response_sch import Response
from services.pipelines_srv import PipelinesService
from utils.check_session import auth_required

router = APIRouter()


def create_pipeline_service():
    return PipelinesService()


@router.get("/pipelines/jenkins", tags=["jenkins_pipelines"])
@auth_required
async def get_all_jenkins_pipelines(request: Request,
                                    pipeline_service: PipelinesService = Depends(
                                        create_pipeline_service)) -> PipelinesResponse:
    return await pipeline_service.get_all_jenkins_pipelines(request)


@router.get("/pipelines/jenkins/{pipeline_id}/builds", tags=["jenkins_pipelines"])
@auth_required
async def get_jenkins_pipeline_builds(request: Request, pipeline_id: int,
                                      pipeline_service: PipelinesService = Depends(
                                          create_pipeline_service)) -> Response:
    return await pipeline_service.get_jenkins_pipeline_builds(request, pipeline_id)


@router.get("/pipelines/jenkins/{pipeline_id}/params", tags=["jenkins_pipelines"])
@auth_required
async def get_jenkins_pipeline_params(request: Request, pipeline_id: int,
                                      pipeline_service: PipelinesService = Depends(
                                          create_pipeline_service)) -> Response:
    return await pipeline_service.get_jenkins_pipeline_params(request, pipeline_id)


@router.post("/pipelines/jenkins/{pipeline_id}/builds", tags=["jenkins_pipelines"])
@auth_required
async def run_new_jenkins_pipeline_build(request: Request, pipeline_id: int, params: JenkinsStartPipelineParams,
                                         pipeline_service: PipelinesService = Depends(
                                             create_pipeline_service)) -> Response:
    return await pipeline_service.run_new_jenkins_pipeline_build(request, pipeline_id, params)


@router.get("/pipelines/jenkins/{pipeline_id}/builds/{build_id}", tags=["jenkins_pipelines"])
@auth_required
async def get_jenkins_pipeline_build(request: Request, pipeline_id: int, build_id: int,
                                     pipeline_service: PipelinesService = Depends(create_pipeline_service)) -> Response:
    return await pipeline_service.get_jenkins_pipeline_build(request, pipeline_id, build_id)


@router.post("/pipelines/jenkins/{pipeline_id}/builds/{build_id}/cancel", tags=["jenkins_pipelines"])
@auth_required
async def cancel_jenkins_pipeline_build(request: Request, pipeline_id: int, build_id: int,
                                        pipeline_service: PipelinesService = Depends(
                                            create_pipeline_service)) -> Response:
    return await pipeline_service.cancel_jenkins_pipeline_build(request, pipeline_id, build_id)