import asyncio
import base64
import datetime
import json
import re
from typing import List, Dict

import httpx
from fastapi import status

from daos.applications_dao import ApplicationDAO
from exceptions.custom_http_expeption import CustomHTTPException
from exceptions.github_expeption import CustomGithubException
from utils.clients.base import BaseClient
from utils.enums import AppType


class GitHubErrorMessages:
    INVALID_DATA = "Invalid data received from GitHub"
    CONNECTION_ERROR = "Could not connect to GitHub"


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
            return response.status_code == status.HTTP_200_OK
        except httpx.RequestError:
            return False

    async def check_connection_to_org_repos(self, org_name) -> bool:
        """Check if the token has access to the specified GitHub organization repositories."""
        response = await self._client.get(f"{self._base_url}/orgs/{org_name}/repos")

        if response.status_code == status.HTTP_200_OK:
            return True
        else:
            return False

    async def get_pipelines_list(self) -> List:
        """Fetch all repositories the authenticated user has access to."""
        try:
            response = await self._client.get(f"{self._base_url}/user/repos")
            response.raise_for_status()
            pipelines = response.json()
            updated_pipelines = []
            for pipeline in pipelines:
                url = f"{self._base_url}/repositories/{pipeline['id']}/actions/workflows"
                response = await self._client.get(url)
                response.raise_for_status()

                workflows = response.json()["workflows"]
                for workflow in workflows:
                    updated_pipelines.append({'id': pipeline["id"], 'name': f"[{pipeline['name']}] {workflow['name']}",
                                              'app': self._app_id, 'type': AppType.GITHUB.value})

            return updated_pipelines
        except httpx.RequestError:
            raise CustomGithubException(
                detail=GitHubErrorMessages.INVALID_DATA,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception:
            raise CustomHTTPException(
                detail=GitHubErrorMessages.CONNECTION_ERROR,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    async def get_pipelines_list_by_pattern(self, regex_pattern: str) -> List:
        """Fetch all repositories by regex_pattern."""
        pipelines = await self.get_pipelines_list()
        if not pipelines:
            return []

        filtered_pipelines = []

        for pipeline in pipelines:
            if re.search(regex_pattern, pipeline["name"]):
                filtered_pipelines.append(pipeline)

        return filtered_pipelines

    async def get_project_pipelines_list(self, project_id: str, workflow_name: str) -> List:
        """Get information about a project's pipelines."""
        try:
            workflows_url = f"{self._base_url}/repositories/{project_id}/actions/workflows"
            workflow_response = await self.get_json(workflows_url)
            workflows = workflow_response.get("workflows", [])
            # Reformat workflow name since it is at pipeline creation
            workflow_name = workflow_name.split("] ")[1]
            workflow = next(
                (workflow for workflow in workflows if workflow['name'] == workflow_name),
                None
            )

            runs_url = f"{self._base_url}/repositories/{project_id}/actions/runs?workflow_id={workflow['id']}"
            runs_response = await self.get_json(runs_url)
            runs = runs_response.get("workflow_runs", [])

            workflow_runs = []
            job_tasks = []
            for run in runs:
                run_id = run["id"]
                job_url = f"{self._base_url}/repositories/{project_id}/actions/runs/{run_id}/jobs"
                job_tasks.append(self.get_json(job_url))

            job_data_list = await asyncio.gather(*job_tasks)

            for run, job_data in zip(runs, job_data_list):
                run_id = run["id"]
                run_status = run["conclusion"]
                commit_msg = run["head_commit"]["message"]

                created_at = run["created_at"]

                duration = 0
                stages = []
                for job in job_data["jobs"]:
                    stage_name = job["name"]
                    stage_status = job["conclusion"]
                    started_at = job["started_at"]
                    completed_at = job["completed_at"]

                    stage_duration = 0
                    if started_at and completed_at:
                        started_at_time = datetime.datetime.fromisoformat(started_at.replace("Z", ""))
                        completed_at_time = datetime.datetime.fromisoformat(completed_at.replace("Z", ""))
                        stage_duration = (completed_at_time - started_at_time).total_seconds()
                        duration += int(stage_duration)

                    stages.append({
                        "id": job["id"],
                        "name": stage_name,
                        "status": stage_status,
                        "started_at": started_at,
                        "duration": int(stage_duration)
                    })

                workflow_runs.append({
                    "id": run_id,
                    "status": run_status,
                    "commit_msg": commit_msg,
                    "duration": int(duration),
                    "stages": stages,
                    "created_at": int(datetime.datetime.fromisoformat(created_at).timestamp())
                })

            return workflow_runs

        except httpx.RequestError:
            raise CustomGithubException(
                detail=GitHubErrorMessages.INVALID_DATA,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        except Exception:
            raise CustomHTTPException(
                detail=GitHubErrorMessages.CONNECTION_ERROR,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    async def get_project_pipeline_info(self, project_id: str, run_id: int) -> Dict:
        """Get information about a project's pipeline run."""
        try:
            data = {}
            run_info_url = f"{self._base_url}/repositories/{project_id}/actions/runs/{run_id}"
            job_url = f"{self._base_url}/repositories/{project_id}/actions/runs/{run_id}/jobs"

            run_data, job_data = await asyncio.gather(
                self.get_json(run_info_url),
                self.get_json(job_url)
            )

            stages = []
            duration = 0
            for job in job_data["jobs"]:
                stage_name = job["name"]
                stage_status = job["conclusion"]
                started_at = job["started_at"]
                completed_at = job["completed_at"]

                stage_duration = None
                if started_at and completed_at:
                    started_at_time = datetime.datetime.fromisoformat(started_at.replace("Z", ""))
                    completed_at_time = datetime.datetime.fromisoformat(completed_at.replace("Z", ""))
                    stage_duration = (completed_at_time - started_at_time).total_seconds()
                    duration += int(stage_duration)

                stages.append({
                    "id": job["id"],
                    "name": stage_name,
                    "status": stage_status,
                    "started_at": started_at,
                    "duration": int(stage_duration)
                })

            data["id"] = run_id
            data["status"] = run_data['conclusion']
            data["commit_msg"] = run_data['head_commit']['message']
            data["stages"] = stages
            data["duration"] = duration
            data["created_at"] = int(datetime.datetime.fromisoformat(run_data['created_at']).timestamp())
            return data
        except httpx.RequestError:
            raise CustomGithubException(
                detail=GitHubErrorMessages.INVALID_DATA,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception:
            raise CustomHTTPException(
                detail=GitHubErrorMessages.CONNECTION_ERROR,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    async def get_pipeline_params(self, project_id: str):
        """Get Github pipeline parameters."""
        try:
            repo_variables_url = f"{self._base_url}/repositories/{project_id}/actions/variables"
            repo_branches_url = f"{self._base_url}/repositories/{project_id}/branches"
            repo_variables = await self.get_json(repo_variables_url)
            repo_branches = await self.get_json(repo_branches_url)

            variables = [{'key': 'branch', 'type': 'choice', 'value': [x['name']
                                                                       for x in repo_branches], 'required': True}]

            for variable in repo_variables['variables']:
                variables.append(
                    {'key': variable['name'], 'type': 'string', 'value': variable['value'], 'required': False})

            parameters_file_url = f"{self._base_url}/repositories/{project_id}/contents/parameters.json"
            parameters_file_resp = await self._client.get(parameters_file_url)

            if parameters_file_resp.status_code != 200:
                return variables

            file_content_base64 = parameters_file_resp.json()['content']
            file_content_bytes = base64.b64decode(file_content_base64)
            file_content = file_content_bytes.decode('utf-8')
            for param in json.loads(file_content)['parameters']:
                if param['id'] != 'branch':
                    variables.append(
                        {
                            'key': param.get('id'),
                            'type': param.get('type'),
                            'value': param.get('value'),
                            'description': param.get('description'),
                            'depends_on': param.get('depends_on'),
                            'required': param.get('required', False)
                        }
                    )

            return variables
        except httpx.RequestError:
            raise CustomGithubException(
                detail=GitHubErrorMessages.INVALID_DATA,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception:
            raise CustomHTTPException(
                detail=GitHubErrorMessages.CONNECTION_ERROR,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    async def start_new_pipeline(self, workflow_name: str, project_id: int, params: dict):
        """Start GitHub pipeline."""
        try:
            url = f"{self._base_url}/repositories/{project_id}/actions/workflows"
            workflow_response = await self.get_json(url)
            workflows = workflow_response.get("workflows", [])
            # Reformat workflow name since it is at pipeline creation
            workflow_name = workflow_name.split("] ")[1]

            workflow_info = next(
                (workflow for workflow in workflows if workflow["name"] == workflow_name),
                None
            )

            ref = str(params.get("branch", "main"))
            inputs = {key: value for key, value in params.items() if key != "branch"}
            variables = {"ref": ref, "inputs": inputs}

            response = await self._client.post(f"{workflow_info['url']}/dispatches", json=variables)
            response.raise_for_status()

            return response.text
        except httpx.RequestError:
            raise CustomGithubException(
                detail=GitHubErrorMessages.INVALID_DATA,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception:
            raise CustomHTTPException(
                detail=GitHubErrorMessages.CONNECTION_ERROR,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    async def retry_pipeline(self, project_id: str, run_id: int):
        """Retry GitHub pipeline."""
        try:
            url = f"{self._base_url}/repositories/{project_id}/actions/runs/{run_id}/rerun"

            response = await self._client.post(url)
            response.raise_for_status()
        except httpx.RequestError:
            raise CustomGithubException(
                detail=GitHubErrorMessages.INVALID_DATA,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception:
            raise CustomHTTPException(
                detail=GitHubErrorMessages.CONNECTION_ERROR,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    async def cancel_pipeline(self, project_id: str, run_id: int):
        """Cancel Github pipeline."""
        try:
            url = f"{self._base_url}/repositories/{project_id}/actions/runs/{run_id}/cancel"

            response = await self._client.post(url)
            response.raise_for_status()
        except httpx.RequestError:
            raise CustomGithubException(
                detail=GitHubErrorMessages.INVALID_DATA,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception:
            raise CustomHTTPException(
                detail=GitHubErrorMessages.CONNECTION_ERROR,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    async def get_project_pipeline_jobs(self, project_id: str, run_id: int):
        """Get Github pipeline jobs."""
        try:
            url = f"{self._base_url}/repositories/{project_id}/actions/runs/{run_id}/jobs"
            result = self.get_json(url)
            return result
        except httpx.RequestError:
            raise CustomGithubException(
                detail=GitHubErrorMessages.INVALID_DATA,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception:
            raise CustomHTTPException(
                detail=GitHubErrorMessages.CONNECTION_ERROR,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    async def get_project_pipeline_job_logs(self, project_id: str, job_id: str):
        """Get GitHub pipeline job logs."""
        try:
            job_info_url = f"{self._base_url}/repositories/{project_id}/actions/jobs/{job_id}"
            logs_url = f"{self._base_url}/repositories/{project_id}/actions/jobs/{job_id}/logs"

            job_info = await self.get_json(job_info_url)
            logs_response = (await self._client.get(logs_url, follow_redirects=True))
            logs_response.raise_for_status()

            job_info['log'] = self.escape_ansi(logs_response.text).splitlines()

            return job_info
        except httpx.RequestError:
            raise CustomGithubException(
                detail=GitHubErrorMessages.INVALID_DATA,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception:
            raise CustomHTTPException(
                detail=GitHubErrorMessages.CONNECTION_ERROR,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    async def get_json(self, url: str):
        response = await self._client.get(url)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def escape_ansi(line: str) -> str:
        """Remove ANSI escape codes from a text line.
        Args:
            line (str): The input text line containing ANSI escape codes.
        Returns:
            str: The text line with ANSI escape codes removed.
        """
        ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
        return ansi_escape.sub('', line)
