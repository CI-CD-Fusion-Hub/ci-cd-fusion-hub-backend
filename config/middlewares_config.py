from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from config.config import Settings

config = Settings().app


def configure(app: FastAPI):

    # Set default values
    allow_origins = ["*"]
    same_site_value = "Strict"
    ssl_cert = None
    ssl_key = None

    # Override values for non-prod environments
    if config["env"] != 'prod':
        allow_origins = ["http://10.90.90.3:5173"]
        same_site_value = "None"
        ssl_cert = "localhost.crt"
        ssl_key = "localhost.key"

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(SessionMiddleware,
                       secret_key=config['secret_key'],
                       https_only=True,
                       same_site=same_site_value,
                       max_age=int(config['session_lifetime']))
