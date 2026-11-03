from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404, HttpRequest
from ninja import NinjaAPI

from src.core.exceptions import ApplicationError
from src.tasks.apis import router as tasks_router

api = NinjaAPI(
    title="Template Ninja",
    version="1.0.0",
    urls_namespace="api",
    description="HTTP → Ninja → DTO → Service → Django ORM → PostgreSQL",
)

api.add_router("/tasks", tasks_router)


def _validation_errors(exc: DjangoValidationError) -> dict[str, list[str]]:
    if hasattr(exc, "message_dict"):
        return {key: [str(item) for item in value] for key, value in exc.message_dict.items()}
    return {"non_field_errors": [str(item) for item in exc.messages]}


@api.exception_handler(ApplicationError)
def handle_application_error(request: HttpRequest, exc: ApplicationError):
    return api.create_response(request, {"message": str(exc)}, status=exc.status_code)


@api.exception_handler(DjangoValidationError)
def handle_django_validation_error(request: HttpRequest, exc: DjangoValidationError):
    return api.create_response(
        request,
        {"message": "Validation failed", "errors": _validation_errors(exc)},
        status=400,
    )


@api.exception_handler(PermissionDenied)
def handle_permission_denied(request: HttpRequest, exc: PermissionDenied):
    return api.create_response(
        request,
        {"message": str(exc) or "Permission denied"},
        status=403,
    )


@api.exception_handler(Http404)
def handle_not_found(request: HttpRequest, exc: Http404):
    return api.create_response(request, {"message": "Not found"}, status=404)
