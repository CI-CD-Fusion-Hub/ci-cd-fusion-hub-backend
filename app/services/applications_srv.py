import re

from app.daos.applications_dao import ApplicationDAO
from app.daos.pipelines_dao import PipelineDAO
from app.exceptions.application_exception import ApplicationNotFoundException
from app.schemas.applications_sch import ApplicationOut, CreateApplication, UpdateApplication
from app.utils.clients.github import GithubClient
from app.utils.clients.gitlab import GitlabClient
from app.utils.clients.jenkins import JenkinsClient
from app.utils.enums import AppType, AppStatus
from app.utils.logger import Logger
from app.utils.pipeline_identifier import PipelineIdentifier
from app.utils.response import ok, error
from fastapi import status as Status

LOGGER = Logger().start_logger()


class ApplicationService:
    def __init__(self):
        self.app_dao = ApplicationDAO()
        self.pipelines_dao = PipelineDAO()

    @classmethod
    async def _get_client(cls, app_data: CreateApplication):
        client = None

        if app_data.type == AppType.GITLAB.value:
            LOGGER.info("Initializing GitLab client.")
            client = GitlabClient(base_url=app_data.base_url, token=app_data.auth_pass)
        if app_data.type == AppType.GITHUB.value:
            LOGGER.info("Initializing GitHub client.")
            client = GithubClient(base_url=app_data.base_url, token=app_data.auth_pass)
        elif app_data.type == AppType.JENKINS.value:
            LOGGER.info("Initializing Jenkins client.")
            client = JenkinsClient(base_url=app_data.base_url, user=app_data.auth_user, token=app_data.auth_pass)

        return client

    async def verify_application(self, app_data: CreateApplication):
        client = await self._get_client(app_data)
        if client is None:
            LOGGER.warning("No client initialized for the provided app type.")
            return error(message="Invalid application type provided.", status_code=Status.HTTP_400_BAD_REQUEST)

        if not await client.check_connection():
            LOGGER.warning(f"Application verification failed for {app_data.type}.")
            return error(message="Application is NOT accessible.", status_code=Status.HTTP_400_BAD_REQUEST)

        LOGGER.info(f"Application verification successful for {app_data.type}.")
        return ok(message="Application is accessible!")

    async def get_all_applications(self):
        applications = await self.app_dao.get_all()
        if not applications:
            LOGGER.info("No applications found in the database.")

        LOGGER.info(f"Retrieved {len(applications)} applications.")
        return ok(message="Successfully provided all applications.",
                  data=[ApplicationOut.model_validate(application.as_dict()) for application in applications])

    async def get_application_by_id(self, application_id: int):
        application = await self.app_dao.get_by_id(application_id)
        if not application:
            LOGGER.warning(f"Application with ID {application_id} not found.")
            raise ApplicationNotFoundException(f"Application with ID {application_id} does not exist.")

        LOGGER.info(f"Successfully retrieved application with ID {application_id}.")
        return ok(message="Successfully provided application.",
                  data=ApplicationOut.model_validate(application.as_dict()))

    async def create_application(self, app_data: CreateApplication):
        client = await self._get_client(app_data)
        if client is None:
            LOGGER.warning("No client initialized for the provided app type.")
            return error(message="Invalid application type provided.", status_code=Status.HTTP_400_BAD_REQUEST)

        if not await client.check_connection():
            LOGGER.warning("Application connection check failed.")
            return error(message="Application is NOT accessible.", status_code=Status.HTTP_400_BAD_REQUEST)

        application = await self.app_dao.create(app_data.model_dump())
        LOGGER.info(f"Successfully created application with type {app_data.type}.")
        return ok(message="Successfully created application.",
                  data=ApplicationOut.model_validate(application.as_dict()))

    async def delete_application(self, application_id: int):
        if not await self.app_dao.get_by_id(application_id):
            LOGGER.warning(f"Attempted to delete a non-existent application with ID {application_id}.")
            raise ApplicationNotFoundException(f"Application with ID {application_id} does not exist.")

        await self.app_dao.delete(application_id)
        LOGGER.info(f"Application with ID {application_id} has been successfully deleted.")

        return ok(message="Application has been successfully deleted.")

    async def update_application(self, application_id: int, app_data: UpdateApplication):
        application = await self.app_dao.get_by_id(application_id)
        if not application:
            LOGGER.warning(f"Application with ID {application_id} not found.")
            raise ApplicationNotFoundException(f"Application with ID {application_id} does not exist.")

        data_to_update = {k: v for k, v in app_data.model_dump().items() if v is not None}
        application = await self.app_dao.update(application_id, data_to_update)

        if application.status != AppStatus.ACTIVE.value:
            return ok(message="Successfully updated application.",
                      data=ApplicationOut.model_validate(application.as_dict()))

        LOGGER.debug(f"Updating application `{application.name}` pipelines.")

        existing_pipelines_in_db = await self.pipelines_dao.get_by_application_id(application_id)
        fetched_app_pipelines = await PipelineIdentifier.fetch_pipelines_from_application(application)

        pipelines_to_delete = await PipelineIdentifier.identify_old_pipelines(existing_pipelines_in_db,
                                                                              fetched_app_pipelines)
        LOGGER.debug(f"Identified {len(pipelines_to_delete)} pipelines to delete.")

        existing_pipeline_names = {f"{pipeline.name}-{pipeline.application_id}" for pipeline in
                                   existing_pipelines_in_db}
        new_pipelines = await PipelineIdentifier.identify_new_pipelines(fetched_app_pipelines, existing_pipeline_names)
        LOGGER.debug(f"Identified {len(new_pipelines)} new pipelines.")

        pipeline_ids_to_delete = [p.id for p in pipelines_to_delete]
        pipeline_ids_to_delete_by_pattern = [pipeline.id for pipeline in existing_pipelines_in_db
                                             if not re.search(app_data.regex_pattern, pipeline.name)]
        ids_to_delete = list(set(pipeline_ids_to_delete + pipeline_ids_to_delete_by_pattern))

        LOGGER.debug(f"Deleting {len(ids_to_delete)} pipelines.")
        await self.pipelines_dao.delete_multiple(ids_to_delete)

        if new_pipelines:
            LOGGER.debug(f"Creating {len(new_pipelines)} new pipelines.")
            await self.pipelines_dao.create_bulk(new_pipelines)
        else:
            LOGGER.debug("No new pipelines to be added.")

        return ok(message="Successfully updated application.",
                  data=ApplicationOut.model_validate(application.as_dict()))
