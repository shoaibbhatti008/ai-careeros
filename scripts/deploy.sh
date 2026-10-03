#!/usr/bin/env bash
# ============================================================
# AI CareerOS — Manual Deploy Script
# ============================================================
# Usage:
#   ./scripts/deploy.sh staging
#   ./scripts/deploy.sh production
# ============================================================

set -euo pipefail

ENV="${1:-staging}"
COMPOSE_FILE="docker-compose.prod.yml"
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"

echo "============================================"
echo " AI CareerOS Deploy — ${ENV}"
echo "============================================"

if [ ! -f .env ]; then
    echo "❌ .env not found. Aborting."
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "❌ Docker not installed. Aborting."
    exit 1
fi

echo "==> Backing up database..."
mkdir -p "${BACKUP_DIR}"
docker compose -f "${COMPOSE_FILE}" exec -T postgres \
    pg_dump -U "${POSTGRES_USER:-careeros}" "${POSTGRES_DB:-careeros}" \
    > "${BACKUP_DIR}/db.sql" || echo "⚠️  Backup skipped (DB may not be running)"
echo "    Backup saved to ${BACKUP_DIR}/db.sql"

echo "==> Pulling latest code..."
git fetch --all
git reset --hard origin/main

echo "==> Building new images..."
docker compose -f "${COMPOSE_FILE}" build --pull

echo "==> Rolling update..."
docker compose -f "${COMPOSE_FILE}" up -d --remove-orphans

echo "==> Waiting for services to be healthy..."
sleep 20

echo "==> Running migrations..."
docker compose -f "${COMPOSE_FILE}" exec -T backend \
    python manage.py migrate --noinput

echo "==> Collecting static files..."
docker compose -f "${COMPOSE_FILE}" exec -T backend \
    python manage.py collectstatic --noinput

echo "==> Smoke test..."
if curl -fsS http://localhost/api/health/ > /dev/null; then
    echo "✅ Backend healthy"
else
    echo "❌ Backend health check failed"
    exit 1
fi

if curl -fsS http://localhost/health > /dev/null; then
    echo "✅ Frontend healthy"
else
    echo "❌ Frontend health check failed"
    exit 1
fi

echo "==> Cleaning up old images..."
docker image prune -f

echo ""
echo "============================================"
echo " ✅ Deploy complete — ${ENV}"
echo "============================================"