from django.db import models
from django.utils.translation import gettext_lazy as _

from src.common.models import TimeStampedModel


class Task(TimeStampedModel):
    class Status(models.TextChoices):
        OPEN = "open", _("open")
        DONE = "done", _("done")

    title = models.CharField(_("title"), max_length=255)
    description = models.TextField(_("description"), blank=True)
    status = models.CharField(
        _("status"),
        max_length=16,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
    )

    class Meta:
        verbose_name = _("task")
        verbose_name_plural = _("tasks")
        ordering = ["-created", "-id"]

    def __str__(self) -> str:
        return self.title
