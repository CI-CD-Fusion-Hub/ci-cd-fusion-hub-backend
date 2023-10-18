from functools import wraps

from starlette.requests import Request
from config.config import Settings
from daos.users_dao import UserDAO
from utils.enums import AccessLevel, UserStatus
from utils.logger import Logger
from utils.response import unauthorized

LOGGER = Logger().start_logger()
config = Settings()


def auth_required(function_to_protect):
    @wraps(function_to_protect)
    async def wrapper(request: Request, *args, **kwargs):
        email = request.session.get("USER_NAME")
        if not email:
            return unauthorized()

        user_dao = UserDAO()
        user = await user_dao.get_detailed_user_info_by_email(email)
        if not user:
            return unauthorized()

        if user.status != UserStatus.ACTIVE.value:
            return unauthorized()

        request.session['ACCESS_LEVEL'] = user.access_level
        request.session['ID'] = user.id
        return await function_to_protect(request, *args, **kwargs)

    return wrapper


def admin_access_required(function_to_protect):
    @wraps(function_to_protect)
    async def wrapper(request: Request, *args, **kwargs):
        if request.session.get('ACCESS_LEVEL') == AccessLevel.ADMIN.value:
            return await function_to_protect(request, *args, **kwargs)

        return unauthorized()

    return wrapper


# Optimize this
async def get_user_pipelines(request: Request):
    email = request.session.get("USER_NAME")

    if not email:
        return unauthorized()

    user_dao = UserDAO()
    user = await user_dao.get_detailed_user_info_by_email(email)
    if not user:
        return unauthorized()

    pipelines = set()
    for role_member in user.roles:
        for pipeline in role_member.role.pipelines:
            pipelines.add(pipeline.pipeline.id)

    return list(pipelines)
