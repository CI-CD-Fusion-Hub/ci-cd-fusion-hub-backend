import hashlib
import secrets

import httpx
from fastapi import Request
from fastapi import status as Status
from fastapi.responses import RedirectResponse
from cas import CASClient

from config.events_config import create_admin_user
from daos.auth_dao import AuthDAO
from exceptions.custom_http_expeption import CustomHTTPException
from schemas.auth_sch import LoginUser, CreateAuthMethod, AuthOut, CASProperties, AADProperties
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
        self.login_endpoint_path = "/api/v1/login"

    @classmethod
    def _verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return hashlib.sha512(plain_password.encode('utf-8')).hexdigest() == hashed_password

    @classmethod
    async def logout(cls, request):
        LOGGER.info(f"User {request.session.get(SessionAttributes.USER_NAME.value)} successfully logged out.")
        request.session.clear()
        return ok(message="Successful logout.")

    @classmethod
    def _get_user_info(cls, access_token: str):
        try:
            headers = {'Authorization': 'Bearer ' + access_token}
            graph_data = httpx.get("https://graph.microsoft.com/v1.0/me", headers=headers)

            if graph_data.status_code != 200:
                return error(
                    message="Bearer token validation failed.",
                    status_code=Status.HTTP_401_UNAUTHORIZED
                )
            return graph_data.json()
        except httpx.RequestError:
            raise CustomHTTPException(
                detail="Failed to get user information from Azure.",
                status_code=Status.HTTP_400_BAD_REQUEST
            )

    async def login(self, request: Request, credentials: LoginUser):
        user = await self.user_dao.get_by_email(credentials.email)
        if not user:
            LOGGER.warning(f"User with Email {credentials.email} does not exist.")
            return error(
                message=f"User with Email {credentials.email} does not exist.",
                status_code=Status.HTTP_404_NOT_FOUND
            )

        if user.status != UserStatus.ACTIVE.value:
            LOGGER.warning(f"User with Email {credentials.email} is inactive.")
            return error(
                message=f"User with Email {credentials.email} is inactive.",
                status_code=Status.HTTP_400_BAD_REQUEST
            )

        if not self._verify_password(credentials.password, user.password):
            LOGGER.warning("Invalid password or email.")
            return error(
                message="Invalid password or email.",
                status_code=Status.HTTP_400_BAD_REQUEST
            )

        request.session[SessionAttributes.USER_NAME.value] = credentials.email

        LOGGER.info(f"User {credentials.email} successfully logged in.")
        return ok(message="Successfully logged in.", data=UserBaseOut.model_validate(user.as_dict()))

    async def azure_login(self, request):
        auth_url = await self.get_auth_url(request)
        LOGGER.info(f"Redirecting to Azure login: {auth_url}")
        return RedirectResponse(url=auth_url)

    async def get_auth_url(self, request: Request):
        state = secrets.token_urlsafe(16)
        request.session[SessionAttributes.OAUTH_STATE.value] = state

        try:
            properties = AADProperties.model_validate((await self.auth_dao.get_all()).properties)
            await oauth2_scheme.set_azure_config()

            origin_url = str(request.url)
            # Handle localhost setup
            origin_url = origin_url.replace("0.0.0.0", "localhost")
            if request.url.scheme != "https":
                origin_url = origin_url.replace("http://", "https://")

            current_url = origin_url.replace(self.login_endpoint_path, "/api/v1/login/az/callback")

            LOGGER.info(f"Original url: {origin_url}")
            auth_url = oauth2_scheme.msal_app.get_authorization_request_url(properties.aad_scope,
                                                                            state=state, redirect_uri=current_url)
            LOGGER.info(f"Generated Azure auth URL: {auth_url}")
            return auth_url

        except Exception as e:
            LOGGER.error(f"Error in get_auth_url: {e}")
            raise CustomHTTPException(
                detail="Failed to login in Azure.",
                status_code=Status.HTTP_400_BAD_REQUEST
            )

    async def az_callback(self, request: Request, code: str, state: str) -> RedirectResponse:
        if code is None or state is None:
            LOGGER.warning("Code and state are required.")
            return error(
                message="Code and state are required.",
                status_code=Status.HTTP_400_BAD_REQUEST
            )

        access_token = await self._acquire_token(request)
        user_info = self._get_user_info(access_token)
        first_name = user_info.get('givenName', 'Unknown')
        last_name = user_info.get('surname', 'Unknown')
        email = user_info.get('mail', 'Unknown')
        await self._add_user_in_db(email, first_name, last_name)

        request.session['access_token'] = access_token
        request.session[SessionAttributes.USER_NAME.value] = email

        LOGGER.info(f"User {email} successfully logged in.")
        return RedirectResponse(url="/pipelines")

    async def _add_user_in_db(self, email: str, first_name: str, last_name: str) -> None:
        try:
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
                LOGGER.info(f"User {email} added to the database.")
        except Exception as e:
            LOGGER.error(f"Failed to add user {email} to the database: {str(e)}")
            raise CustomHTTPException(
                detail="Failed to get user information from Azure.",
                status_code=Status.HTTP_400_BAD_REQUEST
            )

    async def _acquire_token(self, request: Request):
        state = request.query_params.get("state")
        if state != request.session.get(SessionAttributes.OAUTH_STATE.value):
            LOGGER.error("State is invalid.")
            return error(
                message="Invalid OAuth state.",
                status_code=Status.HTTP_400_BAD_REQUEST
            )

        properties = AADProperties.model_validate((await self.auth_dao.get_all()).properties)

        original_url = str(request.url)

        # Handle localhost setup
        original_url = original_url.replace("0.0.0.0", "localhost")
        if request.url.scheme != "https":
            original_url = original_url.replace("http://", "https://")

        index_of_question_mark = original_url.find('?')
        current_url = original_url[:index_of_question_mark] if index_of_question_mark != -1 else original_url

        LOGGER.info(f"Original url: {current_url}")
        token_response = oauth2_scheme.msal_app.acquire_token_by_authorization_code(
            request.query_params.get("code"), properties.aad_scope, redirect_uri=current_url
        )

        if "error" in token_response:
            LOGGER.error(f"Token acquisition error: {token_response['error']}")
            return error(
                message=f"Error: {token_response['error']}.",
                status_code=Status.HTTP_400_BAD_REQUEST
            )

        access_token = token_response["access_token"]
        LOGGER.info("Token acquired successfully.")
        return access_token

    async def add_auth_method(self, auth_data: CreateAuthMethod):
        auth_db = await self.auth_dao.get_all()
        if not auth_db:
            auth_db = await self.auth_dao.create(auth_data)
            LOGGER.info("Auth data created.")
        else:
            if auth_db.type != auth_data.type:
                await self.user_dao.delete_all()
                LOGGER.warning("Deleted all users due to a change in authentication type.")

            auth_db = await self.auth_dao.update(auth_db.id, auth_data.model_dump())
            LOGGER.info("Auth data updated.")

        try:
            if auth_data.type == AuthMethods.LOCAL.value:
                await create_admin_user()
                LOGGER.info("Admin user from environment is created.")

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
                LOGGER.info(f"Admin user created with email: {user_email}")

        except ValueError:
            LOGGER.info("User with that name already exist.")

        return ok(message="Successfully created auth method.", data=AuthOut.model_validate(auth_db.as_dict()))

    async def get_auth_method(self):
        auth_db = await self.auth_dao.get_all()
        if not auth_db:
            LOGGER.info("No authentication method found.")
            return ok(message="Successfully provided auth method.", data=AuthOut(id=0, type=AuthMethods.LOCAL.value))

        LOGGER.info("Authentication method found.")
        return ok(message="Successfully provided auth method.", data=AuthOut.model_validate(auth_db.as_dict()))

    async def get_login_auth_method(self):
        auth_db = await self.auth_dao.get_all()
        if not auth_db:
            LOGGER.info("No authentication method found.")
            return ok(message="Local method.", data=True)

        LOGGER.info(f"Authentication method found. Local method - {auth_db.type == AuthMethods.LOCAL.value}")
        return ok(message="Local method.", data=auth_db.type == AuthMethods.LOCAL.value)

    async def cas_login(self, request):
        properties: CASProperties = CASProperties.model_validate((await self.auth_dao.get_all()).properties)
        secure_url = str(request.url)
        if request.url.scheme != "https":
            secure_url = secure_url.replace("http://", "https://")

        index_of_question_mark = secure_url.find('?')
        current_url = secure_url[:index_of_question_mark] if index_of_question_mark != -1 else secure_url

        LOGGER.info(f"Original url: {current_url}")

        cas_client = CASClient(
            version=properties.cas_version,
            service_url=current_url,
            server_url=properties.cas_server_url,
            verify_ssl_certificate=properties.cas_verify_ssl
        )

        ticket = request.query_params.get('ticket')
        if not ticket:
            LOGGER.info("No ticket, the request come from end user, send to CAS login")
            cas_client.server_url = properties.cas_server_url
            return RedirectResponse(cas_client.get_login_url())

        LOGGER.info(f"There is a ticket, the request come from CAS as callback: {ticket}")
        LOGGER.info(f"Ticket {ticket} validating...")

        cas_client.server_url = properties.cas_server_url

        user, attributes, pgtiou = cas_client.verify_ticket(ticket)

        if not user:
            LOGGER.info(f"Ticket {ticket} It's not valid. Redirecting to cas login url.")
            cas_client.server_url = properties.cas_server_url
            return RedirectResponse(cas_client.get_login_url())

        request.session['ticket'] = ticket

        first_name = attributes.get('givenName', 'Unknown')
        last_name = attributes.get('surname', 'Unknown')
        email = str(user).lower()

        await self._add_user_in_db(email, first_name, last_name)

        request.session[SessionAttributes.USER_NAME.value] = email
        LOGGER.info(f"Ticket {ticket} is valid.")
        return RedirectResponse(url="/pipelines")





