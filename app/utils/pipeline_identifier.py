from typing import List, Dict, Set

from app.utils.clients.client_manager import ClientManager
from app.utils.logger import Logger
from app.models import db_models as model

LOGGER = Logger().start_logger()


class PipelineIdentifier:
    @classmethod
    async def identify_old_pipelines(cls, existing_pipelines: List[model.Pipelines],
                                     fetched_pipelines: List[Dict]) -> List[model.Pipelines]:
        """
        Find old pipelines by comparing existing and fetched pipelines.

        :param existing_pipelines: List of existing pipeline objects.
        :param fetched_pipelines: List of fetched pipeline dictionaries.
        :return: List of old pipeline objects.
        """
        fetched_pipeline_names = {f"{pipeline['name']}-{pipeline['app']}" for pipeline in fetched_pipelines}

        old_pipelines = [
            existing_pipeline for existing_pipeline in existing_pipelines
            if f"{existing_pipeline.name}-{existing_pipeline.application_id}" not in fetched_pipeline_names
        ]

        return old_pipelines

    @classmethod
    async def fetch_pipelines_from_applications(cls, applications: List[model.Applications]) -> List[Dict]:
        """
        Fetch pipelines from multiple applications.

        :param applications: List of application objects.
        :return: List of fetched pipeline dictionaries.
        """
        fetched_pipelines = []
        for application in applications:
            pipelines = await cls.fetch_pipelines_from_application(application)
            fetched_pipelines.extend(pipelines)

        return fetched_pipelines

    @classmethod
    async def fetch_pipelines_from_application(cls, application: model.Applications) -> List[Dict]:
        """
        Fetch pipelines for a single application.

        :param application: Application object.
        :return: List of fetched pipeline dictionaries.
        """
        LOGGER.debug(f"Fetching pipelines for application: {application.name}")

        client = await ClientManager().create_client(application)

        if application.regex_pattern:
            pipelines = await client.get_pipelines_list_by_pattern(application.regex_pattern)
        else:
            pipelines = await client.get_pipelines_list()

        LOGGER.debug(f"Fetched {len(pipelines)} pipelines for application: {application.name}")

        return pipelines

    @classmethod
    async def identify_new_pipelines(cls, fetched_pipelines: List[Dict],
                                     existing_pipeline_names: Set[str]) -> List[Dict]:
        """
        Find new pipelines from fetched pipelines.

        :param fetched_pipelines: List of fetched pipeline dictionaries.
        :param existing_pipeline_names: Set of existing pipeline names.
        :return: List of new pipeline dictionaries.
        """
        new_pipelines = []
        unique_names = set()

        for fetched_pipeline in fetched_pipelines:
            unique_name = f"{fetched_pipeline['name']}-{fetched_pipeline['app']}"
            if unique_name not in existing_pipeline_names and unique_name not in unique_names:
                new_pipeline = {
                    "name": fetched_pipeline['name'],
                    "application_id": fetched_pipeline['app'],
                    "project_id": str(fetched_pipeline['id'])
                }
                new_pipelines.append(new_pipeline)
                unique_names.add(unique_name)
                LOGGER.debug(f"Identified new pipeline: {unique_name}")

        return new_pipelines
