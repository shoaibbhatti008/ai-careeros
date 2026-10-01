"""Views for conversations app."""

from apps.users.permissions import IsOwner
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Conversation
from .serializers import (
    ConversationCreateSerializer,
    ConversationDetailSerializer,
    ConversationListSerializer,
    ConversationUpdateSerializer,
    MessageCreateSerializer,
    MessageListSerializer,
)


class ConversationListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/conversations/  — list user's conversations
    POST /api/conversations/  — create a conversation

    Query params:
    - archived: true | false
    - pinned: true | false
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Conversation.objects.filter(user=self.request.user)
        params = self.request.query_params

        if (archived := params.get("archived")) is not None:
            qs = qs.filter(is_archived=archived.lower() == "true")
        else:
            qs = qs.filter(is_archived=False)

        if (pinned := params.get("pinned")) is not None:
            qs = qs.filter(is_pinned=pinned.lower() == "true")

        return qs.order_by("-is_pinned", "-updated_at")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ConversationCreateSerializer
        return ConversationListSerializer


class ConversationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/conversations/<id>/  — retrieve conversation with messages
    PATCH  /api/conversations/<id>/  — update (title, archive, pin)
    DELETE /api/conversations/<id>/  — delete conversation
    """

    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ("PATCH", "PUT"):
            return ConversationUpdateSerializer
        return ConversationDetailSerializer


class MessageListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/conversations/<id>/messages/  — list messages
    POST /api/conversations/<id>/messages/  — create a message
    """

    permission_classes = [IsAuthenticated]

    def get_conversation(self) -> Conversation:
        return get_object_or_404(
            Conversation,
            pk=self.kwargs["conversation_id"],
            user=self.request.user,
        )

    def get_queryset(self):
        conversation = self.get_conversation()
        return conversation.messages.order_by("created_at")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return MessageCreateSerializer
        return MessageListSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["conversation"] = self.get_conversation()
        return ctx
