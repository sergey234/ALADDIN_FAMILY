#!/usr/bin/env bash
# Production SFM smoke — every 15m (B-OPS-08)
set -euo pipefail
BACKEND="${ALADDIN_BACKEND_PATH:-/opt/aladdin-backend}"
LOG_TAG="aladdin-sfm-prod-smoke"

if ! bash "${BACKEND}/docs/server/sfm_truth_check.sh" >/tmp/sfm_smoke.json 2>/tmp/sfm_smoke.err; then
  echo "${LOG_TAG} FAIL $(cat /tmp/sfm_smoke.err)" | systemd-cat -t "$LOG_TAG" -p err
  if [[ -x "${BACKEND}/docs/server/sfm_auto_remediate.sh" ]]; then
    bash "${BACKEND}/docs/server/sfm_auto_remediate.sh" || true
    if bash "${BACKEND}/docs/server/sfm_truth_check.sh" >/tmp/sfm_smoke.json 2>/tmp/sfm_smoke.err; then
      echo "${LOG_TAG} recovered after auto-remediate" | systemd-cat -t "$LOG_TAG" -p warning
    else
      exit 1
    fi
  else
    exit 1
  fi
fi

# Do not use curl -f: SFM correctly returns HTTP 503 for unknown functions; -f exits 22.
HTTP=$(curl -s -m 5 -X POST http://127.0.0.1:8003/api/execute \
  -H 'Content-Type: application/json' \
  -d '{"function":"__smoke_nonexistent__","params":{}}' -w '%{http_code}' -o /tmp/sfm_unknown.json)
if [[ "$HTTP" != "503" ]]; then
  echo "${LOG_TAG} unknown-fn expected 503 got ${HTTP}" | systemd-cat -t "$LOG_TAG" -p err
  exit 2
fi

echo "${LOG_TAG} PASS $(cat /tmp/sfm_smoke.json)" | systemd-cat -t "$LOG_TAG" -p info
exit 0
