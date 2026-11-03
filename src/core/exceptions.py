class ApplicationError(Exception):
    """Base error for the service layer. API handlers map it to HTTP."""

    status_code: int = 400

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        if status_code is not None:
            self.status_code = status_code
