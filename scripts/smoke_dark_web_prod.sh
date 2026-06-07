#!/usr/bin/env bash
# Prod smoke: Dark Web API (no secrets printed). Run from dev machine with SSH key.
#
# Usage: ./scripts/smoke_dark_web_prod.sh [host]
#
set -euo pipefail

HOST="${1:-149.154.65.180}"
SSH_KEY="${SSH_KEY_PATH:-$HOME/.ssh/aladdin_server}"
SSH_OPTS=(-o BatchMode=yes -o IdentitiesOnly=yes -i "${SSH_KEY}")

ssh "${SSH_OPTS[@]}" "root@${HOST}" 'bash -s' <<'REMOTE'
set -e
BASE="http://127.0.0.1:8002"
DEVICE="dw_smoke_$(date +%s)"

echo "=== health ==="
curl -sS -m 8 "${BASE}/api/health"

echo ""
echo "=== register device ==="
REG=$(curl -sS -m 15 -X POST "${BASE}/api/auth/register-device" \
  -H "Content-Type: application/json" \
  -d "{\"device_id\":\"${DEVICE}\",\"deviceType\":\"ios\"}")
TOKEN=$(python3 -c "import json,sys; print(json.loads(sys.argv[1]).get('access_token',''))" "${REG}")
if [ -z "${TOKEN}" ]; then echo "NO TOKEN"; exit 1; fi
USER_ID=$(python3 -c "import jwt,sys; p=jwt.decode(sys.argv[1], options={'verify_signature':False}); print(p.get('user_id') or p.get('id') or p.get('sub'))" "${TOKEN}")
echo "user_id=${USER_ID}"

echo ""
echo "=== stats (expect 0/0/0) ==="
curl -sS "${BASE}/api/reports/dark-web/stats?user_id=${USER_ID}" | python3 -m json.tool

echo ""
echo "=== fast scan clean email (expect found:false without HIBP key) ==="
curl -sS -m 20 -X POST "${BASE}/api/reports/dark-web/scan/fast" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"clean-${DEVICE}@example.com\",\"method\":\"fast\"}" | python3 -m json.tool | head -25

echo ""
echo "=== secure scan pwned password SHA-1 (expect found:true, free HIBP) ==="
# SHA-1("password") — well-known pwned test vector
curl -sS -m 20 -X POST "${BASE}/api/reports/dark-web/scan/secure" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"passwordHash":"5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8","method":"secure"}' | python3 -m json.tool | head -25

echo ""
echo "=== HIBP key loaded? ==="
cd /opt/aladdin-backend
./venv/bin/python3 -c "from security.api.dark_web_scan_service import _hibp_api_key; v=_hibp_api_key(); print('HIBP:', 'SET' if v else 'EMPTY')"

echo ""
echo "OK: dark web prod smoke finished"
REMOTE
