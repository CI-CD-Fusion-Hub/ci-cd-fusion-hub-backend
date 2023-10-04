from enum import Enum


class AppType(Enum):
    GITLAB = "GitLab"
    GITHUB = "GitHub"
    JENKINS = "Jenkins"
    AZURE_DEVOPS = "AzureDevOps"
