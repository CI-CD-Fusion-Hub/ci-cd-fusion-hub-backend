from fastapi import Request
from fastapi import status as Status

from daos.users_requests_dao import UserRequestsDAO
from schemas.users_requests_sch import CreateUsersRequest, UpdateUsersRequest, Pipeline, \
    UsersRequestOut, User
from utils.enums import SessionAttributes, AccessLevel, RequestStatus
from utils.response import ok, error


class UsersRequestsService:
    def __init__(self):
        self.user_requests_dao = UserRequestsDAO()

    async def get_all_users_requests(self):
        users_requests = await self.user_requests_dao.get_all()

        users_requests_data = []
        for user_request in users_requests:
            users_request_data = UsersRequestOut.model_validate(user_request.as_dict())
            users_request_data.user = User(email=user_request.user.email, id=user_request.user.id)
            users_request_data.pipelines = [(Pipeline(name=pipeline.pipeline.name, id=pipeline.pipeline.id))
                                            for pipeline in user_request.pipelines]
            users_requests_data.append(users_request_data)

        return ok(
            message="Successfully provided all users requests.",
            data=[user_requests
                  for user_requests in users_requests_data]
        )

    async def get_by_id(self, users_request_id: int):
        user_request = await self.user_requests_dao.get_detailed_users_request_info_by_id(users_request_id)
        if not user_request:
            return error(
                message=f"User request with ID {users_request_id} does not exist.",
                status_code=Status.HTTP_400_BAD_REQUEST
            )

        users_request_data = UsersRequestOut.model_validate(user_request.as_dict())
        users_request_data.pipelines = [(Pipeline(name=pipeline.pipeline.name, id=pipeline.pipeline.id))
                                        for pipeline in user_request.pipelines]
        return ok(
            message="Successfully provided users request details.",
            data=users_request_data
        )

    async def update_users_request(self, users_request_id: int, users_request_data: UpdateUsersRequest):
        user_request = await self.user_requests_dao.get_detailed_users_request_info_by_id(users_request_id)
        if not user_request:
            return error(
                message=f"User request with ID {users_request_id} does not exist.",
                status_code=Status.HTTP_400_BAD_REQUEST
            )

        updated_data = users_request_data.model_dump(exclude={'pipelines'})
        await self.user_requests_dao.update(users_request_id, updated_data)
        return ok(message="Successfully updated user request.")

    async def delete_users_request(self, users_request_id: int):
        user_request = await self.user_requests_dao.get_by_id(users_request_id)
        if not user_request:
            return error(
                message=f"User request with ID {users_request_id} does not exist.",
                status_code=Status.HTTP_400_BAD_REQUEST
            )

        await self.user_requests_dao.delete(users_request_id)
        return ok(message="User request has been successfully deleted.")
