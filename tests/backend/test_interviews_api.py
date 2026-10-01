"""Tests for interviews API."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.interviews.models import InterviewSession

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
class TestInterviewsAPI:
    def test_list_requires_auth(self, api_client):
        response = api_client.get("/api/interviews/")
        assert response.status_code == 401

    def test_list_returns_only_own_sessions(self, auth_client, user):
        other = User.objects.create_user(
            email="other@example.com", password="TestPass123!@#"
        )
        InterviewSession.objects.create(user=user, title="Mine")
        InterviewSession.objects.create(user=other, title="Theirs")

        response = auth_client.get("/api/interviews/")
        assert response.status_code == 200
        results = response.data.get("results", response.data)
        assert len(results) == 1
        assert results[0]["title"] == "Mine"

    def test_create_session(self, auth_client):
        response = auth_client.post(
            "/api/interviews/",
            {"title": "Mock Interview", "interview_type": "technical"},
            format="json",
        )
        assert response.status_code == 201
        assert response.data["title"] == "Mock Interview"

    def test_cannot_access_other_users_session(self, auth_client):
        other = User.objects.create_user(
            email="other@example.com", password="TestPass123!@#"
        )
        other_session = InterviewSession.objects.create(user=other, title="Secret")
        response = auth_client.get(f"/api/interviews/{other_session.id}/")
        assert response.status_code == 404

    def test_update_session(self, auth_client, user):
        session = InterviewSession.objects.create(user=user, title="Old")
        response = auth_client.patch(
            f"/api/interviews/{session.id}/", {"title": "New"}, format="json"
        )
        assert response.status_code == 200
        session.refresh_from_db()
        assert session.title == "New"

    def test_delete_session(self, auth_client, user):
        session = InterviewSession.objects.create(user=user, title="Delete")
        response = auth_client.delete(f"/api/interviews/{session.id}/")
        assert response.status_code == 204
        assert not InterviewSession.objects.filter(pk=session.pk).exists()

    def test_create_question(self, auth_client, user):
        session = InterviewSession.objects.create(user=user, title="Test")
        response = auth_client.post(
            f"/api/interviews/{session.id}/questions/",
            {"order": 1, "text": "Tell me about yourself."},
            format="json",
        )
        assert response.status_code == 201
        assert response.data["text"] == "Tell me about yourself."

    def test_list_questions(self, auth_client, user):
        session = InterviewSession.objects.create(user=user, title="Test")
        response = auth_client.get(f"/api/interviews/{session.id}/questions/")
        assert response.status_code == 200