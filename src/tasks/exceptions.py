from src.core.exceptions import ApplicationError


class TaskNotFoundError(ApplicationError):
    status_code = 404

    def __init__(self) -> None:
        super().__init__("Not found")


class TaskAlreadyDoneError(ApplicationError):
    status_code = 409
