"""
Security middlewares for AI CareerOS.

- RequestIDMiddleware: attaches a unique request ID to every request.
- SecurityHeadersMiddleware: adds additional security headers.
"""

import uuid

from django.utils.deprecation import MiddlewareMixin


class RequestIDMiddleware(MiddlewareMixin):
    """
    Attaches a unique request ID to every request.

    The ID is:
    - Available as `request.request_id`
    - Returned in the `X-Request-ID` response header
    - Usable in logs and audit logs
    """

    HEADER = "HTTP_X_REQUEST_ID"
    RESPONSE_HEADER = "X-Request-ID"

    def process_request(self, request) -> None:
        request_id = request.META.get(self.HEADER) or str(uuid.uuid4())
        request.request_id = request_id

    def process_response(self, request, response):
        request_id = getattr(request, "request_id", None)
        if request_id:
            response[self.RESPONSE_HEADER] = request_id
        return response


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Adds security headers to every response.

    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY
    - Referrer-Policy: strict-origin-when-cross-origin
    - Permissions-Policy: minimal permissions
    - Cross-Origin-Opener-Policy
    """

    def process_response(self, request, response):
        response.setdefault("X-Content-Type-Options", "nosniff")
        response.setdefault("X-Frame-Options", "DENY")
        response.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.setdefault(
            "Permissions-Policy",
            "geolocation=(), microphone=(), camera=(), payment=()",
        )
        response.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        return response
