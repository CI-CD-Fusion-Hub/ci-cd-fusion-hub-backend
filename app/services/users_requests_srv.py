from fastapi import status as Status

from app.daos.users_requests_dao import UserRequestsDAO
from app.schemas.users_requests_sch import UpdateUsersRequest, Pipeline, \
    UsersRequestOut, User
from app.utils.logger import Logger
from app.utils.response import ok, error

LOGGER = Logger().start_logger()


class UsersRequestsService:
    def __init__(self):
        self.user_requests_dao = UserRequestsDAO()

    async def get_all_users_requests(self):
        users_requests = await self.user_requests_dao.get_all()

        if not users_requests:
            LOGGER.info("No user requests found in the database.")
            return ok(message="No user requests available.", data=[])

        users_requests_data = []
        for user_request in users_requests:
            users_request_data = UsersRequestOut.model_validate(user_request.as_dict())
            users_request_data.user = User(email=user_request.user.email, id=user_request.user.id)
            users_request_data.pipelines = [(Pipeline(name=pipeline.pipeline.name, id=pipeline.pipeline.id))
                                            for pipeline in user_request.pipelines if pipeline.pipeline]
            users_requests_data.append(users_request_data)

        LOGGER.info(f"Retrieved {len(users_requests_data)} user requests.")
        return ok(
            message="Successfully provided all users requests.",
            data=[user_requests
                  for user_requests in users_requests_data]
        )

    async def get_by_id(self, users_request_id: int):
        user_request = await self.user_requests_dao.get_detailed_users_request_info_by_id(users_request_id)
        if not user_request:
            LOGGER.warning(f"User request with ID {users_request_id} not found.")
            return error(
                message=f"User request with ID {users_request_id} does not exist.",
                status_code=Status.HTTP_400_BAD_REQUEST
            )

        users_request_data = UsersRequestOut.model_validate(user_request.as_dict())
        users_request_data.pipelines = [(Pipeline(name=pipeline.pipeline.name, id=pipeline.pipeline.id))
                                        for pipeline in user_request.pipelines if pipeline.pipeline]

        LOGGER.info(f"Successfully retrieved user request details for ID {users_request_id}.")
        return ok(
            message="Successfully provided users request details.",
            data=users_request_data
        )

    async def update_users_request(self, users_request_id: int, users_request_data: UpdateUsersRequest):
        user_request = await self.user_requests_dao.get_detailed_users_request_info_by_id(users_request_id)
        if not user_request:
            LOGGER.warning(f"Attempted to update a non-existent user request with ID {users_request_id}.")
            return error(
                message=f"User request with ID {users_request_id} does not exist.",
                status_code=Status.HTTP_400_BAD_REQUEST
            )

        updated_data = users_request_data.model_dump(exclude={'pipelines'})
        await self.user_requests_dao.update(users_request_id, updated_data)

        LOGGER.info(f"User request with ID {users_request_id} has been successfully updated.")
        return ok(message="Successfully updated user request.")

    async def delete_users_request(self, users_request_id: int):
        user_request = await self.user_requests_dao.get_by_id(users_request_id)
        if not user_request:
            LOGGER.warning(f"Attempted to delete a non-existent user request with ID {users_request_id}.")
            return error(
                message=f"User request with ID {users_request_id} does not exist.",
                status_code=Status.HTTP_400_BAD_REQUEST
            )

        await self.user_requests_dao.delete(users_request_id)
        LOGGER.info(f"User request with ID {users_request_id} has been successfully deleted.")

        return ok(message="User request has been successfully deleted.")
