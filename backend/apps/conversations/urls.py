"""URL routing for conversations app."""

from django.urls import path

from .views import (
    ConversationDetailView,
    ConversationListCreateView,
    MessageListCreateView,
)

app_name = "conversations"

urlpatterns = [
    path("", ConversationListCreateView.as_view(), name="list-create"),
    path("<uuid:pk>/", ConversationDetailView.as_view(), name="detail"),
    path(
        "<uuid:conversation_id>/messages/",
        MessageListCreateView.as_view(),
        name="messages-list-create",
    ),
]
