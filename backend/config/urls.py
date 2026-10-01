"""
URL configuration for AI CareerOS.
"""

from django.conf import settings
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def health_check(request):
    """Health check endpoint."""
    from django.core.cache import cache
    from django.db import connection

    status = {"status": "healthy", "version": "0.1.0", "checks": {}}

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        status["checks"]["database"] = "ok"
    except Exception as exc:
        status["checks"]["database"] = f"error: {exc}"
        status["status"] = "unhealthy"

    try:
        cache.set("_health_check", "ok", timeout=5)
        if cache.get("_health_check") == "ok":
            status["checks"]["redis"] = "ok"
        else:
            status["checks"]["redis"] = "error"
            status["status"] = "unhealthy"
    except Exception as exc:
        status["checks"]["redis"] = f"error: {exc}"
        status["status"] = "unhealthy"

    http_status = 200 if status["status"] == "healthy" else 503
    return JsonResponse(status, status=http_status)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check, name="health-check"),
    path("api/users/", include("apps.users.urls")),
    path("api/security/", include("apps.security.urls")),
    path("api/resumes/", include("apps.resumes.urls")),
    path("api/jobs/", include("apps.jobs.urls")),
    path("api/documents/", include("apps.documents.urls")),  # ← Naya
    path("api/conversations/", include("apps.conversations.urls")),  # ← Naya
    path("api/matches/", include("apps.matches.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]

if settings.DEBUG:
    try:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass
