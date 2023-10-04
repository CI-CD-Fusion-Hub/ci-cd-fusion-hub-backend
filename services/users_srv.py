import hashlib

from exceptions.user_exception import UserNotFoundException
from schemas.users_sch import CreateUser, UserOut, UpdateUser
from daos.users_dao import UserDAO
from utils.response import ok, error


class UserService:
    def __init__(self):
        self.user_dao = UserDAO()

    async def get_all_users(self):
        users = await self.user_dao.get_all()
        return ok(message="Successfully provided all users.", data=[UserOut.model_validate(user.as_dict()) for user in users])

    async def get_user_by_id(self, user_id: int):
        user = await self.user_dao.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(f"User with ID {user_id} does not exist.")
        return ok(message="Successfully provided user.", data=UserOut.model_validate(user.as_dict()))

    async def create_user(self, user_data: CreateUser):
        try:
            user_data.password = hashlib.sha512(user_data.password.encode('utf-8')).hexdigest()
            user = await self.user_dao.create(user_data)
            return ok(message="Successfully created user.", data=UserOut.model_validate(user.as_dict()))
        except ValueError as e:
            return error(message=str(e))

    async def update_user(self, user_id: int, user_data: UpdateUser):
        user = await self.user_dao.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(f"User with ID {user_id} does not exist.")

        if user_data.password:
            user_data.password = hashlib.sha512(user_data.password.encode('utf-8')).hexdigest()

        data_to_update = user_data.model_dump()
        data_to_update = {k: v for k, v in data_to_update.items() if v is not None and k != "confirm_password"}

        user = await self.user_dao.update(user_id, data_to_update)

        return ok(message="Successfully updated user.", data=UserOut.model_validate(user.as_dict()))

    async def delete_user(self, user_id: int):
        if not await self.user_dao.get_by_id(user_id):
            raise UserNotFoundException(f"User with ID {user_id} does not exist.")
        await self.user_dao.delete(user_id)
        return ok(message="User has been successfully deleted.")