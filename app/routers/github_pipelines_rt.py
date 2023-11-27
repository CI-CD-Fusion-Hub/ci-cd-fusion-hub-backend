from fastapi import APIRouter, Depends, Request

from app.schemas.pipelines_sch import PipelinesResponse, GithubStartPipelineParams
from app.schemas.response_sch import Response
from app.services.pipelines_srv import PipelinesService
from app.utils.check_session import auth_required

router = APIRouter()


def create_pipeline_service():
    return PipelinesService()


@router.get("/pipelines/github", tags=["github_pipelines"])
@auth_required
async def get_all_github_pipeline(request: Request,
                                  pipeline_service: PipelinesService = Depends(
                                      create_pipeline_service)) -> PipelinesResponse:
    return await pipeline_service.get_all_github_pipelines(request)


@router.get("/pipelines/github/{pipeline_id}/builds", tags=["github_pipelines"])
@auth_required
async def get_github_pipeline_builds(request: Request, pipeline_id: int,
                                     pipeline_service: PipelinesService = Depends(create_pipeline_service)) -> Response:
    return await pipeline_service.get_github_pipeline_builds(request, pipeline_id)


@router.get("/pipelines/github/{pipeline_id}/builds/{build_id}", tags=["github_pipelines"])
@auth_required
async def get_github_pipeline_build(request: Request, pipeline_id: int, build_id: int,
                                    pipeline_service: PipelinesService = Depends(create_pipeline_service)) -> Response:
    return await pipeline_service.get_github_pipeline_build(request, pipeline_id, build_id)


@router.get("/pipelines/github/{pipeline_id}/params", tags=["github_pipelines"])
@auth_required
async def get_github_pipeline_params(request: Request, pipeline_id: int,
                                     pipeline_service: PipelinesService = Depends(create_pipeline_service)) -> Response:
    return await pipeline_service.get_github_pipeline_params(request, pipeline_id)


@router.post("/pipelines/github/{pipeline_id}/builds", tags=["github_pipelines"])
@auth_required
async def run_new_github_pipeline_build(request: Request, pipeline_id: int, params: GithubStartPipelineParams,
                                        pipeline_service: PipelinesService = Depends(
                                            create_pipeline_service)) -> Response:
    return await pipeline_service.run_new_github_pipeline_build(request, pipeline_id, params)


@router.post("/pipelines/github/{pipeline_id}/builds/{build_id}/retry", tags=["github_pipelines"])
@auth_required
async def retry_github_pipeline_build(request: Request, pipeline_id: int, build_id: int,
                                      pipeline_service: PipelinesService = Depends(
                                          create_pipeline_service)) -> Response:
    return await pipeline_service.retry_github_pipeline_build(request, pipeline_id, build_id)


@router.post("/pipelines/github/{pipeline_id}/builds/{build_id}/cancel", tags=["github_pipelines"])
@auth_required
async def cancel_github_pipeline_build(request: Request, pipeline_id: int, build_id: int,
                                       pipeline_service: PipelinesService = Depends(
                                           create_pipeline_service)) -> Response:
    return await pipeline_service.cancel_github_pipeline_build(request, pipeline_id, build_id)


@router.get("/pipelines/github/{pipeline_id}/builds/{build_id}/jobs", tags=["github_pipelines"])
@auth_required
async def get_github_pipeline_build_jobs(request: Request, pipeline_id: int, build_id: int,
                                         pipeline_service: PipelinesService = Depends(
                                             create_pipeline_service)) -> Response:
    return await pipeline_service.get_github_pipeline_build_jobs(request, pipeline_id, build_id)


@router.get("/pipelines/github/{pipeline_id}/builds/{build_id}/jobs/{job_id}/trace", tags=["github_pipelines"])
@auth_required
async def get_github_pipeline_build_job_trace(request: Request, pipeline_id: int, build_id: int, job_id: int,
                                              pipeline_service: PipelinesService = Depends(
                                                  create_pipeline_service)) -> Response:
    return await pipeline_service.get_github_pipeline_build_job_trace(request, pipeline_id, build_id, job_id)