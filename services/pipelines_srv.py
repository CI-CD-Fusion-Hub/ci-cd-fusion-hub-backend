from daos.pipelines_dao import PipelineDAO
from exceptions.pipeline_exceptions import PipelineNotFoundException
from schemas.pipelines_sch import PipelineOut
from utils.response import ok


class PipelinesService:
    def __init__(self):
        self.pipelines_dao = PipelineDAO()

    async def get_all_pipelines(self):
        pipelines = await self.pipelines_dao.get_all()
        return ok(message="Successfully provided all pipelines.",
                  data=[PipelineOut.model_validate(pipeline.as_dict()) for pipeline in pipelines])

    async def get_pipeline_by_id(self, pipeline_id: int):
        pipeline = await self.pipelines_dao.get_by_id(pipeline_id)
        if not pipeline:
            raise PipelineNotFoundException(f"Pipeline with ID {pipeline} does not exist.")

        return ok(message="Successfully provided access role.", data=PipelineOut.model_validate(pipeline.as_dict()))
