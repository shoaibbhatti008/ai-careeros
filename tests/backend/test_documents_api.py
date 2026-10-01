"""Tests for documents API."""

from io import BytesIO

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from apps.documents.models import Document

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
class TestDocumentsAPI:
    def test_list_requires_auth(self, api_client):
        response = api_client.get("/api/documents/")
        assert response.status_code == 401

    def test_list_returns_only_own_documents(self, auth_client, user):
        other = User.objects.create_user(
            email="other@example.com", password="TestPass123!@#"
        )
        # Can't easily create Document without file, so use a minimal one
        Document.objects.create(
            user=user,
            title="Mine",
            file="documents/test.txt",
            file_size=100,
        )
        Document.objects.create(
            user=other,
            title="Theirs",
            file="documents/other.txt",
            file_size=100,
        )

        response = auth_client.get("/api/documents/")
        assert response.status_code == 200
        results = response.data.get("results", response.data)
        assert len(results) == 1
        assert results[0]["title"] == "Mine"

    def test_upload_document(self, auth_client):
        content = b"Hello, this is a test document."
        upload = SimpleUploadedFile("test.txt", content, content_type="text/plain")

        response = auth_client.post(
            "/api/documents/",
            {
                "title": "Test Doc",
                "doc_type": "notes",
                "file": upload,
            },
            format="multipart",
        )
        assert response.status_code == 201
        assert response.data["title"] == "Test Doc"

    def test_upload_rejects_bad_extension(self, auth_client):
        upload = SimpleUploadedFile("bad.exe", b"binary", content_type="application/octet-stream")
        response = auth_client.post(
            "/api/documents/",
            {"title": "Bad", "doc_type": "other", "file": upload},
            format="multipart",
        )
        assert response.status_code == 400

    def test_cannot_access_other_users_document(self, auth_client):
        other = User.objects.create_user(
            email="other@example.com", password="TestPass123!@#"
        )
        other_doc = Document.objects.create(
            user=other,
            title="Secret",
            file="documents/secret.txt",
            file_size=100,
        )
        response = auth_client.get(f"/api/documents/{other_doc.id}/")
        assert response.status_code == 404

    def test_delete_own_document(self, auth_client, user):
        doc = Document.objects.create(
            user=user,
            title="Delete me",
            file="documents/del.txt",
            file_size=100,
        )
        response = auth_client.delete(f"/api/documents/{doc.id}/")
        assert response.status_code == 204
        assert not Document.objects.filter(pk=doc.pk).exists()

    def test_chunks_list_for_own_document(self, auth_client, user):
        doc = Document.objects.create(
            user=user,
            title="With chunks",
            file="documents/chunks.txt",
            file_size=100,
        )
        response = auth_client.get(f"/api/documents/{doc.id}/chunks/")
        assert response.status_code == 200