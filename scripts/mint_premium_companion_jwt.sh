#!/usr/bin/env bash
# Premium JWT — быстрый путь: mint на VPS (без 20s register-device).
#
# Usage:
#   export PREMIUM_TOKEN="$(./scripts/mint_premium_companion_jwt.sh)"
#   MINT_VIA_REGISTER=1 ./scripts/mint_premium_companion_jwt.sh  # медленный fallback
#
set -euo pipefail

SSH_HOST="${MINT_SSH_HOST:-149.154.65.180}"
SSH_USER="${MINT_SSH_USER:-root}"
SSH_KEY="${SSH_KEY_PATH:-$HOME/.ssh/aladdin_server}"
SSH_OPTS=(-o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=8)
[[ -f "${SSH_KEY}" ]] && SSH_OPTS+=(-i "${SSH_KEY}")

mint_via_ssh() {
  ssh "${SSH_OPTS[@]}" "${SSH_USER}@${SSH_HOST}" 'cd /opt/aladdin-backend && ./venv/bin/python3 -' <<'PY'
import os
import time
import jwt

secret = os.environ.get("JWT_SECRET")
if not secret:
    for line in open(".env"):
        if line.startswith("JWT_SECRET="):
            secret = line.strip().split("=", 1)[1].strip().strip('"').strip("'")
            break
if not secret:
    raise SystemExit("JWT_SECRET missing")

now = int(time.time())
payload = {
    "sub": "companion-premium-smoke",
    "type": "device_auth",
    "age_band": "parent",
    "app_id": "aladdin_family",
    "subscription": {"level": "premium", "limits": {"max_ai_messages": 1000, "voice_minutes_month": 120}},
    "subscription_level": "premium",
    "parent_consent": {
        "memory": True,
        "memory_enabled": True,
        "companion": True,
        "child_can_use_companion": True,
        "allowed_characters": ["unicorn", "aladdin", "genie"],
    },
    "iat": now,
    "exp": now + 3600,
}
alg = os.environ.get("JWT_ALGORITHM", "HS256")
print(jwt.encode(payload, secret, algorithm=alg))
PY
}

if [[ "${MINT_VIA_REGISTER:-0}" != "1" ]]; then
  mint_via_ssh
  exit 0
fi

BASE="${1:-https://aladdin-ai.ru}"
DEVICE_ID="companion-premium-mint-$(date +%s)"
RESP=$(curl -sS -m 12 -X POST "${BASE}/api/auth/register-device" \
  -H "Content-Type: application/json" \
  -d "{\"deviceId\":\"${DEVICE_ID}\",\"deviceType\":\"ios\"}")
TOKEN=$(echo "${RESP}" | python3 -c "import json,sys; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null || true)
LEVEL=$(echo "${TOKEN}" | cut -d. -f2 2>/dev/null | tr '_-' '/+' | python3 -c "
import sys, base64, json
s=sys.stdin.read().strip()
if not s:
    print('free'); sys.exit(0)
s += '=' * ((4 - len(s) % 4) % 4)
p=json.loads(base64.b64decode(s))
sub=p.get('subscription') or {}
print(sub.get('level') or p.get('subscription_level') or 'free')
" 2>/dev/null || echo "free")

if [[ "${LEVEL}" == "premium" && -n "${TOKEN}" ]]; then
  echo "${TOKEN}"
else
  mint_via_ssh
fi
