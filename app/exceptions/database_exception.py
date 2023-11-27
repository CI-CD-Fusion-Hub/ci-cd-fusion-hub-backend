class DatabaseIntegrityException(Exception):
    """Raised for general database integrity issues."""
    def __init__(self, detail: str):
        self.detail = detail
