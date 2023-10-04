from functools import wraps
from starlette.requests import Request
from config.config import Settings
from utils.logger import Logger
from utils.response import unauthorized

LOGGER = Logger().start_logger()
config = Settings()


def token_required(function_to_protect):
    @wraps(function_to_protect)
    async def wrapper(request: Request, *args, **kwargs):
        headers = request.headers

        if config.app['auth_header_name'] in headers and headers[config.app['auth_header_name']] in config.app['access_tokens']:
            return await function_to_protect(request, *args, **kwargs)

        return unauthorized()

    return wrapper
