"""Tests for agents API."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.agents.models import AgentTask, ApprovalRequest

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
class TestAgentTasksAPI:
    def test_list_requires_auth(self, api_client):
        response = api_client.get("/api/agents/tasks/")
        assert response.status_code == 401

    def test_list_returns_only_own_tasks(self, auth_client, user):
        other = User.objects.create_user(
            email="other@example.com", password="TestPass123!@#"
        )
        AgentTask.objects.create(user=user, agent_name="resume", task_type="analyze")
        AgentTask.objects.create(user=other, agent_name="job", task_type="search")

        response = auth_client.get("/api/agents/tasks/")
        assert response.status_code == 200
        results = response.data.get("results", response.data)
        assert len(results) == 1
        assert results[0]["agent_name"] == "resume"

    def test_create_task(self, auth_client):
        response = auth_client.post(
            "/api/agents/tasks/",
            {"agent_name": "resume", "task_type": "analyze_resume"},
            format="json",
        )
        assert response.status_code == 201
        assert response.data["agent_name"] == "resume"

    def test_retrieve_task_detail(self, auth_client, user):
        task = AgentTask.objects.create(user=user, agent_name="resume", task_type="analyze")
        response = auth_client.get(f"/api/agents/tasks/{task.id}/")
        assert response.status_code == 200
        assert response.data["agent_name"] == "resume"

    def test_cannot_access_other_users_task(self, auth_client):
        other = User.objects.create_user(
            email="other@example.com", password="TestPass123!@#"
        )
        other_task = AgentTask.objects.create(
            user=other, agent_name="resume", task_type="analyze"
        )
        response = auth_client.get(f"/api/agents/tasks/{other_task.id}/")
        assert response.status_code == 404


@pytest.mark.django_db
class TestApprovalsAPI:
    def test_list_requires_auth(self, api_client):
        response = api_client.get("/api/agents/approvals/")
        assert response.status_code == 401

    def test_list_returns_only_own_approvals(self, auth_client, user):
        other = User.objects.create_user(
            email="other@example.com", password="TestPass123!@#"
        )
        ApprovalRequest.objects.create(
            user=user, title="Mine", action_type="send_email"
        )
        ApprovalRequest.objects.create(
            user=other, title="Theirs", action_type="send_email"
        )

        response = auth_client.get("/api/agents/approvals/")
        assert response.status_code == 200
        results = response.data.get("results", response.data)
        assert len(results) == 1
        assert results[0]["title"] == "Mine"

    def test_approve_request(self, auth_client, user):
        approval = ApprovalRequest.objects.create(
            user=user, title="Send email", action_type="send_email"
        )
        response = auth_client.post(
            f"/api/agents/approvals/{approval.id}/decide/",
            {"decision": "approved", "note": "Looks good"},
            format="json",
        )
        assert response.status_code == 200
        approval.refresh_from_db()
        assert approval.status == "approved"

    def test_reject_request(self, auth_client, user):
        approval = ApprovalRequest.objects.create(
            user=user, title="Send email", action_type="send_email"
        )
        response = auth_client.post(
            f"/api/agents/approvals/{approval.id}/decide/",
            {"decision": "rejected"},
            format="json",
        )
        assert response.status_code == 200
        approval.refresh_from_db()
        assert approval.status == "rejected"

    def test_cannot_decide_already_decided(self, auth_client, user):
        approval = ApprovalRequest.objects.create(
            user=user,
            title="Done",
            action_type="send_email",
            status="approved",
        )
        response = auth_client.post(
            f"/api/agents/approvals/{approval.id}/decide/",
            {"decision": "approved"},
            format="json",
        )
        assert response.status_code == 400

    def test_cannot_decide_other_users_approval(self, auth_client):
        other = User.objects.create_user(
            email="other@example.com", password="TestPass123!@#"
        )
        other_approval = ApprovalRequest.objects.create(
            user=other, title="Secret", action_type="send_email"
        )
        response = auth_client.post(
            f"/api/agents/approvals/{other_approval.id}/decide/",
            {"decision": "approved"},
            format="json",
        )
        assert response.status_code == 404