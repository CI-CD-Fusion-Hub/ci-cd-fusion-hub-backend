import threading
import traceback
from asyncio import sleep
from typing import List, Dict, Set

from daos.applications_dao import ApplicationDAO
from daos.pipelines_dao import PipelineDAO
from schemas.applications_sch import ApplicationOut
from utils.clients.client_manager import ClientManager
from utils.logger import Logger

LOGGER = Logger().start_logger()


class Cron:
    def __init__(self, pipeline_dao=None, application_dao=None):
        self.pipeline_dao = pipeline_dao or PipelineDAO()
        self.application_dao = application_dao or ApplicationDAO()

    @classmethod
    async def _fetch_pipelines_from_applications(cls, applications: List) -> List[Dict]:
        fetched_pipelines = []
        for application in applications:
            LOGGER.debug(f"Going to fetch application of type: {application.type}")

            application_out = ApplicationOut.model_validate(application.as_dict())
            client = await ClientManager().create_client(application_out)

            if application.regex_pattern:
                pipelines = await client.get_pipelines_list_by_pattern(application.regex_pattern)
            else:
                pipelines = await client.get_pipelines_list()

            fetched_pipelines.extend(pipelines)

            LOGGER.debug(f"Fetched {len(pipelines)} pipelines from {application.type} for application ID: "
                         f"{application.name}")

        return fetched_pipelines

    @classmethod
    async def _identify_new_pipelines(cls, fetched_pipelines: List[Dict],
                                      existing_pipeline_names: Set[str]) -> List[Dict]:
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

    async def sync_pipelines(self, interval: int):
        while True:
            LOGGER.debug(f"Pipelines sync has started in a `Thread` with ID - {threading.get_ident()}")
            try:
                pipeline_dao = PipelineDAO()
                LOGGER.debug("Fetching all applications and pipelines from the database.")
                applications = await self.application_dao.get_all()
                pipelines = await self.pipeline_dao.get_all()
                existing_pipeline_names = {f"{pipeline.name}-{pipeline.application_id}" for pipeline in pipelines}

                fetched_pipelines = await self._fetch_pipelines_from_applications(applications)
                new_pipelines = await self._identify_new_pipelines(fetched_pipelines, existing_pipeline_names)

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
