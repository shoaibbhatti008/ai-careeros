"""
Celery configuration for AI CareerOS.

Run worker:
    celery -A config worker -l info

Run beat:
    celery -A config beat -l info
"""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("careeros")

# Read config from Django settings, prefix CELERY_
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks from all installed apps
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self) -> None:
    """Simple debug task to verify Celery is working."""
    print(f"Request: {self.request!r}")
