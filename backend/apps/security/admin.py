"""Admin for security app."""

from django.contrib import admin

from .models import AuditLog, LoginAttempt, SecurityEvent


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "action", "user", "ip_address", "request_id")
    list_filter = ("action", "created_at")
    search_fields = ("user__email", "ip_address", "request_id")
    readonly_fields = (
        "id",
        "user",
        "action",
        "ip_address",
        "user_agent",
        "request_id",
        "metadata",
        "created_at",
    )

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ("created_at", "email", "was_successful", "ip_address")
    list_filter = ("was_successful", "created_at")
    search_fields = ("email", "ip_address")
    readonly_fields = (
        "id",
        "email",
        "user",
        "was_successful",
        "ip_address",
        "user_agent",
        "created_at",
    )

    def has_add_permission(self, request) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False


@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    list_display = ("created_at", "event_type", "severity", "user", "resolved")
    list_filter = ("severity", "event_type", "resolved")
    search_fields = ("event_type", "description", "user__email")
    readonly_fields = ("id", "created_at")
