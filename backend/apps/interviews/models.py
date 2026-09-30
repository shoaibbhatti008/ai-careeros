"""InterviewSession, InterviewQuestion, InterviewAnswer models."""

from apps.common.models import OwnedModel
from django.db import models
from django.utils.translation import gettext_lazy as _


class InterviewSession(OwnedModel):
    """
    A mock interview session for a user.
    """

    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        IN_PROGRESS = "in_progress", _("In progress")
        COMPLETED = "completed", _("Completed")
        ABANDONED = "abandoned", _("Abandoned")

    class InterviewType(models.TextChoices):
        BEHAVIORAL = "behavioral", _("Behavioral")
        TECHNICAL = "technical", _("Technical")
        SYSTEM_DESIGN = "system_design", _("System design")
        CODING = "coding", _("Coding")
        CULTURE_FIT = "culture_fit", _("Culture fit")
        MIXED = "mixed", _("Mixed")

    title = models.CharField(max_length=200, db_index=True)
    job = models.ForeignKey(
        "jobs.Job",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="interview_sessions",
    )
    resume = models.ForeignKey(
        "resumes.Resume",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="interview_sessions",
    )
    interview_type = models.CharField(
        max_length=30,
        choices=InterviewType.choices,
        default=InterviewType.MIXED,
        db_index=True,
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True
    )

    # Feedback
    overall_score = models.FloatField(null=True, blank=True)
    feedback = models.JSONField(default=dict, blank=True)

    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta(OwnedModel.Meta):
        verbose_name = _("interview session")
        verbose_name_plural = _("interview sessions")
        indexes = [
            models.Index(fields=["user", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.status})"


class InterviewQuestion(OwnedModel):
    """
    A question within an interview session.
    """

    session = models.ForeignKey(
        InterviewSession,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    order = models.PositiveIntegerField()
    text = models.TextField()
    question_type = models.CharField(max_length=50, blank=True, db_index=True)
    expected_topics = models.JSONField(default=list, blank=True)
    ai_hint = models.TextField(blank=True)

    class Meta(OwnedModel.Meta):
        verbose_name = _("interview question")
        verbose_name_plural = _("interview questions")
        ordering = ["session", "order"]
        constraints = [
            models.UniqueConstraint(
                fields=["session", "order"],
                name="unique_session_question_order",
            ),
        ]

    def __str__(self) -> str:
        return f"Q{self.order}: {self.text[:60]}"


class InterviewAnswer(OwnedModel):
    """
    A user's answer to an interview question + AI feedback.
    """

    question = models.OneToOneField(
        InterviewQuestion,
        on_delete=models.CASCADE,
        related_name="answer",
    )
    text = models.TextField()
    audio_file = models.FileField(upload_to="interviews/%Y/%m/", blank=True, null=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)

    ai_score = models.FloatField(null=True, blank=True)
    ai_feedback = models.JSONField(default=dict, blank=True)

    class Meta(OwnedModel.Meta):
        verbose_name = _("interview answer")
        verbose_name_plural = _("interview answers")

    def __str__(self) -> str:
        return f"Answer to Q{self.question.order}"
