#!/usr/bin/env bash
# Проверка OpenRouter API key (VPS или локально). Не печатает ключ.
set -euo pipefail

ENV_FILE="${1:-/root/.hermes/.env}"
if [[ ! -f "$ENV_FILE" ]]; then
  echo "FAIL: env file not found: $ENV_FILE"
  exit 1
fi

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

if [[ -z "${OPENROUTER_API_KEY:-}" ]]; then
  echo "FAIL: OPENROUTER_API_KEY empty in $ENV_FILE"
  exit 1
fi

RESP="$(curl -sS -m 15 https://openrouter.ai/api/v1/auth/key \
  -H "Authorization: Bearer ${OPENROUTER_API_KEY}")"

if echo "$RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); sys.exit(0 if d.get('data') else 1)" 2>/dev/null; then
  echo "OK: OpenRouter key valid ($(echo "$RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('label',''))" 2>/dev/null))"
  exit 0
fi

MSG="$(echo "$RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('error',{}).get('message','unknown'))" 2>/dev/null || echo "$RESP")"
echo "FAIL: OpenRouter key invalid — $MSG"
echo "Fix: create key at https://openrouter.ai/settings/keys then run scripts/hermes_openrouter_key_update.sh on VPS"
exit 1
