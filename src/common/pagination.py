from ninja import Field, Schema
from ninja.pagination import LimitOffsetPagination


class DefaultPagination(LimitOffsetPagination):
    class Input(Schema):
        limit: int = Field(20, ge=1, le=100)
        offset: int = Field(0, ge=0)

    def __init__(self, max_limit: int = 100, **kwargs: object) -> None:
        super().__init__(max_limit=max_limit, **kwargs)
