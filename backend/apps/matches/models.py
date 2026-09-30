"""JobMatch and SkillGap models."""

from apps.common.models import OwnedModel
from django.db import models
from django.utils.translation import gettext_lazy as _


class JobMatch(OwnedModel):
    """
    A user's match score against a specific Job.
    """

    resume = models.ForeignKey(
        "resumes.Resume",
        on_delete=models.CASCADE,
        related_name="job_matches",
    )
    job = models.ForeignKey(
        "jobs.Job",
        on_delete=models.CASCADE,
        related_name="matches",
    )

    score = models.FloatField(db_index=True)  # 0.0 to 1.0
    match_reasons = models.JSONField(default=list, blank=True)
    missing_skills = models.JSONField(default=list, blank=True)
    extra_skills = models.JSONField(default=list, blank=True)

    is_saved = models.BooleanField(default=False, db_index=True)
    is_dismissed = models.BooleanField(default=False, db_index=True)
    user_notes = models.TextField(blank=True)

    class Meta(OwnedModel.Meta):
        verbose_name = _("job match")
        verbose_name_plural = _("job matches")
        constraints = [
            models.UniqueConstraint(
                fields=["user", "resume", "job"],
                name="unique_user_resume_job_match",
            ),
        ]
        indexes = [
            models.Index(fields=["user", "-score"]),
            models.Index(fields=["user", "is_saved"]),
        ]

    def __str__(self) -> str:
        return f"{self.user.email} → {self.job.title} ({self.score:.2f})"


class SkillGap(OwnedModel):
    """
    A missing skill for a target role.
    """

    class Priority(models.TextChoices):
        LOW = "low", _("Low")
        MEDIUM = "medium", _("Medium")
        HIGH = "high", _("High")
        CRITICAL = "critical", _("Critical")

    resume = models.ForeignKey(
        "resumes.Resume",
        on_delete=models.CASCADE,
        related_name="skill_gaps",
    )
    skill = models.ForeignKey(
        "resumes.Skill",
        on_delete=models.CASCADE,
        related_name="gaps",
    )
    target_role = models.CharField(max_length=200, blank=True, db_index=True)
    priority = models.CharField(
        max_length=20, choices=Priority.choices, default=Priority.MEDIUM, db_index=True
    )
    importance = models.FloatField(default=0.5)  # 0.0 to 1.0
    learning_resources = models.JSONField(default=list, blank=True)
    is_resolved = models.BooleanField(default=False, db_index=True)
    notes = models.TextField(blank=True)

    class Meta(OwnedModel.Meta):
        verbose_name = _("skill gap")
        verbose_name_plural = _("skill gaps")
        constraints = [
            models.UniqueConstraint(
                fields=["user", "resume", "skill", "target_role"],
                name="unique_user_resume_skill_target_gap",
            ),
        ]
        indexes = [
            models.Index(fields=["user", "priority"]),
            models.Index(fields=["user", "is_resolved"]),
        ]

    def __str__(self) -> str:
        return f"{self.user.email} gap: {self.skill.name}"
