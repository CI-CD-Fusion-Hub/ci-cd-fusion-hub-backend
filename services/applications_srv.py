from daos.applications_dao import ApplicationDAO
from exceptions.application_exception import ApplicationNotFoundException
from schemas.applications_sch import ApplicationOut, CreateApplication, UpdateApplication
from utils.enums import AppType
from utils.clients.gitlab import GitlabClient
from utils.clients.jenkins import JenkinsClient
from utils.response import ok, error


class ApplicationService:
    def __init__(self):
        self.app_dao = ApplicationDAO()

    async def get_all_applications(self):
        applications = await self.app_dao.get_all()
        return ok(message="Successfully provided all applications.",
                  data=[ApplicationOut.model_validate(application.as_dict()) for application in applications])

    async def get_application_by_id(self, application_id: int):
        application = await self.app_dao.get_by_id(application_id)
        if not application:
            raise ApplicationNotFoundException(f"Application with ID {application_id} does not exist.")

        return ok(message="Successfully provided application.",
                  data=ApplicationOut.model_validate(application.as_dict()))

    async def create_application(self, app_data: CreateApplication):
        application = await self.app_dao.create(app_data.model_dump())
        return ok(message="Successfully created application.", data=ApplicationOut.model_validate(application.as_dict()))

    async def delete_application(self, application_id: int):
        if not await self.app_dao.get_by_id(application_id):
            raise ApplicationNotFoundException(f"Application with ID {application_id} does not exist.")
        await self.app_dao.delete(application_id)

        return ok(message="Application has been successfully deleted.")

    async def update_application(self, application_id: int, app_data: UpdateApplication):
        application = await self.app_dao.get_by_id(application_id)
        if not application:
            raise ApplicationNotFoundException(f"Application with ID {application_id} does not exist.")

        data_to_update = app_data.model_dump()
        data_to_update = {k: v for k, v in data_to_update.items() if v is not None}

        application = await self.app_dao.update(application_id, data_to_update)

        return ok(message="Successfully updated application.", data=ApplicationOut.model_validate(application.as_dict()))

    @staticmethod
    async def verify_application(app_data: CreateApplication):
        client = None

        if app_data.type == AppType.GITLAB.value:
            client = GitlabClient(base_url=app_data.base_url, token=app_data.auth_pass)
        elif app_data.type == AppType.JENKINS.value:
            client = JenkinsClient(base_url=app_data.base_url, user=app_data.auth_user, token=app_data.auth_pass)

        if client is None:
            return error(message="Invalid application type provided.")

        if await client.check_application_connection():
            return ok(message="Application is accessible!")
        else:
            return error(message="Application is NOT accessible.")





