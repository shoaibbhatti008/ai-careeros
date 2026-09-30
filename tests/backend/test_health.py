"""Tests for the health check endpoint."""

import pytest
from django.test import Client


@pytest.mark.django_db
def test_health_endpoint_responds() -> None:
    """Health check should return JSON with status, version, and checks."""
    client = Client()
    response = client.get("/api/health/")

    # In test mode, Redis may not be available → accept 200 or 503
    assert response.status_code in (200, 503)

    data = response.json()
    assert "status" in data
    assert "version" in data
    assert "checks" in data
    assert data["version"] == "0.1.0"


@pytest.mark.django_db
def test_health_check_includes_database_key() -> None:
    """Health check should report database status."""
    client = Client()
    response = client.get("/api/health/")
    data = response.json()

    assert "database" in data["checks"]


@pytest.mark.django_db
def test_health_check_includes_redis_key() -> None:
    """Health check should report redis status."""
    client = Client()
    response = client.get("/api/health/")
    data = response.json()

    assert "redis" in data["checks"]