from typing import List

from fastapi.responses import JSONResponse

from daos.pipelines_dao import PipelineDAO
from exceptions.pipeline_exceptions import PipelineNotFoundException
from schemas.applications_sch import ApplicationOut
from schemas.pipelines_sch import PipelineOut, GitlabStartPipelineParams, JenkinsStartPipelineParams
from utils.clients.client_manager import ClientManager
from utils.enums import AppType
from utils.response import ok


class PipelinesService:
    def __init__(self, pipelines_dao: PipelineDAO = None, client_manager: ClientManager = None):
        self.pipelines_dao = pipelines_dao or PipelineDAO()
        self.client_manager = client_manager or ClientManager()

    async def _get_pipeline_and_client(self, pipeline_id: int) -> tuple:
        """Retrieve pipeline and its associated client."""
        pipeline = await self.pipelines_dao.get_by_id(pipeline_id)
        if not pipeline:
            raise PipelineNotFoundException(f"Pipeline with ID {pipeline_id} does not exist.")

        application = ApplicationOut.model_validate(pipeline.application.as_dict())
        client = await self.client_manager.create_client(application)
        if not client:
            raise ConnectionError(f"Unable to connect to {application.type}.")

        return pipeline, client

    async def get_all_pipelines(self, ids: List[int]) -> JSONResponse:
        pipelines = await self.pipelines_dao.get_pipelines_by_ids(ids)
        return ok(message="Successfully provided all pipelines.",
                  data=[PipelineOut.model_validate(pipeline.as_dict()) for pipeline in pipelines])

    async def get_pipeline_by_id(self, pipeline_id: int) -> JSONResponse:
        pipeline = await self.pipelines_dao.get_by_id(pipeline_id)
        if not pipeline:
            raise PipelineNotFoundException(f"Pipeline with ID {pipeline} does not exist.")

        return ok(message="Successfully provided pipeline.", data=PipelineOut.model_validate(pipeline.as_dict()))

    async def get_all_gitlab_pipelines(self) -> JSONResponse:
        pipelines = await self.pipelines_dao.get_by_application_type(AppType.GITLAB.value)
        return ok(message="Successfully provided all gitlab pipelines.",
                  data=[PipelineOut.model_validate(pipeline.as_dict()) for pipeline in pipelines])

    async def get_gitlab_pipeline_builds(self, pipeline_id: int) -> JSONResponse:
        pipeline, client = await self._get_pipeline_and_client(pipeline_id)
        data = await client.get_project_pipelines_list(pipeline.project_id)
        return ok(message="Successfully provided gitlab pipeline builds.", data=data)

    async def get_gitlab_pipeline_build(self, pipeline_id: int, build_id: int) -> JSONResponse:
        pipeline, client = await self._get_pipeline_and_client(pipeline_id)
        data = await client.get_project_pipeline_info(pipeline.project_id, build_id)
        return ok(message="Successfully provided gitlab pipeline build.", data=data)

    async def get_gitlab_pipeline_build_jobs(self, pipeline_id: int, build_id: int) -> JSONResponse:
        pipeline, client = await self._get_pipeline_and_client(pipeline_id)
        data = await client.get_project_pipeline_jobs(pipeline.project_id, build_id)
        return ok(message="Successfully provided pipeline builds.", data=data)

    async def get_gitlab_pipeline_build_job_trace(self, pipeline_id: int, build_id: int, job_id: int) -> JSONResponse:
        pipeline, client = await self._get_pipeline_and_client(pipeline_id)
        data = await client.get_project_pipeline_job_logs(pipeline.project_id, job_id)
        return ok(message="Successfully provided pipeline build stage.", data=data)

    async def run_new_gitlab_pipeline_build(self, pipeline_id: int, params: GitlabStartPipelineParams) -> JSONResponse:
        pipeline, client = await self._get_pipeline_and_client(pipeline_id)
        data = await client.start_new_pipeline(pipeline.project_id, params.model_dump())
        return ok(message="Successfully started gitlab pipeline build.", data=data)

    async def retry_gitlab_pipeline_build(self, pipeline_id: int, build_id: int) -> JSONResponse:
        pipeline, client = await self._get_pipeline_and_client(pipeline_id)
        data = await client.retry_pipeline(pipeline.project_id, build_id)
        return ok(message="Successfully retried gitlab pipeline build.", data=data)

    async def cancel_gitlab_pipeline_build(self, pipeline_id: int, build_id: int) -> JSONResponse:
        pipeline, client = await self._get_pipeline_and_client(pipeline_id)
        data = await client.cancel_pipeline(pipeline.project_id, build_id)
        return ok(message="Successfully provided gitlab pipeline build.", data=data)

    async def get_gitlab_pipeline_params(self, pipeline_id: int) -> JSONResponse:
        pipeline, client = await self._get_pipeline_and_client(pipeline_id)
        params = await client.get_pipeline_params(pipeline.project_id)
        return ok(message="Successfully provided gitlab pipeline params.", data=params)

    async def get_all_jenkins_pipelines(self) -> JSONResponse:
        pipelines = await self.pipelines_dao.get_by_application_type(AppType.JENKINS.value)
        return ok(message="Successfully provided all jenkins pipelines.",
                  data=[PipelineOut.model_validate(pipeline.as_dict()) for pipeline in pipelines])

    async def get_jenkins_pipeline_builds(self, pipeline_id) -> JSONResponse:
        pipeline, client = await self._get_pipeline_and_client(pipeline_id)
        data = await client.get_pipeline_builds(pipeline.name)
        return ok(message="Successfully provided jenkins pipeline builds.", data=data)

    async def get_jenkins_pipeline_build(self, pipeline_id: int, build_id: int) -> JSONResponse:
        pipeline, client = await self._get_pipeline_and_client(pipeline_id)
        data = await client.get_pipeline_build(pipeline.name, build_id)
        return ok(message="Successfully provided gitlab pipeline build.", data=data)

    async def run_new_jenkins_pipeline_build(self, pipeline_id: int, params: JenkinsStartPipelineParams) -> JSONResponse:
        pipeline, client = await self._get_pipeline_and_client(pipeline_id)
        await client.start_pipeline(pipeline.name, params.model_dump())
        return ok(message="Successfully started gitlab pipeline build.")

    async def cancel_jenkins_pipeline_build(self, pipeline_id: int, build_id: int) -> JSONResponse:
        pipeline, client = await self._get_pipeline_and_client(pipeline_id)
        await client.cancel_pipeline(pipeline.name, build_id)
        return ok(message="Successfully canceled jenkins pipeline build.")

    async def get_jenkins_pipeline_params(self, pipeline_id: int) -> JSONResponse:
        pipeline, client = await self._get_pipeline_and_client(pipeline_id)
        params = await client.get_pipeline_params(pipeline.name)
        return ok(message="Successfully provided jenkins pipeline params.", data=params)








