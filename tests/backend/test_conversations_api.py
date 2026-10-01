"""Tests for conversations API."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.conversations.models import Conversation, Message

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
class TestConversationsAPI:
    def test_list_requires_auth(self, api_client):
        response = api_client.get("/api/conversations/")
        assert response.status_code == 401

    def test_list_returns_only_own_conversations(self, auth_client, user):
        other = User.objects.create_user(
            email="other@example.com", password="TestPass123!@#"
        )
        Conversation.objects.create(user=user, title="Mine")
        Conversation.objects.create(user=other, title="Theirs")

        response = auth_client.get("/api/conversations/")
        assert response.status_code == 200
        results = response.data.get("results", response.data)
        assert len(results) == 1
        assert results[0]["title"] == "Mine"

    def test_create_conversation(self, auth_client):
        response = auth_client.post(
            "/api/conversations/",
            {"title": "New Chat"},
            format="json",
        )
        assert response.status_code == 201
        assert response.data["title"] == "New Chat"

    def test_retrieve_conversation_with_messages(self, auth_client, user):
        conv = Conversation.objects.create(user=user, title="Test")
        Message.objects.create(user=user, conversation=conv, role="user", content="Hi")
        Message.objects.create(user=user, conversation=conv, role="assistant", content="Hello")

        response = auth_client.get(f"/api/conversations/{conv.id}/")
        assert response.status_code == 200
        assert len(response.data["messages"]) == 2

    def test_cannot_access_other_users_conversation(self, auth_client):
        other = User.objects.create_user(
            email="other@example.com", password="TestPass123!@#"
        )
        other_conv = Conversation.objects.create(user=other, title="Secret")
        response = auth_client.get(f"/api/conversations/{other_conv.id}/")
        assert response.status_code == 404

    def test_update_conversation(self, auth_client, user):
        conv = Conversation.objects.create(user=user, title="Old")
        response = auth_client.patch(
            f"/api/conversations/{conv.id}/",
            {"title": "New", "is_pinned": True},
            format="json",
        )
        assert response.status_code == 200
        conv.refresh_from_db()
        assert conv.title == "New"
        assert conv.is_pinned is True

    def test_delete_conversation(self, auth_client, user):
        conv = Conversation.objects.create(user=user, title="Delete")
        response = auth_client.delete(f"/api/conversations/{conv.id}/")
        assert response.status_code == 204
        assert not Conversation.objects.filter(pk=conv.pk).exists()

    def test_list_messages(self, auth_client, user):
        conv = Conversation.objects.create(user=user, title="With msgs")
        Message.objects.create(user=user, conversation=conv, role="user", content="Hi")
        response = auth_client.get(f"/api/conversations/{conv.id}/messages/")
        assert response.status_code == 200
        results = response.data.get("results", response.data)
        assert len(results) == 1

    def test_create_message(self, auth_client, user):
        conv = Conversation.objects.create(user=user, title="Chat")
        response = auth_client.post(
            f"/api/conversations/{conv.id}/messages/",
            {"role": "user", "content": "Hello there"},
            format="json",
        )
        assert response.status_code == 201
        assert response.data["content"] == "Hello there"

    def test_cannot_send_message_to_other_users_conversation(self, auth_client):
        other = User.objects.create_user(
            email="other@example.com", password="TestPass123!@#"
        )
        other_conv = Conversation.objects.create(user=other, title="Secret")
        response = auth_client.post(
            f"/api/conversations/{other_conv.id}/messages/",
            {"role": "user", "content": "Hack"},
            format="json",
        )
        assert response.status_code == 404