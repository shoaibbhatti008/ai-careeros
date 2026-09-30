"""
Production settings for AI CareerOS.

Security-hardened. Never use for development.
"""

from .base import *  # noqa: F401, F403

DEBUG = False

# ============================================================
# Security Headers
# ============================================================

SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
X_FRAME_OPTIONS = "DENY"

# ============================================================
# Static Files (Whitenoise)
# ============================================================

MIDDLEWARE.insert(  # noqa: F405
    1,
    "whitenoise.middleware.WhiteNoiseMiddleware",
)
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ============================================================
# Email
# ============================================================

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
