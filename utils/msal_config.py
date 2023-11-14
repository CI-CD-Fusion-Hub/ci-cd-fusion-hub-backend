from fastapi.security import OAuth2AuthorizationCodeBearer

from msal import ConfidentialClientApplication

from daos.auth_dao import AuthDAO
from schemas.auth_sch import ADDSProperties


async def get_azure_config_from_db():
    auth_dao = AuthDAO()
    properties = ADDSProperties.model_validate((await auth_dao.get_all()).properties)
    azure_cfg = {
        "tenant_id": properties.adds_tenant_id,
        "client_id": properties.adds_client_id,
        "client_secret": properties.adds_client_secret,
    }

    if not azure_cfg.get("tenant_id") or not azure_cfg.get("client_id") or not azure_cfg.get("client_secret"):
        return None

    return azure_cfg


# OAuth2 Authorization Code Bearer
class DynamicOAuth2AuthorizationCodeBearer(OAuth2AuthorizationCodeBearer):
    def __init__(self, authorizationUrl: str = "", tokenUrl: str = "", **kwargs):
        self.msal_app = None

        # Call the asynchronous method here
        super().__init__(authorizationUrl=authorizationUrl, tokenUrl=tokenUrl, **kwargs)

    async def set_azure_config(self):
        # Replace this with your logic to dynamically fetch Azure AD configuration from the database
        azure_cfg = await get_azure_config_from_db()

        # Set the tokenUrl and authorizationUrl dynamically if configuration is found
        if azure_cfg:
            authority = f"https://login.microsoftonline.com/{azure_cfg['tenant_id']}"
            msal_app = ConfidentialClientApplication(
                azure_cfg['client_id'], authority=authority, client_credential=azure_cfg['client_secret']
            )

            self.tokenUrl = f"{authority}/oauth2/v2.0/token"
            self.authorizationUrl = f"{authority}/oauth2/v2.0/authorize"

            self.msal_app = msal_app


# Instantiate the class without passing authorizationUrl and tokenUrl
oauth2_scheme = DynamicOAuth2AuthorizationCodeBearer()
