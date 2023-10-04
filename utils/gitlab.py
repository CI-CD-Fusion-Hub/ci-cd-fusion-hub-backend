import httpx
from sqlalchemy import select

from daos.applications_dao import ApplicationDAO
from utils import database
from models import db_models as model


class Gitlab:
    def __init__(self, base_url: str, token: str, application_id: int = None):
        """Initialize the GitLab client."""
        self._client = httpx.AsyncClient(headers={'PRIVATE-TOKEN': token}, timeout=3)
        self._base_url = base_url
        self._app_id = application_id

    @classmethod
    async def from_application_id(cls, application_id: int):
        """Alternative constructor using application ID."""
        app = await ApplicationDAO().get_by_id(application_id)
        return cls(base_url=app.base_url, token=app.auth_pass, application_id=application_id)

    async def check_application_connection(self) -> bool:
        """Check if the provided GitLab private token is valid."""
        try:
            response = await self._client.get(url=f"{self._base_url}/user")
            return response.status_code == 200
        except httpx.RequestError:
            return False

    async def get_projects_list(self):
        try:
            result = await self._client.get(
                f"{self._base_url}/projects?per_page=100&page=1&order_by=id&sort=asc")

            projects = []
            for i in range(1, int(result.headers['X-Total-Pages'])):
                projects.append((await self._client.get(
                    f"{self._base_url}/projects?per_page=100&page={i + 1}&order_by=id&sort=asc")).json())

            all_projects = result.json()
            pipelines = []
            for pipeline in all_projects:
                pipelines.append({'id': pipeline['id'], 'name': pipeline['name'], 'app': self._app_id, 'type': 'gitlab'})

            return pipelines
        except httpx.RequestError:
            return []
        except ValueError:
            return []
