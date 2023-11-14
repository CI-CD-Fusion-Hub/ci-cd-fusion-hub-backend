import hashlib
import secrets

import httpx
from fastapi import Request
from fastapi import status as Status
from fastapi.responses import RedirectResponse
from cas import CASClient


from config.config import Settings
from daos.auth_dao import AuthDAO
from exceptions.custom_http_expeption import CustomHTTPException
from schemas.auth_sch import LoginUser, CreateAuthMethod, AuthOut
from schemas.users_sch import UserBaseOut, CreateUser
from daos.users_dao import UserDAO
from utils.enums import UserStatus, SessionAttributes, AccessLevel, AuthMethods
from utils.msal_config import oauth2_scheme
from utils.response import ok, error
from utils.logger import Logger

LOGGER = Logger().start_logger()


class AuthService:
    def __init__(self):
        self.user_dao = UserDAO()
        self.auth_dao = AuthDAO()

    @classmethod
    def _verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return hashlib.sha512(plain_password.encode('utf-8')).hexdigest() == hashed_password

    @classmethod
    async def logout(cls, request):
        request.session.clear()
        return ok(message="Successful logout.")

    async def login(self, request: Request, credentials: LoginUser):
        user = await self.user_dao.get_by_email(credentials.email)
        if not user:
            return error(
                message=f"User with Email {credentials.email} does not exist.",
                status_code=Status.HTTP_404_NOT_FOUND
            )

        if user.status != UserStatus.ACTIVE.value:
            return error(
                message=f"User with Email {credentials.email} is inactive.",
                status_code=Status.HTTP_400_BAD_REQUEST
            )

        if not self._verify_password(credentials.password, user.password):
            return error(
                message="Invalid password or email.",
                status_code=Status.HTTP_400_BAD_REQUEST
            )

        request.session[SessionAttributes.USER_NAME.value] = credentials.email

        return ok(message="Successfully logged in.", data=UserBaseOut.model_validate(user.as_dict()))

    async def az_login(self, request):
        auth_url = await self.get_auth_url(request)
        return RedirectResponse(url=auth_url)

    async def get_auth_url(self, request: Request):
        state = secrets.token_urlsafe(16)
        request.session["oauth_state"] = state
        az = await self.auth_dao.get_all()
        await oauth2_scheme.set_azure_config()
        current_url = str(request.url)
        # Handle localhost setup
        if '0.0.0.0' in current_url:
            current_url = current_url.replace("0.0.0.0", "localhost")

        current_url = current_url.replace("/api/v1/login", "/api/v1/login/az/callback")
        return oauth2_scheme.msal_app.get_authorization_request_url(az.properties['adds_scope'], state=state, redirect_uri=current_url)

    async def az_callback(self, request, code, state):
        if code is None or state is None:
            return error(
                message="Code and state are required.",
                status_code=Status.HTTP_400_BAD_REQUEST
            )

        access_token = await self._acquire_token(request)
        await self.add_user_in_db(request, access_token)

        request.session['access_token'] = access_token
        return RedirectResponse(url="/pipelines")

    async def add_user_in_db(self, request: Request, access_token: str):
        try:
            headers = {'Authorization': 'Bearer ' + access_token}
            graph_data = httpx.get("https://graph.microsoft.com/v1.0/me", headers=headers)

            if graph_data.status_code != 200:
                return error(
                    message="Bearer token validation failed.",
                    status_code=Status.HTTP_401_UNAUTHORIZED
                )
            user_info_response = graph_data.json()

            user_db = await self.user_dao.get_by_email(user_info_response['mail'])
            if not user_db:
                user = CreateUser(
                    first_name=user_info_response['givenName'],
                    last_name=user_info_response['surname'],
                    email=user_info_response['mail'],
                    password="",
                    confirm_password="",
                    status=UserStatus.ACTIVE.value,
                    access_level=AccessLevel.NORMAL.value
                )
                await self.user_dao.create(user)

            request.session[SessionAttributes.USER_NAME.value] = user_info_response['mail']
        except httpx.RequestError:
            raise CustomHTTPException(
                detail="Failed to get user information from Azure.",
                status_code=Status.HTTP_400_BAD_REQUEST
            )

    async def _acquire_token(self, request: Request):
        state = request.query_params.get("state")
        if state != request.session.get("oauth_state"):
            return error(
                message="Invalid OAuth state.",
                status_code=Status.HTTP_400_BAD_REQUEST
            )

        az = await self.auth_dao.get_all()
        original_url = str(request.url)

        # Handle localhost setup
        if '0.0.0.0' in original_url:
            original_url = original_url.replace("0.0.0.0", "localhost")

        index_of_question_mark = original_url.find('?')

        # Create a new URL without query parameters
        current_url = original_url[:index_of_question_mark] if index_of_question_mark != -1 else original_url

        token_response = oauth2_scheme.msal_app.acquire_token_by_authorization_code(
            request.query_params.get("code"), az.properties['adds_scope'], redirect_uri=current_url
        )

        if "error" in token_response:
            return error(
                message=f"Error: {token_response['error']}.",
                status_code=Status.HTTP_400_BAD_REQUEST
            )

        access_token = token_response["access_token"]
        return access_token

    async def add_auth_method(self, auth_data: CreateAuthMethod):
        try:
            auth_db = await self.auth_dao.get_all()
            if not auth_db:
                auth = await self.auth_dao.create(auth_data)
            else:
                auth = await self.auth_dao.update(auth_db.id, auth_data.model_dump())

            if auth_db.type != auth_data.type:
                await self.user_dao.delete_all()
            try:
                for user_email in auth_data.admin_users:
                    user = CreateUser(
                        first_name="Admin",
                        last_name="User",
                        email=user_email,
                        password="",
                        confirm_password="",
                        status=UserStatus.ACTIVE.value,
                        access_level=AccessLevel.ADMIN.value
                    )
                    await self.user_dao.create(user)
            except ValueError:
                LOGGER.info("User with that name already exist.")

            return ok(message="Successfully created auth method.", data=AuthOut.model_validate(auth.as_dict()))
        except ValueError as e:
            return error(message=str(e))

    async def get_auth_method(self):
        auth_db = await self.auth_dao.get_all()
        if not auth_db:
            return ok(message="Successfully provided access role.", data={})

        return ok(message="Successfully provided access role.", data=AuthOut.model_validate(auth_db.as_dict()))

    async def get_login_auth_method(self):
        auth_db = await self.auth_dao.get_all()
        if not auth_db:
            return ok(message="Local method.", data=True)

        return ok(message="Local method.", data=auth_db.type == AuthMethods.LOCAL.value)

    async def cas_login(self, request):
        auth_db = await self.auth_dao.get_all()
        cas_client = CASClient(
            version=auth_db.properties['cas_version'],
            service_url=auth_db.properties['cas_service_url'],
            server_url=auth_db.properties['cas_server_url'],
            verify_ssl_certificate=auth_db.properties['cas_verify_ssl']
        )

        ticket = request.query_params.get('ticket')
        cas_client.server_url = auth_db.properties['cas_server_url']
        if not ticket:
            LOGGER.info("No ticket, the request come from end user, send to CAS login")
            return RedirectResponse(cas_client.get_login_url())

        LOGGER.info(f"There is a ticket, the request come from CAS as callback: {ticket}")
        LOGGER.info(f"Ticket {ticket} validating...")

        user, attributes, pgtiou = cas_client.verify_ticket(ticket)
        print(user)
        print(attributes)

        if not user:
            LOGGER.info(f"Ticket {ticket} It's not valid. Redirecting to cas login url.")
            return RedirectResponse(cas_client.get_login_url())

        request.session['ticket'] = ticket

        first_name = attributes.get('first_name', 'Unknown')
        last_name = attributes.get('last_name', 'Unknown')
        email = attributes.get('email', 'Unknown')

        user_db = await self.user_dao.get_by_email(email)
        if not user_db:
            user = CreateUser(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password="",
                confirm_password="",
                status=UserStatus.ACTIVE.value,
                access_level=AccessLevel.NORMAL.value
            )
            await self.user_dao.create(user)

        request.session[SessionAttributes.USER_NAME.value] = email
        LOGGER.info(f"Ticket {ticket} is valid.")
        return RedirectResponse(url="/pipelines")





