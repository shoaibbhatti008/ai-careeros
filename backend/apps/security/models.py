"""Security models — audit logs and login history."""

import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class AuditLog(models.Model):
    """
    Immutable audit log for sensitive actions.

    Every sensitive action (login, password change, permission change, etc.)
    writes a record here. This is append-only.
    """

    class Action(models.TextChoices):
        LOGIN_SUCCESS = "login_success", _("Login success")
        LOGIN_FAILED = "login_failed", _("Login failed")
        LOGOUT = "logout", _("Logout")
        PASSWORD_CHANGE = "password_change", _("Password change")
        PASSWORD_RESET = "password_reset", _("Password reset")
        USER_CREATED = "user_created", _("User created")
        USER_UPDATED = "user_updated", _("User updated")
        PERMISSION_CHANGE = "permission_change", _("Permission change")
        RATE_LIMIT_HIT = "rate_limit_hit", _("Rate limit hit")
        SUSPICIOUS_ACTIVITY = "suspicious_activity", _("Suspicious activity")
        PROMPT_INJECTION_BLOCKED = "prompt_injection_blocked", _("Prompt injection blocked")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=50, choices=Action.choices, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    request_id = models.CharField(max_length=100, blank=True, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = _("audit log")
        verbose_name_plural = _("audit logs")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["action", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"[{self.created_at:%Y-%m-%d %H:%M}] {self.action} — {self.user or 'anonymous'}"


class LoginAttempt(models.Model):
    """
    Tracks login attempts for security monitoring and brute-force detection.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="login_attempts",
    )
    was_successful = models.BooleanField(default=False, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = _("login attempt")
        verbose_name_plural = _("login attempts")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email", "-created_at"]),
            models.Index(fields=["ip_address", "-created_at"]),
        ]

    def __str__(self) -> str:
        status = "✓" if self.was_successful else "✗"
        return f"{status} {self.email} @ {self.created_at:%Y-%m-%d %H:%M}"


class SecurityEvent(models.Model):
    """
    High-level security events (rate limit hits, suspicious activity, etc.).
    """

    class Severity(models.TextChoices):
        LOW = "low", _("Low")
        MEDIUM = "medium", _("Medium")
        HIGH = "high", _("High")
        CRITICAL = "critical", _("Critical")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=100, db_index=True)
    severity = models.CharField(
        max_length=20, choices=Severity.choices, default=Severity.LOW, db_index=True
    )
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="security_events",
    )
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    resolved = models.BooleanField(default=False, db_index=True)

    class Meta:
        verbose_name = _("security event")
        verbose_name_plural = _("security events")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"[{self.severity}] {self.event_type} — {self.created_at:%Y-%m-%d %H:%M}"
