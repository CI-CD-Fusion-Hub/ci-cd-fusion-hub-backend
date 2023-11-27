from app.schemas.applications_sch import ApplicationOut
from app.utils.clients.base import BaseClient
from app.utils.clients.factories.client_factory_provider import ClientFactoryProvider


class ClientManager:
    @staticmethod
    async def create_client(application: ApplicationOut) -> BaseClient:
        factory = ClientFactoryProvider.get_factory(application.type)
        if not factory:
            raise ValueError(f"No factory found for application type {application.type}")
        return await factory.create_client(application)
