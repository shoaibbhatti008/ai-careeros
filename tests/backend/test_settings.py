"""Tests for settings and environment loading."""

import pytest
from django.conf import settings


def test_django_settings_loaded() -> None:
    """Django settings should load without error."""
    assert settings.INSTALLED_APPS is not None
    assert "django.contrib.auth" in settings.INSTALLED_APPS


def test_rest_framework_configured() -> None:
    """REST Framework should be configured."""
    assert "rest_framework" in settings.INSTALLED_APPS
    assert hasattr(settings, "REST_FRAMEWORK")
    assert "DEFAULT_AUTHENTICATION_CLASSES" in settings.REST_FRAMEWORK


def test_celery_configured() -> None:
    """Celery should be configured."""
    assert hasattr(settings, "CELERY_BROKER_URL")
    assert hasattr(settings, "CELERY_RESULT_BACKEND")
    assert settings.CELERY_TASK_TIME_LIMIT > 0


def test_jwt_configured() -> None:
    """JWT should be configured with lifetimes."""
    assert "SIMPLE_JWT" in dir(settings)
    assert settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds() > 0


def test_database_configured() -> None:
    """Database should be configured (SQLite in tests)."""
    assert "default" in settings.DATABASES
    assert settings.DATABASES["default"]["ENGINE"] == "django.db.backends.sqlite3"


def test_agent_safety_limits_configured() -> None:
    """Agent safety limits should be present."""
    # These are set via env, but with defaults; verify defaults exist
    assert hasattr(settings, "CELERY_TASK_TIME_LIMIT")
    assert settings.CELERY_TASK_TIME_LIMIT == 5 * 60