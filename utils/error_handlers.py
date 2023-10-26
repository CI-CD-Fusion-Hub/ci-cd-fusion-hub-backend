import traceback
from fastapi import Request

from exceptions.access_roles_exception import AccessRoleNotFoundException
from exceptions.application_exception import ApplicationNotFoundException
from exceptions.custom_http_expeption import CustomHTTPException
from exceptions.database_exception import DatabaseIntegrityException
from exceptions.gitlab_exception import GitLabConnectionException
from exceptions.pipeline_exceptions import PipelineNotFoundException
from exceptions.user_exception import UserNotFoundException
from utils.response import error


async def exception_handler(request: Request, exc: Exception):
    traceback.print_exc()
    return error()


async def http_exception_handler(request: Request, exc: CustomHTTPException):
    traceback.print_exc()
    return error(exc.detail, exc.status_code)


async def user_exception_handler(request: Request, exc: UserNotFoundException):
    traceback.print_exc()
    return error(message=exc.detail)


async def application_exception_handler(request: Request, exc: ApplicationNotFoundException):
    traceback.print_exc()
    return error(message=exc.detail)


async def access_roles_exception_handler(request: Request, exc: AccessRoleNotFoundException):
    traceback.print_exc()
    return error(message=exc.detail)


async def database_integrity_exception_handler(request: Request, exc: DatabaseIntegrityException):
    traceback.print_exc()
    return error(message=exc.detail)


async def pipelines_exception_handler(request: Request, exc: PipelineNotFoundException):
    traceback.print_exc()
    return error(message=exc.detail)


async def gitlab_exception_handler(request: Request, exc: GitLabConnectionException):
    traceback.print_exc()
    return error(message=exc.detail)
