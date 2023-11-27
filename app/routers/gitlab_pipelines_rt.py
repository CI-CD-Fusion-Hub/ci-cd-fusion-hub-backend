from fastapi import APIRouter, Depends, Request

from app.schemas.pipelines_sch import GitlabStartPipelineParams, PipelinesResponse
from app.schemas.response_sch import Response
from app.services.pipelines_srv import PipelinesService
from app.utils.check_session import auth_required

router = APIRouter()


def create_pipeline_service():
    return PipelinesService()


@router.get("/pipelines/gitlab", tags=["gitlab_pipelines"])
@auth_required
async def get_all_gitlab_pipeline(request: Request,
                                  pipeline_service: PipelinesService = Depends(
                                      create_pipeline_service)) -> PipelinesResponse:
    return await pipeline_service.get_all_gitlab_pipelines(request)


@router.get("/pipelines/gitlab/{pipeline_id}/builds", tags=["gitlab_pipelines"])
@auth_required
async def get_gitlab_pipeline_builds(request: Request, pipeline_id: int,
                                     pipeline_service: PipelinesService = Depends(create_pipeline_service)) -> Response:
    return await pipeline_service.get_gitlab_pipeline_builds(request, pipeline_id)


@router.get("/pipelines/gitlab/{pipeline_id}/builds/{build_id}", tags=["gitlab_pipelines"])
@auth_required
async def get_gitlab_pipeline_build(request: Request, pipeline_id: int, build_id: int,
                                    pipeline_service: PipelinesService = Depends(create_pipeline_service)) -> Response:
    return await pipeline_service.get_gitlab_pipeline_build(request, pipeline_id, build_id)


@router.get("/pipelines/gitlab/{pipeline_id}/params", tags=["gitlab_pipelines"])
@auth_required
async def get_gitlab_pipeline_params(request: Request, pipeline_id: int,
                                     pipeline_service: PipelinesService = Depends(create_pipeline_service)) -> Response:
    return await pipeline_service.get_gitlab_pipeline_params(request, pipeline_id)


@router.post("/pipelines/gitlab/{pipeline_id}/builds", tags=["gitlab_pipelines"])
@auth_required
async def run_new_gitlab_pipeline_build(request: Request, pipeline_id: int, params: GitlabStartPipelineParams,
                                        pipeline_service: PipelinesService = Depends(
                                            create_pipeline_service)) -> Response:
    return await pipeline_service.run_new_gitlab_pipeline_build(request, pipeline_id, params)


@router.post("/pipelines/gitlab/{pipeline_id}/builds/{build_id}/retry", tags=["gitlab_pipelines"])
@auth_required
async def retry_gitlab_pipeline_build(request: Request, pipeline_id: int, build_id: int,
                                      pipeline_service: PipelinesService = Depends(
                                          create_pipeline_service)) -> Response:
    return await pipeline_service.retry_gitlab_pipeline_build(request, pipeline_id, build_id)


@router.post("/pipelines/gitlab/{pipeline_id}/builds/{build_id}/cancel", tags=["gitlab_pipelines"])
@auth_required
async def cancel_gitlab_pipeline_build(request: Request, pipeline_id: int, build_id: int,
                                       pipeline_service: PipelinesService = Depends(
                                           create_pipeline_service)) -> Response:
    return await pipeline_service.cancel_gitlab_pipeline_build(request, pipeline_id, build_id)


@router.get("/pipelines/gitlab/{pipeline_id}/builds/{build_id}/jobs", tags=["gitlab_pipelines"])
@auth_required
async def get_gitlab_pipeline_build_jobs(request: Request, pipeline_id: int, build_id: int,
                                         pipeline_service: PipelinesService = Depends(
                                             create_pipeline_service)) -> Response:
    return await pipeline_service.get_gitlab_pipeline_build_jobs(request, pipeline_id, build_id)


@router.get("/pipelines/gitlab/{pipeline_id}/builds/{build_id}/jobs/{job_id}/trace", tags=["gitlab_pipelines"])
@auth_required
async def get_gitlab_pipeline_build_job_trace(request: Request, pipeline_id: int, build_id: int, job_id: int,
                                              pipeline_service: PipelinesService = Depends(
                                                  create_pipeline_service)) -> Response:
    return await pipeline_service.get_gitlab_pipeline_build_job_trace(request, pipeline_id, build_id, job_id)
