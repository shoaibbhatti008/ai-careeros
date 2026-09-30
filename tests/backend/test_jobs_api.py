"""Tests for jobs API."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.jobs.models import Job, JobSource

User = get_user_model()


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def user(db) -> User:
    return User.objects.create_user(email="user@example.com", password="TestPass123!@#")


@pytest.fixture
def auth_client(api_client, user) -> APIClient:
    login = api_client.post(
        "/api/users/login/",
        {"email": user.email, "password": "TestPass123!@#"},
        format="json",
    )
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
    return api_client


@pytest.mark.django_db
class TestJobsAPI:
    def test_list_requires_auth(self, api_client):
        response = api_client.get("/api/jobs/")
        assert response.status_code == 401

    def test_list_returns_jobs(self, auth_client):
        Job.objects.create(title="Django Dev", company="Acme", status="open")
        Job.objects.create(title="React Dev", company="Beta", status="open")

        response = auth_client.get("/api/jobs/")
        assert response.status_code == 200
        results = response.data.get("results", response.data)
        assert len(results) == 2

    def test_filter_by_company(self, auth_client):
        Job.objects.create(title="Django Dev", company="Acme", status="open")
        Job.objects.create(title="React Dev", company="Beta", status="open")

        response = auth_client.get("/api/jobs/?company=Acme")
        assert response.status_code == 200
        results = response.data.get("results", response.data)
        assert len(results) == 1
        assert results[0]["company"] == "Acme"

    def test_search_by_title(self, auth_client):
        Job.objects.create(title="Django Dev", company="Acme", status="open")
        Job.objects.create(title="React Dev", company="Beta", status="open")

        response = auth_client.get("/api/jobs/?search=Django")
        assert response.status_code == 200
        results = response.data.get("results", response.data)
        assert len(results) == 1
        assert "Django" in results[0]["title"]

    def test_create_job(self, auth_client):
        response = auth_client.post(
            "/api/jobs/",
            {
                "title": "New Job",
                "company": "NewCo",
                "description": "Great role",
                "employment_type": "full_time",
                "remote_policy": "remote",
            },
            format="json",
        )
        assert response.status_code == 201
        assert response.data["title"] == "New Job"

    def test_retrieve_job_detail(self, auth_client):
        job = Job.objects.create(title="Test", company="Acme", status="open")
        response = auth_client.get(f"/api/jobs/{job.id}/")
        assert response.status_code == 200
        assert response.data["title"] == "Test"

    def test_job_sources_list(self, auth_client):
        JobSource.objects.create(name="Manual", slug="manual", is_active=True)
        response = auth_client.get("/api/jobs/sources/")
        assert response.status_code == 200
        results = response.data.get("results", response.data)
        assert len(results) == 1
        assert results[0]["name"] == "Manual"