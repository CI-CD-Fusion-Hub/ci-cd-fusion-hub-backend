from enum import Enum


class AppType(Enum):
    GITLAB = "GitLab"
    GITHUB = "GitHub"
    JENKINS = "Jenkins"
    AZURE_DEVOPS = "AzureDevOps"


class AccessLevel(Enum):
    ADMIN = 'Admin'
    NORMAL = 'User'


class UserStatus(Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'


class AuthMethods(Enum):
    CAS = 'CAS'
    AAD = 'Azure AD'
    LOCAL = 'Local'


class RequestStatus(Enum):
    PENDING = 'pending'
    CANCELED = 'canceled'
    DECLINED = 'declined'
    COMPLETED = 'completed'
    INPROGRESS = 'in-progress'


class SessionAttributes(Enum):
    OAUTH_STATE = 'oauth_state'
    AUTH_METHOD = 'auth_method'
    USER_ID = 'user_id'
    USER_NAME = 'user_name'
    USER_ACCESS_LEVEL = 'user_access_level'
    USER_ROLES = 'user_roles'
    USER_PIPELINES = 'user_pipelines'
    USER_INFO = 'user_info'
