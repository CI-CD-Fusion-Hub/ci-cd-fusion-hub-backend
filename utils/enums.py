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
