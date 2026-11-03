from django.http import HttpRequest
from ninja import Query, Router, Status
from ninja.pagination import paginate

from src.common.pagination import DefaultPagination
from src.core.schemas import DjangoValidationSchema, MessageSchema, RequestValidationSchema
from src.tasks.schemas import TaskFilterSchema, TaskSchemaIn, TaskSchemaOut, TaskUpdateSchemaIn
from src.tasks.services import TaskService

router = Router(tags=["tasks"])


@router.get("", response={200: list[TaskSchemaOut], 422: RequestValidationSchema})
@paginate(DefaultPagination)
def task_list_api(request: HttpRequest, filters: Query[TaskFilterSchema]):
    return TaskService.list(filters=filters)


@router.get("/{task_id}", response={200: TaskSchemaOut, 404: MessageSchema})
def task_detail_api(request: HttpRequest, task_id: int):
    return TaskService.get(task_id=task_id)


@router.post(
    "",
    response={
        201: TaskSchemaOut,
        400: DjangoValidationSchema,
        422: RequestValidationSchema,
    },
)
def task_create_api(request: HttpRequest, data: TaskSchemaIn):
    return Status(201, TaskService.create(schema=data))


@router.patch(
    "/{task_id}",
    response={
        200: TaskSchemaOut,
        400: DjangoValidationSchema,
        404: MessageSchema,
        422: RequestValidationSchema,
    },
)
def task_update_api(request: HttpRequest, task_id: int, data: TaskUpdateSchemaIn):
    return TaskService.update(task_id=task_id, schema=data)


@router.post(
    "/{task_id}/complete",
    response={200: TaskSchemaOut, 404: MessageSchema, 409: MessageSchema},
)
def task_complete_api(request: HttpRequest, task_id: int):
    return TaskService.complete(task_id=task_id)
