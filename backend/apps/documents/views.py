"""Views for documents app."""

from apps.users.permissions import IsOwner
from rest_framework import generics
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated

from .models import Document, DocumentChunk
from .serializers import (
    DocumentChunkSerializer,
    DocumentDetailSerializer,
    DocumentListSerializer,
    DocumentUploadSerializer,
)


class DocumentListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/documents/  — list current user's documents
    POST /api/documents/  — upload a new document (multipart/form-data)

    Query params:
    - doc_type: filter by document type
    - status: pending | processing | ready | failed
    - search: search in title
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        qs = Document.objects.filter(user=self.request.user)
        params = self.request.query_params

        if doc_type := params.get("doc_type"):
            qs = qs.filter(doc_type=doc_type)

        if status_param := params.get("status"):
            qs = qs.filter(status=status_param)

        if search := params.get("search"):
            qs = qs.filter(title__icontains=search)

        return qs.order_by("-created_at")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return DocumentUploadSerializer
        return DocumentListSerializer


class DocumentDetailView(generics.RetrieveDestroyAPIView):
    """
    GET    /api/documents/<id>/  — retrieve a document
    DELETE /api/documents/<id>/  — delete a document
    """

    permission_classes = [IsAuthenticated, IsOwner]
    serializer_class = DocumentDetailSerializer

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)


class DocumentChunkListView(generics.ListAPIView):
    """
    GET /api/documents/<id>/chunks/  — list chunks of a document
    """

    serializer_class = DocumentChunkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DocumentChunk.objects.filter(
            document_id=self.kwargs["document_id"],
            user=self.request.user,
        ).order_by("chunk_index")
