from app.schemas.applications_sch import ApplicationOut
from app.utils.clients.factories.base_factory import BaseClientFactory
from app.utils.clients.github import GithubClient


class GithubClientFactory(BaseClientFactory):
    """Factory class to create Gitlab client instance."""
    async def create_client(self, application: ApplicationOut) -> GithubClient:
        """
        Create a Gitlab client based on the application details.
        :param application: The application details.
        :return: GitlabClient: The Gitlab client instance.
        """
        return await GithubClient.from_application_id(application.id)
