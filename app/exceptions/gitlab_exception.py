class GitLabConnectionException(Exception):
    """Raised when failed to connect to GitLab instance."""
    def __init__(self, detail: str):
        self.detail = detail
