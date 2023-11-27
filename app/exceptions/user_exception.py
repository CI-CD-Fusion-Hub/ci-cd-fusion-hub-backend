class UserNotFoundException(Exception):
    """Raised when user not found in database."""
    def __init__(self, detail: str):
        self.detail = detail
