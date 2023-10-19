from fastapi import FastAPI, Request
from exceptions.access_roles_exception import AccessRoleNotFoundException
from exceptions.application_exception import ApplicationNotFoundException
from exceptions.database_exception import DatabaseIntegrityException
from exceptions.pipeline_exceptions import PipelineNotFoundException
from exceptions.user_exception import UserNotFoundException
from utils.error_handlers import (http_exception_handler, user_exception_handler,
                                  application_exception_handler, access_roles_exception_handler,
                                  database_integrity_exception_handler, pipelines_exception_handler)


async def http_exception_handler_(request: Request, exc: Exception):
    return await http_exception_handler(request, exc)


async def user_exception_handler_(request: Request, exc: UserNotFoundException):
    return await user_exception_handler(request, exc)


async def application_exception_handler_(request: Request, exc: ApplicationNotFoundException):
    return await application_exception_handler(request, exc)


async def access_roles_exception_handler_(request: Request, exc: AccessRoleNotFoundException):
    return await access_roles_exception_handler(request, exc)


async def database_integrity_exception_handler_(request: Request, exc: DatabaseIntegrityException):
    return await database_integrity_exception_handler(request, exc)


async def pipelines_exception_handler_(request: Request, exc: PipelineNotFoundException):
    return await pipelines_exception_handler(request, exc)


def configure(app: FastAPI):
    app.exception_handler(Exception)(http_exception_handler_)
    app.exception_handler(UserNotFoundException)(user_exception_handler_)
    app.exception_handler(ApplicationNotFoundException)(application_exception_handler_)
    app.exception_handler(AccessRoleNotFoundException)(access_roles_exception_handler_)
    app.exception_handler(DatabaseIntegrityException)(database_integrity_exception_handler_)
    app.exception_handler(PipelineNotFoundException)(pipelines_exception_handler_)
