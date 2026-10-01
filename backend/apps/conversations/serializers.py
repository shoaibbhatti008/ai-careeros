"""Serializers for conversations app."""

from rest_framework import serializers

from .models import Conversation, Message


class MessageListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing messages."""

    class Meta:
        model = Message
        fields = [
            "id",
            "role",
            "content",
            "tokens_used",
            "message_metadata",
            "created_at",
        ]
        read_only_fields = fields


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a message."""

    class Meta:
        model = Message
        fields = ["id", "role", "content", "tokens_used", "message_metadata"]
        read_only_fields = ["id", "tokens_used", "message_metadata"]

    def create(self, validated_data: dict) -> Message:
        conversation = self.context["conversation"]
        user = self.context["request"].user

        message = Message.objects.create(
            user=user,
            conversation=conversation,
            **validated_data,
        )

        # Update conversation counter
        conversation.message_count = conversation.messages.count()
        conversation.save(update_fields=["message_count"])

        return message


class ConversationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing conversations."""

    class Meta:
        model = Conversation
        fields = [
            "id",
            "title",
            "is_archived",
            "is_pinned",
            "message_count",
            "total_tokens",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "message_count",
            "total_tokens",
            "created_at",
            "updated_at",
        ]


class ConversationDetailSerializer(serializers.ModelSerializer):
    """Full serializer for a conversation."""

    messages = MessageListSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = [
            "id",
            "title",
            "is_archived",
            "is_pinned",
            "message_count",
            "total_tokens",
            "resume",
            "job",
            "metadata",
            "messages",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "message_count",
            "total_tokens",
            "created_at",
            "updated_at",
        ]


class ConversationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a conversation."""

    class Meta:
        model = Conversation
        fields = ["id", "title", "resume", "job", "metadata"]
        read_only_fields = ["id"]

    def create(self, validated_data: dict) -> Conversation:
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class ConversationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a conversation (title, archive, pin)."""

    class Meta:
        model = Conversation
        fields = ["title", "is_archived", "is_pinned"]
