import threading
import traceback
from asyncio import sleep
from typing import List, Dict, Set

from daos.applications_dao import ApplicationDAO
from daos.pipelines_dao import PipelineDAO
from utils.enums import AppType
from utils.clients.gitlab import Gitlab
from utils.jenkins import Jenkins
from utils.logger import Logger

LOGGER = Logger().start_logger()


class Cron:

    @staticmethod
    async def _fetch_pipelines_from_applications(applications: List) -> List[Dict]:
        fetched_pipelines = []
        for application in applications:
            if application.type == AppType.JENKINS.value:
                fetched_pipelines += await Cron._fetch_from_jenkins(application)
            elif application.type == AppType.GITLAB.value:
                fetched_pipelines += await Cron._fetch_from_gitlab(application)
        return fetched_pipelines

    @staticmethod
    async def _fetch_from_jenkins(application) -> List[Dict]:
        LOGGER.debug(f"Going to fetch application of type: {application.type}")
        jenkins_client = await Jenkins.from_application_id(application.id)
        jenkins_pipelines = await jenkins_client.get_pipelines_list()
        LOGGER.debug(f"Fetched {len(jenkins_pipelines)} pipelines from Jenkins for application ID: {application.name}")
        return jenkins_pipelines

    @staticmethod
    async def _fetch_from_gitlab(application) -> List[Dict]:
        LOGGER.debug(f"Going to fetch application of type: {application.type}")
        gitlab_client = await Gitlab.from_application_id(application.id)
        gitlab_pipelines = await gitlab_client.get_projects_list()
        LOGGER.debug(f"Fetched {len(gitlab_pipelines)} pipelines from GitLab for application ID: {application.name}")
        return gitlab_pipelines

    @staticmethod
    async def _identify_new_pipelines(fetched_pipelines: List[Dict], existing_pipeline_names: Set[str]) -> List[Dict]:
        new_pipelines = []
        unique_names = set()
        for fetched_pipeline in fetched_pipelines:
            unique_name = f"{fetched_pipeline['name']}-{fetched_pipeline['app']}"
            if unique_name not in existing_pipeline_names and unique_name not in unique_names:
                new_pipeline = {"name": fetched_pipeline['name'], "application_id": fetched_pipeline['app'],
                                "project_id": str(fetched_pipeline['id'])}
                new_pipelines.append(new_pipeline)
                unique_names.add(unique_name)
                LOGGER.debug(f"Identified new pipeline: {unique_name}")
        return new_pipelines

    @staticmethod
    async def sync_pipelines(interval: int):
        while True:
            LOGGER.debug(f"Pipelines sync has started in a `Thread` with ID - {threading.get_ident()}")
            try:
                pipeline_dao = PipelineDAO()
                LOGGER.debug("Fetching all applications and pipelines from the database.")
                applications = await ApplicationDAO().get_all()
                pipelines = await pipeline_dao.get_all()
                existing_pipeline_names = {f"{pipeline.name}-{pipeline.application_id}" for pipeline in pipelines}

                fetched_pipelines = await Cron._fetch_pipelines_from_applications(applications)
                new_pipelines = await Cron._identify_new_pipelines(fetched_pipelines, existing_pipeline_names)

                if new_pipelines:
                    await pipeline_dao.create_bulk(new_pipelines)
                    LOGGER.debug(f"Added {len(new_pipelines)} new pipelines to the database.")
                else:
                    LOGGER.debug("No new pipelines to be added.")

                LOGGER.debug(f"Next synchronization will be executed after {interval} seconds.")
            except Exception as e:
                traceback.print_exc()
                LOGGER.error(f"Pipelines sync has failed. Please, check what is going on: {e}")

            await sleep(interval)
