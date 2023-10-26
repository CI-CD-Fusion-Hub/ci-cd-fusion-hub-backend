from fastapi import Request

from daos.pipelines_dao import PipelineDAO
from exceptions.pipeline_exceptions import PipelineNotFoundException
from schemas.applications_sch import ApplicationOut
from schemas.pipelines_sch import PipelineOut, GitlabStartPipelineParams, JenkinsStartPipelineParams
from utils.clients.client_manager import ClientManager
from utils.enums import AppType, SessionAttributes, AccessLevel
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

    @classmethod
    async def _validate_user_access(cls, request: Request, pipeline_id: int):
        user_access_level = request.session.get(SessionAttributes.USER_ACCESS_LEVEL.value)
        user_pipelines = request.session.get(SessionAttributes.USER_PIPELINES.value)
        if user_access_level != AccessLevel.ADMIN.value and pipeline_id not in user_pipelines:
            raise PipelineNotFoundException(f"Pipeline with ID {pipeline_id} does not exist.")

    async def get_all_pipelines(self, request: Request):
        user_access_level = request.session.get(SessionAttributes.USER_ACCESS_LEVEL.value)
        user_pipelines = request.session.get(SessionAttributes.USER_PIPELINES.value)

        if user_access_level != AccessLevel.ADMIN.value:
            pipelines = await self.pipelines_dao.get_pipelines_by_ids(user_pipelines)
        else:
            pipelines = await self.pipelines_dao.get_all()

        return ok(message="Successfully provided all pipelines.",
                  data=[PipelineOut.model_validate(pipeline.as_dict()) for pipeline in pipelines])

    async def get_pipeline_by_id(self, request: Request, pipeline_id: int):
        await self._validate_user_access(request, pipeline_id)

        pipeline = await self.pipelines_dao.get_by_id(pipeline_id)
        if not pipeline:
            raise PipelineNotFoundException(f"Pipeline with ID {pipeline_id} does not exist.")

        return ok(message="Successfully provided pipeline.", data=PipelineOut.model_validate(pipeline.as_dict()))

    async def get_all_gitlab_pipelines(self, request: Request):
        user_access_level = request.session.get(SessionAttributes.USER_ACCESS_LEVEL.value)
        user_pipelines = request.session.get(SessionAttributes.USER_PIPELINES.value)

        if user_access_level != AccessLevel.ADMIN.value:
            pipelines = await self.pipelines_dao.get_by_application_type_and_ids(AppType.GITLAB.value, user_pipelines)
        else:
            pipelines = await self.pipelines_dao.get_by_application_type(AppType.GITLAB.value)

        return ok(
            message="Successfully provided all gitlab pipelines.",
            data=[PipelineOut.model_validate(pipeline.as_dict()) for pipeline in pipelines]
        )

    async def get_gitlab_pipeline_builds(self, request: Request, pipeline_id: int):
        await self._validate_user_access(request, pipeline_id)

        pipeline, client = await self._get_pipeline_and_client(pipeline_id)
        data = await client.get_project_pipelines_list(pipeline.project_id)
        return ok(message="Successfully provided gitlab pipeline builds.", data=data)

    async def get_gitlab_pipeline_build(self, request: Request, pipeline_id: int, build_id: int):
        await self._validate_user_access(request, pipeline_id)

        pipeline, client = await self._get_pipeline_and_client(pipeline_id)
        data = await client.get_project_pipeline_info(pipeline.project_id, build_id)
        data['name'] = pipeline.name
        return ok(message="Successfully provided gitlab pipeline build.", data=data)

    async def get_gitlab_pipeline_build_jobs(self, request: Request, pipeline_id: int, build_id: int):
        await self._validate_user_access(request, pipeline_id)

        pipeline, client = await self._get_pipeline_and_client(pipeline_id)
        data = await client.get_project_pipeline_jobs(pipeline.project_id, build_id)
        return ok(message="Successfully provided gitlab pipeline jobs.", data=data)

    async def get_gitlab_pipeline_build_job_trace(self, request: Request,
                                                  pipeline_id: int, build_id: int, job_id: int):
        await self._validate_user_access(request, pipeline_id)

        pipeline, client = await self._get_pipeline_and_client(pipeline_id)
        data = await client.get_project_pipeline_job_logs(pipeline.project_id, job_id)
        return ok(message="Successfully provided pipeline build stage.", data=data)

    async def run_new_gitlab_pipeline_build(self, request: Request,
                                            pipeline_id: int, params: GitlabStartPipelineParams):
        await self._validate_user_access(request, pipeline_id)

        pipeline, client = await self._get_pipeline_and_client(pipeline_id)
        data = await client.start_new_pipeline(pipeline.project_id, params.model_dump())
        return ok(message="Successfully started gitlab pipeline build.", data=data)

    async def retry_gitlab_pipeline_build(self, request: Request, pipeline_id: int, build_id: int):
        await self._validate_user_access(request, pipeline_id)

        pipeline, client = await self._get_pipeline_and_client(pipeline_id)
        data = await client.retry_pipeline(pipeline.project_id, build_id)
        return ok(message="Successfully retried gitlab pipeline build.", data=data)

    async def cancel_gitlab_pipeline_build(self, request: Request, pipeline_id: int, build_id: int):
        await self._validate_user_access(request, pipeline_id)

        pipeline, client = await self._get_pipeline_and_client(pipeline_id)
        data = await client.cancel_pipeline(pipeline.project_id, build_id)
        return ok(message="Successfully canceled gitlab pipeline build.", data=data)

    async def get_gitlab_pipeline_params(self, request: Request, pipeline_id: int):
        await self._validate_user_access(request, pipeline_id)

        pipeline, client = await self._get_pipeline_and_client(pipeline_id)
        params = await client.get_pipeline_params(pipeline.project_id)
        return ok(message="Successfully provided gitlab pipeline params.", data=params)

    async def get_all_jenkins_pipelines(self, request: Request):
        user_access_level = request.session.get(SessionAttributes.USER_ACCESS_LEVEL.value)
        user_pipelines = request.session.get(SessionAttributes.USER_PIPELINES.value)

        if user_access_level != AccessLevel.ADMIN.value:
            pipelines = await self.pipelines_dao.get_by_application_type_and_ids(AppType.JENKINS.value, user_pipelines)
        else:
            pipelines = await self.pipelines_dao.get_by_application_type(AppType.JENKINS.value)

        return ok(message="Successfully provided all jenkins pipelines.",
                  data=[PipelineOut.model_validate(pipeline.as_dict()) for pipeline in pipelines])

    async def get_jenkins_pipeline_builds(self, request: Request, pipeline_id):
        await self._validate_user_access(request, pipeline_id)

        pipeline, client = await self._get_pipeline_and_client(pipeline_id)
        data = await client.get_pipeline_builds(pipeline.name)
        return ok(message="Successfully provided jenkins pipeline builds.", data=data)

    async def get_jenkins_pipeline_build(self, request: Request, pipeline_id: int, build_id: int):
        await self._validate_user_access(request, pipeline_id)

        pipeline, client = await self._get_pipeline_and_client(pipeline_id)
        data = await client.get_pipeline_build(pipeline.name, build_id)
        return ok(message="Successfully provided jenkins pipeline build.", data=data)

    async def run_new_jenkins_pipeline_build(self, request: Request,
                                             pipeline_id: int, params: JenkinsStartPipelineParams):
        await self._validate_user_access(request, pipeline_id)

        pipeline, client = await self._get_pipeline_and_client(pipeline_id)
        await client.start_pipeline(pipeline.name, params.model_dump())
        return ok(message="Successfully started jenkins pipeline build.")

    async def cancel_jenkins_pipeline_build(self, request: Request, pipeline_id: int, build_id: int):
        await self._validate_user_access(request, pipeline_id)

        pipeline, client = await self._get_pipeline_and_client(pipeline_id)
        await client.cancel_pipeline(pipeline.name, build_id)
        return ok(message="Successfully canceled jenkins pipeline build.")

    async def get_jenkins_pipeline_params(self, request: Request, pipeline_id: int):
        await self._validate_user_access(request, pipeline_id)

        pipeline, client = await self._get_pipeline_and_client(pipeline_id)
        params = await client.get_pipeline_params(pipeline.name)
        return ok(message="Successfully provided jenkins pipeline params.", data=params)
