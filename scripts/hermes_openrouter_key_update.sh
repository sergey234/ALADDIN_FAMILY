#!/usr/bin/env bash
# Обновить OPENROUTER_API_KEY на VPS (оба .env). Ключ передаётся через env, не в argv.
# Usage (on VPS): OPENROUTER_API_KEY='sk-or-...' ./hermes_openrouter_key_update.sh
set -euo pipefail

NEW_KEY="${OPENROUTER_API_KEY:-}"
if [[ -z "$NEW_KEY" ]]; then
  echo "Usage: OPENROUTER_API_KEY='sk-or-v1-...' $0"
  exit 1
fi

HERMES_ENV="/root/.hermes/.env"
BACKEND_ENV="/opt/aladdin-backend/.env"

for f in "$HERMES_ENV" "$BACKEND_ENV"; do
  if [[ ! -f "$f" ]]; then
    echo "WARN: skip missing $f"
    continue
  fi
  cp -a "$f" "${f}.bak.$(date +%Y%m%d-%H%M%S)"
  if grep -q '^OPENROUTER_API_KEY=' "$f"; then
    sed -i "s|^OPENROUTER_API_KEY=.*|OPENROUTER_API_KEY=${NEW_KEY}|" "$f"
  else
    echo "OPENROUTER_API_KEY=${NEW_KEY}" >> "$f"
  fi
  chmod 600 "$f"
  echo "Updated OPENROUTER_API_KEY in $f (backup created)"
done

systemctl restart aladdin-backend.service
sleep 3
curl -sS -m 8 http://127.0.0.1:8002/api/health
echo
"$(dirname "$0")/hermes_openrouter_key_check.sh" "$HERMES_ENV"
