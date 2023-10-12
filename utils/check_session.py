from functools import wraps
from starlette.requests import Request
from config.config import Settings
from utils.logger import Logger
from utils.response import unauthorized

LOGGER = Logger().start_logger()
config = Settings()


# This approach is fast but consider check if user is inactive(This will cause call to DB every request)
def auth_required(function_to_protect):
    @wraps(function_to_protect)
    async def wrapper(request: Request, *args, **kwargs):
        if request.session.get('USER_NAME'):
            return await function_to_protect(request, *args, **kwargs)

        return unauthorized()

    return wrapper

