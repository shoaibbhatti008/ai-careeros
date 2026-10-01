"""Tests for matches API."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.jobs.models import Job
from apps.matches.models import JobMatch, SkillGap
from apps.resumes.models import Resume, Skill

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
class TestJobMatchesAPI:
    def test_list_requires_auth(self, api_client):
        response = api_client.get("/api/matches/")
        assert response.status_code == 401

    def test_list_returns_only_own_matches(self, auth_client, user):
        other = User.objects.create_user(
            email="other@example.com", password="TestPass123!@#"
        )
        resume = Resume.objects.create(user=user, title="My resume")
        other_resume = Resume.objects.create(user=other, title="Other resume")
        job1 = Job.objects.create(title="Job A", company="Co", status="open")
        job2 = Job.objects.create(title="Job B", company="Co", status="open")

        JobMatch.objects.create(user=user, resume=resume, job=job1, score=0.8)
        JobMatch.objects.create(user=other, resume=other_resume, job=job2, score=0.9)

        response = auth_client.get("/api/matches/")
        assert response.status_code == 200
        results = response.data.get("results", response.data)
        assert len(results) == 1
        assert results[0]["score"] == 0.8

    def test_update_match_save(self, auth_client, user):
        resume = Resume.objects.create(user=user, title="R")
        job = Job.objects.create(title="J", company="C", status="open")
        match = JobMatch.objects.create(
            user=user, resume=resume, job=job, score=0.7
        )
        response = auth_client.patch(
            f"/api/matches/{match.id}/", {"is_saved": True}, format="json"
        )
        assert response.status_code == 200
        match.refresh_from_db()
        assert match.is_saved is True

    def test_delete_match(self, auth_client, user):
        resume = Resume.objects.create(user=user, title="R")
        job = Job.objects.create(title="J", company="C", status="open")
        match = JobMatch.objects.create(
            user=user, resume=resume, job=job, score=0.7
        )
        response = auth_client.delete(f"/api/matches/{match.id}/")
        assert response.status_code == 204
        assert not JobMatch.objects.filter(pk=match.pk).exists()

    def test_compute_match(self, auth_client, user):
        resume = Resume.objects.create(user=user, title="R")
        job = Job.objects.create(title="J", company="C", status="open")
        response = auth_client.post(
            "/api/matches/compute/",
            {"resume_id": str(resume.id), "job_id": str(job.id)},
            format="json",
        )
        assert response.status_code in (200, 201)
        assert response.data["score"] > 0
        assert response.data["job"]["title"] == "J"

    def test_compute_match_rejects_other_users_resume(self, auth_client):
        other = User.objects.create_user(
            email="other@example.com", password="TestPass123!@#"
        )
        other_resume = Resume.objects.create(user=other, title="Not mine")
        job = Job.objects.create(title="J", company="C", status="open")
        response = auth_client.post(
            "/api/matches/compute/",
            {"resume_id": str(other_resume.id), "job_id": str(job.id)},
            format="json",
        )
        assert response.status_code == 404

    def test_cannot_access_other_users_match(self, auth_client):
        other = User.objects.create_user(
            email="other@example.com", password="TestPass123!@#"
        )
        other_resume = Resume.objects.create(user=other, title="R")
        job = Job.objects.create(title="J", company="C", status="open")
        other_match = JobMatch.objects.create(
            user=other, resume=other_resume, job=job, score=0.5
        )
        response = auth_client.get(f"/api/matches/{other_match.id}/")
        assert response.status_code == 404


@pytest.mark.django_db
class TestSkillGapsAPI:
    def test_list_requires_auth(self, api_client):
        response = api_client.get("/api/matches/skill-gaps/")
        assert response.status_code == 401

    def test_create_skill_gap(self, auth_client, user):
        resume = Resume.objects.create(user=user, title="R")
        skill = Skill.objects.create(name="Python", slug="python", category="programming")
        response = auth_client.post(
            "/api/matches/skill-gaps/",
            {
                "resume_id": str(resume.id),
                "skill_id": str(skill.id),
                "target_role": "Backend Engineer",
                "priority": "high",
            },
            format="json",
        )
        assert response.status_code == 201
        assert response.data["target_role"] == "Backend Engineer"

    def test_create_skill_gap_rejects_other_users_resume(self, auth_client):
        other = User.objects.create_user(
            email="other@example.com", password="TestPass123!@#"
        )
        other_resume = Resume.objects.create(user=other, title="R")
        skill = Skill.objects.create(name="Python", slug="python2")
        response = auth_client.post(
            "/api/matches/skill-gaps/",
            {
                "resume_id": str(other_resume.id),
                "skill_id": str(skill.id),
                "target_role": "Backend",
            },
            format="json",
        )
        assert response.status_code == 400

    def test_update_skill_gap_resolve(self, auth_client, user):
        resume = Resume.objects.create(user=user, title="R")
        skill = Skill.objects.create(name="Django", slug="django", category="framework")
        gap = SkillGap.objects.create(
            user=user,
            resume=resume,
            skill=skill,
            target_role="Backend",
            priority="medium",
        )
        response = auth_client.patch(
            f"/api/matches/skill-gaps/{gap.id}/",
            {"is_resolved": True},
            format="json",
        )
        assert response.status_code == 200
        gap.refresh_from_db()
        assert gap.is_resolved is True