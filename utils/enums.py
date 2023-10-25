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


class SessionAttributes(Enum):
    USER_ID = 'USER_ID'
    USER_NAME = 'USER_NAME'
    USER_ACCESS_LEVEL = 'USER_ACCESS_LEVEL'
    USER_ROLES = 'USER_ROLES'
    USER_PIPELINES = 'USER_PIPELINES'
    USER_INFO = 'USER_INFO'
