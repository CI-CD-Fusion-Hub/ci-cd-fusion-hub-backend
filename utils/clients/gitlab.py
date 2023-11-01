import json
import re
from datetime import datetime
from typing import List, Dict

import httpx
from fastapi import status

from daos.applications_dao import ApplicationDAO
from exceptions.custom_http_expeption import CustomHTTPException
from exceptions.gitlab_exception import GitLabConnectionException
from utils.clients.base import BaseClient
from utils.enums import AppType

INVALID_DATA_ERROR = "Invalid data received from GitLab."


class GitlabClient(BaseClient):

    async def check_connection(self):
        """Check if the provided GitLab private token is valid."""
        try:
            response = await self._client.get(url=f"{self._base_url}/user")
            return response.status_code == 200
        except httpx.RequestError:
            return False

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

    async def get_pipelines_list(self) -> List:
        """Get all pipelines from Gitlab."""
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
            raise GitLabConnectionException(detail=f"Failed to connect to GitLab - {self._base_url}.")
        except ValueError:
            raise CustomHTTPException(
                detail=INVALID_DATA_ERROR,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    async def get_project_pipelines_list(self, project_id: str) -> List:
        """Get all pipelines for specific project."""
        try:
            pipelines = \
                (await self._client.get(f"{self._base_url}/projects/{project_id}/pipelines?simple=true"))

            pipelines_json = pipelines.json()
            if pipelines.status_code != 200:
                raise GitLabConnectionException(detail=f"Failed to connect to GitLab - {self._base_url}. "
                                                       f"Message - {pipelines_json}.")

            pipeline_result = []
            for pipeline in pipelines_json:
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
                # store the latest job for each stage
                stage_latest_jobs = {}
                for job in result:
                    if job['pipeline']['id'] == int(pipeline["id"]):
                        stage_name = job['stage']
                        # check if this job is more recent than the stored job for the same stage
                        if stage_name not in stage_latest_jobs \
                                or job['created_at'] > stage_latest_jobs[stage_name]['created_at']:
                            stage_latest_jobs[stage_name] = job

                for stage_name, job in stage_latest_jobs.items():
                    job["duration"] = 0 if not job['duration'] else int(job["duration"])

                    pipeline_result[index]["duration"] += job["duration"]
                    pipeline_result[index]["commit_msg"] = job["commit"]["title"]
                    pipeline_result[index]['stages'].append({
                        "id": job['id'],
                        "name": stage_name,
                        "status": job['status'],
                        "started_at": job['started_at'],
                        "duration": int(job["duration"])
                    })

                pipeline_result[index]['stages'] = pipeline_result[index]['stages'][::-1]
                pipeline_result[index]["duration"] = int(pipeline_result[index]["duration"])

            return pipeline_result
        except httpx.RequestError:
            raise GitLabConnectionException(detail=f"Failed to connect to GitLab - {self._base_url}.")
        except ValueError:
            raise CustomHTTPException(
                detail=INVALID_DATA_ERROR,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    async def get_pipelines_list_by_pattern(self, regex_pattern: str) -> List:
        """Get all pipelines for specific project by regex pattern."""
        pipelines = await self.get_pipelines_list()

        if not pipelines:
            return []

        filtered_pipelines = []
        for pipeline in pipelines:
            if re.search(regex_pattern, pipeline["name"]):
                filtered_pipelines.append(pipeline)

        return filtered_pipelines

    async def get_project_pipeline_info(self, project_id: str, pipeline_id: int) -> Dict:
        """Get GitLab pipeline information"""
        try:
            stages = (
                await self._client.get(f"{self._base_url}/projects/{project_id}/pipelines/{pipeline_id}/jobs")).json()

            if not stages:
                return {}

            first_stage = stages[0]

            pipeline_json = {
                "id": first_stage['pipeline']['id'],
                "status": first_stage['pipeline']['status'],
                "commit_msg": first_stage["commit"]["title"],
                "duration": 0,
                "stages": [],
                "created_at": int(datetime.fromisoformat(first_stage['pipeline']['created_at']).timestamp())
            }

            for stage in stages:
                if stage["duration"]:
                    pipeline_json["duration"] += int(stage["duration"])
                else:
                    stage["duration"] = 0

                pipeline_json['stages'].append(
                    {
                        "id": stage['id'],
                        "name": stage['stage'],
                        "status": stage['status'],
                        "duration": int(stage["duration"]),
                        "started_at": stage['started_at'] if stage['started_at'] else None
                    })

            pipeline_json['stages'] = pipeline_json['stages'][::-1]
            pipeline_json["duration"] = int(pipeline_json["duration"])

            return pipeline_json
        except httpx.RequestError:
            raise GitLabConnectionException(detail=f"Failed to connect to GitLab - {self._base_url}.")
        except ValueError:
            raise CustomHTTPException(
                detail=INVALID_DATA_ERROR,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    async def get_project_pipeline_jobs(self, project_id: str, pipeline_id: int) -> List:
        """Get GitLab pipeline jobs."""
        try:
            result = (await self._client.get(f"{self._base_url}/projects/{project_id}/pipelines/{pipeline_id}/jobs"))

            if result.status_code != 200:
                return []

            return result.json()
        except httpx.RequestError:
            raise GitLabConnectionException(detail=f"Failed to connect to GitLab - {self._base_url}.")
        except ValueError:
            raise CustomHTTPException(
                detail=INVALID_DATA_ERROR,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    async def get_project_pipeline_job_logs(self, project_id: str, stage_id: str) -> List:
        """Get GitLab pipeline job logs."""
        try:
            result = (await self._client.get(f"{self._base_url}/projects/{project_id}/jobs/{stage_id}")).json()
            result['log'] = self.escape_ansi(
                (await self._client.get(
                    f"{self._base_url}/projects/{project_id}/jobs/{stage_id}/trace")).text).splitlines()

            return result
        except httpx.RequestError:
            raise GitLabConnectionException(detail=f"Failed to connect to GitLab - {self._base_url}.")
        except ValueError:
            raise CustomHTTPException(
                detail=INVALID_DATA_ERROR,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    async def start_new_pipeline(self, project_id: int, params: dict):
        """Start GitLab pipeline."""
        try:
            variables = []

            if params and params != {}:
                for variable in params:
                    variables.append({
                        'key': variable,
                        'value': str(params[variable])
                    })

            result = (await self._client.post(
                f"{self._base_url}/projects/{project_id}/pipeline?ref={params['branch']}",
                json={'variables': variables})).json()

            return result
        except httpx.RequestError:
            raise GitLabConnectionException(detail=f"Failed to connect to GitLab - {self._base_url}.")
        except ValueError:
            raise CustomHTTPException(
                detail=INVALID_DATA_ERROR,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    async def retry_pipeline(self, project_id: str, pipeline_id: int):
        """Retry GitLab pipeline."""
        try:
            result = (await self._client.post(
                f"{self._base_url}/projects/{project_id}/pipelines/{pipeline_id}/retry")).json()

            return result
        except httpx.RequestError:
            raise GitLabConnectionException(detail=f"Failed to connect to GitLab - {self._base_url}.")
        except ValueError:
            raise CustomHTTPException(
                detail=INVALID_DATA_ERROR,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    async def cancel_pipeline(self, project_id: str, pipeline_id: int):
        """Cancel GitLab pipeline."""
        try:
            result = (await self._client.post(
                f"{self._base_url}/projects/{project_id}/pipelines/{pipeline_id}/cancel")).json()

            return result
        except httpx.RequestError:
            raise GitLabConnectionException(detail=f"Failed to connect to GitLab - {self._base_url}.")
        except ValueError:
            raise CustomHTTPException(
                detail=INVALID_DATA_ERROR,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    async def delete_pipeline(self, project_id: str, pipeline_id: int):
        """Delete GitLab pipeline."""
        try:
            result = (await self._client.delete(
                f"{self._base_url}/projects/{project_id}/pipelines/{pipeline_id}")).text

            return result
        except httpx.RequestError:
            raise GitLabConnectionException(detail=f"Failed to connect to GitLab - {self._base_url}.")
        except ValueError:
            raise CustomHTTPException(
                detail=INVALID_DATA_ERROR,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    async def get_pipeline_params(self, project_id: str):
        """Get GitLab pipeline parameters."""
        try:
            test = (await self._client.get(
                f"{self._base_url}/projects/{project_id}/repository/files/parameters.json/raw")).text

            result = (await self._client.get(f"{self._base_url}/projects/{project_id}/variables")).json()
            branches = (await self._client.get(f"{self._base_url}/projects/{project_id}/repository/branches")).json()

            variables = [{'key': 'branch', 'type': 'choice', 'value': [x['name']
                                                                       for x in branches], 'protected': False}]
            if 'message' not in result:
                for var in result:
                    print(var)
                    variables.append(
                        {'key': var['key'], 'type': 'string', 'value': var['value'], 'protected': var['protected']})

                if 'message' not in test:
                    for param in json.loads(test)['parameters']:
                        if param['id'] != 'branch':
                            variables.append(
                                {
                                    'key': param['id'],
                                    'type': param['type'],
                                    'value': param['value'],
                                    'description': param.get('description'),
                                    'depends_on': param.get('depends_on'),
                                    'protected': False
                                }
                            )

            return variables
        except httpx.RequestError:
            raise GitLabConnectionException(detail=f"Failed to connect to GitLab - {self._base_url}.")
        except ValueError:
            raise CustomHTTPException(
                detail=INVALID_DATA_ERROR,
                status_code=status.HTTP_400_BAD_REQUEST
            )
