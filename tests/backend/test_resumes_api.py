"""Tests for resumes API."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.resumes.models import Resume, ResumeVersion, Skill

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
class TestResumesAPI:
    def test_list_requires_auth(self, api_client):
        response = api_client.get("/api/resumes/")
        assert response.status_code == 401

    def test_list_returns_only_own_resumes(self, api_client, user, auth_client):
        # Create another user's resume
        other = User.objects.create_user(email="other@example.com", password="TestPass123!@#")
        Resume.objects.create(user=other, title="Other resume")
        Resume.objects.create(user=user, title="My resume")

        response = auth_client.get("/api/resumes/")
        assert response.status_code == 200
        # Pagination wraps in "results"
        results = response.data.get("results", response.data)
        assert len(results) == 1
        assert results[0]["title"] == "My resume"

    def test_create_resume(self, auth_client):
        response = auth_client.post(
            "/api/resumes/",
            {"title": "My Resume", "raw_text": "Some resume text"},
            format="json",
        )
        assert response.status_code == 201
        assert response.data["title"] == "My Resume"

    def test_retrieve_resume_detail(self, auth_client, user):
        resume = Resume.objects.create(user=user, title="Test")
        response = auth_client.get(f"/api/resumes/{resume.id}/")
        assert response.status_code == 200
        assert response.data["title"] == "Test"

    def test_cannot_access_other_users_resume(self, api_client, auth_client):
        other = User.objects.create_user(email="other@example.com", password="TestPass123!@#")
        other_resume = Resume.objects.create(user=other, title="Secret")
        response = auth_client.get(f"/api/resumes/{other_resume.id}/")
        assert response.status_code == 404  # Ownership filter returns 404, not 403

    def test_update_resume(self, auth_client, user):
        resume = Resume.objects.create(user=user, title="Old")
        response = auth_client.patch(
            f"/api/resumes/{resume.id}/", {"title": "New"}, format="json"
        )
        assert response.status_code == 200
        resume.refresh_from_db()
        assert resume.title == "New"

    def test_delete_resume(self, auth_client, user):
        resume = Resume.objects.create(user=user, title="Delete me")
        response = auth_client.delete(f"/api/resumes/{resume.id}/")
        assert response.status_code == 204
        assert not Resume.objects.filter(pk=resume.pk).exists()

    def test_skills_list(self, auth_client):
        Skill.objects.create(name="Python", slug="python", category="programming")
        response = auth_client.get("/api/resumes/skills/")
        assert response.status_code == 200
        results = response.data.get("results", response.data)
        assert len(results) == 1
        assert results[0]["name"] == "Python"

    def test_create_resume_version(self, auth_client, user):
        resume = Resume.objects.create(user=user, title="With versions")
        response = auth_client.post(
            f"/api/resumes/{resume.id}/versions/",
            {"raw_text": "Version 1 content", "source": "manual"},
            format="json",
        )
        assert response.status_code == 201
        assert response.data["version_number"] == 1
        assert response.data["is_current"] is True