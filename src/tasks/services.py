from django.db import transaction
from django.db.models import QuerySet

from src.common.services import model_update
from src.tasks.exceptions import TaskAlreadyDoneError, TaskNotFoundError
from src.tasks.models import Task
from src.tasks.schemas import TaskFilterSchema, TaskSchemaIn, TaskUpdateSchemaIn


class TaskService:
    """Use cases for a task. Each method is one operation."""

    @staticmethod
    def get(*, task_id: int) -> Task:
        try:
            return Task.objects.get(id=task_id)
        except Task.DoesNotExist as exc:
            raise TaskNotFoundError() from exc

    @staticmethod
    def list(*, filters: TaskFilterSchema) -> QuerySet[Task]:
        return filters.filter(Task.objects.all())

    @staticmethod
    @transaction.atomic
    def create(*, schema: TaskSchemaIn) -> Task:
        task = Task(
            title=schema.title,
            description=schema.description,
            status=Task.Status.OPEN,
        )
        task.full_clean()
        task.save()
        return task

    @staticmethod
    @transaction.atomic
    def update(*, task_id: int, schema: TaskUpdateSchemaIn) -> Task:
        task = TaskService.get(task_id=task_id)
        updated, _has_updated = model_update(
            instance=task,
            fields=["title", "description"],
            data=schema.model_dump(exclude_unset=True),
        )
        return updated

    @staticmethod
    @transaction.atomic
    def complete(*, task_id: int) -> Task:
        task = TaskService.get(task_id=task_id)
        if task.status == Task.Status.DONE:
            raise TaskAlreadyDoneError("Task is already done")

        updated, _has_updated = model_update(
            instance=task,
            fields=["status"],
            data={"status": Task.Status.DONE},
        )
        return updated
