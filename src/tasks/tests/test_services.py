import pytest

from src.core.exceptions import ApplicationError
from src.tasks.models import Task
from src.tasks.schemas import TaskFilterSchema, TaskSchemaIn, TaskUpdateSchemaIn
from src.tasks.services import TaskService
from src.tasks.tests.factories import TaskFactory

pytestmark = pytest.mark.django_db(transaction=True)


class TestTaskList:
    def test_filters_by_status_and_title(self) -> None:
        TaskFactory(title="Write docs", status=Task.Status.OPEN)
        TaskFactory(title="Write tests", status=Task.Status.DONE)
        TaskFactory(title="Deploy", status=Task.Status.DONE)

        tasks = list(
            TaskService.list(
                filters=TaskFilterSchema(status=Task.Status.DONE, search="write"),
            )
        )

        assert [task.title for task in tasks] == ["Write tests"]


class TestTaskGet:
    def test_raises_when_the_task_is_missing(self) -> None:
        with pytest.raises(ApplicationError, match="Not found") as exc_info:
            TaskService.get(task_id=999999)

        assert exc_info.value.status_code == 404


class TestTaskCreate:
    def test_persists_an_open_task(self) -> None:
        task = TaskService.create(schema=TaskSchemaIn(title="Buy milk", description="2 liters"))

        stored = Task.objects.get(id=task.id)
        assert stored.title == "Buy milk"
        assert stored.description == "2 liters"
        assert stored.status == Task.Status.OPEN


class TestTaskUpdate:
    def test_updates_only_provided_fields(self) -> None:
        task = TaskFactory(title="Old", description="keep")

        updated = TaskService.update(task_id=task.id, schema=TaskUpdateSchemaIn(title="New"))

        updated.refresh_from_db()
        assert updated.title == "New"
        assert updated.description == "keep"

    def test_skips_save_when_nothing_changes(self) -> None:
        task = TaskFactory(title="Same", description="")
        modified_before = task.modified

        updated = TaskService.update(task_id=task.id, schema=TaskUpdateSchemaIn(title="Same"))

        updated.refresh_from_db()
        assert updated.modified == modified_before


class TestTaskComplete:
    def test_marks_task_done(self) -> None:
        task = TaskFactory()

        completed = TaskService.complete(task_id=task.id)

        completed.refresh_from_db()
        assert completed.status == Task.Status.DONE

    def test_second_completion_is_rejected(self) -> None:
        task = TaskFactory(status=Task.Status.DONE)

        with pytest.raises(ApplicationError, match="already done"):
            TaskService.complete(task_id=task.id)
