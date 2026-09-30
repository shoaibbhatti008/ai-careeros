"""Resume, ResumeVersion, and Skill models."""

from apps.common.models import OwnedModel, TimeStampedModel
from django.db import models
from django.utils.translation import gettext_lazy as _


class Skill(TimeStampedModel):
    """Canonical skill catalog (shared across users)."""

    class Category(models.TextChoices):
        PROGRAMMING = "programming", _("Programming")
        FRAMEWORK = "framework", _("Framework")
        DATABASE = "database", _("Database")
        DEVOPS = "devops", _("DevOps")
        SOFT_SKILL = "soft_skill", _("Soft skill")
        LANGUAGE = "language", _("Language")
        TOOL = "tool", _("Tool")
        OTHER = "other", _("Other")

    name = models.CharField(max_length=100, unique=True, db_index=True)
    slug = models.SlugField(max_length=120, unique=True, db_index=True)
    category = models.CharField(
        max_length=30, choices=Category.choices, default=Category.OTHER, db_index=True
    )
    aliases = models.JSONField(default=list, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = _("skill")
        verbose_name_plural = _("skills")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Resume(OwnedModel):
    """A user's resume (top-level container)."""

    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        ACTIVE = "active", _("Active")
        ARCHIVED = "archived", _("Archived")

    title = models.CharField(max_length=200, db_index=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True
    )
    is_primary = models.BooleanField(default=False, db_index=True)
    language = models.CharField(max_length=10, default="en")

    class Meta(OwnedModel.Meta):
        verbose_name = _("resume")
        verbose_name_plural = _("resumes")
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["user", "is_primary"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.user.email})"


class ResumeVersion(OwnedModel):
    """Immutable snapshot of a resume."""

    class Source(models.TextChoices):
        UPLOAD = "upload", _("Upload")
        MANUAL = "manual", _("Manual entry")
        AI_GENERATED = "ai_generated", _("AI generated")

    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name="versions",
    )
    version_number = models.PositiveIntegerField()
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.UPLOAD)

    raw_text = models.TextField(blank=True)
    parsed_data = models.JSONField(default=dict, blank=True)
    file = models.FileField(upload_to="resumes/%Y/%m/", blank=True, null=True)
    file_size = models.PositiveIntegerField(default=0)
    file_hash = models.CharField(max_length=64, blank=True, db_index=True)

    analysis = models.JSONField(default=dict, blank=True)
    extracted_skills = models.ManyToManyField(Skill, blank=True, related_name="resume_versions")

    is_current = models.BooleanField(default=False, db_index=True)
    notes = models.TextField(blank=True)

    class Meta(OwnedModel.Meta):
        verbose_name = _("resume version")
        verbose_name_plural = _("resume versions")
        constraints = [
            models.UniqueConstraint(
                fields=["resume", "version_number"],
                name="unique_resume_version_number",
            ),
        ]
        indexes = [
            models.Index(fields=["resume", "is_current"]),
        ]

    def __str__(self) -> str:
        return f"{self.resume.title} v{self.version_number}"
