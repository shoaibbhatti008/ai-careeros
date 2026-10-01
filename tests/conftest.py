"""
Root pytest configuration for AI CareerOS tests.

Ensures backend/ is on sys.path so both Django apps and the pure-Python
agents package are importable.
"""

import sys
from pathlib import Path

# Compute project root (folder containing `backend/` and `tests/`)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"

# Add backend/ to sys.path (for `agents` package and Django apps)
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))