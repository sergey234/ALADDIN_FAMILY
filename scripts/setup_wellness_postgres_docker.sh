#!/usr/bin/env bash
# p3-11 — local/VPS Postgres for wellness (docker)
set -euo pipefail

PG_PORT="${WELLNESS_PG_PORT:-5433}"
PG_USER="${WELLNESS_PG_USER:-wellness}"
PG_PASS="${WELLNESS_PG_PASS:-wellness_change_me}"
PG_DB="${WELLNESS_PG_DB:-wellness}"

echo ">>> Starting postgres:15 on port ${PG_PORT}"
docker rm -f aladdin-wellness-pg 2>/dev/null || true
docker run -d --name aladdin-wellness-pg \
  -e POSTGRES_USER="${PG_USER}" \
  -e POSTGRES_PASSWORD="${PG_PASS}" \
  -e POSTGRES_DB="${PG_DB}" \
  -p "127.0.0.1:${PG_PORT}:5432" \
  postgres:15

sleep 3
export WELLNESS_PG_DSN="postgresql://${PG_USER}:${PG_PASS}@127.0.0.1:${PG_PORT}/${PG_DB}"
echo "WELLNESS_PG_DSN=${WELLNESS_PG_DSN}"
echo ">>> Apply schema"
cd "$(dirname "$0")/.."
PYTHONPATH=. python3 -c "
from security.services.ai_platform.wellness_store_postgres import ensure_schema
assert ensure_schema(), 'schema failed'
print('schema OK')
"
echo ">>> Add to /opt/aladdin-backend/.env:"
echo "WELLNESS_PG_DSN=${WELLNESS_PG_DSN}"
echo "WELLNESS_PG_DUAL_WRITE=1"
echo "WELLNESS_PG_READ=0"
