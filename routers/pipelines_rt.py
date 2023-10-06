from fastapi import APIRouter, Depends

from schemas.pipelines_sch import GitlabStartPipelineParams
from services.pipelines_srv import PipelinesService

router = APIRouter()


def create_pipeline_service():
    return PipelinesService()


@router.get("/pipelines/gitlab", tags=["gitlab_pipelines"])
async def get_all_gitlab_pipeline(pipeline_service: PipelinesService = Depends(create_pipeline_service)):
    return await pipeline_service.get_all_gitlab_pipelines()


@router.get("/pipelines/gitlab/{pipeline_id}/builds", tags=["gitlab_pipelines"])
async def get_gitlab_pipeline_builds(pipeline_id: int,
                                     pipeline_service: PipelinesService = Depends(create_pipeline_service)):
    return await pipeline_service.get_gitlab_pipeline_builds(pipeline_id)


@router.get("/pipelines/gitlab/{pipeline_id}/builds/{build_id}", tags=["gitlab_pipelines"])
async def get_gitlab_pipeline_build(pipeline_id: int, build_id: int,
                                    pipeline_service: PipelinesService = Depends(create_pipeline_service)):
    return await pipeline_service.get_gitlab_pipeline_build(pipeline_id, build_id)


@router.post("/pipelines/gitlab/{pipeline_id}/builds", tags=["gitlab_pipelines"])
async def run_new_gitlab_pipeline_build(pipeline_id: int, params: GitlabStartPipelineParams,
                                        pipeline_service: PipelinesService = Depends(create_pipeline_service)):
    return await pipeline_service.run_new_gitlab_pipeline_build(pipeline_id, params)


@router.post("/pipelines/gitlab/{pipeline_id}/builds/{build_id}/retry", tags=["gitlab_pipelines"])
async def retry_gitlab_pipeline_build(pipeline_id: int, build_id: int,
                                      pipeline_service: PipelinesService = Depends(create_pipeline_service)):
    return await pipeline_service.retry_gitlab_pipeline_build(pipeline_id, build_id)


@router.post("/pipelines/gitlab/{pipeline_id}/builds/{build_id}/cancel", tags=["gitlab_pipelines"])
async def cancel_gitlab_pipeline_build(pipeline_id: int, build_id: int,
                                       pipeline_service: PipelinesService = Depends(create_pipeline_service)):
    return await pipeline_service.cancel_gitlab_pipeline_build(pipeline_id, build_id)


@router.get("/pipelines/gitlab/{pipeline_id}/builds/{build_id}/jobs", tags=["gitlab_pipelines"])
async def get_gitlab_pipeline_build_jobs(pipeline_id: int, build_id: int,
                                         pipeline_service: PipelinesService = Depends(create_pipeline_service)):
    return await pipeline_service.get_gitlab_pipeline_build_jobs(pipeline_id, build_id)


@router.get("/pipelines/gitlab/{pipeline_id}/builds/{build_id}/jobs/{job_id}/trace", tags=["gitlab_pipelines"])
async def get_gitlab_pipeline_build_job_trace(pipeline_id: int, build_id: int, job_id: int,
                                              pipeline_service: PipelinesService = Depends(create_pipeline_service)):
    return await pipeline_service.get_gitlab_pipeline_build_job_trace(pipeline_id, build_id, job_id)


@router.get("/pipelines", tags=["pipelines"])
async def get_all_pipelines(pipeline_service: PipelinesService = Depends(create_pipeline_service)):
    return await pipeline_service.get_all_pipelines()


@router.get("/pipelines/{pipeline_id}", tags=["pipelines"])
async def get_pipeline(pipeline_id: int, pipeline_service: PipelinesService = Depends(create_pipeline_service)):
    return await pipeline_service.get_pipeline_by_id(pipeline_id)
