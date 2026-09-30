"""Security-focused tests for authentication."""

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
        "email": "user@example.com",
        "password": "TestPass123!@#",
        "password_confirm": "TestPass123!@#",
    }


@pytest.mark.django_db
class TestAuthSecurity:
    def test_cannot_access_me_without_token(self, api_client):
        response = api_client.get("/api/users/me/")
        assert response.status_code == 401

    def test_cannot_access_me_with_invalid_token(self, api_client):
        api_client.credentials(HTTP_AUTHORIZATION="Bearer invalid.token.here")
        response = api_client.get("/api/users/me/")
        assert response.status_code == 401

    def test_cannot_access_me_with_tampered_token(self, api_client, user_data):
        reg = api_client.post("/api/users/register/", user_data, format="json")
        access = reg.data["access"]
        parts = access.split(".")
        tampered = parts[0] + "." + parts[1] + ".tampered_signature"
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {tampered}")
        response = api_client.get("/api/users/me/")
        assert response.status_code == 401

    def test_password_not_returned_in_response(self, api_client, user_data):
        response = api_client.post("/api/users/register/", user_data, format="json")
        assert "password" not in response.data.get("user", {})

        me_response = api_client.get(
            "/api/users/me/",
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}",
        )
        assert "password" not in me_response.data

    def test_email_enumeration_prevented(self, api_client, user_data):
        api_client.post("/api/users/register/", user_data, format="json")

        wrong_email = api_client.post(
            "/api/users/login/",
            {"email": "nonexistent@example.com", "password": "any"},
            format="json",
        )
        wrong_password = api_client.post(
            "/api/users/login/",
            {"email": user_data["email"], "password": "wrong"},
            format="json",
        )
        assert wrong_email.status_code == 401
        assert wrong_password.status_code == 401
    