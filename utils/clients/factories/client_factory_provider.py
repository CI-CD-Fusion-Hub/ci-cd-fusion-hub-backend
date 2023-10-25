from utils.clients.factories.github_factory import GithubClientFactory
from utils.clients.factories.gitlab_factory import GitlabClientFactory
from utils.clients.factories.jenkins_factory import JenkinsClientFactory
from utils.enums import AppType


class ClientFactoryProvider:
    """Provides the appropriate factory based on the application type."""
    factories = {
        AppType.GITLAB.value: GitlabClientFactory(),
        AppType.JENKINS.value: JenkinsClientFactory(),
        AppType.GITHUB.value: GithubClientFactory()
    }

    @classmethod
    def get_factory(cls, app_type: str):
        """
        Get the appropriate factory based on the application type.

        :param app_type: The application type (e.g., "GitLab", "Jenkins").
        :return: The factory instance.
        """
        return cls.factories.get(app_type)
