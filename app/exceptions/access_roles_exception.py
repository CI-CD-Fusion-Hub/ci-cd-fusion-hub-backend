class AccessRoleNotFoundException(Exception):
    """Raised when access role not found in database."""
    def __init__(self, detail: str):
        self.detail = detail
