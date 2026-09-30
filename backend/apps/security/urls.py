"""URL routing for security app."""

from django.urls import path

from .views import (
    AuditLogListView,
    LoginHistoryView,
    SecurityEventsView,
    SecurityOverviewView,
)

app_name = "security"

urlpatterns = [
    path("audit-logs/", AuditLogListView.as_view(), name="audit-logs"),
    path("login-history/", LoginHistoryView.as_view(), name="login-history"),
    path("events/", SecurityEventsView.as_view(), name="events"),
    path("overview/", SecurityOverviewView.as_view(), name="overview"),
]
