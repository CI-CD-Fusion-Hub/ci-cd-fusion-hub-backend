import uvicorn
from fastapi import FastAPI
from config import middlewares_config as middlewares, \
    exception_handlers_config as exception_handlers, \
    routers_config as routers, events_config as events

from config.config import Settings


config = Settings().app
app = FastAPI(docs_url=f"{config['root_path']}/docs")

middlewares.configure(app)
routers.configure(app)
exception_handlers.configure(app)
events.configure(app)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=config['host'],
        port=int(config['port']),
        ssl_keyfile=config.get('ssl_key', None),
        ssl_certfile=config.get('ssl_cert', None)
    )
