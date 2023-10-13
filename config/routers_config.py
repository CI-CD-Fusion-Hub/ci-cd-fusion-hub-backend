from fastapi import FastAPI
from config.config import Settings

from routers import (
    status_rt,
    users_rt,
    applications_rt,
    access_roles_rt,
    pipelines_rt,
    auth_rt
)

config = Settings().app


def configure(app: FastAPI):
    app.include_router(users_rt.router, prefix=config['root_path'])
    app.include_router(status_rt.router, prefix=config['root_path'])
    app.include_router(applications_rt.router, prefix=config['root_path'])
    app.include_router(access_roles_rt.router, prefix=config['root_path'])
    app.include_router(pipelines_rt.router, prefix=config['root_path'])
    app.include_router(auth_rt.router, prefix=config['root_path'])
