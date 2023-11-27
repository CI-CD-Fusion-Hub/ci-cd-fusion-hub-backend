import threading
import traceback
from asyncio import sleep

from app.daos.applications_dao import ApplicationDAO
from app.daos.pipelines_dao import PipelineDAO
from app.utils.enums import AppStatus
from app.utils.logger import Logger
from app.utils.pipeline_identifier import PipelineIdentifier

LOGGER = Logger().start_logger()


class Cron:
    def __init__(self, pipeline_dao=None, application_dao=None):
        self.pipeline_dao = pipeline_dao or PipelineDAO()
        self.application_dao = application_dao or ApplicationDAO()

    async def sync_pipelines(self, interval: int):
        while True:
            LOGGER.debug(f"Pipelines sync has started in a `Thread` with ID - {threading.get_ident()}")
            try:
                pipeline_dao = PipelineDAO()
                LOGGER.debug("Fetching all applications and pipelines from the database.")
                applications = await self.application_dao.get_all_by_status(AppStatus.ACTIVE.value)
                pipelines = await self.pipeline_dao.get_by_application_status(AppStatus.ACTIVE.value)
                existing_pipeline_names = {f"{pipeline.name}-{pipeline.application_id}" for pipeline in pipelines}

                fetched_pipelines = await PipelineIdentifier.fetch_pipelines_from_applications(applications)
                new_pipelines = await PipelineIdentifier.identify_new_pipelines(fetched_pipelines,
                                                                                existing_pipeline_names)

                pipeline_ids_to_delete = [p.id for p in
                                          await PipelineIdentifier.identify_old_pipelines(pipelines, fetched_pipelines)]

                if pipeline_ids_to_delete:
                    LOGGER.debug(f"Identified {len(pipeline_ids_to_delete)} pipelines to delete. Deleting..")
                    await self.pipeline_dao.delete_multiple(pipeline_ids_to_delete)

                if new_pipelines:
                    await pipeline_dao.create_bulk(new_pipelines)
                    LOGGER.debug(f"Added {len(new_pipelines)} new pipelines to the database.")

                LOGGER.debug(f"Next synchronization will be executed after {interval} seconds.")
            except Exception as e:
                traceback.print_exc()
                LOGGER.error(f"Pipelines sync has failed. Please, check what is going on: {e}")

            await sleep(interval)
