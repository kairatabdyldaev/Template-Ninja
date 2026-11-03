from typing import Any

from django.db import models


def model_update[ModelT: models.Model](
    *,
    instance: ModelT,
    fields: list[str],
    data: dict[str, Any],
) -> tuple[ModelT, bool]:
    """Update one instance and persist it only when a listed field changes."""
    update_fields: list[str] = []

    for field in fields:
        if field not in data:
            continue
        if getattr(instance, field) != data[field]:
            setattr(instance, field, data[field])
            update_fields.append(field)

    if not update_fields:
        return instance, False

    instance.full_clean()

    model_field_names = {field.name for field in instance._meta.fields}
    if "modified" in model_field_names:
        update_fields.append("modified")

    instance.save(update_fields=update_fields)
    return instance, True
