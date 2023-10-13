import hashlib
from fastapi import Request


from exceptions.user_exception import UserNotFoundException
from schemas.users_sch import CreateUser, UserOut, UpdateUser, UserBaseOut, LoginUser
from daos.users_dao import UserDAO
from utils.response import ok, error


class UserService:
    def __init__(self):
        self.user_dao = UserDAO()

    async def get_all_users(self):
        users = await self.user_dao.get_all()
        return ok(message="Successfully provided all users.", data=[UserBaseOut.model_validate(user.as_dict()) for user in users])

    async def get_user_by_id(self, user_id: int):
        user = await self.user_dao.get_detailed_user_info(user_id)
        if not user:
            raise UserNotFoundException(f"User with ID {user_id} does not exist.")

        user_data = UserOut.model_validate(user.as_dict())

        user_data.roles = [role_member.role.as_dict() for role_member in user.roles]

        pipelines = []
        for role_member in user.roles:
            for pipeline in role_member.role.pipelines:
                pipelines.append(pipeline.pipeline)

        user_data.pipelines = list(pipelines)

        return ok(message="Successfully provided user details.", data=user_data)

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

    async def fetch_user_unassigned_roles(self, user_id: int):
        unassigned_roles = await self.user_dao.get_user_unassigned_roles(user_id)
        return ok(message="Successfully provided unassigned users for access role.",
                  data=[role.as_dict() for role in unassigned_roles])

    async def login(self, request: Request, credentials: LoginUser):
        user = await self.user_dao.get_by_email(credentials.email)
        if not user:
            raise UserNotFoundException(f"User with Email {credentials.email} does not exist.")

        if user.status != 'active':
            raise UserNotFoundException(f"User with Email {credentials.email} is inactive.")

        if not self._verify_password(credentials.password, user.password):
            raise UserNotFoundException("Invalid password or email.")

        request.session['USER_NAME'] = credentials.email

        return ok(message="Successfully logged in.")

    @classmethod
    def _verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return hashlib.sha512(plain_password.encode('utf-8')).hexdigest() == hashed_password

    @classmethod
    async def logout(cls, request):
        request.session.clear()
        return ok(message="Successful logout.")
