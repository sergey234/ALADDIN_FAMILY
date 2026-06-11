#!/usr/bin/env bash
# SFM healthcheck — GATE-A honest probe (B-OPS-09)
set -euo pipefail
BACKEND="${ALADDIN_BACKEND_PATH:-/opt/aladdin-backend}"
CHECK="${BACKEND}/docs/server/sfm_truth_check.sh"

if [[ -x "$CHECK" ]]; then
  if bash "$CHECK" >/dev/null 2>&1; then
    echo "SFM healthcheck PASS"
    exit 0
  fi
fi

HEALTH=$(curl -sf -m 5 http://127.0.0.1:8003/api/health || echo '{}')
if echo "$HEALTH" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d.get('sfm_loaded') else 1)" 2>/dev/null; then
  echo "SFM healthcheck PASS (health)"
  exit 0
fi

echo "SFM healthcheck FAIL: $HEALTH" >&2
systemctl restart aladdin-sfm-core || true
exit 2
