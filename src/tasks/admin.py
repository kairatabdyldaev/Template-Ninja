from django.contrib import admin

from src.tasks.models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "created", "modified")
    list_filter = ("status",)
    search_fields = ("title",)
