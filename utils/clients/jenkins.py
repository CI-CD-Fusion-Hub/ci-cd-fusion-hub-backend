import asyncio
import base64
import re
from typing import List

import httpx
from fastapi import status

from daos.applications_dao import ApplicationDAO
from utils.clients.base import BaseClient


class JenkinsClient(BaseClient):
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

    async def check_connection(self):
        """Check if the provided Jenkins username and API token are valid."""
        try:
            response = await self._client.get(f"{self._base_url}/whoAmI/api/json")
            return response.status_code == status.HTTP_200_OK
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

    async def get_pipelines_list_by_pattern(self, regex_pattern: str) -> List:
        pipelines = await self.get_pipelines_list()

        if not pipelines:
            return []

        filtered_pipelines = []
        for pipeline in pipelines:
            if re.search(regex_pattern, pipeline['name']):
                filtered_pipelines.append(pipeline)

        return filtered_pipelines

    async def get_pipeline_builds(self, pipeline_name: str):
        """
        Fetch build information for specific pipeline/job.

        :param pipeline_name: Name of the Jenkins pipeline/job.
        :return: Dictionary containing build related information for specific pipeline/job.
        """
        result = (await self._client.get(
            f"{self._base_url}/job/{pipeline_name}/api/json?tree=name,buildable,builds[number,result,timestamp,duration]&pretty")
                  ).json()

        pipeline_result = []
        for build in result['builds']:
            pipeline_json = {
                "id": build['number'],
                "name": f"{result['name']} - {build['number']}",
                "status": 'running' if build['result'] is None else str(build['result']).lower(),
                "created_at": int(build['timestamp'] / 1000),
                "duration": int(build['duration'] / 1000)
            }

            pipeline_result.append(pipeline_json)

        return pipeline_result

    async def get_pipeline_build(self, pipeline_name: str, job_id: str):
        """
        Fetch build details and console log for a specific Jenkins job build.

        :param pipeline_name: Name of the Jenkins pipeline/job.
        :param job_id: ID of the specific build of the Jenkins job.
        :return: Dictionary containing build details and console log.
        """
        build_url = f"{self._base_url}/job/{pipeline_name}/{job_id}/api/json?tree=duration,fullDisplayName,result,timestamp&pretty"
        console_log_url = f"{self._base_url}/job/{pipeline_name}/{job_id}/consoleText"

        build_response, console_log_response = await asyncio.gather(
            self._client.get(build_url),
            self._client.get(console_log_url)
        )

        build = build_response.json()
        console_log = console_log_response.text.splitlines()

        if not build_response or not console_log_response:
            raise ValueError("Failed to fetch data from Jenkins")

        build_info = {
            "name": build['fullDisplayName'],
            "duration": int(build['duration'] / 1000),
            "created_at": int(build['timestamp'] / 1000),
            "status": 'running' if build['result'] is None else str(build['result']).lower(),
            "log": console_log
        }

        return build_info

    async def start_pipeline(self, pipeline_name: str, parameters: dict):
        pipeline_variables = await self.get_pipeline_params(pipeline_name)
        build_url = "buildWithParameters" if len(pipeline_variables) > 0 else "build"

        response = (await self._client.post(f"{self._base_url}/job/{pipeline_name}/{build_url}", json=parameters))
        if not response.is_success:
            raise ValueError("Failed to start Jenkins job.")

    async def get_pipeline_params(self, pipeline_name: str):
        result = (
            await self._client.get(f"{self._base_url}/job/{pipeline_name}/api/json?tree=property[*[*[*]]]")).json()

        variables = []
        for var in result['property']:
            if var['_class'] == 'hudson.model.ParametersDefinitionProperty':
                for variable in var['parameterDefinitions']:
                    if variable['type'] == 'ChoiceParameterDefinition':
                        variables.append({'key': variable['name'],
                                          'type': str(variable['type']).lower().split("parameter")[0],
                                          'value': variable['choices'], 'protected': False})
                    elif variable['type'] == 'PasswordParameterDefinition':
                        variables.append({'key': variable['name'],
                                          'type': str(variable['type']).lower().split("parameter")[0],
                                          'value': '',
                                          'protected': True})
                    else:
                        variables.append({'key': variable['name'],
                                          'type': str(variable['type']).lower().split("parameter")[0],
                                          'value': variable['defaultParameterValue']['value'], 'protected': False})

        return variables

    async def cancel_pipeline(self, pipeline_name: str, job_id: str):
        """
        Cancel a specific Jenkins pipeline job.

        :param pipeline_name: Name of the Jenkins pipeline.
        :param job_id: ID of the job to be canceled.
        :raises ValueError: If the request to stop the Jenkins job fails.
        """
        endpoint = f"{self._base_url}/job/{pipeline_name}/{job_id}/stop"
        response = await self._client.post(endpoint)

        if response.status_code in [200, 302]:
            return
        elif response.status_code == 404:  # Not Found
            raise ValueError(f"Jenkins job with ID {job_id} in pipeline {pipeline_name} not found.")
        else:
            raise ValueError(f"Failed to stop Jenkins job with ID {job_id} in pipeline {pipeline_name}.")
