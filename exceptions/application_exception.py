class ApplicationNotFoundException(Exception):
    """Raised when application not found in database."""
    def __init__(self, detail: str):
        self.detail = detail
