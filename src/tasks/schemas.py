from typing import Annotated

from ninja import Field, FilterLookup, FilterSchema, ModelSchema

from src.tasks.models import Task


class TaskSchemaIn(ModelSchema):
    title: str = Field(min_length=1, max_length=255)
    description: str = ""

    class Meta:
        model = Task
        fields = ["title", "description"]


class TaskUpdateSchemaIn(ModelSchema):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None

    class Meta:
        model = Task
        fields = ["title", "description"]
        fields_optional = "__all__"


class TaskSchemaOut(ModelSchema):
    class Meta:
        model = Task
        fields = ["id", "title", "description", "status", "created", "modified"]


class TaskFilterSchema(FilterSchema):
    status: Task.Status | None = None
    search: Annotated[str | None, FilterLookup("title__icontains")] = None
