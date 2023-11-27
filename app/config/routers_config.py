from fastapi import FastAPI
from app.config.config import Settings

from app.routers import jenkins_pipelines_rt, pipelines_rt, applications_rt, auth_rt, status_rt, gitlab_pipelines_rt, \
    access_roles_rt, users_requests_rt, users_rt, github_pipelines_rt

config = Settings().app


def configure(app: FastAPI):
    app.include_router(auth_rt.router, prefix=config['root_path'])
    app.include_router(users_rt.router, prefix=config['root_path'])
    app.include_router(users_requests_rt.router, prefix=config['root_path'])
    app.include_router(status_rt.router, prefix=config['root_path'])
    app.include_router(applications_rt.router, prefix=config['root_path'])
    app.include_router(access_roles_rt.router, prefix=config['root_path'])
    app.include_router(gitlab_pipelines_rt.router, prefix=config['root_path'])
    app.include_router(github_pipelines_rt.router, prefix=config['root_path'])
    app.include_router(jenkins_pipelines_rt.router, prefix=config['root_path'])
    app.include_router(pipelines_rt.router, prefix=config['root_path'])
