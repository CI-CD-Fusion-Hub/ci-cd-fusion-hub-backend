from typing import List

from fastapi import APIRouter, Depends, Request

from schemas.pipelines_sch import GitlabStartPipelineParams, JenkinsStartPipelineParams
from services.pipelines_srv import PipelinesService
from utils.check_session import auth_required, get_user_pipelines

router = APIRouter()


def create_pipeline_service():
    return PipelinesService()


####################
# Gitlab pipelines
####################
@router.get("/pipelines/gitlab", tags=["gitlab_pipelines"])
@auth_required
async def get_all_gitlab_pipeline(request: Request,
                                  pipeline_service: PipelinesService = Depends(create_pipeline_service),
                                  ser_pipelines: List[int] = Depends(get_user_pipelines)):
    return await pipeline_service.get_all_gitlab_pipelines()


@router.get("/pipelines/gitlab/{pipeline_id}/builds", tags=["gitlab_pipelines"])
@auth_required
async def get_gitlab_pipeline_builds(request: Request, pipeline_id: int,
                                     pipeline_service: PipelinesService = Depends(create_pipeline_service)):
    return await pipeline_service.get_gitlab_pipeline_builds(pipeline_id)


@router.get("/pipelines/gitlab/{pipeline_id}/builds/{build_id}", tags=["gitlab_pipelines"])
@auth_required
async def get_gitlab_pipeline_build(request: Request, pipeline_id: int, build_id: int,
                                    pipeline_service: PipelinesService = Depends(create_pipeline_service)):
    return await pipeline_service.get_gitlab_pipeline_build(pipeline_id, build_id)


@router.post("/pipelines/gitlab/{pipeline_id}/builds", tags=["gitlab_pipelines"])
@auth_required
async def run_new_gitlab_pipeline_build(request: Request, pipeline_id: int, params: GitlabStartPipelineParams,
                                        pipeline_service: PipelinesService = Depends(create_pipeline_service)):
    return await pipeline_service.run_new_gitlab_pipeline_build(pipeline_id, params)


@router.post("/pipelines/gitlab/{pipeline_id}/builds/{build_id}/retry", tags=["gitlab_pipelines"])
@auth_required
async def retry_gitlab_pipeline_build(request: Request, pipeline_id: int, build_id: int,
                                      pipeline_service: PipelinesService = Depends(create_pipeline_service)):
    return await pipeline_service.retry_gitlab_pipeline_build(pipeline_id, build_id)


@router.post("/pipelines/gitlab/{pipeline_id}/builds/{build_id}/cancel", tags=["gitlab_pipelines"])
@auth_required
async def cancel_gitlab_pipeline_build(request: Request, pipeline_id: int, build_id: int,
                                       pipeline_service: PipelinesService = Depends(create_pipeline_service)):
    return await pipeline_service.cancel_gitlab_pipeline_build(pipeline_id, build_id)


@router.get("/pipelines/gitlab/{pipeline_id}/builds/{build_id}/jobs", tags=["gitlab_pipelines"])
@auth_required
async def get_gitlab_pipeline_build_jobs(request: Request, pipeline_id: int, build_id: int,
                                         pipeline_service: PipelinesService = Depends(create_pipeline_service)):
    return await pipeline_service.get_gitlab_pipeline_build_jobs(pipeline_id, build_id)


@router.get("/pipelines/gitlab/{pipeline_id}/builds/{build_id}/jobs/{job_id}/trace", tags=["gitlab_pipelines"])
@auth_required
async def get_gitlab_pipeline_build_job_trace(request: Request, pipeline_id: int, build_id: int, job_id: int,
                                              pipeline_service: PipelinesService = Depends(create_pipeline_service)):
    return await pipeline_service.get_gitlab_pipeline_build_job_trace(pipeline_id, build_id, job_id)


####################
# Jenkins pipelines
####################
@router.get("/pipelines/jenkins", tags=["jenkins_pipelines"])
@auth_required
async def get_all_jenkins_pipelines(request: Request, pipeline_service: PipelinesService = Depends(create_pipeline_service)):
    return await pipeline_service.get_all_jenkins_pipelines()


@router.get("/pipelines/jenkins/{pipeline_id}/builds", tags=["jenkins_pipelines"])
@auth_required
async def get_jenkins_pipeline_builds(request: Request, pipeline_id: int,
                                      pipeline_service: PipelinesService = Depends(create_pipeline_service)):
    return await pipeline_service.get_jenkins_pipeline_builds(pipeline_id)


@router.post("/pipelines/jenkins/{pipeline_id}/builds", tags=["jenkins_pipelines"])
@auth_required
async def run_new_jenkins_pipeline_build(request: Request, pipeline_id: int, params: JenkinsStartPipelineParams,
                                         pipeline_service: PipelinesService = Depends(create_pipeline_service)):
    return await pipeline_service.run_new_jenkins_pipeline_build(pipeline_id, params)


@router.get("/pipelines/jenkins/{pipeline_id}/builds/{build_id}", tags=["jenkins_pipelines"])
@auth_required
async def get_jenkins_pipeline_build(request: Request, pipeline_id: int, build_id: int,
                                     pipeline_service: PipelinesService = Depends(create_pipeline_service)):
    return await pipeline_service.get_jenkins_pipeline_build(pipeline_id, build_id)


@router.post("/pipelines/jenkins/{pipeline_id}/builds/{build_id}/cancel", tags=["jenkins_pipelines"])
@auth_required
async def cancel_jenkins_pipeline_build(request: Request, pipeline_id: int, build_id: int,
                                        pipeline_service: PipelinesService = Depends(create_pipeline_service)):
    return await pipeline_service.cancel_jenkins_pipeline_build(pipeline_id, build_id)


####################
# Database pipelines
####################
@router.get("/pipelines", tags=["pipelines"])
@auth_required
async def get_all_pipelines(request: Request,
                            pipeline_service: PipelinesService = Depends(create_pipeline_service),
                            ser_pipelines: List[int] = Depends(get_user_pipelines)):
    return await pipeline_service.get_all_pipelines(ser_pipelines)


@router.get("/pipelines/{pipeline_id}", tags=["pipelines"])
@auth_required
async def get_pipeline(request: Request, pipeline_id: int,
                       pipeline_service: PipelinesService = Depends(create_pipeline_service)):
    return await pipeline_service.get_pipeline_by_id(pipeline_id)
