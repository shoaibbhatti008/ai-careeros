"""
Development settings for AI CareerOS.

Inherits from base and adds dev-specific configuration.
"""

from .base import *  # noqa: F401, F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Dev-only apps
INSTALLED_APPS += [  # noqa: F405
    "debug_toolbar",
]

# Dev-only middleware (debug toolbar should be first)
MIDDLEWARE.insert(  # noqa: F405
    0,
    "debug_toolbar.middleware.DebugToolbarMiddleware",
)

INTERNAL_IPS = ["127.0.0.1", "localhost"]

# Allow all CORS in dev
CORS_ALLOW_ALL_ORIGINS = True

# Email: console backend in dev
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Simpler passwords in dev
AUTH_PASSWORD_VALIDATORS = []
