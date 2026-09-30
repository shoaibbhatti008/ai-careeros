"""
AI CareerOS Settings Package.

Settings are split by environment:
- base: common to all environments
- development: local development
- production: production-hardened
- testing: test runs

Default to development for safety.
"""

from .development import *  # noqa: F401, F403
