"""Serializers for security app."""

from rest_framework import serializers

from .models import AuditLog, LoginAttempt, SecurityEvent


class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True, default=None)

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "user_email",
            "action",
            "ip_address",
            "user_agent",
            "request_id",
            "metadata",
            "created_at",
        ]
        read_only_fields = fields


class LoginAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginAttempt
        fields = [
            "id",
            "email",
            "was_successful",
            "ip_address",
            "user_agent",
            "created_at",
        ]
        read_only_fields = fields


class SecurityEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityEvent
        fields = [
            "id",
            "event_type",
            "severity",
            "description",
            "ip_address",
            "metadata",
            "created_at",
            "resolved",
        ]
        read_only_fields = fields
