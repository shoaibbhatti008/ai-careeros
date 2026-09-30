"""
Environment variable loader with type validation.

Reads from .env file and OS environment. Fails fast on
missing required variables.

Usage:
    from config.env import env
    SECRET_KEY = env("SECRET_KEY")                # required
    DEBUG = env.bool("DEBUG", default=False)      # optional
    ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")     # comma-separated
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

if ENV_FILE.exists():
    load_dotenv(ENV_FILE)


class EnvError(Exception):
    """Raised when an environment variable is missing or invalid."""


class Env:
    """Typed environment variable reader."""

    def __call__(self, key: str, default: str | None = None) -> str:
        value = os.environ.get(key, default)
        if value is None:
            raise EnvError(
                f"Required environment variable '{key}' is not set. "
                f"Check your .env file or OS environment."
            )
        return value

    def bool(self, key: str, default: bool = False) -> bool:
        value = os.environ.get(key)
        if value is None:
            return default
        return value.strip().lower() in ("true", "1", "yes", "on")

    def int(self, key: str, default: int = 0) -> int:
        value = os.environ.get(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError as exc:
            raise EnvError(f"'{key}' must be an integer, got: {value!r}") from exc

    def float(self, key: str, default: float = 0.0) -> float:
        value = os.environ.get(key)
        if value is None:
            return default
        try:
            return float(value)
        except ValueError as exc:
            raise EnvError(f"'{key}' must be a float, got: {value!r}") from exc

    def list(self, key: str, default: list[str] | None = None) -> list[str]:
        value = os.environ.get(key)
        if value is None:
            return default if default is not None else []
        return [item.strip() for item in value.split(",") if item.strip()]


env = Env()
