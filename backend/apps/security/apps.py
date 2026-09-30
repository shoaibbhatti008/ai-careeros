"""Security app configuration."""

from django.apps import AppConfig


class SecurityConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.security"
    verbose_name = "Security & Audit"

    def ready(self) -> None:
        """Connect signals on app startup."""
        from . import signals  # noqa: F401
