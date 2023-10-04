from fastapi import APIRouter, Depends

from services.pipelines_srv import PipelinesService

router = APIRouter()


def create_pipeline_service():
    return PipelinesService()


@router.get("/pipelines", tags=["pipelines"])
async def get_all_pipelines(pipeline_service: PipelinesService = Depends(create_pipeline_service)):
    return await pipeline_service.get_all_pipelines()


@router.get("/pipelines/{pipeline_id}", tags=["pipelines"])
async def get_pipeline(pipeline_id: int, pipeline_service: PipelinesService = Depends(create_pipeline_service)):
    return await pipeline_service.get_pipeline_by_id(pipeline_id)
