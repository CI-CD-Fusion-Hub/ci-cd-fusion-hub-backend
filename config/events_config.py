import asyncio
from sqlalchemy import create_engine

from utils.cron import Cron
from config.config import Settings
from models.db_models import Base
from utils.database import SQLALCHEMY_DATABASE_URL

config = Settings().app


async def startup_event():
    # Database setup
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    Base.metadata.create_all(bind=engine)

    # Start pipeline sync
    asyncio.create_task(Cron.sync_pipelines(config['pipelines_sync_interval']))


async def shutdown_event():
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks, return_exceptions=True)


def configure(app):
    app.add_event_handler("startup", startup_event)
    app.add_event_handler("shutdown", shutdown_event)
