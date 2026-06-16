#!/usr/bin/env bash
# Conditional SFM auto-remediation (af-smoke-06) — restart core only when unloaded.
set -euo pipefail

LOG_TAG="aladdin-sfm-auto-remediate"
SFM_STATUS_URL="${SFM_STATUS_URL:-http://127.0.0.1:8003/api/sfm/status}"

if ! curl -sf -m 5 "$SFM_STATUS_URL" >/tmp/sfm_remediate_status.json 2>/dev/null; then
  echo "${LOG_TAG} status unreachable — restarting aladdin-sfm-core" | systemd-cat -t "$LOG_TAG" -p warning
  systemctl restart aladdin-sfm-core.service
  sleep 16
  exit 0
fi

sfm_loaded=$(python3 -c "import json; print(str(json.load(open('/tmp/sfm_remediate_status.json')).get('sfm_loaded')).lower())")
if [[ "$sfm_loaded" == "true" ]]; then
  echo "${LOG_TAG} sfm_loaded=true — no restart needed" | systemd-cat -t "$LOG_TAG" -p info
  exit 0
fi

echo "${LOG_TAG} sfm_loaded=${sfm_loaded} — restarting aladdin-sfm-core" | systemd-cat -t "$LOG_TAG" -p warning
systemctl restart aladdin-sfm-core.service
sleep 16
if curl -sf -m 5 "$SFM_STATUS_URL" | python3 -c "import json,sys; d=json.load(sys.stdin); raise SystemExit(0 if d.get('sfm_loaded') else 1)"; then
  echo "${LOG_TAG} restart OK — sfm_loaded=true" | systemd-cat -t "$LOG_TAG" -p info
  exit 0
fi

echo "${LOG_TAG} restart FAILED — sfm still not loaded" | systemd-cat -t "$LOG_TAG" -p err
exit 1
