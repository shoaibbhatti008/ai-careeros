"""Pytest configuration for backend tests."""

import os

import django


def pytest_configure():
    """Configure Django settings before tests run."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.testing")
    django.setup()
