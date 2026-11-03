import pytest
from django.core.exceptions import ValidationError

from src.tasks.models import Task

pytestmark = pytest.mark.django_db(transaction=True)


class TestTaskModel:
    def test_empty_title_fails_validation(self) -> None:
        task = Task(title="", description="")

        with pytest.raises(ValidationError):
            task.full_clean()
