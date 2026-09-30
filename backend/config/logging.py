"""
Structured logging configuration.

JSON in production, human-readable in development.
"""

import os

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.environ.get("LOG_FORMAT", "human").lower()

JSON_FORMATTER = {
    "format": '{"time":"%(asctime)s","level":"%(levelname)s",'
    '"logger":"%(name)s","message":"%(message)s",'
    '"module":"%(module)s","line":%(lineno)d}',
}

HUMAN_FORMATTER = {
    "format": "[%(asctime)s] %(levelname)-8s %(name)s: %(message)s",
    "datefmt": "%Y-%m-%d %H:%M:%S",
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": JSON_FORMATTER,
        "human": HUMAN_FORMATTER,
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json" if LOG_FORMAT == "json" else "human",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": LOG_LEVEL,
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "celery": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
    },
}
