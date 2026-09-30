"""Views for security app — audit logs, login history, security events."""

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AuditLog, LoginAttempt, SecurityEvent
from .serializers import (
    AuditLogSerializer,
    LoginAttemptSerializer,
    SecurityEventSerializer,
)


class AuditLogListView(generics.ListAPIView):
    """
    GET /api/security/audit-logs/

    Returns audit logs for the current user only.
    """

    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AuditLog.objects.filter(user=self.request.user)[:200]


class LoginHistoryView(generics.ListAPIView):
    """
    GET /api/security/login-history/

    Returns login attempts for the current user only.
    """

    serializer_class = LoginAttemptSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return LoginAttempt.objects.filter(user=self.request.user)[:100]


class SecurityEventsView(generics.ListAPIView):
    """
    GET /api/security/events/

    Returns security events for the current user only.
    """

    serializer_class = SecurityEventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SecurityEvent.objects.filter(user=self.request.user)[:100]


class SecurityOverviewView(APIView):
    """
    GET /api/security/overview/

    Returns a summary of security-related info for the current user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(
            {
                "user_id": str(user.id),
                "email": user.email,
                "last_login": user.last_login,
                "account_created": user.date_joined,
                "is_active": user.is_active,
                "recent_logins_count": LoginAttempt.objects.filter(
                    user=user, was_successful=True
                ).count(),
                "failed_logins_count": LoginAttempt.objects.filter(
                    user=user, was_successful=False
                ).count(),
                "unresolved_events_count": SecurityEvent.objects.filter(
                    user=user, resolved=False
                ).count(),
            }
        )
