import base64

import httpx

from daos.applications_dao import ApplicationDAO


class Jenkins:
    def __init__(self, base_url: str, user: str, token: str, application_id: int = None):
        """Initialize the Jenkins client."""
        self._user = user
        self._base_url = base_url
        self._token = token
        self._client = httpx.AsyncClient(headers=self._generate_credentials(), timeout=3)
        self._app_id = application_id

    @classmethod
    async def from_application_id(cls, application_id: int):
        """Alternative constructor using application ID."""
        app = await ApplicationDAO().get_by_id(application_id)
        return cls(base_url=app.base_url, user=app.auth_user, token=app.auth_pass, application_id=application_id)

    def _generate_credentials(self) -> dict:
        """Generate the Authorization header using the provided user and token."""
        credentials = base64.b64encode(f"{self._user}:{self._token}".encode()).decode()
        return {
            "Authorization": f"Basic {credentials}"
        }

    async def check_application_connection(self) -> bool:
        """Check if the provided Jenkins username and API token are valid."""
        try:
            response = await self._client.get(f"{self._base_url}/whoAmI/api/json")
            return response.status_code == 200
        except httpx.RequestError:
            return False

    async def get_pipelines_list(self):
        try:
            result = (await self._client.get(
                f"{self._base_url}/api/json?tree=jobs[fullName,jobs[fullName,jobs[fullName,jobs[fullName,jobs[fullName]]]]]")).json()

            pipelines = []
            for pipeline in result['jobs']:
                if pipeline['_class'] == 'com.cloudbees.hudson.plugins.folder.Folder':
                    for job in pipeline['jobs']:
                        pipelines.append(
                            {'id': job['fullName'], 'name': job['fullName'], 'app': self._app_id, 'type': 'jenkins'})
                else:
                    pipelines.append({'id': pipeline['fullName'], 'name': pipeline['fullName'], 'app': self._app_id,
                                      'type': 'jenkins'})

            return pipelines

        except httpx.RequestError:
            return []
        except ValueError:
            return []
