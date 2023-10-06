from daos.pipelines_dao import PipelineDAO
from exceptions.pipeline_exceptions import PipelineNotFoundException
from schemas.applications_sch import ApplicationOut
from schemas.pipelines_sch import PipelineOut, GitlabStartPipelineParams
from utils.enums import AppType
from utils.clients.gitlab import Gitlab
from utils.jenkins import Jenkins
from utils.response import ok, error


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

        return ok(message="Successfully provided pipeline.", data=PipelineOut.model_validate(pipeline.as_dict()))

    async def get_all_gitlab_pipelines(self):
        pipelines = await self.pipelines_dao.get_by_application_type(AppType.GITLAB.value)
        return ok(message="Successfully provided all gitlab pipelines.",
                  data=[PipelineOut.model_validate(pipeline.as_dict()) for pipeline in pipelines])

    async def get_gitlab_pipeline_builds(self, pipeline_id: int):
        pipeline = await self.pipelines_dao.get_by_id(pipeline_id)
        if not pipeline:
            raise PipelineNotFoundException(f"Pipeline with ID {pipeline} does not exist.")

        application = ApplicationOut.model_validate(pipeline.application.as_dict())
        client = await self.create_client(application)
        if not client:
            return error(message=f"Unable to connect to {application.type}.")

        data = await client.get_project_pipelines_list(pipeline.project_id)
        return ok(message="Successfully provided gitlab pipeline builds.", data=data)

    async def create_client(self, application: ApplicationOut):
        client = None
        if application.type == AppType.JENKINS.value:
            client = await Jenkins.from_application_id(application.id)
        elif application.type == AppType.GITLAB.value:
            client = await Gitlab.from_application_id(application.id)

        return client

    async def get_gitlab_pipeline_build(self, pipeline_id: int, build_id: int):
        pipeline = await self.pipelines_dao.get_by_id(pipeline_id)
        if not pipeline:
            raise PipelineNotFoundException(f"Pipeline with ID {pipeline} does not exist.")

        application = ApplicationOut.model_validate(pipeline.application.as_dict())
        client = await self.create_client(application)
        if not client:
            return error(message=f"Unable to connect to {application.type}.")

        data = await client.get_project_pipeline_info(pipeline.project_id, build_id)
        return ok(message="Successfully provided gitlab pipeline build.", data=data)

    async   def get_gitlab_pipeline_build_jobs(self, pipeline_id, build_id):
        pipeline = await self.pipelines_dao.get_by_id(pipeline_id)
        if not pipeline:
            raise PipelineNotFoundException(f"Pipeline with ID {pipeline} does not exist.")

        application = ApplicationOut.model_validate(pipeline.application.as_dict())
        client = await self.create_client(application)
        if not client:
            return error(message=f"Unable to connect to {application.type}.")

        data = await client.get_project_pipeline_jobs(pipeline.project_id, build_id)
        return ok(message="Successfully provided pipeline builds.", data=data)

    async def get_gitlab_pipeline_build_job_trace(self, pipeline_id: int, build_id: int, job_id: int):
        pipeline = await self.pipelines_dao.get_by_id(pipeline_id)
        if not pipeline:
            raise PipelineNotFoundException(f"Pipeline with ID {pipeline} does not exist.")

        application = ApplicationOut.model_validate(pipeline.application.as_dict())
        client = await self.create_client(application)
        if not client:
            return error(message=f"Unable to connect to {application.type}.")

        data = await client.get_project_pipeline_job_logs(pipeline.project_id, job_id)
        return ok(message="Successfully provided pipeline build stage.", data=data)

    async def run_new_gitlab_pipeline_build(self, pipeline_id, params: GitlabStartPipelineParams):
        pipeline = await self.pipelines_dao.get_by_id(pipeline_id)
        if not pipeline:
            raise PipelineNotFoundException(f"Pipeline with ID {pipeline} does not exist.")

        application = ApplicationOut.model_validate(pipeline.application.as_dict())
        client = await self.create_client(application)
        if not client:
            return error(message=f"Unable to connect to {application.type}.")

        data = await client.start_new_pipeline(pipeline.project_id, params.model_dump())
        return ok(message="Successfully provided gitlab pipeline build.", data=data)

    async def retry_gitlab_pipeline_build(self, pipeline_id, build_id):
        pipeline = await self.pipelines_dao.get_by_id(pipeline_id)
        if not pipeline:
            raise PipelineNotFoundException(f"Pipeline with ID {pipeline} does not exist.")

        application = ApplicationOut.model_validate(pipeline.application.as_dict())
        client = await self.create_client(application)
        if not client:
            return error(message=f"Unable to connect to {application.type}.")

        data = await client.retry_pipeline(pipeline.project_id, build_id)
        return ok(message="Successfully provided gitlab pipeline build.", data=data)

    async def cancel_gitlab_pipeline_build(self, pipeline_id, build_id):
        pipeline = await self.pipelines_dao.get_by_id(pipeline_id)
        if not pipeline:
            raise PipelineNotFoundException(f"Pipeline with ID {pipeline} does not exist.")

        application = ApplicationOut.model_validate(pipeline.application.as_dict())
        client = await self.create_client(application)
        if not client:
            return error(message=f"Unable to connect to {application.type}.")

        data = await client.cancel_pipeline(pipeline.project_id, build_id)
        return ok(message="Successfully provided gitlab pipeline build.", data=data)






