#!/usr/bin/env bash
# R-08…R-10 + B-QA-03 runtime — VPS hub smokes + 24h mock grep
set -euo pipefail

HOST="${HUB_SMOKE_HOST:-root@149.154.65.180}"
SSH_KEY="${HUB_SMOKE_KEY:-$HOME/.ssh/aladdin_server}"
REMOTE="/opt/aladdin-backend"
PY="$REMOTE/venv/bin/python3"

ssh -i "$SSH_KEY" -o BatchMode=yes "$HOST" bash -s <<'REMOTE_SCRIPT'
set -euo pipefail
cd /opt/aladdin-backend
PY=/opt/aladdin-backend/venv/bin/python3

echo "=== antifake ==="
$PY docs/server/test_antifake_prod_smoke.py
echo "=== darkweb ==="
$PY docs/server/test_darkweb_prod_smoke.py
echo "=== identity ==="
$PY docs/server/test_identity_theft_prod_smoke.py
echo "=== mock grep 24h ==="
for u in aladdin-api aladdin-backend nginx; do
  c=$(journalctl -u "$u" --since "24 hours ago" 2>/dev/null | grep -cE "mock-real-protection|sfm_mock|sfm_stub" || true)
  echo "$u: $c"
done
REMOTE_SCRIPT

echo "OK: hub demo VPS smokes complete"
