#!/usr/bin/env bash
# Алерт: доля SFM fallback > порога за последний час (Phase 2.4).
set -euo pipefail

LOG="${COMPANION_LLM_METRICS_LOG:-/var/log/aladdin-backend/companion_llm.log}"
THRESHOLD_PCT="${COMPANION_LLM_SFM_ALERT_PCT:-3}"
WINDOW_SEC="${COMPANION_LLM_ALERT_WINDOW_SEC:-3600}"

if [[ ! -f "$LOG" ]]; then
  echo "WARN: log missing $LOG (no data yet)"
  exit 0
fi

NOW="$(date +%s)"
CUTOFF=$((NOW - WINDOW_SEC))

read -r TOTAL SFM <<< "$(python3 - "$LOG" "$CUTOFF" <<'PY'
import json, sys
path, cutoff = sys.argv[1], int(sys.argv[2])
total = sfm = 0
with open(path, encoding="utf-8", errors="ignore") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if int(row.get("ts", 0)) < cutoff:
            continue
        total += 1
        if row.get("llm_path") == "sfm":
            sfm += 1
print(total, sfm)
PY
)"

if [[ "${TOTAL:-0}" -lt 10 ]]; then
  echo "OK: sample too small (total=$TOTAL)"
  exit 0
fi

PCT=$((100 * SFM / TOTAL))
echo "companion_llm last_hour: total=$TOTAL sfm=$SFM pct=${PCT}% threshold=${THRESHOLD_PCT}%"

if [[ "$PCT" -ge "$THRESHOLD_PCT" ]]; then
  echo "ALERT: SFM fallback ${PCT}% >= ${THRESHOLD_PCT}% — check OpenRouter / Hermes"
  exit 2
fi
echo "OK"
exit 0
