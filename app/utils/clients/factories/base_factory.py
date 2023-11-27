from abc import ABC, abstractmethod
from app.schemas.applications_sch import ApplicationOut


class BaseClientFactory(ABC):
    """Abstract base class to client factory"""
    @abstractmethod
    async def create_client(self, application: ApplicationOut):
        """
        Abstract method to create a client based on the application details.
        :param application: The application details.
        :return: The client instance.
        """
        pass
