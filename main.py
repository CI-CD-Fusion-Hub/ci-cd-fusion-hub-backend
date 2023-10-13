import uvicorn
from fastapi import FastAPI
from config import middlewares_config, exception_handlers_config, routers_config, event_config

from config.config import Settings


config = Settings().app
app = FastAPI(docs_url=f"{config['root_path']}/docs")

middlewares_config.configure(app)
routers_config.configure(app)
exception_handlers_config.configure(app)
event_config.configure_events(app)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=config['host'],
        port=int(config['port']),
        ssl_keyfile=config.get('ssl_key', None),
        ssl_certfile=config.get('ssl_cert', None)
    )
