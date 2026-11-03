import pytest

from src.tasks.models import Task
from src.tasks.tests.factories import TaskFactory


@pytest.fixture
def task(db) -> Task:
    return TaskFactory()
