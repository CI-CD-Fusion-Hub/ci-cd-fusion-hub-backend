from app.schemas.applications_sch import ApplicationOut
from app.utils.clients.factories.base_factory import BaseClientFactory
from app.utils.clients.gitlab import GitlabClient


class GitlabClientFactory(BaseClientFactory):
    """Factory class to create Gitlab client instance."""
    async def create_client(self, application: ApplicationOut) -> GitlabClient:
        """
        Create a Gitlab client based on the application details.
        :param application: The application details.
        :return: GitlabClient: The Gitlab client instance.
        """
        return await GitlabClient.from_application_id(application.id)
