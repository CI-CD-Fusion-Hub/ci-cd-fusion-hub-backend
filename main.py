import asyncio

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy import create_engine

from exceptions.access_roles_exception import AccessRoleNotFoundException
from exceptions.application_exception import ApplicationNotFoundException
from exceptions.database_exception import DatabaseIntegrityException
from exceptions.user_exception import UserNotFoundException
from utils.cron import Cron
from utils.error_handlers import http_exception_handler, user_exception_handler, application_exception_handler, \
    access_roles_exception_handler, database_integrity_exception_handler
from models.db_models import Base
from utils.database import SQLALCHEMY_DATABASE_URL
from config.config import Settings

from routers import (
    status_rt,
    users_rt,
    applications_rt,
    access_roles_rt,
    pipelines_rt
)

###############
# Database Setup
###############
Base.metadata.create_all(bind=create_engine(SQLALCHEMY_DATABASE_URL))

###############
# Setup
###############
config = Settings().app
app = FastAPI(docs_url=f"{config['root_path']}/docs")
app.add_middleware(SessionMiddleware, secret_key=config['secret_key'], https_only=False)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

###############
# Routes
###############
app.include_router(users_rt.router, prefix=config['root_path'])
app.include_router(status_rt.router, prefix=config['root_path'])
app.include_router(applications_rt.router, prefix=config['root_path'])
app.include_router(access_roles_rt.router, prefix=config['root_path'])
app.include_router(pipelines_rt.router, prefix=config['root_path'])


###############
# Exception handlers
###############
@app.exception_handler(Exception)
async def handle_http_exception(request: Request, exc: Exception):
    return await http_exception_handler(request, exc)


@app.exception_handler(UserNotFoundException)
async def handle_http_exception(request: Request, exc: Exception):
    return await user_exception_handler(request, exc)


@app.exception_handler(ApplicationNotFoundException)
async def handle_http_exception(request: Request, exc: Exception):
    return await application_exception_handler(request, exc)


@app.exception_handler(AccessRoleNotFoundException)
async def handle_http_exception(request: Request, exc: Exception):
    return await access_roles_exception_handler(request, exc)


@app.exception_handler(DatabaseIntegrityException)
async def database_integrity_exception_(request: Request, exc: Exception):
    return await database_integrity_exception_handler(request, exc)


###############
# Cron jobs
###############
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(Cron.sync_pipelines(config['pipelines_sync_interval']))


@app.on_event("shutdown")
async def shutdown_event():
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

    [task.cancel() for task in tasks]

    await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    uvicorn.run(app, host=config['host'], port=config['port'])
