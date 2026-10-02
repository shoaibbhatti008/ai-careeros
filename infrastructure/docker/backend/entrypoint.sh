#!/bin/bash
# ============================================================
# AI CareerOS — Backend Entrypoint
# ============================================================
set -e

echo "[entrypoint] Starting AI CareerOS backend..."

# Wait for PostgreSQL
if [ -n "$POSTGRES_HOST" ]; then
    echo "[entrypoint] Waiting for PostgreSQL at $POSTGRES_HOST:${POSTGRES_PORT:-5432}..."
    until python -c "
import os, sys, socket
host = os.environ.get('POSTGRES_HOST', 'localhost')
port = int(os.environ.get('POSTGRES_PORT', 5432))
try:
    s = socket.create_connection((host, port), timeout=2)
    s.close()
except Exception:
    sys.exit(1)
" 2>/dev/null; do
        sleep 2
    done
    echo "[entrypoint] PostgreSQL is up."
fi

# Wait for Redis
if [ -n "$REDIS_HOST" ]; then
    echo "[entrypoint] Waiting for Redis at $REDIS_HOST:${REDIS_PORT:-6379}..."
    until python -c "
import os, sys, socket
host = os.environ.get('REDIS_HOST', 'localhost')
port = int(os.environ.get('REDIS_PORT', 6379))
try:
    s = socket.create_connection((host, port), timeout=2)
    s.close()
except Exception:
    sys.exit(1)
" 2>/dev/null; do
        sleep 2
    done
    echo "[entrypoint] Redis is up."
fi

# Run migrations
echo "[entrypoint] Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "[entrypoint] Collecting static files..."
python manage.py collectstatic --noinput --clear

# Execute the CMD
echo "[entrypoint] Starting application: $@"
exec "$@"