"""URL routing for documents app."""

from django.urls import path

from .views import (
    DocumentChunkListView,
    DocumentDetailView,
    DocumentListCreateView,
)

app_name = "documents"

urlpatterns = [
    path("", DocumentListCreateView.as_view(), name="list-create"),
    path("<uuid:pk>/", DocumentDetailView.as_view(), name="detail"),
    path(
        "<uuid:document_id>/chunks/",
        DocumentChunkListView.as_view(),
        name="chunks-list",
    ),
]
