from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from utils.logger import Logger
from config.config import Settings

config = Settings().database
LOGGER = Logger().start_logger()

SQLALCHEMY_DATABASE_URL = f"postgresql://{config['user']}:{config['password']}@{config['host']}/{config['name']}"
SQLALCHEMY_ASYNC_DATABASE_URL = f"postgresql+asyncpg://{config['user']}:{config['password']}@{config['host']}/{config['name']}"

engine = create_async_engine(SQLALCHEMY_ASYNC_DATABASE_URL,
                             pool_size=100,
                             max_overflow=2,
                             pool_pre_ping=True,
                             pool_use_lifo=True)

SessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()


def convert_params(params):
    new_params = {}
    for key, value in params.items():
        if value.isdigit():
            new_params[key] = int(value)
        else:
            new_params[key] = value
    return new_params
