"""Conversation and Message models."""

from apps.common.models import OwnedModel
from django.db import models
from django.utils.translation import gettext_lazy as _


class Conversation(OwnedModel):
    """
    A conversation between a user and the AI assistant.
    """

    title = models.CharField(max_length=300, blank=True, db_index=True)
    is_archived = models.BooleanField(default=False, db_index=True)
    is_pinned = models.BooleanField(default=False, db_index=True)

    # Aggregated counters
    message_count = models.PositiveIntegerField(default=0)
    total_tokens = models.PositiveIntegerField(default=0)

    # Optional references
    resume = models.ForeignKey(
        "resumes.Resume",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="conversations",
    )
    job = models.ForeignKey(
        "jobs.Job",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="conversations",
    )

    metadata = models.JSONField(default=dict, blank=True)

    class Meta(OwnedModel.Meta):
        verbose_name = _("conversation")
        verbose_name_plural = _("conversations")
        indexes = [
            models.Index(fields=["user", "is_archived"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self) -> str:
        return self.title or f"Conversation {self.id}"


class Message(OwnedModel):
    """
    A message in a conversation.

    Note: role distinguishes user/assistant/system/tool.
    """

    class Role(models.TextChoices):
        USER = "user", _("User")
        ASSISTANT = "assistant", _("Assistant")
        SYSTEM = "system", _("System")
        TOOL = "tool", _("Tool")

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    role = models.CharField(max_length=20, choices=Role.choices, db_index=True)
    content = models.TextField()
    tokens_used = models.PositiveIntegerField(default=0)

    # Optional metadata (agent name, tool name, citations, etc.)
    message_metadata = models.JSONField(default=dict, blank=True)

    class Meta(OwnedModel.Meta):
        verbose_name = _("message")
        verbose_name_plural = _("messages")
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["conversation", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"[{self.role}] {self.content[:50]}"
