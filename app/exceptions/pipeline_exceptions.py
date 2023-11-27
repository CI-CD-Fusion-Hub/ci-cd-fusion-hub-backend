class PipelineNotFoundException(Exception):
    """Raised when pipeline not found in database."""
    def __init__(self, detail: str):
        self.detail = detail
