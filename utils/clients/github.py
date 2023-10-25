import re
from typing import List

import httpx

from daos.applications_dao import ApplicationDAO
from utils.clients.base import BaseClient
from utils.enums import AppType


class GithubClient(BaseClient):
    def __init__(self, base_url: str, token: str, application_id: int = None):
        """Initialize the GitHub client."""
        self._client = httpx.AsyncClient(
            headers={'Authorization': f"token {token}", 'Accept': 'application/vnd.github.v3+json'},
            timeout=3
        )
        self._base_url = base_url
        self._app_id = application_id

    @classmethod
    async def from_application_id(cls, application_id: int):
        """Alternative constructor using application ID."""
        app = await ApplicationDAO().get_by_id(application_id)
        return cls(base_url=app.base_url, token=app.auth_pass, application_id=application_id)

    async def check_connection(self):
        """Check if the provided GitLab private token is valid."""
        try:
            response = await self._client.get(url=f"{self._base_url}/user")
            return response.status_code == 200
        except httpx.RequestError:
            return False

    async def check_connection_to_org_repos(self, org_name) -> bool:
        """
        Check if the token has access to the specified GitHub organization repositories.
        """
        response = await self._client.get(f"{self._base_url}/orgs/{org_name}/repos")

        if response.status_code == 200:
            return True
        else:
            return False

    async def get_pipelines_list(self) -> List:
        """
        Fetch all repositories the authenticated user has access to.
        """
        try:
            response = await self._client.get(f"{self._base_url}/user/repos")
            response.raise_for_status()
            pipelines = response.json()

            updated_pipelines = []
            for pipeline in pipelines:
                updated_pipelines.append({'id': pipeline['id'], 'name': pipeline['name'], 'app': self._app_id,
                                          'type': AppType.GITLAB.value})

            return updated_pipelines
        except httpx.RequestError:
            return []
        except ValueError:
            return []

    async def get_pipelines_list_by_pattern(self, regex_pattern: str) -> List:
        """
        Fetch all repositories by regex_pattern.
        """
        pipelines = await self.get_pipelines_list()
        if not pipelines:
            return []

        filtered_pipelines = []

        for pipeline in pipelines:
            if re.search(regex_pattern, pipeline["name"]):
                filtered_pipelines.append(pipeline)

        return filtered_pipelines




