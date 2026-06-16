#!/usr/bin/env bash
# Family prod smoke with Level-A remediation: smoke → on FAIL restart API → smoke (×2).
#
# Insertion points:
#   1) systemd aladdin-family-prod-smoke.service (timer every 30 min)
#   2) deploy_family_backend.sh (post-deploy gate)
#
# Env: FAMILY_SMOKE_BASE, FAMILY_SMOKE_TIMESTAMP_FILE, FAMILY_REMEDIATE_NOTIFY=1

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${ROOT}"

PYTHON="${FAMILY_SMOKE_PYTHON:-./venv/bin/python3}"
SMOKE_SCRIPT="${FAMILY_SMOKE_SCRIPT:-docs/server/test_family_prod_smoke.py}"
RETRIES="${FAMILY_SMOKE_RETRY_AFTER_RESTART:-2}"
export FAMILY_SMOKE_BASE="${FAMILY_SMOKE_BASE:-http://127.0.0.1:8002}"
export FAMILY_SMOKE_TIMESTAMP_FILE="${FAMILY_SMOKE_TIMESTAMP_FILE:-/var/lib/aladdin/family_smoke_last_success.timestamp}"

run_smoke() {
  "${PYTHON}" "${SMOKE_SCRIPT}"
}

if run_smoke; then
  echo ">>> family_smoke_with_remediate: PASS (first try)"
  exit 0
fi

echo ">>> family_smoke_with_remediate: initial FAIL — restart API + retry (max ${RETRIES})"

for attempt in $(seq 1 "${RETRIES}"); do
  echo ">>> remediation attempt ${attempt}/${RETRIES}"
  "${SCRIPT_DIR}/family_auto_remediate.sh"
  if run_smoke; then
    echo ">>> family_smoke_with_remediate: RECOVERED after restart attempt ${attempt}"
    FAMILY_REMEDIATE_NOTIFY="${FAMILY_REMEDIATE_NOTIFY:-1}" \
      bash "${SCRIPT_DIR}/family_telegram_notify.sh" \
      "ALADDIN family: smoke recovered after API restart (attempt ${attempt}/${RETRIES})"
    exit 0
  fi
  echo ">>> family_smoke_with_remediate: still FAIL after attempt ${attempt}"
done

echo ">>> family_smoke_with_remediate: FAIL after ${RETRIES} restart retries — need human"
FAMILY_REMEDIATE_NOTIFY="${FAMILY_REMEDIATE_NOTIFY:-1}" \
  bash "${SCRIPT_DIR}/family_telegram_notify.sh" \
  "ALADDIN family: smoke FAIL after ${RETRIES} API restart retries — need developer"
exit 1
