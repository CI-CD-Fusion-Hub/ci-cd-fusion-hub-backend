from fastapi import FastAPI, Request
from app.exceptions.access_roles_exception import AccessRoleNotFoundException
from app.exceptions.application_exception import ApplicationNotFoundException
from app.exceptions.custom_http_expeption import CustomHTTPException
from app.exceptions.database_exception import DatabaseIntegrityException
from app.exceptions.github_expeption import CustomGithubException
from app.exceptions.gitlab_exception import GitLabConnectionException
from app.exceptions.pipeline_exceptions import PipelineNotFoundException
from app.exceptions.user_exception import UserNotFoundException
from app.utils.error_handlers import (exception_handler, http_exception_handler, user_exception_handler,
                                      application_exception_handler, access_roles_exception_handler,
                                      database_integrity_exception_handler, pipelines_exception_handler,
                                      gitlab_exception_handler, github_exception_handler)


async def exception_handler_(request: Request, exc: Exception):
    return await exception_handler(request, exc)


async def http_exception_handler_(request: Request, exc: CustomHTTPException):
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


async def gitlab_exception_handler_(request: Request, exc: GitLabConnectionException):
    return await gitlab_exception_handler(request, exc)


async def github_exception_handler_(request: Request, exc: CustomGithubException):
    return await github_exception_handler(request, exc)


def configure(app: FastAPI):
    app.exception_handler(Exception)(exception_handler_)
    app.exception_handler(CustomHTTPException)(http_exception_handler_)
    app.exception_handler(UserNotFoundException)(user_exception_handler_)
    app.exception_handler(ApplicationNotFoundException)(application_exception_handler_)
    app.exception_handler(AccessRoleNotFoundException)(access_roles_exception_handler_)
    app.exception_handler(DatabaseIntegrityException)(database_integrity_exception_handler_)
    app.exception_handler(PipelineNotFoundException)(pipelines_exception_handler_)
    app.exception_handler(GitLabConnectionException)(gitlab_exception_handler_)
    app.exception_handler(CustomGithubException)(github_exception_handler_)

