import hashlib

from fastapi import Request
from fastapi import status as Status

from app.daos.pipelines_dao import PipelineDAO
from app.daos.users_requests_dao import UserRequestsDAO
from app.exceptions.user_exception import UserNotFoundException
from app.schemas.pipelines_sch import PipelineOut
from app.schemas.users_requests_sch import UsersRequestOut, User, Pipeline, UpdateUsersRequest, CreateUsersRequest
from app.schemas.users_sch import CreateUser, UserOut, UpdateUser, UserBaseOut, UpdateUserProfile
from app.daos.users_dao import UserDAO
from app.utils.enums import AccessLevel, SessionAttributes, RequestStatus, AuthMethods, AppStatus
from app.utils.logger import Logger
from app.utils.response import ok, error

LOGGER = Logger().start_logger()


class UserService:
    def __init__(self):
        self.user_dao = UserDAO()
        self.user_requests_dao = UserRequestsDAO()
        self.pipelines_dao = PipelineDAO()

    @classmethod
    async def get_user_info_from_request(cls, request):
        return ok(
            message="Successfully provided user details.",
            data=request.session.get(SessionAttributes.USER_INFO.value)
        )

    @classmethod
    def _has_pipeline_access(cls, user_pipelines, pipeline_ids):
        return bool(user_pipelines.intersection(pipeline_ids))

    @classmethod
    def _get_existing_request_pipelines(cls, user_requests, pipeline_ids):
        existing_pipelines = {
            pipeline.pipeline.name
            for user_request in user_requests
            for pipeline in user_request.pipelines
            if pipeline.pipeline.id in pipeline_ids and user_request.status == RequestStatus.PENDING.value
        }
        return existing_pipelines

    async def get_all_users(self):
        users = await self.user_dao.get_all()
        LOGGER.info("Successfully retrieved all users.")

        return ok(message="Successfully provided all users.",
                  data=[UserBaseOut.model_validate(user.as_dict()) for user in users])

    async def get_user_by_id(self, request: Request, user_id: int):
        user_access_level_session = request.session.get(SessionAttributes.USER_ACCESS_LEVEL.value)
        user_id_session = request.session.get(SessionAttributes.USER_ID.value)

        if user_access_level_session != AccessLevel.ADMIN.value and user_id_session != user_id:
            LOGGER.warning(f"Access denied for user ID {user_id}")
            raise UserNotFoundException(f"User with ID {user_id} does not exist.")

        user = await self.user_dao.get_detailed_user_info(user_id)
        if not user:
            LOGGER.warning(f"User with ID {user_id} does not exist.")
            raise UserNotFoundException(f"User with ID {user_id} does not exist.")

        user_data = UserOut.model_validate(user.as_dict())

        user_data.roles = [role_member.role.as_dict() for role_member in user.roles]

        pipelines = []
        for role_member in user.roles:
            for pipeline in role_member.role.pipelines:
                pipelines.append(pipeline.pipeline)

        user_data.pipelines = list(pipelines)
        LOGGER.info(f"Successfully retrieved details for user ID {user_id}.")
        return ok(message="Successfully provided user details.", data=user_data)

    async def create_user(self, request: Request, user_data: CreateUser):
        try:
            auth_method = request.session.get(SessionAttributes.AUTH_METHOD.value)

            if auth_method != AuthMethods.LOCAL.value:
                LOGGER.info(f"Creating user with non-local auth method: {auth_method}")
                user_data.password = ""
                user = await self.user_dao.create(user_data)
                return ok(
                    message="Successfully created user.",
                    data=UserOut.model_validate(user.as_dict())
                )

            if not user_data.password:
                LOGGER.warning("Attempt to create user without a password")
                return error(
                    message="Password is required.",
                    status_code=Status.HTTP_400_BAD_REQUEST
                )

            LOGGER.info("Creating user with local auth method")
            user_data.password = hashlib.sha512(user_data.password.encode('utf-8')).hexdigest()
            user = await self.user_dao.create(user_data)
            return ok(
                message="Successfully created user.",
                data=UserOut.model_validate(user.as_dict())
            )

        except ValueError as e:
            LOGGER.error(f"ValueError in create_user: {e}")
            return error(message=str(e))

    async def update_user(self, user_id: int, user_data: UpdateUser | UpdateUserProfile):
        user = await self.user_dao.get_by_id(user_id)
        if not user:
            LOGGER.warning(f"User with ID {user_id} does not exist.")
            raise UserNotFoundException(f"User with ID {user_id} does not exist.")

        if user_data.password:
            LOGGER.info("Updating password for user")
            user_data.password = hashlib.sha512(user_data.password.encode('utf-8')).hexdigest()

        data_to_update = user_data.model_dump()
        data_to_update = {k: v for k, v in data_to_update.items() if v is not None and k != "confirm_password"}

        user = await self.user_dao.update(user_id, data_to_update)

        LOGGER.info(f"Successfully updated user ID {user_id}.")
        return ok(message="Successfully updated user.", data=UserOut.model_validate(user.as_dict()))

    async def delete_user(self, user_id: int):
        if not await self.user_dao.get_by_id(user_id):
            LOGGER.warning(f"Attempted to delete a non-existent user with ID {user_id}.")
            return error(
                message=f"User with ID {user_id} does not exist.",
                status_code=Status.HTTP_404_NOT_FOUND
            )

        await self.user_dao.delete(user_id)
        LOGGER.info(f"User with ID {user_id} has been successfully deleted.")
        return ok(message="User has been successfully deleted.")

    async def fetch_user_unassigned_roles(self, user_id: int):
        unassigned_roles = await self.user_dao.get_user_unassigned_roles(user_id)
        return ok(message="Successfully provided unassigned users for access role.",
                  data=[role.as_dict() for role in unassigned_roles])

    async def get_user_requests(self, request):
        user_id_session = request.session.get(SessionAttributes.USER_ID.value)
        users_requests = await self.user_requests_dao.get_all()

        if not users_requests:
            LOGGER.info("No user requests found in the database.")
            return ok(message="No user requests available.", data=[])

        filtered_requests = [user_request for user_request in users_requests if
                             user_request.user_id == user_id_session]

        if not filtered_requests:
            LOGGER.info(f"No user requests found for user ID {user_id_session}.")
            return ok(message="No user requests available for the user.", data=[])

        users_requests_data = []
        for user_request in filtered_requests:
            users_request_data = UsersRequestOut.model_validate(user_request.as_dict())
            users_request_data.user = User(email=user_request.user.email, id=user_request.user.id)
            users_request_data.pipelines = [(Pipeline(name=pipeline.pipeline.name, id=pipeline.pipeline.id))
                                            for pipeline in user_request.pipelines]
            users_requests_data.append(users_request_data)

        LOGGER.info(f"Successfully retrieved user requests for user ID {user_id_session}.")
        return ok(
            message="Successfully provided all users requests.",
            data=[user_requests
                  for user_requests in users_requests_data]
        )

    async def update_user_requests(self, request_id: int, users_request_data: UpdateUsersRequest):
        user_request = await self.user_requests_dao.get_detailed_users_request_info_by_id(request_id)
        if not user_request:
            LOGGER.warning(f"User request with ID {request_id} does not exist.")
            return error(
                message=f"User request with ID {request_id} does not exist.",
                status_code=Status.HTTP_404_NOT_FOUND
            )

        if user_request.status != RequestStatus.PENDING.value \
                or users_request_data.status == RequestStatus.COMPLETED.value \
                or users_request_data.status == RequestStatus.DECLINED.value \
                or users_request_data.status == RequestStatus.INPROGRESS.value:
            LOGGER.warning("User request cannot be edited due to its status.")
            return error(
                message="User request cannot be edited.",
                status_code=Status.HTTP_400_BAD_REQUEST
            )

        user_request_data_pipelines = set(users_request_data.pipelines)
        existing_request_pipelines = set(p.pipeline_id for p in user_request.pipelines)
        to_be_add = user_request_data_pipelines - existing_request_pipelines
        to_be_remove = existing_request_pipelines - user_request_data_pipelines

        pipeline_ids_to_add = list(to_be_add)
        pipeline_ids_to_remove = list(to_be_remove)

        updated_data = users_request_data.model_dump(exclude={'pipelines'})
        await self.user_requests_dao.update(request_id, updated_data)
        LOGGER.info(f"User request with ID {request_id} updated.")

        if pipeline_ids_to_add:
            await self.user_requests_dao.add_pipelines_to_request(request_id, pipeline_ids_to_add)
            LOGGER.debug(f"Pipelines added to request ID {request_id}: {pipeline_ids_to_add}")

        if pipeline_ids_to_remove:
            await self.user_requests_dao.remove_pipelines_from_request(request_id, pipeline_ids_to_remove)
            LOGGER.debug(f"Pipelines removed from request ID {request_id}: {pipeline_ids_to_remove}")

        return ok(message="Successfully updated user request.")

    async def create_user_requests(self, request: Request, users_request_data: CreateUsersRequest):
        user_id = request.session.get(SessionAttributes.USER_ID.value)
        user_pipelines = set(request.session.get(SessionAttributes.USER_PIPELINES.value))
        users_request_data.user_id = user_id

        if self._has_pipeline_access(user_pipelines, users_request_data.pipelines):
            LOGGER.warning(f"User {user_id} already has access to some provided pipelines.")
            return error(
                message="User already has access to some of the provided pipelines.",
                status_code=Status.HTTP_400_BAD_REQUEST
            )

        user_requests = await self.user_requests_dao.get_detailed_users_request_info_by_user_id(user_id)

        existing_user_request_pipelines = \
            self._get_existing_request_pipelines(user_requests, users_request_data.pipelines)
        if existing_user_request_pipelines:
            LOGGER.warning(f"User {user_id} already has a request for {existing_user_request_pipelines}.")
            return error(
                message=f"User already have request created for {existing_user_request_pipelines}.",
                status_code=Status.HTTP_400_BAD_REQUEST
            )

        users_request = await self.user_requests_dao.create(users_request_data)
        await self.user_requests_dao.add_pipelines_to_request(users_request.id, users_request_data.pipelines)

        LOGGER.info(f"Successfully created user request for user ID {user_id}.")
        return ok(message="Successfully created user request.")

    async def get_user_unassigned_pipelines(self, request):
        user_pipeline_ids = set(request.session.get(SessionAttributes.USER_PIPELINES.value))
        all_pipeline_objects = await self.pipelines_dao.get_by_application_status(AppStatus.ACTIVE.value)
        unassigned_pipelines = [pipeline for pipeline in all_pipeline_objects if pipeline.id not in user_pipeline_ids]

        return ok(message="Successfully provided unassigned pipelines for user.",
                  data=[PipelineOut.model_validate(pipeline.as_dict()) for pipeline in unassigned_pipelines])
