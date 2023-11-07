from fastapi import Request
from fastapi import status as Status

from daos.users_requests_dao import UserRequestsDAO
from schemas.users_requests_sch import UsersRequestBaseOut, CreateUsersRequest, UpdateUsersRequest, Pipeline, \
    UsersRequestOut
from utils.enums import SessionAttributes
from utils.response import ok, error


class UsersRequestsService:
    def __init__(self):
        self.user_requests_dao = UserRequestsDAO()

    async def get_all_users_requests(self):
        users_requests = await self.user_requests_dao.get_all()
        return ok(message="Successfully provided all users requests.",
                  data=[UsersRequestBaseOut.model_validate(user_requests.as_dict()) for user_requests in users_requests])

    async def get_by_id(self, users_request_id: int):
        user_request = await self.user_requests_dao.get_detailed_users_request_info(users_request_id)
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

    async def create_users_request(self, request: Request, users_request_data: CreateUsersRequest):
        user_id = request.session.get(SessionAttributes.USER_ID.value)
        user_pipelines = list(request.session.get(SessionAttributes.USER_PIPELINES.value))
        users_request_data.user_id = user_id

        pipeline_ids = [p.id for p in users_request_data.pipelines]

        already_access = False
        for pipeline_id in pipeline_ids:
            if pipeline_id in user_pipelines:
                already_access = True

        if already_access:
            return error(
                message="User already have access to some of the provided pipelines.",
                status_code=Status.HTTP_400_BAD_REQUEST
            )

        users_request = await self.user_requests_dao.create(users_request_data)
        await self.user_requests_dao.add_pipelines_to_request(users_request.id, pipeline_ids)

        return ok(message="Successfully created user request.")

    async def update_users_request(self, request: Request,
                                   users_request_id: int, users_request_data: UpdateUsersRequest):
        user_request = await self.user_requests_dao.get_detailed_users_request_info(users_request_id)
        if not user_request:
            return error(
                message=f"User request with ID {users_request_id} does not exist.",
                status_code=Status.HTTP_400_BAD_REQUEST
            )

        user_request_data_pipelines = set(p.id for p in users_request_data.pipelines)
        existing_pipelines = set(p.pipeline_id for p in user_request.pipelines)
        to_be_add = user_request_data_pipelines - existing_pipelines
        to_be_remove = existing_pipelines - user_request_data_pipelines

        pipeline_ids_to_add = list(to_be_add)
        pipeline_ids_to_remove = list(to_be_remove)

        updated_data = users_request_data.model_dump(exclude={'pipelines'})
        await self.user_requests_dao.update(users_request_id, updated_data)

        if pipeline_ids_to_add:
            await self.user_requests_dao.add_pipelines_to_request(users_request_id, pipeline_ids_to_add)

        if pipeline_ids_to_remove:
            await self.user_requests_dao.remove_pipelines_from_request(users_request_id, pipeline_ids_to_remove)

        return ok(message="Successfully updated user request.")

    async def delete_users_request(self, request, users_request_id: int):
        user_request = await self.user_requests_dao.get_by_id(users_request_id)
        if not user_request:
            return error(
                message=f"User request with ID {users_request_id} does not exist.",
                status_code=Status.HTTP_400_BAD_REQUEST
            )

        await self.user_requests_dao.delete(users_request_id)
        return ok(message="User request has been successfully deleted.")


