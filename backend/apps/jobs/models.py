"""Job and JobSource models."""

from apps.common.models import TimeStampedModel
from django.db import models
from django.utils.translation import gettext_lazy as _


class JobSource(TimeStampedModel):
    """
    An approved source of job postings.

    Only approved sources may be accessed by the Job Agent.
    """

    class SourceType(models.TextChoices):
        MANUAL = "manual", _("Manual entry")
        API = "api", _("API")
        FEED = "feed", _("RSS / feed")
        APPROVED_WEB = "approved_web", _("Approved web source")

    name = models.CharField(max_length=200, unique=True, db_index=True)
    slug = models.SlugField(max_length=220, unique=True, db_index=True)
    source_type = models.CharField(
        max_length=30, choices=SourceType.choices, default=SourceType.MANUAL, db_index=True
    )
    base_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    is_approved = models.BooleanField(default=False, db_index=True)
    config = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _("job source")
        verbose_name_plural = _("job sources")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Job(TimeStampedModel):
    """
    A job posting. Not user-owned — shared catalog.
    """

    class EmploymentType(models.TextChoices):
        FULL_TIME = "full_time", _("Full time")
        PART_TIME = "part_time", _("Part time")
        CONTRACT = "contract", _("Contract")
        INTERNSHIP = "internship", _("Internship")
        FREELANCE = "freelance", _("Freelance")

    class RemotePolicy(models.TextChoices):
        ONSITE = "onsite", _("On-site")
        HYBRID = "hybrid", _("Hybrid")
        REMOTE = "remote", _("Remote")

    class Status(models.TextChoices):
        OPEN = "open", _("Open")
        CLOSED = "closed", _("Closed")
        UNKNOWN = "unknown", _("Unknown")

    # Identity
    external_id = models.CharField(max_length=200, blank=True, db_index=True)
    source = models.ForeignKey(
        JobSource,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="jobs",
    )
    source_url = models.URLField(blank=True)

    # Content
    title = models.CharField(max_length=300, db_index=True)
    company = models.CharField(max_length=200, db_index=True)
    location = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    requirements = models.TextField(blank=True)
    responsibilities = models.TextField(blank=True)

    # Metadata
    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME,
    )
    remote_policy = models.CharField(
        max_length=20, choices=RemotePolicy.choices, default=RemotePolicy.ONSITE
    )
    seniority = models.CharField(max_length=50, blank=True)
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    currency = models.CharField(max_length=10, blank=True)

    # Classification
    skills = models.ManyToManyField("resumes.Skill", blank=True, related_name="jobs")
    tags = models.JSONField(default=list, blank=True)

    # Lifecycle
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.OPEN, db_index=True
    )
    posted_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    # Integrity
    content_hash = models.CharField(max_length=64, blank=True, db_index=True)
    raw_data = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = _("job")
        verbose_name_plural = _("jobs")
        ordering = ["-posted_at", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["source", "external_id"],
                name="unique_source_external_id",
                condition=models.Q(external_id__gt=""),
            ),
        ]
        indexes = [
            models.Index(fields=["status", "-posted_at"]),
            models.Index(fields=["company"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} @ {self.company}"
