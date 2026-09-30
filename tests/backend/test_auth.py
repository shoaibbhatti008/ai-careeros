"""Tests for authentication endpoints."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def user_data() -> dict:
    return {
        "email": "test@example.com",
        "password": "TestPass123!@#",
        "password_confirm": "TestPass123!@#",
        "first_name": "Test",
        "last_name": "User",
    }


@pytest.mark.django_db
class TestRegistration:
    def test_register_creates_user(self, api_client, user_data):
        response = api_client.post("/api/users/register/", user_data, format="json")
        assert response.status_code == 201
        assert "access" in response.data
        assert "refresh" in response.data
        assert response.data["user"]["email"] == "test@example.com"
        assert User.objects.filter(email="test@example.com").exists()

    def test_register_rejects_duplicate_email(self, api_client, user_data):
        api_client.post("/api/users/register/", user_data, format="json")
        response = api_client.post("/api/users/register/", user_data, format="json")
        assert response.status_code == 400
        assert "email" in response.data

    def test_register_rejects_mismatched_passwords(self, api_client, user_data):
        user_data["password_confirm"] = "DifferentPass123!"
        response = api_client.post("/api/users/register/", user_data, format="json")
        assert response.status_code == 400
        assert "password_confirm" in response.data

    def test_register_rejects_weak_password(self, api_client, user_data):
        user_data["password"] = "123"
        user_data["password_confirm"] = "123"
        response = api_client.post("/api/users/register/", user_data, format="json")
        assert response.status_code == 400

    def test_register_creates_user_profile(self, api_client, user_data):
        api_client.post("/api/users/register/", user_data, format="json")
        user = User.objects.get(email="test@example.com")
        assert hasattr(user, "profile")


@pytest.mark.django_db
class TestLogin:
    def test_login_with_valid_credentials(self, api_client, user_data):
        api_client.post("/api/users/register/", user_data, format="json")
        response = api_client.post(
            "/api/users/login/",
            {"email": user_data["email"], "password": user_data["password"]},
            format="json",
        )
        assert response.status_code == 200
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_with_wrong_password(self, api_client, user_data):
        api_client.post("/api/users/register/", user_data, format="json")
        response = api_client.post(
            "/api/users/login/",
            {"email": user_data["email"], "password": "WrongPass123!"},
            format="json",
        )
        assert response.status_code == 401

    def test_login_with_nonexistent_email(self, api_client):
        response = api_client.post(
            "/api/users/login/",
            {"email": "nobody@example.com", "password": "any"},
            format="json",
        )
        assert response.status_code == 401


@pytest.mark.django_db
class TestMe:
    def test_me_requires_authentication(self, api_client):
        response = api_client.get("/api/users/me/")
        assert response.status_code == 401

    def test_me_returns_current_user(self, api_client, user_data):
        reg = api_client.post("/api/users/register/", user_data, format="json")
        access = reg.data["access"]
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.get("/api/users/me/")
        assert response.status_code == 200
        assert response.data["email"] == "test@example.com"


@pytest.mark.django_db
class TestLogout:
    def test_logout_blacklists_token(self, api_client, user_data):
        reg = api_client.post("/api/users/register/", user_data, format="json")
        access = reg.data["access"]
        refresh = reg.data["refresh"]

        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = api_client.post(
            "/api/users/logout/",
            {"refresh": refresh},
            format="json",
        )
        assert response.status_code == 200

        refresh_response = api_client.post(
            "/api/users/token/refresh/",
            {"refresh": refresh},
            format="json",
        )
        assert refresh_response.status_code == 401


@pytest.mark.django_db
class TestPasswordChange:
    def test_password_change_success(self, api_client, user_data):
        reg = api_client.post("/api/users/register/", user_data, format="json")
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {reg.data['access']}")

        response = api_client.post(
            "/api/users/me/password/",
            {
                "current_password": user_data["password"],
                "new_password": "NewPass456!@#",
                "new_password_confirm": "NewPass456!@#",
            },
            format="json",
        )
        assert response.status_code == 200

        login = api_client.post(
            "/api/users/login/",
            {"email": user_data["email"], "password": "NewPass456!@#"},
            format="json",
        )
        assert login.status_code == 200

    def test_password_change_wrong_current(self, api_client, user_data):
        reg = api_client.post("/api/users/register/", user_data, format="json")
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {reg.data['access']}")

        response = api_client.post(
            "/api/users/me/password/",
            {
                "current_password": "WrongPass123!",
                "new_password": "NewPass456!@#",
                "new_password_confirm": "NewPass456!@#",
            },
            format="json",
        )
        assert response.status_code == 400