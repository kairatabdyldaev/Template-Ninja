from ninja import Schema


class MessageSchema(Schema):
    message: str


class ValidationErrorItemSchema(Schema):
    loc: list[str | int]
    msg: str
    type: str


class RequestValidationSchema(Schema):
    detail: list[ValidationErrorItemSchema]


class DjangoValidationSchema(Schema):
    message: str
    errors: dict[str, list[str]]
