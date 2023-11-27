import traceback
from fastapi import Request

from app.exceptions.access_roles_exception import AccessRoleNotFoundException
from app.exceptions.application_exception import ApplicationNotFoundException
from app.exceptions.custom_http_expeption import CustomHTTPException
from app.exceptions.database_exception import DatabaseIntegrityException
from app.exceptions.github_expeption import CustomGithubException
from app.exceptions.gitlab_exception import GitLabConnectionException
from app.exceptions.pipeline_exceptions import PipelineNotFoundException
from app.exceptions.user_exception import UserNotFoundException
from app.utils.response import error


async def exception_handler(request: Request, exc: Exception):
    traceback.print_exc()
    return error()


async def http_exception_handler(request: Request, exc: CustomHTTPException):
    traceback.print_exc()
    return error(message=exc.detail, status_code=exc.status_code)


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


async def github_exception_handler(request: Request, exc: CustomGithubException):
    traceback.print_exc()
    return error(message=exc.detail, status_code=exc.status_code)
