from functools import wraps

from starlette.requests import Request
from config.config import Settings
from daos.users_dao import UserDAO
from utils.enums import AccessLevel, UserStatus, SessionAttributes
from utils.logger import Logger
from utils.response import unauthorized

LOGGER = Logger().start_logger()
config = Settings()


def auth_required(function_to_protect):
    @wraps(function_to_protect)
    async def wrapper(request: Request, *args, **kwargs):
        email = request.session.get(SessionAttributes.USER_NAME.value)
        if not email:
            return unauthorized()

        user_dao = UserDAO()
        user = await user_dao.get_detailed_user_info_by_email(email)
        if not user:
            return unauthorized()

        if user.status != UserStatus.ACTIVE.value:
            return unauthorized()

        pipelines = set()
        roles = set()
        for role_member in user.roles:
            roles.add(role_member.role.id)
            for pipeline in role_member.role.pipelines:
                pipelines.add(pipeline.pipeline.id)

        request.session[SessionAttributes.USER_ACCESS_LEVEL.value] = user.access_level
        request.session[SessionAttributes.USER_ID.value] = user.id
        request.session[SessionAttributes.USER_ROLES.value] = list(roles)
        request.session[SessionAttributes.USER_PIPELINES.value] = list(pipelines)
        return await function_to_protect(request, *args, **kwargs)

    return wrapper


def admin_access_required(function_to_protect):
    @wraps(function_to_protect)
    async def wrapper(request: Request, *args, **kwargs):
        if request.session.get(SessionAttributes.USER_ACCESS_LEVEL.value) == AccessLevel.ADMIN.value:
            return await function_to_protect(request, *args, **kwargs)

        return unauthorized()

    return wrapper
