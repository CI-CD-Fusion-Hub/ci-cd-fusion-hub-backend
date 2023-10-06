import re
from datetime import datetime

import httpx

from daos.applications_dao import ApplicationDAO
from utils.enums import AppType


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

    @staticmethod
    def escape_ansi(line):
        ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
        return ansi_escape.sub('', line)

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
                pipelines.append({'id': pipeline['id'], 'name': pipeline['name'], 'app': self._app_id,
                                  'type': AppType.GITLAB.value})

            return pipelines
        except httpx.RequestError:
            return []
        except ValueError:
            return []

    async def get_project_pipelines_list(self, project_id: str):
        result = (await self._client.get(f"{self._base_url}/projects/{project_id}/pipelines?simple=true")).json()
        pipeline_result = []
        for pipeline in result:
            pipeline_json = {
                "id": pipeline['id'],
                "status": pipeline['status'],
                "commit_msg": None,
                "duration": 0,
                "stages": [],
                "created_at": int(datetime.fromisoformat(pipeline['created_at']).timestamp())
            }

            pipeline_result.append(pipeline_json)

        result = (await self._client.get(f"{self._base_url}/projects/{project_id}/jobs")).json()
        for index, pipeline in enumerate(pipeline_result):
            for stage in result:
                if stage['pipeline']['id'] == int(pipeline["id"]):
                    pipeline_result[index]["duration"] += stage["duration"]
                    pipeline_result[index]["commit_msg"] = stage["commit"]["title"]
                    pipeline_result[index]['stages'].append(
                        {"id": stage['id'], "name": stage['stage'], "status": stage['status']})

            pipeline_result[index]["duration"] = int(pipeline_result[index]["duration"])

        return pipeline_result

    async def get_project_pipeline_info(self, project_id: str, pipeline_id: int):
        result = (await self._client.get(f"{self._base_url}/projects/{project_id}/pipelines/{pipeline_id}"))

        if result.status_code != 200:
            return []

        return result.json()

    async def get_project_pipeline_jobs(self, project_id: str, pipeline_id: int):
        result = (await self._client.get(f"{self._base_url}/projects/{project_id}/pipelines/{pipeline_id}/jobs"))

        if result.status_code != 200:
            return []

        return result.json()

    async def get_project_pipeline_job_logs(self, project_id: str, stage_id: str):
        result = (await self._client.get(f"{self._base_url}/projects/{project_id}/jobs/{stage_id}")).json()
        result['log'] = self.escape_ansi(
            (await self._client.get(f"{self._base_url}/projects/{project_id}/jobs/{stage_id}/trace")).text).splitlines()

        return result

    async def start_new_pipeline(self, project_id: int, params: dict):
        variables = []

        if params and params != {}:
            for variable in params['parameters']:
                if variable == 'branch':
                    branch = params['parameters'][variable]

                variables.append({
                    'key': variable,
                    'value': str(params['parameters'][variable])
                })

        result = (await self._client.post(
            f"{self._base_url}/projects/{project_id}/pipeline?ref={params['parameters']['branch']}",
            json={'variables': variables})).json()

        return result

    async def retry_pipeline(self, project_id: str, pipeline_id: int):
        result = (await self._client.post(
            f"{self._base_url}/projects/{project_id}/pipelines/{pipeline_id}/retry")).json()

        return result

    async def cancel_pipeline(self, project_id: str, pipeline_id: int):
        result = (await self._client.post(
            f"{self._base_url}/projects/{project_id}/pipelines/{pipeline_id}/cancel")).json()

        return result

    async def delete_pipeline(self, project_id: str, pipeline_id: int):
        result = (await self._client.delete(
            f"{self._base_url}/projects/{project_id}/pipelines/{pipeline_id}")).text

        return result




