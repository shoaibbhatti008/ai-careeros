"""
Security signals — track logins, logouts, and other sensitive actions.
"""

from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.dispatch import receiver

from .models import AuditLog, LoginAttempt
from .rate_limit import get_client_ip


def _get_client_info(request) -> tuple[str | None, str]:
    """Extract IP and user agent from request."""
    if request is None:
        return None, ""
    ip = get_client_ip(request)
    user_agent = request.META.get("HTTP_USER_AGENT", "")[:500]
    return ip, user_agent


@receiver(user_logged_in)
def on_user_logged_in(sender, request, user, **kwargs) -> None:
    """Record successful login."""
    ip, user_agent = _get_client_info(request)
    request_id = getattr(request, "request_id", "") if request else ""

    AuditLog.objects.create(
        user=user,
        action=AuditLog.Action.LOGIN_SUCCESS,
        ip_address=ip,
        user_agent=user_agent,
        request_id=request_id,
    )
    LoginAttempt.objects.create(
        email=user.email,
        user=user,
        was_successful=True,
        ip_address=ip,
        user_agent=user_agent,
    )


@receiver(user_logged_out)
def on_user_logged_out(sender, request, user, **kwargs) -> None:
    """Record logout."""
    if user is None:
        return
    ip, user_agent = _get_client_info(request)
    request_id = getattr(request, "request_id", "") if request else ""

    AuditLog.objects.create(
        user=user,
        action=AuditLog.Action.LOGOUT,
        ip_address=ip,
        user_agent=user_agent,
        request_id=request_id,
    )


@receiver(user_login_failed)
def on_user_login_failed(sender, credentials, request, **kwargs) -> None:
    """Record failed login attempt."""
    ip, user_agent = _get_client_info(request)
    email = credentials.get("email") or credentials.get("username", "unknown")

    LoginAttempt.objects.create(
        email=email,
        was_successful=False,
        ip_address=ip,
        user_agent=user_agent,
    )

    AuditLog.objects.create(
        action=AuditLog.Action.LOGIN_FAILED,
        ip_address=ip,
        user_agent=user_agent,
        metadata={"email": email},
    )
