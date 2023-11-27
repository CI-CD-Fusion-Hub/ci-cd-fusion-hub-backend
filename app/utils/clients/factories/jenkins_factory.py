from app.schemas.applications_sch import ApplicationOut
from app.utils.clients.factories.base_factory import BaseClientFactory
from app.utils.clients.jenkins import JenkinsClient


class JenkinsClientFactory(BaseClientFactory):
    """Factory class to create Jenkins client instance."""
    async def create_client(self, application: ApplicationOut) -> JenkinsClient:
        """
        Create a Jenkins client based on the application details.
        :param application: The application details.
        :return: JenkinsClient: The Jenkins client instance.
        """
        return await JenkinsClient.from_application_id(application.id)
