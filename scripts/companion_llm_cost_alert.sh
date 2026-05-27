#!/usr/bin/env bash
# OPS-04 — early LLM cost alert (cron on VPS, e.g. hourly).
# Env: COMPANION_COST_ALERT_RUB_DAY (default 500), COMPANION_DB_PATH, optional TELEGRAM_BOT_TOKEN + CHAT_ID
set -euo pipefail

THRESHOLD_RUB="${COMPANION_COST_ALERT_RUB_DAY:-500}"
DB="${COMPANION_DB_PATH:-/opt/aladdin-backend/data/companion_platform.db}"
LOG="${COMPANION_COST_LOG:-/var/log/aladdin-backend/companion_llm_cost.log}"
mkdir -p "$(dirname "${LOG}")" 2>/dev/null || true

if [[ ! -f "${DB}" ]]; then
  echo "WARN: DB not found ${DB}" >&2
  exit 0
fi

ESTIMATE_RUB=$(python3 - <<'PY'
import os, sqlite3
db = os.environ.get("COMPANION_DB_PATH", "/opt/aladdin-backend/data/companion_platform.db")
conn = sqlite3.connect(db)
cur = conn.cursor()
# usage_counters: messages today × rough cost + voice seconds
try:
    cur.execute(
        "SELECT COALESCE(SUM(messages_today),0), COALESCE(SUM(voice_seconds_month),0) FROM usage_counters"
    )
    msgs, voice_sec = cur.fetchone() or (0, 0)
except sqlite3.OperationalError:
    msgs, voice_sec = 0, 0
conn.close()
# MVP heuristic (руб): ~0.05/msg + ~0.02/voice_min
cost = float(msgs) * 0.05 + (float(voice_sec) / 60.0) * 1.2
print(int(cost))
PY
)

echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) estimate_rub=${ESTIMATE_RUB} threshold=${THRESHOLD_RUB}" >> "${LOG}" 2>/dev/null || true

if [[ "${ESTIMATE_RUB}" -ge "${THRESHOLD_RUB}" ]]; then
  MSG="ALADDIN Companion LLM cost alert: ~${ESTIMATE_RUB} RUB (threshold ${THRESHOLD_RUB}/day). Check usage_counters and logs."
  echo "${MSG}" >&2
  if [[ -n "${TELEGRAM_BOT_TOKEN:-}" && -n "${TELEGRAM_CHAT_ID:-}" ]]; then
    curl -sS -m 10 -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
      -d "chat_id=${TELEGRAM_CHAT_ID}" --data-urlencode "text=${MSG}" >/dev/null || true
  fi
  exit 2
fi

echo "OK: estimate ${ESTIMATE_RUB} RUB < ${THRESHOLD_RUB}"
