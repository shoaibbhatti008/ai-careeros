"""
Common abstract base models for AI CareerOS.

NOTE: This is NOT a Django app. It has no apps.py and no migrations.
It only provides abstract base classes for other models to inherit.
"""

import uuid

from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base: UUID pk + created_at + updated_at."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class OwnedModel(TimeStampedModel):
    """
    Abstract base: adds an owner (user) foreign key.

    Every query MUST filter by `user` to enforce ownership.
    """

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_set",
    )

    class Meta(TimeStampedModel.Meta):
        abstract = True
