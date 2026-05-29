#!/usr/bin/env bash
# Hermes LLM watchdog — run from cron every minute on VPS (149.154.65.180).
# - Hermes binary present
# - Optional smoke chat (HERMES_WATCHDOG_SMOKE=1)
# - Key rotator: at least one key configured
#
# Install:
#   cp scripts/hermes_llm_watchdog.sh /opt/aladdin-backend/scripts/
#   chmod +x /opt/aladdin-backend/scripts/hermes_llm_watchdog.sh
#   echo '* * * * * root /opt/aladdin-backend/scripts/hermes_llm_watchdog.sh >> /var/log/aladdin-backend/hermes_watchdog.log 2>&1' \
#     > /etc/cron.d/aladdin-hermes-watchdog
#
set -euo pipefail

ROOT="${ALADDIN_BACKEND_ROOT:-/opt/aladdin-backend}"
HERMES_BIN="${HERMES_BIN:-${ROOT}/venv/bin/hermes}"
LOG_DIR="${LOG_DIR:-/var/log/aladdin-backend}"
mkdir -p "${LOG_DIR}"

ts() { date -u '+%Y-%m-%dT%H:%M:%SZ'; }

if [[ ! -x "${HERMES_BIN}" ]]; then
  echo "$(ts) FAIL hermes binary missing: ${HERMES_BIN}"
  exit 1
fi

cd "${ROOT}"
set -a
# shellcheck disable=SC1091
[[ -f .env ]] && source .env
set +a

if ! "${ROOT}/venv/bin/python3" - <<'PY'
from security.services.hermes_key_rotator import load_api_keys
keys = load_api_keys()
if not keys:
    raise SystemExit("no OPENROUTER keys (set HERMES_OPENROUTER_API_KEYS or HERMES_OPENROUTER_KEYS_FILE)")
print(f"keys={len(keys)}")
PY
then
  echo "$(ts) WARN no rotator keys configured"
  exit 2
fi

if [[ "${HERMES_WATCHDOG_SMOKE:-0}" == "1" ]]; then
  if ! timeout 45 "${HERMES_BIN}" chat -q "ping" -Q >/dev/null 2>"${LOG_DIR}/hermes_watchdog_smoke.err"; then
    err="$(head -c 400 "${LOG_DIR}/hermes_watchdog_smoke.err" 2>/dev/null || true)"
    echo "$(ts) FAIL hermes smoke: ${err}"
    exit 3
  fi
  echo "$(ts) OK hermes smoke"
else
  echo "$(ts) OK hermes binary + keys (smoke skipped; set HERMES_WATCHDOG_SMOKE=1 to enable)"
fi

exit 0
